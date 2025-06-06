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
    def INTERPRETER_EXIT(self):
        """
        To be continued...
        """
        # FIXME
        raise self.vm.PyVMError("INTERPRETER_EXIT not implemented")

    def END_FOR(self):
        """
        To be continued...
        """
        # FIXME
        raise self.vm.PyVMError("END_FOR not implemented")

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

    def BINARY_SLICE(self):
        """
        To be continued...
        """
        # FIXME
        raise self.vm.PyVMError("BINARY_SLICE not implemented")

    def STORE_SLICE(self):
        """
        To be continued...
        """
        # FIXME
        raise self.vm.PyVMError("STORE_SLICE not implemented")

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
        if self.vm.frame.generator:
            self.vm.frame.generator.finished = True
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

    def LOAD_FAST_AND_CLEAR(self):
        """
        To be continued...
        """
        # FIXME
        raise self.vm.PyVMError("LOAD_FAST_AND_CLEAR not implemented")


    # And menay more...
