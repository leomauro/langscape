###############  langlet unparser definition ##################

from langlet_config import parent_langlet
from langscape.base.loader import BaseClass

class LangletUnparser(BaseClass("Unparser", parent_langlet)):
    '''
    Defines langlet specific unparsing / formatting.
    '''

