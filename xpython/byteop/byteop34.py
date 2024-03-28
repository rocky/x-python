# -*- coding: utf-8 -*-
"""Bytecode Interpreter operations for Python 3.4
"""
import inspect
import types

from xdis.opcodes.opcode_3x import parse_fn_counts_30_35
from xdis.version_info import IS_PYPY, PYTHON_VERSION_TRIPLE

from xpython.byteop.byteop24 import Version_info
from xpython.byteop.byteop32 import ByteOp32
from xpython.byteop.byteop33 import ByteOp33
from xpython.pyobj import Function

# Gone since 3.3
del ByteOp32.STORE_LOCALS


class ByteOp34(ByteOp33):
    def __init__(self, vm):
        super(ByteOp34, self).__init__(vm)
        self.version = "3.4.6 (default, Oct 27 1955, 00:00:00)\n[x-python]"
        # FIXME: should be a class
        self.version_info = Version_info(3, 4, 6, "final", 0)

    # New in 3.4

    def LOAD_CLASSDEREF(self, count):
        """
        Much like LOAD_DEREF but first checks the locals dictionary before
        consulting the cell. This is used for loading free variables in class
        bodies.
        """
        self.vm.push(self.vm.frame.cells[count].get())

    ##############################################################################
    # Order of function here is the same as in:
    # https://docs.python.org/3.4/library/dis.htmls#python-bytecode-instructions
    #
    ##############################################################################

    # Changed in 3.4

    # Python 3.4 __build_class__ is more strict about what can be a
    # function type whereas in earlier version we could get away with
    # our own kind of xpython.pyobj.Function object.
    #

    # Python 3.3 docs describe this but seem to follow pre-3.3
    # conventions (which go back to Python 2.x days).
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
        * the code associated with the function (at TOS1)
        * the qualified name of the function (at TOS)
        """

        default_count, kw_default_count, annotate_count = parse_fn_counts_30_35(argc)

        name = self.vm.pop()
        code = self.vm.pop()
        if annotate_count:
            annotate_names = self.vm.pop()
            # annotate count includes +1 for the above names
            annotate_objects = self.vm.popn(annotate_count - 1)
            n = len(annotate_objects)
            # We can annotate a function return value, but
            # that does is not a parameter object and not
            # listed in annotate_objects
            if annotate_names[-1] == "return":
                assert n == len(annotate_names) - 1
            else:
                assert n == len(annotate_names)
            annotations = {annotate_names[i]: annotate_objects[i] for i in range(n)}
        else:
            annotations = {}

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
            # FIXME: figure out qualname
        )

        if (
            inspect.iscode(code)
            and self.version[:2] == PYTHON_VERSION_TRIPLE[:2]
            and self.is_pypy == IS_PYPY
        ):
            # Python 3.4 __build_class__ is more strict about what can be a
            # function type whereas in earlier version we could get away with
            # our own kind of xpython.pyobj.Function object.

            native_fn = types.FunctionType(code, globs, name, tuple(defaults))
            native_fn.__kwdefaults__ = kwdefaults
            native_fn.__annotations__ = annotations
            self.vm.fn2native[fn] = native_fn

        self.vm.push(fn)
