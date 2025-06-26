# From 2.7.18 test_grammar.py adapted so it will run on later Pythons

# Tests EXEC_STMT on 2.7- and exec() builtin on 3.0+

"""This program is self-checking!"""
z = None
del z

exec("z=1+1\n")

assert z == 2

exec("z += 5")
assert z == 7
del z
