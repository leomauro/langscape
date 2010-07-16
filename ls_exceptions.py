# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    10 May 2006

#
#  Collection of exceptions used by Langscape
#
#  Langscape inserts the exception classes directly into the __builtin__ superglobals.

class ParserError(Exception):
    def __init__(self, **kwd):
        self.__dict__.update(**kwd)
        self.value = self.formatter()

    def __str__(self):
        return self.value

class IncompleteTraceError(Exception):
    """
    Exception raised when node trail cannot be completed.
    """

class LexerError(Exception):
    """
    Exception class for lexer errors.
    """
    def __init__(self, value, **kwd):
        self.value = value
        self.__dict__.update(**kwd)

    def __str__(self):
        return self.value

class NodeCycleError(Exception):
    """
    Exception class for node cycles N < ...<A<N.
    """

class TranslationError (Exception):
    """
    Exception class for translation failures.
    """

class TokenError(Exception):
    '''
    Exception class for tokenization failures.
    '''

class NonSelectableError(Exception):
    '''
    Exception class for nid selection failures in nfaparsing.
    '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        if isinstance(self.value, str):
            return self.value
        else:
            return str(self.value)

class InvalidNodeError(Exception):
    '''
    Exception class for CST checking failures.
    '''

class UnknownSymbol(Exception):
    '''
    Exception class for node projection failures.
    '''

