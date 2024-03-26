# -*- coding: utf-8 -*-
"""Byte Interpreter operations for Python 3.3
"""

from xdis.opcodes.opcode_3x import parse_fn_counts_30_35
from xpython.byteop.byteop24 import Version_info
from xpython.byteop.byteop32 import ByteOp32
from xpython.pyobj import Function, Generator


class ByteOp33(ByteOp32):
    def __init__(self, vm):
        super(ByteOp33, self).__init__(vm)
        self.version = "3.3.7 (default, Oct 27 1955, 00:00:00)\n[x-python]"
        self.version_info = Version_info(3, 3, 7, "final", 0)

    def MAKE_CLOSURE(self, argc):
        """
        Creates a new function object, sets its ``__closure__`` slot, and
        pushes it on the stack. TOS is the code qualified name of the
        function, TOS is the code associated with the function and
        TOS1 is the tuple containing cells for the closure's free
        variables. The function also has ``argc`` default parameters,
        which are found below the cells.
        """
        default_count, kw_default_count, annotate_count = parse_fn_counts_30_35(argc)
        code, name = self.vm.popn(2)
        closure = self.vm.pop()

        if kw_default_count:
            kw_default_pairs = self.vm.popn(2 * kw_default_count)
            kwdefaults = dict(
                kw_default_pairs[i : i + 2] for i in range(0, len(kw_default_pairs), 2)
            )
        else:
            kwdefaults = {}

        if default_count:
            defaults = self.vm.popn(default_count)
        else:
            defaults = tuple()

        if annotate_count:
            annotate_names = self.vm.pop()
            annotate_types = self.vm.popn(annotate_count)
            n = len(annotate_names)
            assert n == len(annotate_types)
            annotations = {annotate_names[i]: annotate_types[i] for i in range(n)}
        else:
            annotations = {}

        # FIXME: DRY with code in MAKE_FUNCTION

        globs = self.vm.frame.f_globals

        fn = Function(
            name=name,
            code=code,
            globs=globs,
            argdefs=tuple(defaults),
            closure=closure,
            vm=self.vm,
            kwdefaults=kwdefaults,
            annotations=annotations,
        )

        self.vm.push(fn)

    # Changed from 3.2; 3.3 adds annotations.
    def MAKE_FUNCTION(self, argc):
        """
        Pushes a new function object on the stack. From bottom to top, the consumed
        stack must consist of:

        * argc & 0xFF default argument objects in positional order
        * (argc >> 8) & 0xFF pairs of name and default argument, with the name just
          below the object on the stack, for keyword-only parameters
        * (argc >> 16) & 0x7FFF parameter annotation objects
        * a tuple listing the parameter names for the annotations (only if there are
          only annotation objects)
        * the code associated with the function (at TOS1 if 3.3+ else at TOS for
          3.0..3.2)
        * the qualified name of the function (at TOS if 3.3+)
        """
        default_count, kw_default_count, annotate_count = parse_fn_counts_30_35(argc)

        # The string function name does not seem to be used.
        # In the 3.4, it is dropped.
        self.vm.pop()
        code = self.vm.pop()
        name = code.co_name

        if kw_default_count:
            kw_default_pairs = self.vm.popn(2 * kw_default_count)
            kwdefaults = dict(
                kw_default_pairs[i : i + 2] for i in range(0, len(kw_default_pairs), 2)
            )
        else:
            kwdefaults = {}

        if annotate_count:
            annotate_names = self.vm.pop()
            annotate_objects = self.vm.popn(annotate_count)
            n = len(annotate_objects)
            assert n == len(annotate_names)
            annotations = {annotate_names[i]: annotate_objects[i] for i in range(n)}
        else:
            annotations = {}

        if default_count:
            defaults = self.vm.popn(default_count)
        else:
            defaults = tuple()

        # FIXME: DRY with code in byteop3{2,6}.py

        globs = self.vm.frame.f_globals

        fn = Function(
            name=name,
            code=code,
            globs=globs,
            argdefs=tuple(defaults),
            closure=None,
            vm=self.vm,
            kwdefaults=kwdefaults,
            annotations=annotations,
        )

        self.vm.push(fn)

    def YIELD_FROM(self):
        """
        Pops TOS and delegates to it as a subiterator from a generator.
        """
        u = self.vm.pop()
        x = self.vm.top()

        try:
            if not isinstance(x, Generator) or u is None:
                # Call next on iterators.
                retval = next(x)
            else:
                retval = x.send(u)
            self.vm.return_value = retval
        except StopIteration as e:
            self.vm.pop()
            self.vm.push(e.value)
        else:
            # FIXME: The code has the effect of rerunning the last instruction.
            # I'm not sure if or why it is correct.
            if self.vm.version >= (3, 6):
                self.vm.jump(self.vm.frame.f_lasti - 2)
            else:
                self.vm.jump(self.vm.frame.f_lasti - 1)
            return "yield"

    # Python 3.3 docs describe a 3.4 MAKE_FUNCTION but seem to follow pre-3.3
    # conventions (which go back to Python 2.x days).
    # def MAKE_FUNCTION(self, argc):


if __name__ == "__main__":
    x = ByteOp33(None)
