"""Execute files of Python code."""

import mimetypes
import os
import os.path as osp
import sys
import tokenize

# To silence the "import imp" DeprecationWarning below
import warnings
from typing import Optional

from xdis import load_module
from xdis.version_info import IS_PYPY, PYTHON_VERSION_TRIPLE, version_tuple_to_str

from xpython.stdlib.builtins import make_compatible_builtins
from xpython.version_info import SUPPORTED_BYTECODE, SUPPORTED_PYPY, SUPPORTED_PYTHON
from xpython.vm import PyVM, PyVMUncaughtException, format_instruction
from xpython.vmtrace import PyVMTraced

if PYTHON_VERSION_TRIPLE >= (3, 4):
    from importlib.util import find_spec as find_module
    from types import ModuleType as new_module
else:
    from imp import find_module, new_module

warnings.filterwarnings("ignore")

# This code is ripped off from coverage.py.  Define things it expects.
try:
    open_source = tokenize.open  # pylint: disable=E1101
except Exception:

    def open_source(fname):
        """Open a source file the best way."""
        return open(fname, "rU")


class CannotCompileError(Exception):
    """For raising errors when we have a Compile error."""

    pass


class WrongBytecodeError(Exception):
    """For raising errors when we have the wrong bytecode."""

    pass


class NoSourceError(Exception):
    """For raising errors when we can't find source code."""

    pass


def source_is_older(source_path: str, bytecode_path: str) -> Optional[bool]:
    """
    Check that the modification time on `source_path` is before the modification

    """
    try:
        return os.stat(source_path).st_mtime > os.stat(bytecode_path).st_mtime
    except FileNotFoundError:
        return None


def exec_code_object(
    code,
    env,
    python_version=PYTHON_VERSION_TRIPLE,
    is_pypy=IS_PYPY,
    callback=None,
    format_instruction=format_instruction,
) -> int:
    rc = 0
    if callback:
        vm = PyVMTraced(
            callback,
            python_version,
            is_pypy,
            format_instruction_func=format_instruction,
        )
        try:
            vm.run_code(code, f_globals=env)
        except PyVMUncaughtException:
            vm.last_exception = event_arg = (
                vm.last_exception[0],
                vm.last_exception[1],
                vm.last_traceback,
            )
            callback("fatal", 0, "fatalOpcode", 0, -1, event_arg, [], vm)
    else:
        if python_version != PYTHON_VERSION_TRIPLE[:2]:
            make_compatible_builtins(BUILTINS.__dict__, python_version)
        vm = PyVM(python_version, is_pypy, format_instruction_func=format_instruction)
        try:
            rc = vm.run_code(code, f_globals=env)
        except PyVMUncaughtException:
            pass

    return rc


def get_supported_versions(is_pypy, is_bytecode):
    if is_bytecode:
        supported_versions = SUPPORTED_BYTECODE
        mess = "Python 2.4 .. 2.7, 3.1 .. 3.10"
    else:
        supported_versions = SUPPORTED_PYPY if IS_PYPY else SUPPORTED_PYTHON
        mess = "PYPY 2.7, 3.2, 3.5 and 3.6" if is_pypy else "CPython 2.7, 3.2 .. 3.10"
    return supported_versions, mess


# from coverage.py:

try:
    # In Py 2.x, the builtins were in __builtin__
    BUILTINS = sys.modules["__builtin__"]
except KeyError:
    # In Py 3.x, they're in builtins
    BUILTINS = sys.modules["builtins"]


def rsplit1(s, sep):
    """The same as s.rsplit(sep, 1), but works in 2.3"""
    parts = s.split(sep)
    return sep.join(parts[:-1]), parts[-1]


def run_python_module(modulename, args):
    """Run a python module, as though with ``python -m name args...``.

    `modulename` is the name of the module, possibly a dot-separated name.
    `args` is the argument array to present as sys.argv, including the first
    element naming the module being executed.

    """
    openfile = None
    glo, loc = globals(), locals()
    try:
        try:
            # Search for the module - inside its parent package, if any - using
            # standard import mechanics.
            if "." in modulename:
                packagename, name = rsplit1(modulename, ".")
                package = __import__(packagename, glo, loc, ["__path__"])
                searchpath = package.__path__
            else:
                packagename, name = None, modulename
                searchpath = None  # "top-level search" in imp.find_module()
            openfile, pathname, _ = find_module(name, searchpath)

            # Complain if this is a magic non-file module.
            if openfile is None and pathname is None:
                raise NoSourceError(f"module does not live in a file: {modulename!r}")

            # If `modulename` is actually a package, not a mere module, then we
            # pretend to be Python 2.7 and try running its __main__.py script.
            if openfile is None:
                packagename = modulename
                name = "__main__"
                package = __import__(packagename, glo, loc, ["__path__"])
                searchpath = package.__path__
                openfile, pathname, _ = find_module(name, searchpath)
        except ImportError:
            _, err, _ = sys.exc_info()
            raise NoSourceError(str(err))
    finally:
        if openfile:
            openfile.close()

    # Finally, hand the file off to run_python_file for execution.
    args[0] = pathname
    run_python_file(pathname, args, package=packagename)


def run_python_file(
    filename, args, package=None, callback=None, format_instruction=format_instruction
):
    """Run a python file as if it were the main program on the command line.

    `filename` is the path to the file to execute, it need not be a .py file.
    `args` is the argument array to present as sys.argv, including the first
    element naming the file being executed.  `package` is the name of the
    enclosing package, if any.

    If `callback` is not None, it is a function which is called back as the
    execution progresses. This can be used for example in a debugger, or
    for custom tracing or statistics gathering.
    """
    # Create a module to serve as __main__
    old_main_mod = sys.modules["__main__"]
    main_mod = new_module("__main__")
    sys.modules["__main__"] = main_mod
    main_mod.__file__ = filename
    if package:
        main_mod.__package__ = package
    main_mod.__builtins__ = BUILTINS

    # set sys.argv and the first path element properly.
    old_argv = sys.argv
    old_path0 = sys.path[0]

    # note: the type of args is na tuple; we want type(sys.argv) == list
    sys.argv = [filename] + list(args)

    if package:
        sys.path[0] = ""
    else:
        sys.path[0] = osp.abspath(osp.dirname(filename))

    is_pypy = IS_PYPY
    try:
        # Open the source or bytecode file.
        try:
            mime = mimetypes.guess_type(filename)
            if mime == ("application/x-python-code", None):
                (
                    python_version,
                    timestamp,
                    magic_int,
                    code,
                    is_pypy,
                    source_size,
                    sip_hash,
                ) = load_module(filename)
                supported_versions, mess = get_supported_versions(
                    is_pypy, is_bytecode=True
                )
                if python_version[:2] not in supported_versions:
                    raise WrongBytecodeError(
                        "We only support byte code for %s: %r is %s bytecode"
                        % (mess, filename, version_tuple_to_str(python_version))
                    )
                main_mod.__file__ = code.co_filename
                make_compatible_builtins(main_mod.__builtins__.__dict__, python_version)

                if source_is_older(code.co_filename, filename):
                    print(
                        (
                            f"Warning: source file {code.co_filename} is newer "
                            f"than bytecode {filename}"
                        )
                    )
                    # Hack to update test code. Remove when we have a standalone program to fix.
                    # os.system(f"/bin/bash ./add-single-test.sh {code.co_filename}")
                    pass

            else:
                source_file = open_source(filename)
                try:
                    source = source_file.read()
                finally:
                    source_file.close()

                supported_versions, mess = get_supported_versions(
                    IS_PYPY, is_bytecode=False
                )
                if PYTHON_VERSION_TRIPLE[:2] not in supported_versions:
                    raise CannotCompileError(
                        "We need %s to compile source code; you are running Python %s"
                        % (mess, version_tuple_to_str())
                    )

                # We have the source.  `compile` still needs the last line to be clean,
                # so make sure it is, then compile a code object from it.
                if not source or source[-1] != "\n":
                    source += "\n"
                code = compile(source, filename, "exec")
                python_version = PYTHON_VERSION_TRIPLE

        except (IOError, ImportError):
            raise NoSourceError(f"No file to run: {filename!r}")

        # Execute the source file.
        rc = exec_code_object(
            code,
            main_mod.__dict__,
            python_version,
            is_pypy,
            callback,
            format_instruction=format_instruction,
        )

    finally:
        # Restore the old __main__
        sys.modules["__main__"] = old_main_mod

        # Restore the old argv and path
        sys.argv = old_argv
        sys.path[0] = old_path0

    sys.exit(rc)


def run_python_string(
    source, args, package=None, callback=None, format_instruction=format_instruction
):
    """Run a python string as if it were the main program on the command line."""
    # Create a module to serve as __main__
    old_main_mod = sys.modules["__main__"]
    main_mod = new_module("__main__")
    sys.modules["__main__"] = main_mod
    fake_path = main_mod.__file__ = f"<string {source[:20]}>"
    if package:
        main_mod.__package__ = package
    main_mod.__builtins__ = BUILTINS

    # Set sys.argv and the first path element properly.
    old_path0 = sys.path[0]
    sys.argv = [fake_path] + list(args)

    try:
        supported_versions, mess = get_supported_versions(IS_PYPY, is_bytecode=False)
        if PYTHON_VERSION_TRIPLE[:2] not in supported_versions:
            raise CannotCompileError(
                "We need %s to compile source code; you are running %s"
                % (mess, version_tuple_to_str())
            )

        # `compile` still needs the last line to be clean,
        # so make sure it is, then compile a code object from it.
        if not source or source[-1] != "\n":
            source += "\n"
        code = compile(source, fake_path, "exec")
        python_version = PYTHON_VERSION_TRIPLE

        # Execute the source string.
        exec_code_object(
            code,
            main_mod.__dict__,
            python_version,
            IS_PYPY,
            callback,
            format_instruction=format_instruction,
        )

    finally:
        # Restore the old __main__
        sys.modules["__main__"] = old_main_mod

        # Restore the old argv and path
        sys.path[0] = old_path0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: execfile.py <filename> args")
        sys.exit(1)
    run_python_file(sys.argv[1], sys.argv[2:])
