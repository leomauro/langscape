# This module can be used to counteract all sorts of nested strings.

__all__ = ["flatstring", "flatstring_revert", "is_flatstring"]

import re

dct = {"'": '\x01',
       '"': '\x02',
       '\n': '\x03'}

redct = {'\x01':"'",
         '\x02':'"',
         '\x03':'\n',
         '\x04':''}

flat_prefix = '\x04'*3

pat   = "(%s)" % "|".join( map(re.escape, dct.keys()) )
repat = "(%s)" % "|".join( map(re.escape, redct.keys()) )

def flatstring_revert(S):
    S = re.sub(repat, lambda m: redct[m.group()], S)
    if S:
        if S[0] == '"':
            return S.strip('"')
        if S[0] == "'":
            return S.strip("'")
    return S

def is_flatstring(S):
    return S.startswith(flat_prefix)

def flatstring(S):
    return flat_prefix+re.sub(pat, lambda m: dct[m.group()], S)


if __name__ == '__main__':
    S = flatstring("'''hs\"h'''")
    print S
    print flatstring_revert(S)



