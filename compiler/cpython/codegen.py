from __future__ import with_statement

import imp
import langscape
from langscape.csttools.cstsearch import*
from langscape.csttools.cstutil import*
import pprint
import os
import struct
import marshal
import parser
import dis

MAGIC = imp.get_magic()

class Compiler(object):
    def __init__(self, langlet):
        self.langlet = langlet
        self.python  = langscape.load_langlet("python")

    def serialize(self, code, filename):
        '''
        Save compiled code in .pyc file.
        '''
        filename = filename.splitext()[0] + self.langlet.config.compiled_ext
        with open(filename, "wb") as f:
            mtime = os.path.getmtime(filename)
            mtime = struct.pack('<i', mtime)
            f.write(MAGIC + mtime)
            marshal.dump(code, f)

    def compile(self, cst, filename = "<input>"):
        P = self.python.map_to_python(cst, self.langlet)
        try:
            ast = parser.tuple2ast(P)
            code = ast.compile(filename)
            self.python._code[filename] = ('cst', cst)
        except parser.ParserError, e:
            source = self.langlet.unparse(cst)
            code = compile(source, filename, "exec")
            self.python._code[filename] = ('src', source)
        if filename != "<input>":
            self.serialize(code, filename)
        return code

    def compile_source(self, *args):
        return compile(*args)

    def load_compiled(self, fullname, compiled_module_path):
        with open(compiled_module_path, "rb") as f:
            m_compiled = imp.load_compiled( fullname, compiled_module_path, f )
            return m_compiled





