###############  langlet ParserHook definitions ############

from langlet_config import parent_langlet
from langscape.base.loader import BaseClass
from langscape.base.parserhook import intercept
from langscape.trail.nfadef import INTRON_NID
from langscape.ls_const import*

class LangletParserHook(BaseClass("ParserHook", parent_langlet)):
    '''
    Defines a langlet specific lexical analysis interceptor.
    '''


