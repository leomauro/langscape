import operator
from itertools import*

class NonAdmissableCombination(Exception):pass

class Chainlet(object):
    __top = None                       # the top of a chainlet hieararchy
    def __init__(self, name=""):
        self._alt  = []
        self._mul  = []
        self.parent    = None
        self.name      = name

    def __repr__(self):
        if self._alt:
            return "|".join(str(s) for s in self._alt)
        if self._mul:
            return "*".join(str(s) for s in self._alt)
        if self.name:
            return self.name
        else:
            return object.__repr__(self)

    def __call__(self,name=None):
        '''
        Chainlet generator. Creates a child Chainlet of this Chainlet.
        '''
        chn = Chainlet(name=name)
        chn.parent = self
        return chn

    def __eq__(self,other):
        if self._alt:
            return self._alt == other._alt
        if self._mul:
            return self._mul == other._mul
        return id(self) == id(other)

    def __contains__(self,other):
        return other in self._alt

    def __or__(self, other):
        '''
        Alternative chainlets.
        Let A,B be chainlets and Ax<=A then Ax<=A|B.
        '''
        def cmp(x,y):
            if id(x)<id(y):
                return -1
            elif id(x)>id(y):
                return 1
            return 0

        chn = Chainlet()
        if self._alt or self._mul:
            s = [self._alt + self._mul]
        else:
            s = [self]
        if other._alt or other._mul:
            chn._alt = s+[other._alt + other._mul]
        else:
            chn._alt = s+[other]
        chn._alt.sort(cmp=cmp)      # respecting commutativity
        return chn

    def __mul__(self, other):
        '''
        Cartesian product of chainlets.
        Let A,B be chainlets and Ax<=A,Bx<=B then Ax*Bx<=A*B.
        '''
        chn = Chainlet()
        if self._alt or self._mul:
            s = [self._alt + self._mul]
        else:
            s = [self]
        if other._alt or other._mul:
            chn._mul = s+[other._alt + other._mul]
        else:
            chn._mul = s+[other]
        return chn

    def __lt__(self, other):
        return self<=other and self!=other

    def __le__(self, other):
        if other == self.top:
            return True
        if len(self._alt) == len(self._mul) == 0:
            # A <= B ?
            if len(other._alt) == len(other._mul) == 0:
                if self == other:
                    return True
                elif self.parent:
                    return self.parent<=other
            # A<=B|C  <-> A<=B | A<=C
            elif other._alt:
                for sub in other._alt:
                    if self<=sub:
                        return True
                return False
            # A <= B*C  -> False
            else:
                return False
        elif self._alt:
            # A|B <= C  <=> A<=C | B<=C
            for sub in self._alt:
                if sub <= other:
                    return True
            return False
        elif len(other._mul) == 0:
            # A*B <= C -> A<=C | B<=C
            for sub in self._mul:
                if sub<=other:
                    return True
        else:
            if len(self._mul)!=len(other._mul):
                return False
            else:
                for (A,B) in zip(self._mul,other._mul):
                    if not A<=B:
                        return False
                return True

    def cond(self,*args):
        res  = None              # default return value
        best_approx  = self.top  # most general scheme

        for val,chn in zip(args[::2],args[1::2]):
            if self == chn:
                return val
            elif self<=chn and chn<=best_approx:
                best_approx = chn
                res         = val
        return res

    def select(self,*args):
        return self.cond(*sum([[arg, arg] for arg in args],[]))


    def get_top(self):
        if Chainlet.__top:
            return Chainlet.__top
        else:
            Chainlet.__top = Chainlet("Top")
            return Chainlet.__top

    top = property(get_top,None,None)



def test():
    A   = Chainlet("A")
    B   = Chainlet("B")
    A1  = A("A1")
    A11 = A1("A11")
    B1  = B("B1")
    B11 = B1("B11")
    B12 = B1("B12")
    C = A1

    assert A1<=A
    assert A11<=A1
    assert A1!=A
    assert C<=A|B
    assert C|B1 <=A
    assert A*B <=A
    assert A*A11 <=A1
    assert A1*A11 <=A1*A1
    assert not A1*A11 <=A11*A1
    assert not A1*A11 <= B*A

    assert A|B == B|A
    assert A*B == A*B
    assert A*B != B*A
    assert C.select(A,B) == A
    assert C.select(A1|B1,B) == A1|B1
    assert A11.select(A1|B1,B) == A1|B1


test()
