#  This file is automatically generated; change it on your own risk!

#--begin constants--

ENDMARKER = 761000
NAME = 761001
NUMBER = 761002
STRING = 761003
NEWLINE = 761004
INDENT = 761005
DEDENT = 761006
LPAR = 761007
RPAR = 761008
LSQB = 761009
RSQB = 761010
COLON = 761011
PLUS = 761012
STAR = 761013
VBAR = 761014
COMMENT = 761015
token_input = 761016
unit = 761017
LBRA = 761018
RBRA = 761019
COMMA = 761020
LINE_COMMENT = 761021
WHITE = 761022
Single = 761023
Double = 761024

#--end constants--

tok_name = sym_name = {}
for _name, _value in globals().items():
    if type(_value) is type(0):
        sym_name[_value] = _name

del _name
del _value

