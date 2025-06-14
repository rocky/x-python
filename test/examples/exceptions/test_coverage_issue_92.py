"""This program is self-checking!"""

a_list = []
for i in range(3):
    try:
        a_list.append(i)
    finally:
        a_list.append("f")
    a_list.append("e")
a_list.append("r")
assert a_list == [0, "f", "e", 1, "f", "e", 2, "f", "e", "r"]
