###############  langlet unparser definition ##################

from langlet_config import parent_langlet
from langscape.base.loader import BaseClass

class LangletUnparser(BaseClass("Unparser", parent_langlet)):
    '''
    Defines langlet specific unparsing / formatting.
    '''
    def format_left(self, c0, c1, text):
        if c1 in "([":
            if c0 in " ([":
                return text
            else:
                return " "+text

    def format_op(self, c0, c1, text):
        if self.isop(c1):
            if c1 == "|":
                return " "+text
            return text

    def format_char(self, c0, c1, text):
        if self.ischar(c1):
            if c0 in "+*|":
                return " "+text
            elif c0 in "(":
                return " "+text
            else:
                return super(LangletUnparser, self).format_char(c0, c1, text)

