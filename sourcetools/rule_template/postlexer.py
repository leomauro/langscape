###############  langlet Postlexer + Interceptor definitions ############

from langlet_config import parent_langlet
from langscape.base.loader import BaseClass
from langscape.base.postlexer import postlex

class LangletPrelexer(BaseClass("Prelexer", parent_langlet)):
    '''
    Defines a langlet specific preprocessor for the tokenizer.
    '''

class LangletPostlexer(BaseClass("Postlexer", parent_langlet)):
    '''
    Defines a langlet specific token stream post-processor.
    '''

