# This tests the use of the "global" statement.

# This program has the simplest of subroutine calls
# so generally it is a good program to try
# when expanding the interpreter such as for a new
# Python version.

"""This program is self-checking!"""

global Xyz
Xyz = 2106


def abc():
    global Xyz
    Xyz += 1
    assert Xyz == 2107, "Midst failed"


assert Xyz == 2106, "Pre failed"
abc()
assert Xyz == 2107, "Post failed"
