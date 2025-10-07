# -*- coding: utf-8 -*-
# Copyright (C) 2025 Rocky Bernstein
# This program comes with ABSOLUTELY NO WARRANTY.
# This is free software, and you are welcome to redistribute it
# under certain conditions.
# See the documentation for the full license.
"""Bytecode Interpreter operations for Python 3.12
"""

from xpython.byteop.byteop24 import Version_info
from xpython.byteop.byteop311 import ByteOp311
from xpython.byteop.byteop37 import NULL


# pylint: disable=too-many-public-methods
class ByteOp312(ByteOp311):
    """
    Python 3.12 Opcodes
    """
    def __init__(self, vm):
        super().__init__(vm)
        self.hexversion = 0x30c03f0
        self.version = "3.12.0 (default, Oct 27 1955, 00:00:00)\n[x-python]"
        self.version_info = Version_info(3, 12, 0, "final", 0)

    # Added in 3.12...
    def BINARY_SLICE(self):
        """
        Implements:
          end = STACK.pop()
          start = STACK.pop()
          container = STACK.pop()
          STACK.append(container[start:end])

        Pushes a slice object on the stack. slice(TOS1, TOS) is pushed.
        """
        container, start, stop = self.vm.popn(3)
        self.vm.push(container[slice(start, stop)])

    def INTERPRETER_EXIT(self):
        """
        To be continued...
        """
        # FIXME
        raise self.vm.PyVMError("INTERPRETER_EXIT not implemented")

    def END_FOR(self):
        """Removes the top-of-stack item. Equivalent to POP_TOP. Used
          to clean up at the end of loops, hence the name.
        """
        self.vm.pop()

    def END_SEND(self):
        """
        To be continued...
        """
        # FIXME
        raise self.vm.PyVMError("END_SEND not implemented")

    def RESERVED(self):
        """
        To be continued...
        """
        # FIXME
        raise self.vm.PyVMError("RESERVED not implemented")

    def STORE_SLICE(self):
        """
        Implements:
          end = STACK.pop()
          start = STACK.pop()
          container = STACK.pop()
          values = STACK.pop()
          STACK.push(container)
        """
        values, container, start, end = self.vm.popn(4)
        container[start:end]= values
        self.vm.push(container)

    def CLEANUP_THROW(self):
        """
        To be continued...
        """
        # FIXME
        raise self.vm.PyVMError("CLEANUP_THROW not implemented")

    def LOAD_LOCALS(self):
        """
        To be continued...
        """
        # FIXME
        raise self.vm.PyVMError("LOAD_LOCALS not implemented")

    def RETURN_CONST(self, consti):
        """
        Returns with co_consts[consti] to the caller of the function.
        """
        self.vm.return_value = consti
        return "return"

    def LOAD_FAST_CHECK(self):
        """
        To be continued...
        """
        # FIXME
        raise self.vm.PyVMError("LOAD_FAST_CHECK not implemented")

    # def POP_JUMP_IF_FALSE(self):
    #     """
    #     To be continued...
    #     """
    #     # FIXME
    #     raise self.vm.PyVMError("POP_JUMP_IF_FALSE not implemented")

    # def POP_JUMP_IF_TRUE(self):
    #     """
    #     To be continued...
    #     """
    #     # FIXME
    #     raise self.vm.PyVMError("POP_JUMP_IF_FALSE not implemented")

    def POP_JUMP_IF_NOT_NONE(self):
        """
        To be continued...
        """
        # FIXME
        raise self.vm.PyVMError("POP_JUMP_IF_NOT_NONE not implemented")

    def POP_JUMP_IF_NONE(self):
        """
        To be continued...
        """
        # FIXME
        raise self.vm.PyVMError("POP_JUMP_IF_NONE not implemented")

    def LOAD_SUPER_ATTR(self):
        """
        To be continued...
        """
        # FIXME
        raise self.vm.PyVMError("LOAD_SUPER_ATTR not implemented")

    def LOAD_FAST_AND_CLEAR(self, name):
        """Pushes a reference to the local co_varnames[var_num] onto
        the stack (or pushes NULL onto the stack if the local variable
        has not been initialized) and sets co_varnames[var_num] to
        NULL.
        """
        value = self.vm.frame.f_locals.get(name, NULL)
        if value is NULL:
            self.vm.frame.f_locals[name] = NULL
        self.vm.push(value)


    # And many more...

    # Changed in 3.12...

    def COMPARE_OP(self, opname):
        """Performs a Boolean operation. The operation name can be
        found in cmp_op[opname].

        The cmp_op index is now stored in the four-highest bits of
        oparg instead of the four-lowest bits of oparg.
        """
        x, y = self.vm.popn(2)
        opname >>= 4
        self.vm.push(self.COMPARE_OPERATORS[opname](x, y))

    def FOR_ITER(self, jump_offset):
        """TOS is an iterator. Call its __next__() method. If this
        yields a new value, push it on the stack (leaving the iterator
        below it). If the iterator indicates it is exhausted the
        bytecode counter is incremented by delta.

        Note: jump = delta + f.f_lasti set in parse_byte_and_args()

        Changed in 3.12. Up until 3.11 the iterator was popped when it
        was exhausted.
        """

        try:
            v = next(self.vm.top)
            self.vm.push(v)
        except StopIteration:
            self.vm.jump(jump_offset)

    def LOAD_ATTR(self, name, push_null=False):
        """If the low bit of namei is not set (push_null is False),
        this replaces STACK[-1]
        with getattr(STACK[-1], co_names[namei>>1]).

        If the low bit of namei is set, this will attempt to load a
        method named co_names[namei>>1] from the STACK[-1]
        object. STACK[-1] is popped. This bytecode distinguishes two
        cases: if STACK[-1] has a method with the correct name, the
        bytecode pushes the unbound method and STACK[-1]. STACK[-1]
        will be used as the first argument (self) by CALL or CALL_KW
        when calling the unbound method. Otherwise, NULL and the
        object returned by the attribute lookup are pushed.

        Changed in version 3.12: If the low bit of namei is set, then
        a NULL or self is pushed to the stack before the attribute or
        unbound method respectively.

        Note: name = co_names[namei] and push_null are set in
        parse_byte_and_args()
        """
        obj = self.vm.pop()
        val = getattr(obj, name)

        if push_null:
            self.vm.push(NULL)

        self.vm.push(val)
