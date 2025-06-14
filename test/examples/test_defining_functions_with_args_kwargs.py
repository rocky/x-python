"""This program is self-checking!"""

# Test Various functions argument combinations

def fn(*args):
    assert args == (1, 2)


fn(1, 2)


def kwargs_fn(**kwargs):
    assert sorted(kwargs.keys()) == ["blue", "red"]
    assert sorted(kwargs.values()) == [False, True]


kwargs_fn(red=True, blue=False)


def args_kwargs_fn(*args, **kwargs):
    assert args == (1, 2)
    assert sorted(kwargs.keys()) == ["blue", "red"]
    assert sorted(kwargs.values()) == [False, True]


args_kwargs_fn(1, 2, red=True, blue=False)


def pos_args_kwargs_fn(x, y, *args, **kwargs):
    assert x, y == ("a", "b")
    assert args == (1, 2)
    assert sorted(kwargs.keys()) == ["blue", "red"]
    assert sorted(kwargs.values()) == [False, True]


pos_args_kwargs_fn("a", "b", 1, 2, red=True, blue=False)
