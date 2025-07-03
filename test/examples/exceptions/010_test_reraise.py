"""This program is self-checking!"""

is_bad = True

try:
    try:
        fooey
        assert False, "Should have raised a NameError exception"
    except NameError:
        # Got an excpetion - good
        is_bad = False
        # Reraise exception
        raise

    assert False,"Should have raised a NameError exception"  # noqa

except Exception as e:
    assert isinstance(e, NameError)

assert not is_bad, "Should have caught first NameError exception"
