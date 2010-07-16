from __future__ import with_statement
import langscape.util
from langscape.util.path import path
import pprint
import langscape.csttools.cstbuilder as cstbuilder
import langscape.csttools.cstlayers as cstlayers

__all__ = ["build_all"]

def cstdef_build(langlet_obj):
    cstdef_pth = langlet_obj.path.joinpath("cstdef")
    if not cstdef_pth.isdir():
        cstdef_pth.mkdir()
        file(langlet_obj.path.joinpath("cstdef","__init__.py"), "w")

def cstbuilder_gen(langlet_obj):
    cstlibgen_py_pth = langlet_obj.path.joinpath("cstdef","cstbuilder_gen.py")
    langlet_name = langlet_obj.config.langlet_name
    with open(cstlibgen_py_pth, "w") as cstlibgen_py:
        if langlet_obj.config.encoding:
            print >> cstlibgen_py, langscape.util.get_encoding_str(langlet_obj.config.encoding)+"\n"
        print >> cstlibgen_py, "def build_cstbuilder(cstbuilder):"
        builder = cstbuilder.CSTBuilder(langlet_obj)
        builder.factory(target = cstlibgen_py)
        print >> cstlibgen_py, "    return locals()\n"


def cstdefinit_gen(langlet_obj):
    cstlibgen_py_pth = langlet_obj.path.joinpath("cstdef","__init__.py")


def cstlayers_gen(langlet_obj):
    cstlibgen_py_pth = langlet_obj.path.joinpath("cstdef","cstlayers_gen.py")
    with open(cstlibgen_py_pth, "w") as cstlibgen_py:
        print >> cstlibgen_py, "\n# Hierarchy of layers\n"
        print >> cstlibgen_py, "cstlayers = %s"%pprint.pformat(cstlayers.layers(langlet_obj.parse_nfa))


def build_all(langlet_obj):
    cstdefinit_gen(langlet_obj)
    try:
        langlet_obj.parse_nfa.nfas
    except AttributeError:
        return
    cstdef_build(langlet_obj)
    cstbuilder_gen(langlet_obj)
    cstlayers_gen(langlet_obj)




