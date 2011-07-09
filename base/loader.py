# DISCUSSION: the way loading / importing is approached in langscape is somewhat ad hoc and a
#     source of problems. We already know that the right approach for loading/importing is to
#     start with a Path object and representations of those path objects.
#

import sys
import os
from langscape.util import flip
import langscape.ls_const

__build_langlet = "--build-langlet" in sys.argv

LANGLETPATH = ["langscape.langlets", "langscape.sourcetools"]


def get_package(module):
    return module[:module.rfind(".")]

def find_langlet(langlet_name):
    '''
    Returns module object corresponding to ``<langlet-path>/langlet.py`` module.
    '''
    if not langlet_name.replace("_", "").isalnum():
        raise ValueError("Invalid langlet '%s'"%langlet_name)
    for pth in LANGLETPATH:
        try:
            module_pth = pth+"."+langlet_name+".langlet"
            module = __import__(module_pth, globals(), locals(), [""])
            return (module_pth, module)
        except:
            pass
    module_pth = langlet_name+".langlet"
    module = __import__(module_pth, globals(), locals(), [""])
    return (module_pth, module)


def find_module(langlet_name, module_name):
    name = langlet_name
    while True:
        module_path, langlet = find_langlet(name)
        module_path = module_path.rsplit("langlet",1)[0]+module_name
        try:
            module = __import__(module_path, globals(), locals(), [""])
            return (module_path, module)
        except ImportError:
            if langlet.config.parent_langlet:
                name = langlet.config.parent_langlet
            else:
                try:
                    module = __import__("langscape.base."+module_name, globals(), locals(), [""])
                    return ("langscape.base."+module_name, module)
                except ImportError:
                    raise ImportError("Module '%s' not found in langlet '%s' its parent-langlets or 'langscape.base'."%(module_name, langlet_name))



def load_langlet(langlet_name, **options):
    '''
    Loads langlet module and instantiates Langlet object.
    '''
    from langscape.base.langlet import BaseLanglet
    langlet_path, langlet_config_module = find_module(langlet_name, "langlet_config")
    need_lex_nfa, need_parse_nfa = load_grammars(langlet_name, langlet_config_module.__file__, options)

    langlet_path, langlet_module = find_langlet(langlet_name)
    langlet_obj = getattr(langlet_module, "Langlet")(options)
    langlet_obj.package = get_package(langlet_path)
    langlet_obj._load_symbols()
    # print "PACKAGE", langlet_obj.package
    load_nfas(langlet_obj, need_lex_nfa, need_parse_nfa)
    langlet_obj._load_parse_tables()
    langlet_obj.load_libraries()
    return langlet_obj


def load_grammars(langlet_name, langlet_path, options):
    import langscape.base.grammar_gen as grammar_gen
    global __build_langlet
    if __build_langlet:
        options['build_langlet'] = True
        __build_langlet = False
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
        langlet_obj._load_parse_tables()
        cstdef_gen.build_all(langlet_obj)

def load_compiler(compiler_type):
    module = __import__("langscape.compiler."+compiler_type+".codegen", globals(), locals(), ["langscape"])
    return module.Compiler

def load_cstbuilder(langletpath):
    # print "LOAD-CSTBUILDER FROM", langletpath+".cstdef.cstbuilder_gen"
    cstbuilder_gen = __import__(langletpath+".cstdef.cstbuilder_gen", fromlist=["langscape"])
    return cstbuilder_gen.build_cstbuilder

def load_parse_tables(langletpath):
    lex_nfa   = __import__(langletpath+".lexdef.lex_nfa", fromlist=["langscape"])
    parse_nfa = __import__(langletpath+".parsedef.parse_nfa", fromlist=["langscape"])
    return vars()

def load_symbols(langletpath):
    lex_token    = __import__(langletpath+".lexdef.lex_token", fromlist=["langscape"])
    lex_symbol   = __import__(langletpath+".lexdef.lex_symbol", fromlist=["langscape"])
    parse_token  = __import__(langletpath+".parsedef.parse_token", fromlist=["langscape"])
    parse_symbol = __import__(langletpath+".parsedef.parse_symbol", fromlist=["langscape"])
    return vars()

def load_libs(langlet_name, langletpath):
    importer    = find_module(langlet_name, "importer")
    prelexer    = find_module(langlet_name, "prelexer")
    unparser    = find_module(langlet_name, "unparser")
    postlexer   = langletpath+".postlexer", __import__(langletpath+".postlexer", fromlist=["langscape"])
    transformer = langletpath+".transformer", __import__(langletpath+".transformer", fromlist=["langscape"])
    cstfunction = langletpath+".cstfunction", __import__(langletpath+".cstfunction", fromlist=["langscape"])
    return vars()


def BaseClass(classtype, parent):
    '''
    Loads ``Langlet<classtype>`` class of the declared parent of a langlet. The classtype
    is "Transformer", "Importer", ...

    Inheritance of a concrete langlet class works like ::

        class Langlet<classtype>(BaseClass(classtype, langlet_config.parent)):
            ...
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
        path, module = find_module(parent, mod_pth)
        #pkg = get_package(langlet_path)
        #module = __import__(pkg+"."+mod_pth.lower(), globals(), locals(), ["langscape"])
        return module.__dict__.get("Langlet"+cls) or module.__dict__[cls]


if __name__ == '__main__':
    langlet_mod_path = find_langlet("python")[0]
    langletpath = langlet_mod_path[:langlet_mod_path.rfind(".")]
    print find_module("p4d", "prelexer")


