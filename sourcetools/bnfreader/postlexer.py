###############  langlet Postlexer + Interceptor definitions ############

from langlet_config import parent_langlet
from langscape.base.loader import BaseClass
from langscape.base.postlexer import postlex
from langscape.ls_const import SYMBOL_OFFSET, INTRON_NID
from langscape.csttools.cstutil import csttoken

class LangletPrelexer(BaseClass("Prelexer", parent_langlet)):
    '''
    Defines a langlet specific preprocessor for the tokenizer.
    '''

class LangletPostlexer(BaseClass("Postlexer", parent_langlet)):
    '''
    Defines a langlet specific token stream post-processor.
    '''

    @postlex
    def INTRON(self, pos, tok):
        intron = tok[:]
        intron[0] = INTRON_NID + SYMBOL_OFFSET
        self.add_token(intron)


