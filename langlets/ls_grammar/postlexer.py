###############  langlet Postlexer + Interceptor definitions ############

from langlet_config import parent_langlet
from langscape.base.loader import BaseClass
from langscape.base.postlexer import postlex

class LangletPostlexer(BaseClass("Postlexer", parent_langlet)):
    '''
    Defines a langlet specific token stream post-processor.
    '''
    @postlex
    def NEWLINE(self, pos, tok):
        if pos<len(self.scan)-3:
            T1 = self.scan[pos+2]
            T2 = self.scan[pos+3]
            if self.lex_symbol.COLON in (T1[0], T2[0]):
                self.add_token(tok)
        else:
            self.add_token(tok)
    @postlex
    def WHITE(self, pos, tok):
        if '\n' in tok[1]:
            self.NEWLINE(pos, [self.lex_symbol.NEWLINE]+tok[1:])

    @postlex
    def COMMENT(self, pos, tok):
        self.NEWLINE(pos, [self.lex_symbol.NEWLINE, '\n']+tok[2:])

