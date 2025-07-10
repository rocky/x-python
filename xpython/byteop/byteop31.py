# -*- coding: utf-8 -*-
"""Byte Interpreter operations for Python 3.1
"""
from xpython.byteop.byteop32 import ByteOp32, Version_info
# from xpython.byteop.byteop26 import ByteOp26

# FIXME: "del" removes in a way that messes up modules earlier modules
# e.g. 3.0 that may want to inherit from this module.

# Added 3.2 but not in 3.1
del ByteOp32.DUP_TOP_TWO
del ByteOp32.DELETE_DEREF
# del ByteOp32.SETUP_WITH


class ByteOp31(ByteOp32):
    def __init__(self, vm):
        super(ByteOp32, self).__init__(vm)
        self.version = "3.1.5 (default, Oct 27 1955, 00:00:00)\n[x-python]"
        self.version_info = Version_info(3, 1, 5, "final", 0)

    # Added in 2.4 but removed in 3.2, so we need to readd.
    def DUP_TOPX(self, count: int):
        """
        Duplicate count items, keeping them in the same order. Due to
        implementation limits, count should be between 1 and 5 inclusive.
        """
        items = self.vm.popn(count)
        for _ in range(2):
            self.vm.push(*items)


if __name__ == "__main__":
    x = ByteOp31(None)
