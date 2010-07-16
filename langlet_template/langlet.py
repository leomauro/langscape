#################  imports  #############################################

import langlet_config as config

from langscape.util import flip
from langscape.base.langlet import BaseLanglet, langlet_table
from lexdef.lex_token import LexerToken, LANGLET_ID
from lexdef import lex_symbol
from parsedef import parse_symbol
from parsedef import parse_token
from langscape.csttools.cstbuilder import CSTBuilder

#################  cstbuilder      ######################################

def load_cstbuilder():
    from cstdef.cstbuilder_gen import build_cstbuilder
    langlet = Langlet()
    langlet.load_parse_tables()
    builder = CSTBuilder(langlet)
    return build_cstbuilder(builder)

#################  Langlet Classes ######################################

class Langlet(BaseLanglet):
    _instance = None
    def __init__(self, options = {}):
        if self._instance is not None:
            self.__dict__ = self._instance.__dict__
        else:
            self.options        = options       # command-line options
            self.config         = config        # langlet configuration parameters
            self.lex_token      = LexerToken
            self.lex_symbol     = lex_symbol
            self.parse_token    = self.token  = parse_token
            self.parse_symbol   = self.symbol = parse_symbol
            self.langlet_id     = LANGLET_ID
            self.MAX_NID        = max(parse_symbol.sym_name.values())
            langlet_table.register(self)
            Langlet._instance = self

    def load_parse_tables(self):
        from lexdef import lex_nfa
        from parsedef import parse_nfa
        self.lex_nfa   = lex_nfa
        self.parse_nfa = parse_nfa
        self.keywords  = flip(parse_nfa.keywords)

    def load_libraries(self, **kwd):
        import importer
        import postlexer
        import parserhook
        import transformer
        import unparser
        import cstfunction
        from cstdef.cstlayers_gen import cstlayers
        self.cstlayers   = cstlayers
        self.load_target_langlet()
        self.fn          = cstfunction.LangletCSTFunction(self)
        self.postlexer   = postlexer.LangletPostlexer(self)
        self.unparser    = unparser.LangletUnparser(self, **kwd)
        self.importer    = importer.LangletImporter(self, **kwd)
        self.interceptor = parserhook.LangletParserHook()
        self.transformer = transformer.LangletTransformer(self, **kwd)
        self.load_superglobals(transformer)
        self.load_lexer()
        self.load_parser()
        self.load_compiler()
        self.load_display()



