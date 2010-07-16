from __future__ import with_statement

class Compiler(object):
    def __init__(self, langlet):
        self.langlet = langlet

    def serialize(self, code, filename):
        '''
        Save compiled code.
        '''

    def compile(self, cst, filename = "<input>"):
        return self.langlet.unparse(cst)

    def compile_source(self, source, *args):
        return source

    def load_compiled(self, fullname, compiled_module_path):
        pass




