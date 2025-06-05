"""This program is self-checking!"""
def testit(v):
    print(v)

g = 17
assert g == 17
del g
try:
   testit(g)
except NameError:
    print("Saw a NamedError - Good!")
    assert True, "Deleting should remove variable named 'g'"
else:
    assert False, "Deleting did not remove variable named 'g'"
