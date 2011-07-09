__all__ = ["Prelexer"]

class Prelexer(object):
    def __init__(self, langlet):
        self.langlet  = langlet
        self.auxtoken = None

    def get_first_set(self, nid):
        pass

    def get_last_set(self, nid):
        pass

    def run(self, source):
        '''
        Overwrite this method in subclasses
        '''
        return source


