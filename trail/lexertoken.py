# Module used to specify character sets of token.
#
# BaseLexerToken objects are prototypes. They can be copied and customized
# in lex_token.py modules

import string
import copy
from langscape.util.univset import Any, White, Alpha, Digit

class AnyObject:
    pass

BaseLexerToken          = AnyObject()
BaseLexerToken.charset  = AnyObject()
BaseLexerToken.tokenid  = AnyObject()
BaseLexerToken.default  = AnyObject()
BaseLexerToken.auxiliar = AnyObject()

#
# tokenid token ( for use in Token )
#
# functional lexer token without corresponding charset

BaseLexerToken.tokenid.T_ENDMARKER   = 1
BaseLexerToken.tokenid.T_INDENT      = 2
BaseLexerToken.tokenid.T_DEDENT      = 3
BaseLexerToken.tokenid.T_OP          = 4
BaseLexerToken.tokenid.T_ERRORTOKEN  = 5
BaseLexerToken.tokenid.T_NT          = 6
BaseLexerToken.tokenid.T_N_TOKENS    = 7
BaseLexerToken.tokenid.T_NEWLINE     = 8
BaseLexerToken.tokenid.T_NT_OFFSET   = 9

# defaults

BaseLexerToken.default = {BaseLexerToken.tokenid.T_ENDMARKER: ''}
BaseLexerToken.default[BaseLexerToken.tokenid.T_INDENT] = ""
BaseLexerToken.default[BaseLexerToken.tokenid.T_DEDENT] = ""
BaseLexerToken.default[BaseLexerToken.tokenid.T_NEWLINE] = "\n"


# lexer token with corresp. charset

BaseLexerToken.tokenid.A_LINE_END    = 10
BaseLexerToken.tokenid.A_CHAR        = 11
BaseLexerToken.tokenid.A_WHITE       = 12
BaseLexerToken.tokenid.A_HEX_DIGIT   = 13
BaseLexerToken.tokenid.A_OCT_DIGIT   = 14
BaseLexerToken.tokenid.A_DIGIT       = 15
BaseLexerToken.tokenid.A_BACKSLASH   = 16
BaseLexerToken.tokenid.ANY           = 17
BaseLexerToken.tokenid.A_NON_NULL_DIGIT = 18
BaseLexerToken.tokenid.STOP    = 19

# functional lexer token without corresp. charset
# ( not used by Python )

BaseLexerToken.tokenid.T_APP = 30
BaseLexerToken.tokenid.T_APP_1 = 31
BaseLexerToken.tokenid.T_APP_2 = 32
BaseLexerToken.tokenid.T_APP_3 = 33
BaseLexerToken.tokenid.T_APP_4 = 34
BaseLexerToken.tokenid.T_APP_5 = 35

# charsets
BaseLexerToken.charset.A_LINE_END       = set(map(chr,[10, 13]))         # '\n\r'
BaseLexerToken.charset.A_CHAR           = set(string.letters)|set("_")
BaseLexerToken.charset.A_WHITE          = set(string.whitespace)         # '\t\n\x0b\x0c\r '
BaseLexerToken.charset.A_HEX_DIGIT      = set(string.hexdigits)          # 0-9a-fA-F
BaseLexerToken.charset.A_OCT_DIGIT      = set(string.octdigits)          # 0-7
BaseLexerToken.charset.A_NON_NULL_DIGIT = set('123456789')               # 1-9
BaseLexerToken.charset.A_DIGIT          = set(string.digits)             # 0-9
BaseLexerToken.charset.A_BACKSLASH      = set(['\\'])

# charsets which are treated special by the NFALexer
BaseLexerToken.charset.ANY              = set()
BaseLexerToken.charset.STOP             = set()

# auxiliary strings created by the prelexer
BaseLexerToken.auxiliar.AUX_S1          = '\x01'*3
BaseLexerToken.auxiliar.AUX_S2          = '\x02'*3
BaseLexerToken.auxiliar.AUX_S3          = '\x03'*3
BaseLexerToken.auxiliar.AUX_S4          = '\x04'*3
BaseLexerToken.auxiliar.AUX_S5          = '\x05'*3
BaseLexerToken.auxiliar.AUX_S6          = '\x06'*3
BaseLexerToken.auxiliar.AUX_S7          = '\x07'*3
BaseLexerToken.auxiliar.AUX_S8          = '\x08'*3


def NewLexerToken(langlet_id):
    '''
    Function used to copy the BaseLexerToken as an object prototype and create a new LexerToken.

    This function is called in <langlet-path>/lexdef/lex_token.py modules which are automatically
    generated.

    A langlet offset is passed and BaseLexerToken attribute values are shifted by this offset.
    '''
    LxToken = copy.copy(BaseLexerToken)
    LxToken.tokenid = copy.copy(BaseLexerToken.tokenid)
    LxToken.charset = copy.copy(BaseLexerToken.charset)
    LxToken.default = {}
    LxToken.tok_name = {}
    for name, value in LxToken.tokenid.__dict__.items():
        new_value = value+langlet_id
        setattr(LxToken.tokenid, name, new_value)
        if type(value) is type(0):
            LxToken.tok_name[value+langlet_id] = name
        if value in BaseLexerToken.default:
            LxToken.default[new_value] = BaseLexerToken.default[value]
    LxToken.token_map = LxToken.tokenid.__dict__  # for compliency with parse_token files
    return LxToken

if __name__ == '__main__':
    assert BaseLexerToken.tokenid.A_CHAR == 11
    LexerToken = NewLexerToken(100)
    assert LexerToken.tokenid.A_CHAR == 111
    # o.k. nothing changed
    assert BaseLexerToken.tokenid.A_CHAR == 11



