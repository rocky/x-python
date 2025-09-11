"""A variant of VirtualMachine that adds a callback.
This can be used in a debugger or profiler.
"""

import logging
from types import TracebackType

from xdis import IS_PYPY, PYTHON_VERSION_TRIPLE, codeType2Portable

# We will add a new "DEBUG" opcode
from xdis.opcodes.base import def_op

from xpython.pyobj import Frame, Traceback, traceback_from_frame
from xpython.vm import PyVM, PyVMError, PyVMUncaughtException, byteint, format_instruction

log = logging.getLogger(__name__)


BREAKPOINT_OP = 8

PyVMEVENT_INSTRUCTION = 1  # tracing an instruction
PyVMEVENT_LINE = (
    2  # tracing an instruction which has has a line number. Above includes this.
)
PyVMEVENT_CALL = 4  # tracing calls. Note "Step over" disables this kind of trace
PyVMEVENT_RETURN = 8  # tracing returns
PyVMEVENT_EXCEPTION = 16  # tracing exceptions
PyVMEVENT_YIELD = 32  # tracing "yield"
PyVMEVENT_FATAL = 64  # Final fatal error
PyVMEVENT_STEP_OVER = 128  # tracing using step over - don't trace into calls

PyVMEVENT_FLAG_NAMES = {
    1: "instruction",
    2: "line",
    4: "call",
    8: "return",
    16: "exception",
    32: "yield",
    64: "fatal",
    128: "step_over",
}

PyVMEVENT_FLAG_BITS = {name: bit for bit, name in PyVMEVENT_FLAG_NAMES.items()}

# All flags except STEP_OVER which is a kind of negation
PyVMEVENT_ALL = (
    PyVMEVENT_INSTRUCTION
    | PyVMEVENT_LINE
    | PyVMEVENT_CALL
    | PyVMEVENT_RETURN
    | PyVMEVENT_EXCEPTION
    | PyVMEVENT_YIELD
    | PyVMEVENT_FATAL
)

# All flags cleared
PyVMEVENT_NONE = 0


def pretty_event_flags(flags) -> str:
    """Return pretty representation of trace event flags."""
    names = []
    result = f"0x{flags:08x}"
    for i in range(32):
        flag = 1 << i
        if flags & flag:
            names.append(PyVMEVENT_FLAG_NAMES.get(flag, hex(flag)))
            flags ^= flag
            if not flags:
                break
    else:
        names.append(hex(flags))
    names.reverse()
    return f"{result} ({' | '.join(names)})"


class PyVMTraced(PyVM):
    def __init__(
        self,
        callback,
        python_version: tuple[int, ...]=PYTHON_VERSION_TRIPLE,
        is_pypy: bool=IS_PYPY,
        vmtest_testing: bool=False,
        event_flags: int=PyVMEVENT_ALL,
        format_instruction_func=format_instruction,
    ) -> None:
        super().__init__(
            python_version,
            is_pypy,
            vmtest_testing,
            format_instruction_func=format_instruction_func,
        )
        self.event_flags = event_flags
        self.callback = callback
        # Add a new opcode to allow us high-speed breakpoints

        # FIXME: older xdis uses  "self.opc.l" instead of "self.opc.loc"
        if not hasattr(self.opc, "loc"):
            if hasattr(self.opc, "l"):
                self.opc.loc = self.opc.l
        def_op(self.opc.loc, "BRKPT", BREAKPOINT_OP, 0, 0)

    def add_breakpoint(self, frame: Frame, offset: int) -> None:
        """
        Adds a breakpoint at `offset` of `frame`. This is done by modifying the
        bytecode opcode at the given offset by replacing it with a pseudo-op BRKPT
        instruction. The old opcode is squirreled a way though.
        """
        # FIXME: to be more useful we need to work on a code object, and modified code
        # objects  then get replaced when creating frames.
        # Convert code to something we can change, then
        # Convert its bytecode bytes to a list, update the list and replace this back in
        # the code.
        code = codeType2Portable(frame.f_code, self.version)
        frame.brkpt[offset] = code.co_code[offset]
        bytecode = list(code.co_code)
        bytecode[offset] = BREAKPOINT_OP
        code.co_code = bytes(bytecode)
        frame.f_code = code

    def remove_breakpoint(self, frame: Frame, offset: int) -> None:
        """
        Removes a breakpoint at `offset` of `frame`. This is done by restoring the
        opcode that was previously smashed using `add_breakpoint()`
        """
        # Convert code to something we can change, then
        # Convert its bytecode ytes to a list, update the list and replace this back in
        # the code.
        code = frame.f_code
        bytecode = list(code.co_code)
        bytecode[offset] = frame.brkpt[offset]
        code.co_code = bytes(bytecode)

    # FIXME: put callback in f_trace, and update it accordingly
    # Interpreter main loop
    # This is analogous to CPython's _PyEval_EvalFrameDefault() (in 3.x newer Python)
    # or eval_frame() in older 2.x code.
    def eval_frame(self, frame: Frame) -> None:
        """Run a frame until it returns (somehow).

        Exceptions are raised, the return value is returned.

        This code includes frame tracing (ftrace) support used in debugging. For code
        without tracing see the corresponding code in vm.py.
        """

        # Extra tracing code
        if self.frame:
            # Inherit values from self.frame
            frame.f_trace = self.frame.f_trace
            frame.event_flags = self.frame.event_flags
        else:
            # Get (presumably initial) values from vm
            frame.f_trace = self.callback
            frame.event_flags = self.event_flags

        if frame.event_flags & PyVMEVENT_STEP_OVER:
            frame.event_flags = PyVMEVENT_NONE

        result = None
        # End extra tracing code

        self.f_code = frame.f_code
        if frame.f_lasti == -1:
            # We were started new, not yielded back from.
            frame.f_lasti = 0
            # Don't increment before fetching next instruction.
            frame.fallthrough = False
            byte_code = None

            # Extra tracing code #
            last_i = frame.f_back.f_lasti if frame.f_back else -1
            self.push_frame(frame)
            if frame.f_trace and (frame.event_flags & PyVMEVENT_CALL):
                if frame.event_flags & PyVMEVENT_STEP_OVER:
                    # Since we are about to enter a function, but not
                    # tracing it, clear return-like events return and
                    # yield
                    frame.event_flags &= ~(PyVMEVENT_RETURN | PyVMEVENT_YIELD)
                else:
                    result = frame.f_trace(
                        "call",
                        last_i,
                        "CALL",
                        byte_code,
                        frame.f_lineno,
                        None,
                        [],
                        self,
                    )
                pass
            # End extra tracing code #
        else:
            byte_code = byteint(frame.f_code.co_code[frame.f_lasti])
            self.push_frame(frame)
            if frame.f_trace and frame.event_flags & PyVMEVENT_YIELD:
                result = frame.f_trace(
                    "yield",
                    frame.f_lasti,
                    "YIELD_VALUE",
                    self.opc.YIELD_VALUE,
                    frame.f_lineno,
                    None,
                    [],
                    self,
                )
                pass
            # byte_code == opcode["YIELD_VALUE"]?

        # FIXME: DRY with BRKPT op code
        if result:
            if result == "finish":
                frame.f_trace = None
                frame.event_flags = PyVMEVENT_RETURN | PyVMEVENT_YIELD
            elif result == "return":
                return self.return_value

        self.frame.linestarts = dict(
            self.opc.findlinestarts(frame.f_code, dup_lines=True)
        )

        offset = 0
        while True:
            (
                bytecode_name,
                byte_code,
                int_arg,
                arguments,
                offset,
                line_number,
            ) = self.parse_byte_and_args(byte_code)

            if log.isEnabledFor(logging.INFO):
                self.log(bytecode_name, int_arg, arguments, offset, line_number)

            if (
                frame.f_trace
                and line_number is not None
                and frame.event_flags & (PyVMEVENT_LINE | PyVMEVENT_INSTRUCTION)
            ):
                result = frame.f_trace(
                    "line",
                    offset,
                    bytecode_name,
                    byte_code,
                    line_number,
                    int_arg,
                    arguments,
                    self,
                )
            elif frame.f_trace and frame.event_flags & PyVMEVENT_INSTRUCTION:
                result = frame.f_trace(
                    "instruction",
                    offset,
                    bytecode_name,
                    byte_code,
                    line_number,
                    int_arg,
                    arguments,
                    self,
                )
            else:
                result = True

            if result is None:
                # As per https://docs.python.org/3/library/sys.html#sys.settrace
                # None indicates turning off tracing in this scope.
                # We could imagine a fancier code organization where we use
                # eval_frame() of PyVM instead of PyVMTrace, but save that for later.
                frame.event_flags = 0
            elif callable(result):
                pass
            elif isinstance(result, str):
                if result == "skip":
                    # Don't run instruction
                    continue
                elif result == "return":
                    # Immediate return with value
                    why = result
                    break
                elif result == "finish":
                    # Continue execution without tracing
                    frame.f_trace = None

            # When unwinding the block stack, we need to keep track of why we
            # are doing it.
            why = self.dispatch(bytecode_name, int_arg, arguments, offset, line_number)

            if why == "exception":
                # Deal with exceptions encountered while executing the op.
                # TODO: ceval calls PyTraceBack_Here, not sure what that does.

                if self.version >= (3, 11):
                    self.exception_handling_311()

                if not self.in_exception_processing:
                    self.last_traceback = traceback_from_frame(self.frame)
                    self.in_exception_processing = True

            elif why == "reraise":
                why = "exception"
                if self.version >= (3, 11):
                    self.exception_handling_311()


            if why != "yield":
                while why and frame.block_stack:
                    # Deal with any block management we need to do.
                    why = self.manage_block_stack(why)

            if why:
                break

            pass  # while True

        # Extra tracing code...
        callback = frame.f_trace or self.callback
        if why == "exception":
            if (
                callback
                and frame
                and (not frame or frame.event_flags & PyVMEVENT_EXCEPTION)
            ):
                frame.f_trace(
                    "exception",
                    offset,
                    bytecode_name,
                    byte_code,
                    line_number,
                    int_arg,
                    self.last_exception,
                    self,
                )
            elif callback and (not frame or frame.event_flags & PyVMEVENT_RETURN):
                callback(
                    "return",
                    offset,
                    bytecode_name,
                    byte_code,
                    line_number,
                    int_arg,
                    self.return_value,
                    self,
                )
            pass
        # End extra tracing code

        # TODO: handle generator exception state

        self.pop_frame()

        if why == "exception":
            last_exception = self.last_exception
            if last_exception and last_exception[0]:
                if isinstance(last_exception[2], (Traceback, TracebackType)):
                    if not self.frame:
                        if isinstance(last_exception, tuple):
                            self.last_exception = PyVMUncaughtException.from_tuple(
                                last_exception
                            )
                        raise self.last_exception
                    else:
                        raise last_exception[0]
                    pass
                pass
            else:
                raise PyVMError("Borked exception recording")
            # if self.exception and .... ?
            # log.error("Haven't finished traceback handling, nulling traceback "
            #            "information for now")
            # six.reraise(self.last_exception[0], None)

        self.in_exception_processing = False

        # Extra tracing code:
        if callback and frame.event_flags & PyVMEVENT_RETURN:
            callback(
                "return",
                offset,
                bytecode_name,
                byte_code,
                line_number,
                None,
                self.return_value,
                self,
            )

        return self.return_value


if __name__ == "__main__":

    def sample_callback_hook(
        event, offset, bytecode_name, byte_code, line_number, int_arg, event_arg, vm
    ) -> None:
        print(
            "CALLBACK",
            event,
            offset,
            bytecode_name,
            byte_code,
            line_number,
            int_arg,
            event_arg,
        )

    # Simplest of tests
    def five() -> int:
        return 5

    # Test with a conditional in it
    a, b = 10, 3

    def mymax() -> int:
        return a if a > b else b

    logging.basicConfig(level=logging.DEBUG)
    vm = PyVMTraced(sample_callback_hook)
    frame = vm.make_frame(five.__code__)
    vm.add_breakpoint(frame, 0)
    print("five() is", vm.eval_frame(frame))
    frame.f_lasti = -1  # Reset where we were
    vm.remove_breakpoint(frame, 0)
    print("five() is now", vm.eval_frame(frame))
    print(vm.run_code(mymax.__code__, f_globals=globals(), f_locals=locals()))
