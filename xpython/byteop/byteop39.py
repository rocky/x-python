# -*- coding: utf-8 -*-
# Copyright (C) 2021, 2024 Rocky Bernstein
# This program comes with ABSOLUTELY NO WARRANTY.
# This is free software, and you are welcome to redistribute it
# under certain conditions.
# See the documentation for the full license.

"""Bytecode Interpreter operations for Python 3.9
"""
from xpython.byteop.byteop24 import ByteOp24, Version_info
from xpython.byteop.byteop35 import ByteOp35
from xpython.byteop.byteop36 import ByteOp36
from xpython.byteop.byteop38 import ByteOp38

# Gone in 3.8
del ByteOp24.END_FINALLY
del ByteOp35.BUILD_LIST_UNPACK
del ByteOp35.BUILD_MAP_UNPACK
del ByteOp35.BUILD_SET_UNPACK
del ByteOp35.BUILD_TUPLE_UNPACK
del ByteOp35.WITH_CLEANUP_FINISH
del ByteOp35.WITH_CLEANUP_START
del ByteOp36.BUILD_MAP_UNPACK_WITH_CALL
del ByteOp38.CALL_FINALLY
del ByteOp38.POP_FINALLY


class ByteOp39(ByteOp38):
    def __init__(self, vm):
        super(ByteOp38, self).__init__(vm)
        self.hexversion = 0x30907F0
        self.version = "3.9.7 (default, Oct 27 1955, 00:00:00)\n[x-python]"
        self.version_info = Version_info(3, 9, 7, "final", 0)

    # Changed in 3.9...

    # New in 3.9

    ##############################################################################
    # Order of function here is the same as in:
    # https://docs.python.org/3.9/library/dis.htmls#python-bytecode-instructions
    #
    # A note about parameter names. Generally they are the same as
    # what is described above, however there are some slight changes:
    #
    # * when a parameter name is `namei` (an int), it appears as
    #   `name` (a str) below because the lookup on co_names[namei] has
    #   already been performed in parse_byte_and_args().
    ##############################################################################

    def RERAISE(self):
        # FIXME
        raise RuntimeError("RERAISE not implemented yet")
        pass

    def WITH_EXCEPT_START(self):
        # FIXME
        raise RuntimeError("WITH_EXCEPT_START not implemented yet")
        pass

    def LOAD_ASSERTION_ERROR(self):
        """
        Pushes AssertionError onto the stack. Used by the `assert` statement.
        """
        self.vm.push(AssertionError)

    def LIST_TO_TUPLE(self):
        """
        Pops a list from the stack and pushes a tuple containing the same values.
        """
        self.vm.push(tuple(self.vm.pop()))

    def IS_OP(self, invert):
        """Performs is comparison, or is not if invert is 1."""
        TOS1, TOS = self.vm.popn(2)
        if invert:
            self.vm.push(TOS1 is not TOS)
        else:
            self.vm.push(TOS1 is TOS)
        pass

    def JUMP_IF_NOT_EXC_MATCH(self, target):
        """Tests whether the second value on the stack is an exception
        matching TOS, and jumps if it is not.  Pops two values from
        the stack.
        """
        TOS1, TOS = self.vm.popn(2)
        # FIXME: not sure what operation should be used to test not "matches".
        if not issubclass(TOS1, TOS):
            self.vm.jump(target)
        return

    def CONTAINS_OP(self, invert):
        """Performs in comparison, or not in if invert is 1."""
        TOS1, TOS = self.vm.popn(2)
        if invert:
            self.vm.push(TOS1 not in TOS)
        else:
            self.vm.push(TOS1 in TOS)
        return

    def LIST_EXTEND(self, i):
        """Calls list.extend(TOS1[-i], TOS). Used to build lists."""
        TOS = self.vm.pop()
        destination = self.vm.peek(i)
        assert isinstance(destination, list)
        destination.extend(TOS)

    def SET_UPDATE(self, i):
        """Calls set.update(TOS1[-i], TOS). Used to build sets."""
        TOS = self.vm.pop()
        destination = self.vm.peek(i)
        assert isinstance(destination, set)
        destination.update(TOS)

    def DICT_MERGE(self, i):
        """Like DICT_UPDATE but raises an exception for duplicate keys."""
        TOS = self.vm.pop()
        assert isinstance(TOS, dict)
        destination = self.vm.peek(i)
        assert isinstance(destination, dict)
        dups = set(destination.keys()) & set(TOS.keys())
        if bool(dups):
            raise RuntimeError("Duplicate keys '%s' in DICT_MERGE" % dups)
        destination.update(TOS)

    def DICT_UPDATE(self, i):
        """Calls dict.update(TOS1[-i], TOS). Used to build dicts."""
        TOS = self.vm.pop()
        assert isinstance(TOS, dict)
        destination = self.vm.peek(i)
        assert isinstance(destination, dict)
        destination.update(TOS)
