###############  langlet Postlexer + Interceptor definitions ############

from langlet_config import parent_langlet
from langscape.base.loader import BaseClass
from langscape.base.postlexer import postlex

class LangletPostlexer(BaseClass("Postlexer", parent_langlet)):
    '''
    Defines a langlet specific token stream post-processor.
    '''
    @postlex
    def NAME(self, pos, tok):
        name = tok[1]
        if name[-1] == '-':
            col = tok[-1]
            self.add_token([lex_symbol.NAME, name[:-1], tok[2], col])
            self.add_token([lex_symbol.MINUS, '-', tok[2], col+len(name)-1])
        else:
            self.add_token(tok)

