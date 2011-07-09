import sys

def dbg_import(text):
    # lightweight logging function
    frame  = sys._getframe()
    f_name = frame.f_back.f_code.co_name
    f_line = frame.f_back.f_lineno
    sys.stdout.write("dbg-import: %s: %s: %s\n"%(f_name, f_line, text))

class Importer(object):
    def __init__(self, langlet, *args):
        '''
        :param langlet: langlet module object
        '''
        self.langlet = langlet

    def set_module_descriptor(self, md):
        pass

    def register_importer(self):
        pass

    def find_module(self, *args):
        pass

    def load_module(self, fullname):
        pass
