"""This program is self-checking!"""
import sys  # noqa

if not ((3, 0) <= sys.version_info[:2] <= (3, 2)):
    code = u'u"\xc2\xa4"\n'
    assert eval(code) == u"\xc2\xa4"
