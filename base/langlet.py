#
# BaseLanglet class which defines most of the langlet API
#

from __future__ import with_statement
import sys, os
import __main__
import langscape.base.loader as loader
import langscape.csttools.cstcheck as cstcheck
from langscape.csttools.cstrepr import CSTTextualDisplay
from langscape.csttools.cstutil import*
from langscape.util import flip
from langscape.util.path import path
from langscape.base.display import DisplayMixin
from langscape.trail.nfaparser import TokenStream
from langscape.base.module_descriptor import LangletModuleDescriptor
from langscape.csttools.cstbuilder import CSTBuilder

class BaseLanglet(object):
    def __init__(self, options):
        self.options        = options    # command-line options
        self.config         = None       # langlet configuration information
        self.package        = None       # package path
        self.display        = None       # DisplayMixin instance
        self.cstdisplay     = None       # CSTDisplay instance
        self.lex_token      = None       # LexerToken instance
        self.lex_symbol     = None       # lexdef.lex_symbol module
        self.parse_token    = None       # parsedef.parse_token module
        self.parse_symbol   = None       # parsedef.parse_symbol module
        self.token          = None       # shorter form of 'parse_token'
        self.symbol         = None       # shorter form of 'parse_symbol'
        self.lex_nfa        = None       # lexdef.lex_nfa module
        self.parse_nfa      = None       # parsedef.parse_nfa module
        self.importer       = None       # LangletImporter instance
        self.transformer    = None       # LangletTransformer instance
        self.prelexer       = None       # LangletPostlexer instance
        self.postlexer      = None       # LangletPostlexer instance
        self.unparser       = None       # LangletUnparser instance
        self.fn             = None       # LangletCSTFunction instance
        self.lexer          = None       # NFALexer instance
        self.parser         = None       # NFAParser instance
        self.lexerhook      = None       # Registered lexerhook
        self.keywords       = None       # dict of keywords of this langlet
        self.target         = None       # Langlet instance of transformation target
        self.compiler       = None       # Compiler instance of target langlet
        self.langlet_id     = 0          # NID of this langlet
        self.MAX_NID        = 0          # maximum NID of this langlet
        # when creating a new langlet remove previous excepthooks
        sys.excepthook = sys.__excepthook__

    # public API

    def get_path(self):
        return path(self.config.__file__).dirname()

    path = property(get_path)

    del get_path

    def get_node_name(self, nid, typ = "parse", error_fn = lambda item: None):
        '''
        Node name from node id.
        '''
        name = None
        if nid is None:
            return "None"
        elif is_keyword(nid):
            if typ == "parse":
                return "kwd:"+flip(self.parse_nfa.keywords).get(nid, str(nid))
            else:
                return "kwd:"+flip(self.lex_nfa.keywords).get(nid, str(nid))
        elif is_token(nid):
            if typ == "parse":
                name = self.parse_token.tok_name.get(nid)
            else:
                name = self.lex_token.tok_name.get(nid)
        elif is_symbol(nid):
            if typ == "parse":
                name = self.parse_symbol.sym_name.get(nid)
            else:
                name = self.lex_symbol.sym_name.get(nid)
        if name:
            return name
        else:
            error_fn(nid)
            return "?(nid = %s)"%nid

    def get_kwd_id(self, keyword, typ = "parse", error_fn = lambda item: None):
        if typ == "parse":
            nid = self.parse_nfa.keywords.get(keyword)
        elif typ == "lex":
            nid = self.lex_nfa.keywords.get(keyword)
        if nid is not None:
            return nid
        else:
            error_fn(rule_name)
            return -1

    def get_node_id(self, rule_name, typ = "parse", error_fn = lambda item: None):
        '''
        Node id from rule name
        '''
        if typ == "parse":
            nid = self.parse_symbol.__dict__.get(rule_name)
            if nid is not None:
                return nid
            nid = self.parse_token.token_map.get(rule_name) or self.parse_token.__dict__.get(rule_name)
            if nid is not None:
                return nid
        elif typ == "lex":
            nid = self.lex_symbol.__dict__.get(rule_name)
            if nid is not None:
                return nid
            nid = self.lex_token.token_map.get(rule_name) or self.lex_token.__dict__.get(rule_name)
            if nid is not None:
                return nid
        error_fn(rule_name)
        return -1

    def parse_file(self, filename):
        source = open(filename).read()
        return self.parse(source, filename = filename)

    def tokenize(self, source, filename = ""):
        scanned = self.lexer.scan(source, filename = filename)
        self.display.maybe_show_scan(scanned)
        token_stream = self.postlexer.run(scanned)
        self.display.maybe_show_token(token_stream)
        return TokenStream(token_stream)

    def untokenize(self, tokstream):
        if isinstance(tokstream, TokenStream):
            tokstream = tokstream.tokstream
        node = [self.langlet_id+1000]+tokstream
        return self.unparse(node)

    def parse(self, source, start_symbol = None, filename = ""):
        '''
        Parse input source string into CST.
        '''
        if isinstance(source, TokenStream):
            parse_tree = self.parser.parse(source, start_symbol, filename)
        else:
            if not source.endswith("\n"):
                source+="\n"
            tokstream  = self.tokenize(source, filename = filename)
            parse_tree = cstnode(self.parser.parse(tokstream, start_symbol, filename = filename))
        self.display.maybe_show_cst_before(parse_tree)
        return parse_tree

    def transform(self, tree, **kwd):
        if isinstance(tree, basestring):  # source code
            tree = self.parse(tree, filename = kwd.get("filename"))
        show_token = self.options.get("show_token")
        self.options["show_token"] = False
        cst = self.transformer.run(tree, **kwd)
        cst = self.target.projection(cst)
        self.display.maybe_show_cst_after(cst)
        self.display.maybe_show_source(cst)
        self.transformer.clean_up()
        self.options["show_token"] = show_token
        return cst

    def compile(self, tree):
        self.display.maybe_grammar_check(tree)
        if isinstance(tree, basestring):  # source code
            tree = self.transform(tree)
        return self.compiler.compile(tree)

    def compile_file(self, filename):
        with open(filename) as f:
            source = f.read()
            cst = self.transform(source, filename = filename)
            self.display.maybe_grammar_check(cst)
            return self.compiler.compile(cst, filename)

    def tokenize_file(self, filename):
        source = open(filename).read()
        return self.tokenize(source, filename)

    def unparse(self, node):
        '''
        unparse CST node into source string.
        '''
        return self.unparser.unparse(node)

    def pprint(self, node, **kwd):
        self.cstdisplay.pprint(node, **kwd)

    def import_module(self, module_path):
        return self.importer.load_module(module_path)

    def check_node(self, node, no_ok_msg = True):
        checker = cstcheck.NodeChecker(self)
        return checker.check_node(node)

    def console(self):
        '''
        Creates new console object for this langlet.
        '''
        from langscape.base.console.console import LSConsole
        from langscape.base.console.rrconsole import LSRecordedReplayConsole, \
                                      LSReplayConsoleTest, LSRecordedConsole
        session   = self.options.get("session")
        recording = self.options.get("recording")
        if session:
            if recording:
                console = LSRecordedReplayConsole(self, self.config.langlet_name, session = session, recording = recording)
            else:
                console = LSReplayConsoleTest(self, self.config.langlet_name, session = session)
        elif recording:
            console = LSRecordedConsole(self, self.config.langlet_name, recording = recording)
        else:
            console = LSConsole(self, self.config.langlet_name)
        return console

    def projection(self, node):
        try:
            if is_keyword(node[0]):
                nid = self.parse_nfa.keywords.get(node[1])
                if nid:
                    node[0] = nid
                else:
                    node[0] = node[0]%LANGLET_ID_OFFSET+self.langlet_id
            else:
                node[0] = node[0]%LANGLET_ID_OFFSET+self.langlet_id
            for i,item in enumerate(node[1:]):
                if isinstance(item, list):
                    self.projection(item)
        except IndexError:
            raise
        return node

    def run_module(self, cmdline_module_path):
        '''
        :param cmdline_module_path: command line module path data e.g. ``mod.py`` or ``tests/foo/mod.py``.
        '''
        try:
            sys.argv = sys.argv[sys.argv.index(cmdline_module_path):]
        except ValueError:
            pass
        md = LangletModuleDescriptor()
        md.is_main = True
        md.fpth_mod_input = path(cmdline_module_path)
        md.compute_module_path()
        self.importer.set_module_descriptor(md)
        self.importer.register_importer()
        self.target.register_excepthook(self)
        __import__(md.module_path)


    def register_excepthook(self, langlet):
        '''
        Nothing to register in base langlet.
        '''

    # loading and installing services

    def _load_target_langlet(self):
        if self.config.langlet_name == self.config.target_langlet:
            self.target = self
        else:
            self.target = loader.load_langlet(self.config.target_langlet)
        self.target._load_compiler()

    def _load_compiler(self):
        Compiler = loader.load_compiler(self.config.target_compiler)
        self.compiler = Compiler(self)

    def _load_unparser(self):
        from langscape.csttools.cstunparser import Unparser
        self.unparser = Unparser(self)

    def _load_lexer(self):
        from langscape.trail.nfalexer import NFALexer
        self.lexer = NFALexer(self)

    def _load_parser(self):
        from langscape.trail.nfaparser import NFAParser
        self.parser = NFAParser(self)

    def _load_display(self):
        self.display = DisplayMixin()
        self.display.langlet = self
        self.cstdisplay = CSTTextualDisplay(self)

    def _create_cstbuilder(self):
        build_cstbuilder = loader.load_cstbuilder(self.package)
        builder = CSTBuilder(self)
        return build_cstbuilder(builder)


    def _load_superglobals(self, transformer_module):
        dct = transformer_module.__dict__
        import __builtin__
        superglobals = dct.get("__superglobal__", [])
        for name in superglobals:
            value = dct.get(name)
            if value is None:
                raise ValueError("Unknown superglobal '%s'. No corresponding value found in transformer module"%name)
            else:
                __builtin__.__dict__[name] = value

    def _load_symbols(self):
        if self.package is None:
            raise RuntimeError("Cannot load parse-tables. Langlet package could not be found")
        # load token/symbols
        if self.symbol is None:
            symbols = loader.load_symbols(self.package)
            self.lex_token      = symbols["lex_token"].LexerToken
            self.langlet_id     = symbols["lex_token"].LANGLET_ID
            self.lex_symbol     = symbols["lex_symbol"]
            self.parse_token    = self.token  = symbols["parse_token"]
            self.parse_symbol   = self.symbol = symbols["parse_symbol"]
            self.MAX_NID        = max(self.parse_symbol.sym_name.values())

    def _load_parse_tables(self):
        if self.package is None:
            raise RuntimeError("Cannot load parse-tables. Langlet package could not be found")
        # load token/symbols
        if not self.parse_nfa:
            # load nfas
            nfas = loader.load_parse_tables(self.package)
            self.lex_nfa   = nfas["lex_nfa"]
            self.parse_nfa = nfas["parse_nfa"]
            self.keywords  = flip(self.parse_nfa.keywords)

    def load_libraries(self, **kwd):
        if self.package is None:
            raise RuntimeError("Cannot load parse-tables. Langlet package could not be found.")
        if self.transformer is None:
            modules = loader.load_libs(self.config.langlet_name, self.package)
            _, module = modules["cstfunction"]
            self.fn = module.LangletCSTFunction(self)
            #
            # prelexer
            #
            pth, module = modules["prelexer"]
            if pth == "langscape.base.prelexer":
                self.prelexer = module.Prelexer(self)
            else:
                self.prelexer = module.LangletPrelexer(self)
            #
            # postlexer
            #
            pth, module = modules["postlexer"]
            if pth == "langscape.base.postlexer":
                self.postlexer = module.Postlexer(self)
            else:
                self.postlexer = module.LangletPostlexer(self)
            #
            # unparser
            #
            pth, module = modules["unparser"]
            if pth == "langscape.base.unparser":
                self.unparser = module.Unparser(self)
            else:
                self.unparser = module.LangletUnparser(self)
            #
            # importer
            #
            pth, module = modules["importer"]
            if pth == "langscape.base.importer":
                self.importer = module.Importer(self)
            else:
                self.importer = module.LangletImporter(self)
            _, transformer = modules["transformer"]
            self._load_superglobals(transformer)
            self._load_lexer()
            self._load_parser()
            self._load_display()
            self.transformer = transformer.LangletTransformer(self, **kwd)
            self._load_target_langlet()
            self._load_compiler()





