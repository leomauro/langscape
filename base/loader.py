#! /usr/bin/env python
#
# URL:      http://www.fiber-space.de
# Author:   Kay Schluehr <kay@fiber-space.de>
# Creation: 15 Oct 2009

import sys
import os
from langscape.util import flip

__build_nfa = "--build-nfa" in sys.argv


def find_module(langlet_name, module_name):
    '''
    Searches for module based on langlet name and ``langscape.ls_const.LANGLETPATH``.

    The function returns a pair ``(module_path, module)``.
    '''
    import langscape.ls_const
    for pth in langscape.ls_const.LANGLETPATH:
        try:
            module_pth = pth+"."+langlet_name+"."+module_name
            module = __import__(module_pth, globals(), locals(), [""])
            return (module_pth, module)
        except:
            pass
    raise ImportError("Cannot find module '%s.%s' on LANGLETPATH"%(langlet_name, module_name))


def find_langlet(langlet_name):
    return find_module(langlet_name, "langlet")


def load_langlet(langlet_name, **options):
    '''
    Loads langlet module based on langlet name. A ``Langlet`` object is created and all libraries
    are loaded. The ``load_langlet`` function returns a fully functional ``Langlet`` object.
    '''
    from langscape.base.langlet import BaseLanglet
    langlet_path, langlet_config_module = find_module(langlet_name, "langlet_config")
    need_lex_nfa, need_parse_nfa = load_grammars(langlet_name, langlet_config_module.__file__)

    langlet_path, langlet_module = find_langlet(langlet_name)
    langlet_obj = getattr(langlet_module, "Langlet")(options)

    load_nfas(langlet_obj, need_lex_nfa, need_parse_nfa)
    langlet_obj.load_parse_tables()
    langlet_obj.load_libraries()
    return langlet_obj


def load_grammars(langlet_name, langlet_path):
    import langscape.base.grammar_gen as grammar_gen
    global __build_nfa
    if __build_nfa:
        options = {'build_nfa': True}
        __build_nfa = False
    else:
        options = {}
    need_lex_nfa   = grammar_gen.LexerGrammar(langlet_name, langlet_path, options).load_grammar()
    need_parse_nfa = grammar_gen.ParserGrammar(langlet_name, langlet_path, options).load_grammar()
    return need_lex_nfa, need_parse_nfa


def load_nfas(langlet_obj, need_lex, need_parse):
    from langscape.csttools import cstdef_gen
    from langscape.trail.nfagen import create_lex_nfa, create_parse_nfa
    if need_lex:
        create_lex_nfa(langlet_obj)
        need_parse = True
    if need_parse:
        create_parse_nfa(langlet_obj)
        langlet_obj.load_parse_tables()
        cstdef_gen.build_all(langlet_obj)

def load_cstbuilder(langlet_name):
    pth, langlet = find_langlet(langlet_name)
    return getattr(langlet, "load_cstbuilder")()

def load_compiler(compiler_type):
    module = __import__("langscape.compiler."+compiler_type+".codegen", globals(), locals(), ["langscape"])
    return module.Compiler

def BaseClass(classtype, parent):
    '''
    Loads LangletTransformer, LangletImporter, ... of a langlets parent based on the
    classtype i.e. "Transformer", "Importer", ...
    '''
    fragments = classtype.split(".")
    mod_pth, cls = fragments[:-1], fragments[-1]
    if not mod_pth:
        mod_pth = cls.lower()
    else:
        mod_pth = '.'.join(mod_pth).lower()
    if not parent:
        # load from base
        module = __import__("langscape.base."+mod_pth, globals(), locals(), ["langscape"])
        return module.__dict__[cls]
    else:
        # load from parent langlet
        langlet_path, langlet_module = find_langlet(parent)
        pth = ".".join(langlet_path.split(".")[:-1])
        module = __import__(pth+"."+mod_pth.lower(), globals(), locals(), ["langscape"])
        return module.__dict__.get("Langlet"+cls) or module.__dict__[cls]


