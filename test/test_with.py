"""Test the "with" statement for x-python."""

try:
    import vmtest
except ImportError:
    from . import vmtest

from xdis.version_info import PYTHON_VERSION_TRIPLE


class TestWithStatement(vmtest.VmTestCase):

    if PYTHON_VERSION_TRIPLE < (3, 8):

        def test_simple_context_manager(self):
            self.self_checking()

        def test_suppressed_raise_in_context_manager(self):
            self.self_checking()

        def test_at_context_manager_complete(self):
            self.self_checking()

        def test_at_context_manager_simplified(self):
            self.self_checking()

        def test_raise_in_context_manager(self):
            self.self_checking()

        def test_continue_in_with(self):
            self.self_checking()

        def test_break_in_with(self):
            self.do_one()

        def test_raise_in_with(self):
            self.do_one()

    if PYTHON_VERSION_TRIPLE >= (3, 6):
        print("Test not gone over yet for >= 3.6")
    else:

        def test_return_in_with(self):
            self.assert_ok(
                """\
                class NullContext(object):
                    def __enter__(self):
                        l.append('i')
                        return self

                    def __exit__(self, exc_type, exc_val, exc_tb):
                        l.append('o')
                        return False

                l = []
                def use_with(val):
                    with NullContext():
                        l.append('w')
                        return val
                    l.append('e')

                assert use_with(23) == 23
                l.append('r')
                s = ''.join(l)
                print("Look: %r" % s)
                assert s == "iwor"
                """
            )
