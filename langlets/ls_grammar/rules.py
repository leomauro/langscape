class Rule(object):
    def __init__(self, lst):
        self.lst   = lst
    def __repr__(self):
        return self.__class__.__name__+"("+str(self.lst)[1:-1]+")"

class AltRule(Rule): pass
class ConstRule(Rule): pass
class EmptyRule(Rule): pass
class SequenceRule(Rule): pass

