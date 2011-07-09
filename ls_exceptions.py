#
#  Collection of exceptions used by Langscape
#
#  Langscape inserts the exception classes directly into the __builtin__ superglobals.

class ParserError(Exception):
    """
    Exception class for parser errors.
    """
    def __init__(self, **kwd):
        self.__dict__.update(**kwd)
        self.value = self.formatter()

    def __str__(self):
        return self.value

class IncompleteTraceError(Exception):
    """
    Exception raised when node trail cannot be completed.
    """

class GrammarError(Exception):
    """
    Exception raised when invalid grammar is detected.
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
    Exception class for node inclusion cycles N < ...<A<N.
    """

class TranslationError (Exception):
    """
    Exception class for translation failures.
    """

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

