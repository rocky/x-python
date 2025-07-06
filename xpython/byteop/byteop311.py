# -*- coding: utf-8 -*-
# Copyright (C) 2023-2025 Rocky Bernstein
# This program comes with ABSOLUTELY NO WARRANTY.
# This is free software, and you are welcome to redistribute it
# under certain conditions.
# See the documentation for the full license.
"""Bytecode Interpreter operations for Python 3.11
"""

import inspect
from typing import Tuple

from xdis.version_info import PYTHON_VERSION_TRIPLE

from xpython.byteop.byteop24 import Version_info
from xpython.byteop.byteop36 import (
    COMPREHENSION_FN_NAMES,
    MAKE_FUNCTION_SLOT_NAMES,
    MAKE_FUNCTION_SLOTS,
)
from xpython.byteop.byteop37 import NULL
from xpython.byteop.byteop310 import ByteOp310
from xpython.pyobj import Function


def fmt_load_global(vm, arg, repr_fn=repr) -> str:
    """
    returns the name of the function from the code object in the stack
    """
    namei =  vm.f_code.co_names[arg >> 1]
    return ' (NULL + %s)' % namei if arg & 1 else namei


def fmt_make_function(vm, _=None, repr_fn=repr) -> str:
    """
    returns the name of the function from the code object in the stack
    """
    fn_item = vm.top
    name = fn_item.co_name
    return " (%s)" % name


# pylint: disable=too-many-public-methods
class ByteOp311(ByteOp310):
    """
    Python 3.11 Opcodes
    """
    def __init__(self, vm):
        super(ByteOp310, self).__init__(vm)
        self.stack_fmt["LOAD_GLOBAL"] = fmt_load_global
        self.stack_fmt["MAKE_FUNCTION"] = fmt_make_function
        self.hexversion = 0x30A00F0
        self.version = "3.11.0 (default, Oct 27 1955, 00:00:00)\n[x-python]"
        self.version_info = Version_info(3, 11, 0, "final", 0)

    def is_method(self, argc: int) -> bool:
        """
        Translation of ceval.c is_method() macro:
            #define is_method(stack_pointer, args) (PEEK((args)+2) != NULL)
        and Py_TYPE(function) == &PyMethod_Type)
        """
        function = self.vm.peek(argc + 1)
        return self.vm.peek(argc + 2) is not NULL and inspect.ismethod(function)

    # Added in 3.11...

    # New in 3.11.  Note: below, the parameter mentioned in the
    # docstring is "delta", but the parameter name is "offset", a valu
    # taht value has been adjusted from a relative number divided by two into and
    # absolute offset.
    def CACHE(self):
        """
        Rather than being an actual instruction, this opcode is
        used to mark extra space for the interpreter to cache useful
        data directly in the bytecode itself. It is automatically
        hidden by all dis utilities, but can be viewed with
        show_caches=True.
        """
        return

    # This is handled by the caller.
    # def BINARY_OP(self, op: int):
    #     """
    #       Implements the binary and in-place operators (depending on the value of op):

    #       rhs = STACK.pop()
    #       lhs = STACK.pop()
    #       STACK.append(lhs op rhs)

    #       New in version 3.11.
    #       TOS is a tuple of mapping keys, and TOS1 is the match
    #       subject. Replace TOS with a dict formed from the items of TOS1, but
    #       without any of the keys in TOS.
    #     """
    #     rhs = self.vm.pop()
    #     lhs = self.vm.pop()
    #     self.vm.push(len(self.vm.pop()))
    #     raise self.vm.PyVMError("MATCH_COPY_DICT_WITHOUT_KEYS not implemented")

    def CALL(self, argc: int):
        """Calls a callable object with the number of arguments
        specified by argc, including the named arguments specified by
        the preceding KW_NAMES, if any. On the stack are (in ascending
        order), either:

        * NULL
        * The callable
        * The positional arguments
        * The named arguments

        or:

        * The callable
        * self
        * The remaining positional arguments
        * The named arguments

        argc is the total of the positional and named arguments,
        excluding self when a NULL is not present.

        CALL pops all arguments and the callable object off the stack,
        calls the callable object with those arguments, and pushes the
        return value returned by the callable object.

        Replaces CALL_FUNCTION

        """
        total_args = argc + 1 if self.is_method(argc) else argc
        # FIXME: figure out how to set this
        kw_names_len = len(self.vm.frame.call_shape_kwnames)
        named_args = self.vm.frame.call_shape_kwnames
        positional_args = total_args - kw_names_len
        pos_args = self.vm.popn(positional_args)
        function = self.vm.pop()
        # C interpreter checks for inlining here.
        # We will skip this.

        if not self.vm.is_empty_stack:
            if self.vm.top is NULL:
                self.vm.pop()  # Remove NULL
            # else ???

        ret_val = self.call_function_with_args_resolved(function, pos_args, named_args)

        # Clear names set by KW_NAMES
        self.vm.frame.call_shape_kwnames = {}
        return ret_val

    def KW_NAMES(self, names: Tuple[str]):
        """
        Prefixes CALL. Stores a reference to co_consts[consti] into an internal frame variable
        call_shape.
        for use by CALL. names is a tuple of strings.

        Replaces CALL_FUNCTION_KW
        """

        for name in names:
            self.vm.frame.call_shape_kwnames[name] = self.vm.pop()
        return

    # Changed in 3.11...
    def LOAD_GLOBAL(self, name, push_null: bool=False):
        """
        Loads the global named co_names[namei>>1] onto the stack.

        Note: name = co_names[namei] set in parse_byte_and_args()

        If the low bit of namei is set, then a NULL is pushed to the stack before the global variable.
        """
        f = self.vm.frame
        if name in f.f_globals:
            val = f.f_globals[name]
        elif name in f.f_builtins:
            val = f.f_builtins[name]
        else:
            raise NameError("global name '%s' is not defined" % name)

        if push_null:
            self.vm.push(NULL)

        self.vm.push(val)

    def MAKE_FUNCTION(self, argc: int):
        """
        Pushes a new function object on the stack. From bottom to top,
        the consumed stack must consist of values if the argument
        carries a specified flag value

        * 0x01 a tuple of default values for positional-only and positional-or-keyword
          parameters in positional order
        * 0x02 a dictionary of the default values for the keyword-only parameters
               the key is the parameter name and the value is the default value
        * 0x04 a tuple of strings containing parameters  annotations
        * 0x08 a tuple containing cells for free variables, making a closure
          the code associated with the function (at TOS1)

        Changed from version 3.10: Qualified name at STACK[-1] was removed.
        """
        code = self.vm.pop()

        slot = {
            "defaults": tuple(),
            "kwdefaults": {},
            "annotations": tuple(),
            "closure": tuple(),
        }
        assert 0 <= argc < (1 << MAKE_FUNCTION_SLOTS)
        have_param = list(
            reversed([True if 1 << i & argc else False for i in range(4)])
        )
        for i in range(MAKE_FUNCTION_SLOTS):
            if have_param[i]:
                slot[MAKE_FUNCTION_SLOT_NAMES[i]] = self.vm.pop()

        # FIXME: DRY with code in byteop3{2,4,6}.py

        globs = self.vm.frame.f_globals

        if (
            not inspect.iscode(code)
            and hasattr(code, "to_native")
            and self.version_info[:2] == PYTHON_VERSION_TRIPLE[:2]
        ):
            code = code.to_native()

        # Convert annotations tuple into dictionary
        annotations = {}
        annotations_tup = slot["annotations"]
        for i in range(0, len(annotations_tup), 2):
            annotations[annotations_tup[i]] = annotations_tup[i + 1]

        fn_vm = Function(
            name=code.co_name,
            code=code,
            globs=globs,
            argdefs=slot["defaults"],
            closure=slot["closure"],
            vm=self.vm,
            qualname=code.co_qualname,
            kwdefaults=slot["kwdefaults"],
            annotations=annotations,
        )

        if argc == 0 and code.co_name in COMPREHENSION_FN_NAMES:
            fn_vm.has_dot_zero = True

        if fn_vm._func:
            self.vm.fn2native[fn_vm] = fn_vm._func

        self.vm.push(fn_vm)

    def PRECALL(self, argc: int):
        """
         `meth` is NULL when LOAD_METHOD thinks that it's not
         a method call.

         Stack layout:

                ... | NULL | callable | arg1 | ... | argN
                                                     ^- TOP()
                                        ^- (-oparg)
                             ^- (-oparg-1)
                      ^- (-oparg-2)

        `callable` will be popped by ``call_function``.
         NULL will will be popped manually later.
         If `meth` isn't NULL, it's a method call.  Stack layout:

              ... | method | self | arg1 | ... | argN
                                                 ^- TOP()
                                    ^- (-oparg)
                             ^- (-oparg-1)
                    ^- (-oparg-2)

        `self` and `method` will be popped by ``call_function``.
         We'll be passing `oparg + 1` to call_function, to
         make it accept the `self` as a first argument.

        """
        n_args = argc + 1 if self.is_method(argc) else argc
        function = self.vm.peek(n_args + 1)
        if inspect.ismethod(function):
            pass
        return

    def PUSH_NULL(self):
        """Pushes a NULL to the stack. Used in the call sequence to
        match the NULL pushed by LOAD_METHOD for non-method calls.

        """
        self.vm.push(NULL)

    def COPY(self, i: int):
        """
        Push the i-th item to the top of the stack. The item is not removed from its
        original location.
        """
        stack_i = self.vm.peek(i)
        self.vm.push(stack_i)

    def SWAP(self, i: int):
        """
        Swap TOS with the item at position i.
        2 swaps TOS with TOS1, 3 swaps TOS with TOS2, etc.
        """
        tos = self.vm.top
        stack_i = self.vm.peek(i)

        self.vm.set(i, tos)
        self.vm.set(1, stack_i)  # 1 is TOS

    def CHECK_EXC_MATCH(self):
        """Performs exception matching for except. Tests whether the
        TOS1 is an exception matching TOS. Pops TOS and pushes the
        boolean result of the test.

        TOS is usually the exception in an `except` cluase of a `try` block,
        while TOS1 is usually the exception that got raised.

        For "exception matching" use isinstance(TOS1 TOS.__class__) so superclasses
        """
        tos1, tos = self.vm.popn(2)
        self.vm.push(isinstance(tos, tos.__class__))

    def JUMP_BACKWARD(self, offset: int):
        """
        Decrements bytecode counter by delta. Checks for interrupts.
        """
        self.vm.jump(offset)

    def POP_JUMP_BACKWARD_NO_INTERRUPT(self, offset: int):
        """
        Decrements bytecode counter by delta. Does not check for interrupts.
        """
        self.vm.jump(offset)

    def POP_JUMP_FORWARD_IF_TRUE(self, offset: int):
        """
        If TOS is true, increments the bytecode counter by delta. TOS is popped.
        """
        val = self.vm.pop()
        if val == True:  # noqa
            self.vm.jump(offset)

    def POP_JUMP_BACKWARD_IF_TRUE(self, offset: int):
        """
        If TOS is true, decrements the bytecode counter by delta. TOS is popped.
        """
        val = self.vm.pop()
        if val == True:  # noqa
            self.vm.jump(offset)

    def POP_JUMP_FORWARD_IF_FALSE(self, offset: int):
        """
        If TOS is false, increments the bytecode counter by delta. TOS is popped.
        """
        val = self.vm.pop()
        if val == False:  # noqa
            self.vm.jump(offset)

    def POP_JUMP_BACKWARD_IF_FALSE(self, offset: int):
        """
        If TOS is false, decrements the bytecode counter by delta. TOS is popped.
        """
        val = self.vm.pop()
        if val == False:  # noqa
            self.vm.jump(offset)

    def POP_JUMP_FORWARD_IF_NOT_NONE(self, offset: int):
        """
        If TOS is not None, increments the bytecode counter by delta. TOS is popped.
        """
        val = self.vm.pop()
        if val is not None:
            self.vm.jump(offset)

    def POP_JUMP_BACKWARD_IF_NOT_NONE(self, offset: int):
        """
        If TOS is not None, decrements the bytecode counter by delta. TOS is popped.
        """
        val = self.vm.pop()
        if val is not None:
            self.vm.jump(offset)

    def POP_JUMP_FORWARD_IF_NONE(self, offset: int):
        """
        If TOS is not None, increments the bytecode counter by delta. TOS is popped.
        """
        val = self.vm.pop()
        if val is None:
            self.vm.jump(offset)

    def POP_JUMP_BACKWARD_IF_NONE(self, offset: int):
        """
        If TOS is not None, decrements the bytecode counter by delta. TOS is popped.
        """
        val = self.vm.pop()
        if val is None:
            self.vm.jump(offset)

    def PUSH_EXC_INFO(self):
        """Pops a value from the stack. Pushes the current exception
        to the top of the stack. Pushes the value originally popped
        back to the stack. Used in exception handlers.
        """
        val = self.vm.pop()
        self.vm.push(self.vm.last_exception)
        self.vm.push(val)


    def RESUME(self, where: int):
        """
        A no-op. Performs internal tracing, debugging and optimization checks.

        The where operand marks where the RESUME occurs:

          0 The start of a function
          1 After a yield expression
          2 After a yield from expression
          3 After an await expression        To be continued...
        """
        return
