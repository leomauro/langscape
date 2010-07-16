#################  imports  #############################################

import langlet_config as config

from langscape.csttools.cstutil import*
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
            self._loaded        = False
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

    def map_to_python(self, node, source_langlet = None):
        try:
            node[0] = node[0]%LANGLET_ID_OFFSET
            nid = node[0]
            if nid>self.MAX_NID:
                if source_langlet:
                    raise UnknownSymbol("Cannot map node '%s' to python target"%(nid,
                                        source_langlet.get_node_name(node[0])))
                else:
                    raise UnknownSymbol("Cannot map node '%s' to python target"%nid)

            if is_keyword(nid):
                node[0] = 1
                if len(node) == 4:
                    del node[-1]
            elif is_symbol(nid):
                node[0] = nid - SYMBOL_OFFSET + 256
            elif nid < 256 and len(node) == 4:
                del node[-1]
            for i, item in enumerate(node[1:]):
                if isinstance(item, list):
                    self.map_to_python(item, source_langlet)
        except IndexError:
            raise           # set breakpoint here
        return node

    def load_libraries(self, **kwd):
        if not self._loaded:
            self._loaded = True
            import importer
            import postlexer
            import parserhook
            import transformer
            import unparser
            import cstfunction
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


