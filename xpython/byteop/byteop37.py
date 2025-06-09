"""Bytecode Interpreter operations for Python 3.7"""

from xpython.byteop.byteop24 import ByteOp24, Version_info
from xpython.byteop.byteop36 import ByteOp36

# Gone in 3.7
del ByteOp36.STORE_ANNOTATION

# Gone in 3.6 PyPy (and therefore we kept it in 3.6 Python)
del ByteOp24.CALL_FUNCTION_VAR_KW

# del ByteOp36.WITH_CLEANUP_START
# del ByteOp36.WITH_CLEANUP_FINISH
# del ByteOp36.END_FINALLY
# del ByteOp36.POP_EXCEPT
# del ByteOp36.SETUP_WITH
# del ByteOp36.SETUP_ASYNC_WITH


# pylint: disable=too-few-public-methods
class NullClass:
    """
    Python 3.11 can push a NULL onto the evaluation stack.
    This is used in method lookup, and strings.
    We create a new type for this. Note: Python's builtin None
    can't be used, because that is a valid value.
    """

    def __repr__(self) -> str:
        return "NULL"


# Singleton NULL object. Testing for this should use
# "is" not "=="
NULL = NullClass()


# pylint: disable=too-many-public-methods
class ByteOp37(ByteOp36):
    """
    Python 3.7 opcodes
    """

    def __init__(self, vm):
        super().__init__(vm)

        # Fake up version information
        self.hexversion = 0x3070BF0
        self.version_info = Version_info(3, 7, 11, "final", 0)
        self.version = "3.7.11 (default, Oct 27 1955, 00:00:00)\n[x-python]"

    # Changed in 3.7

    # WITH_CLEANUP_START
    # WITH_CLEANUP_FINISH
    # END_FINALLY
    # POP_EXCEPT
    # SETUP_WITH
    # SETUP_ASYNC_WITH

    # New in 3.7

    ##############################################################################
    # Order of function here is the same as in:
    # https://docs.python.org/3.7/library/dis.htmls#python-bytecode-instructions
    #
    # A note about parameter names. Generally they are the same as
    # what is described above, however there are some slight changes:
    #
    # * when a parameter name is `namei` (an int), it appears as
    #   `name` (a str) below because the lookup on co_names[namei] has
    #   already been performed in parse_byte_and_args().
    ##############################################################################

    def LOAD_METHOD(self, name):
        """Loads a method named co_names[namei] from the TOS object. TOS is
        popped. This bytecode distinguishes two cases: if TOS has a
        method with the correct name, the bytecode pushes the unbound
        method and TOS. TOS will be used as the first argument (self)
        by CALL_METHOD when calling the unbound method. Otherwise,
        NULL and the object return by the attribute lookup are pushed.
        """
        TOS = self.vm.pop()

        if hasattr(TOS, name):
            # FIXME: Figure out how to get an unbound method and self from a callable function.
            # Until then, we need to push NULL and the callable (the default slow path).
            function = getattr(TOS, name)
            if not callable(function):
                raise self.vm.PyVMError(
                    "LOAD_METHOD %s off of %s of type {%s} is not callable."
                    % (name, TOS, type(TOS))
                )
            self.vm.push(NULL)
            self.vm.push(function)
        else:
            raise self.vm.PyVMError(
                "LOAD_METHOD can't find %s off of %s of type %s"
                % (name, TOS, type(TOS))
            )

    def CALL_METHOD(self, count):
        """Calls a method. argc is the number of positional
        arguments. Keyword arguments are not supported. This opcode is
        designed to be used with LOAD_METHOD. Positional arguments are
        on top of the stack. Below them, the two items described in
        LOAD_METHOD are on the stack (either self and an unbound
        method object or NULL and an arbitrary callable). All of them
        are popped and the return value is pushed.

        rocky: In our setting, before "self" we have an additional
        item which is the status of the LOAD_METHOD. In contrast to what can
        be done in the C implementation, there is no way
        in Python to represent a value outside what Python offers.
        In effect, this is what NULL in C is.
        """
        posargs = self.vm.popn(count)
        null_or_meth, self_or_fn = self.vm.popn(2)
        if null_or_meth is NULL:
            function = self_or_fn
            self.call_function_with_args_resolved(function, posargs, {})
        else:
            # FIXME:
            raise self.vm.PyVMError(
                "CALL_METHOD with self and unbound method not implemented yet"
            )
