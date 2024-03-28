"""Testing tools for x-python."""

import inspect
import os.path as osp
import sys
import textwrap
import unittest
from io import StringIO

from xdis import load_module
from xdis.version_info import IS_PYPY, PYTHON_VERSION_TRIPLE, version_tuple_to_str

from xpython.vm import PyVM, PyVMError

# Make this false if you need to run the debugger inside a test.
CAPTURE_STDOUT = "-s" not in sys.argv
# Make this false to see the traceback from a failure inside pyvm.
CAPTURE_EXCEPTION = 1


def get_srcdir():
    filename = osp.normcase(osp.dirname(__file__))
    return osp.realpath(filename)


srcdir = get_srcdir()


def parent_function_name():
    if PYTHON_VERSION_TRIPLE < (3, 5):
        return inspect.stack()[2][3]
    else:
        return inspect.stack()[2].function


LINE_STR = "-" * 25

supported_versions = frozenset(
    [
        (2, 7),
        (3, 2),
        (3, 3),
        (3, 4),
        (3, 5),
        (3, 6),
        (3, 7),
        (3, 8),
        (3, 9),
        (3, 10),
        (3, 11),
    ]
)

def assert_same_exception(e1, e2):
    """Exceptions don't implement __eq__, check it ourselves."""
    assert str(e1) == str(e2)
    assert type(e1) == type(e2)


class VmTestCase(unittest.TestCase):
    def do_one(self):
        self.version_pair = PYTHON_VERSION_TRIPLE[:2]
        assert self.version_pair in supported_versions

        basename = parent_function_name()
        if IS_PYPY:
            version = version_tuple_to_str(end=2, delimiter="")
            path = osp.join(
                srcdir,
                "bytecode-pypy%s" % version,
                "%s.pypy%s.pyc" % (basename, version),
            )
        else:
            version = version_tuple_to_str(end=2)
            path = osp.join(srcdir, "bytecode-%s" % version, "%s.pyc" % basename)

        self.assert_ok(path, arg_type="bytecode-file")

    def self_checking(self):
        """Use this for a program that has asserts to check its validity"""
        self.version_pair = PYTHON_VERSION_TRIPLE[:2]
        assert self.version_pair in supported_versions

        path = osp.join(
            srcdir,
            "bytecode-%s" % version_tuple_to_str(self.version_pair),
            parent_function_name() + ".pyc",
        )
        self.assert_runs_ok(path, arg_type="bytecode-file")

    def assert_ok(self, path_or_code, raises=None, arg_type="string"):
        """Run `code` in our VM and in real Python: they behave the same."""

        if arg_type == "bytecode-file":
            (
                self.version_pair,
                timestamp,
                magic_int,
                code,
                pypy,
                source_size,
                sip_hash,
            ) = load_module(path_or_code)
        else:
            self.version_pair = PYTHON_VERSION_TRIPLE[:2]
            if arg_type == "source":
                code_str = open(path_or_code, "r").read()
            else:
                assert arg_type == "string", (
                    "arg_type parameter needs to be either: bytecode-file, source or string; got %s"
                    % arg_type
                )
                code_str = textwrap.dedent(path_or_code)

            code = compile(code_str, "<%s>" % self.id(), "exec", 0, 1)

        real_stdout = sys.stdout

        # Run the code through our VM.

        vm_stdout = StringIO()
        if CAPTURE_STDOUT:  # pragma: no branch
            sys.stdout = vm_stdout
        vm = PyVM(vmtest_testing=True)

        vm_value = vm_exc = None
        try:
            vm_value = vm.run_code(code)
        except PyVMError:  # pragma: no cover
            # If the VM code raises an error, show it.
            raise
        except AssertionError:  # pragma: no cover
            # If test code fails an assert, show it.
            raise
        except Exception as e:
            # Otherwise, keep the exception for comparison later.
            if not CAPTURE_EXCEPTION:  # pragma: no cover
                raise
            vm_exc = e
        finally:
            real_stdout.write(
                "\n%s %s output %s\n\n" % (LINE_STR, code.co_filename, LINE_STR)
            )
            real_stdout.write(vm_stdout.getvalue())

        # Run the code through the real Python interpreter, for comparison.

        if self.version_pair != PYTHON_VERSION_TRIPLE[:2]:
            return

        py_stdout = StringIO()
        sys.stdout = py_stdout

        py_value = py_exc = None
        globs = {}
        try:
            py_value = eval(code, globs, globs)
        except AssertionError:  # pragma: no cover
            raise
        except Exception as e:
            py_exc = e

        sys.stdout = real_stdout

        assert_same_exception(vm_exc, py_exc)
        self.assertEqual(vm_stdout.getvalue(), py_stdout.getvalue())
        self.assertEqual(vm_value, py_value)
        if raises:
            self.assertIsInstance(vm_exc, raises)
        else:
            self.assertIsNone(vm_exc)

    def assert_runs_ok(self, path_or_code, raises=None, arg_type="string"):
        """Run `code` in our VM."""

        if arg_type == "bytecode-file":
            (
                self.version_pair,
                timestamp,
                magic_int,
                code,
                pypy,
                source_size,
                sip_hash,
            ) = load_module(path_or_code)
        else:
            self.version_pair = PYTHON_VERSION_TRIPLE[:2]
            if arg_type == "source":
                code_str = open(path_or_code, "r").read()
            else:
                assert arg_type == "string", (
                    "arg_type parameter needs to be either: bytecode-file, source or string; got %s"
                    % arg_type
                )
                code_str = textwrap.dedent(path_or_code)

            code = compile(code_str, "<%s>" % self.id(), "exec", 0, 1)

        print(
            "%s bytecode %s for %s %s "
            % (
                LINE_STR,
                version_tuple_to_str(self.version_pair),
                code.co_filename,
                LINE_STR,
            )
        )

        vm = PyVM(python_version=self.version_pair)

        vm_value = vm_exc = None
        try:
            vm_value = vm.run_code(code)
        except PyVMError:  # pragma: no cover
            # If the VM code raises an error, show it.
            self.assertTrue(False)
            raise
        except AssertionError:  # pragma: no cover
            # If test code fails an assert, show it.
            raise
        except Exception as e:
            # Otherwise, keep the exception for comparison later.
            if not CAPTURE_EXCEPTION:  # pragma: no cover
                raise
            vm_exc = e
        else:
            self.assertTrue(True)


if __name__ == "__main__":

    class TestOne(VmTestCase):
        def test_constant(self):
            self.do_one()

    t = TestOne("test_constant")
    t.test_constant()
