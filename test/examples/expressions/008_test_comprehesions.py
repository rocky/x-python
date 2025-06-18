# Test various kinds of comprehensions.
# This originally from byterun was adapted from test_base.py

# In various Pythons there is this .0 parameter
# which isn't listed in the signature by inpsect.
"""This program is self-checking!"""

x = [z * z for z in range(5)]
assert x == [0, 1, 4, 9, 16]

y = {z: z * z for z in range(5)}
assert y == {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

w = {z * z for z in range(5)}
assert w == {0, 1, 4, 9, 16}
