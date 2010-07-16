from langlet_config import parent_langlet
from langscape.base.loader import BaseClass

class LangletCSTFunction(BaseClass("CSTFunction", parent_langlet)):
    '''
    Implements langlet specific functions operating on CSTs which are accessed through the
    Langlet object via the ``self.fn`` attribute.
    '''

