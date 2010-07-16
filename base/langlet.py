#! /usr/bin/env python
#
# URL:      http://www.fiber-space.de
# Author:   Kay Schluehr <kay@fiber-space.de>
# Creation: 15 Oct 2009

from __future__ import with_statement
import sys, os
import __main__
import langscape.base.loader as loader
import langscape.csttools.cstcheck as cstcheck
import langscape.csttools.cstrepr as cstrepr
from langscape.csttools.cstutil import*
from langscape.util import flip
from langscape.util.path import path
from langscape.base.display import DisplayMixin
from langscape.trail.nfaparser import TokenStream

class BaseLanglet(object):

    def get_node_name(self, nid, typ = "parse", error_fn = lambda item: None):
        '''
        Node name from node id.
        '''
        if nid is None:
            return "None"
        elif is_keyword(nid):
            if typ == "parse":
                return flip(self.parse_nfa.keywords).get(nid, "KEYWORD")
            else:
                return flip(self.lex_nfa.keywords).get(nid, "KEYWORD")
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

    def get_node_builder(self, nid):
        name = self.get_node_name(nid)
        return getattr(self.fn, name)

    def parse_file(self, filename):
        source = open(filename).read()
        self.parse(source, filename = filename)

    def tokenize(self, source):
        scanned = self.lexer.scan(source)
        self.display.maybe_show_scan(scanned)
        token_stream = self.postlexer.run(scanned)
        self.display.maybe_show_token(token_stream)
        return TokenStream(token_stream)

    def parse(self, source, start_symbol = None, filename = ""):
        '''
        Parse input source string into CST.
        '''
        if isinstance(source, TokenStream):
            parse_tree = self.parser.parse(source, start_symbol, filename)
        else:
            if not source.endswith("\n"):
                source+="\n"
            tokstream  = self.tokenize(source)
            parse_tree = cstnode(self.parser.parse(tokstream, start_symbol))
        self.display.maybe_show_cst_before(parse_tree)
        return parse_tree

    def transform(self, tree, **kwd):
        if isinstance(tree, basestring):  # source code
            tree = self.parse(tree)
        cst = self.transformer.run(tree, **kwd)
        cst = self.target.projection(cst)
        self.display.maybe_show_cst_after(cst)
        self.display.maybe_show_source(cst)
        return cst

    def compile(self, tree):
        self.display.maybe_grammar_check(tree)
        if isinstance(tree, basestring):  # source code
            tree = self.transform(tree)
        return self.compiler.compile(tree)

    def compile_file(self, filename):
        with open(filename) as f:
            source = f.read()
            cst = self.transform(source)
            self.display.maybe_grammar_check(cst)
            compiled_filename = filename.splitext()[0] + self.config.compiled_ext
            return self.compiler.compile(cst, compiled_filename)

    def tokenize_file(self, filename):
        source = open(filename).read()
        return self.tokenize(source, filename)

    def unparse(self, node):
        '''
        unparse CST node into source string.
        '''
        return self.unparser.unparse(node)

    def pprint(self, node, **kwd):
        #import pprint
        #pprint.pprint(node)
        cstrepr.pprint(self, node, **kwd)

    def import_module(self, module_path):
        return self.importer.load_module(module_path)

    def check_node(self, node, no_ok_msg = True):
        checker = cstcheck.NodeChecker(self)
        return checker.run(node)

    def console(self):
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

    def get_path(self):
        return path(self.config.__file__).dirname()

    path = property(get_path)

    # loading and installing services

    def load_target_langlet(self):
        if self.config.langlet_name == self.config.target_langlet:
            self.target = self
        else:
            self.target = loader.load_langlet(self.config.target_langlet)
        self.target.load_compiler()

    def load_compiler(self):
        Compiler = loader.load_compiler(self.config.target_compiler)
        self.compiler = Compiler(self)

    def load_unparser(self):
        from langscape.csttools.cstunparser import Unparser
        self.unparser = Unparser(self)

    def load_lexer(self):
        from langscape.trail.nfalexer import NFALexer
        self.lexer = NFALexer(self)

    def load_parser(self):
        from langscape.trail.nfaparser import NFAParser
        self.parser = NFAParser(self)

    def load_display(self):
        self.display = DisplayMixin()
        self.display.langlet = self

    def load_superglobals(self, transformer_module):
        dct = transformer_module.__dict__
        import __builtin__
        superglobals = dct.get("__superglobal__", [])
        for name in superglobals:
            value = dct.get(name)
            if value is None:
                raise ValueError("Unknown superglobal '%s'. No corresponding value found in transformer module"%name)
            else:
                __builtin__.__dict__[name] = value

    def projection(self, node):
        try:
            if is_keyword(node[0]):
                nid = self.parse_nfa.keywords.get(node[1])
                if nid:
                    node[0] = nid
                else:
                    node[0] = nid%LANGLET_ID_OFFSET+self.langlet_id
            else:
                node[0] = node[0]%LANGLET_ID_OFFSET+self.langlet_id
            for i,item in enumerate(node[1:]):
                if isinstance(item, list):
                    self.projection(item)
        except IndexError:
            raise
        return node

    def get_module_name(self, module):
        mod_path = module.dirname()
        if mod_path.isdir() and mod_path.isabs():
            sys.path.append(mod_path)
            return path(module).splitext()[0].basename()
        else:
            mod_path = path(os.getcwd())
            sys.path.append(mod_path)
            return module.splitext()[0].replace(os.sep, ".")

    def run_module(self, module):
        '''
        @param module: file system module name.
        @param langlet: langlet module.
        '''
        sys.argv = sys.argv[sys.argv.index(module):]
        module = path(module)
        module_name = self.get_module_name(module)
        self.options["main_module"] = (module, module_name)
        self.importer.register_importer()
        __import__(module_name)
        Module = sys.modules[module_name]
        if hasattr(Module, "__like_main__"):
            import __builtin__
            __builtin__.__dict__["__like_main__"] = Module.__file__
            Module.__like_main__()


class NodeNotFound(Exception):pass

class LangletTable(object):
    def __init__(self):
        self.langlets = {}

    def register(self, langlet):
        self.langlets[langlet.config.LANGLET_ID] = langlet

    def error_report_fn(self, rule_name):
        raise NodeNotFound

    def get_node_name(self, nid, typ = "parse"):
        for langlet in self.langlets.values():
            try:
                return langlet.get_node_name(nid, typ, self.error_report_fn)
            except NodeNotFound:
                pass
        return "?(nid = %s)"%nid

    def get_layers(self, nid):
        langlet_id = nid - nid%LANGLET_ID_OFFSET
        return self.langlets[langlet_id].layers


langlet_table = LangletTable()
