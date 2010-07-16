import pprint
import sys

__all__ = ["ParserHook", "intercept"]

def intercept(*symbol):
    '''
    Decorator used to mark interception handlers.

    The decorator is used as a listener on a specific symbol and will initialized with it.
    '''
    def _setsymbol(f):
        f.do_intercept = symbol
        return f
    return _setsymbol


class ParserHookMeta(type):
    def __init__(cls, name, bases, dct):
        super(ParserHookMeta, cls).__init__(name, bases, dict)
        setattr(cls, "interceptors", {})
        classes = list(bases)+[cls]
        for C in classes:
            for f in C.__dict__.values():
                if hasattr(f, "do_intercept"):
                    handler = lambda self, f = f: lambda *symbol: f(self, *symbol)
                    for c in f.do_intercept:
                        cls.interceptors[c] = handler

class ParserHook:
    '''
    The Interceptor is used to interrupt the NFALexer and take control over
    the lexical analysis process. This way a reentrant parser can be created and
    applied when tokenizing. This feature becomes import for cases as string interpolation:

    http://www.zenspider.com/Languages/Ruby/QuickRef.html#6
    '''
    __metaclass__ = ParserHookMeta




