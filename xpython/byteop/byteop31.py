# -*- coding: utf-8 -*-
"""Byte Interpreter operations for Python 3.1
"""
from xpython.byteop.byteop32 import ByteOp32, Version_info
from xpython.byteop.byteop24 import ByteOp24
from xpython.byteop.byteop26 import ByteOp26

# FIXME: investigate does "del" remove an attribute here?
# have an effect on what another module sees as ByteOp27's attributes?

# Added 3.2 but not in 3.1
del ByteOp32.DUP_TOP_TWO
del ByteOp32.DELETE_DEREF
# del ByteOp32.SETUP_WITH


class ByteOp31(ByteOp32):
    def __init__(self, vm):
        super(ByteOp32, self).__init__(vm)
        self.version = "3.1.5 (default, Oct 27 1955, 00:00:00)\n[x-python]"
        self.version_info = Version_info(3, 1, 5, "final", 0)

    # DUP_TOP_TOPX = ByteOp24.DUP_TOPX
    IMPORT_NAME = ByteOp26.IMPORT_NAME
    ROT_FOUR = ByteOp26.ROT_FOUR


if __name__ == "__main__":
    x = ByteOp31(None)
