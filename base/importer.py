class Importer(object):
    def __init__(self, langlet, *args):
        '''
        :param langlet: langlet module object
        '''
        self.langlet      = langlet

    def register_importer(self):
        pass

    def find_module(self, *args):
        pass

    def load_module(self, fullname):
        pass
