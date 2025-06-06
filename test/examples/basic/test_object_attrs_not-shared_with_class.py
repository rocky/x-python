"""This program is self-checking!"""
class Thing(object):
    pass
t = Thing()
# The below should add attribute foo only to the "t" object, not the
# class Thing.
t.foo = 1
try:
   Thing.foo
except AttributeError:
    assert True, "Good - adding an object attribute does not blead into class"
else:
    assert False, "Adding an object attribute bleeds into class"
