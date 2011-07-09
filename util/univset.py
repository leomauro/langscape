__all__ = ["univset", "Any", "ANY", "White", "Alpha", "U_Alpha", "Digit"]

class univset(object):
    def __init__(self):
        self._diff = set()

    def __sub__(self, other):
        S = self.__class__()
        if type(other) == set:
            Other   = set([s for s in other if s in self])
            S._diff = self._diff | Other
            return S
        else:
            if other == self:
                return set()
            S._diff = self._diff | other._diff
            return S

    def __rsub__(self, other):
        return other & self._diff

    def __contains__(self, obj):
        return not obj in self._diff

    def __and__(self, other):
        if isinstance(other, set):
            return set([s for s in other if s in self])
        return other - self._diff

    def __rand__(self, other):
        if isinstance(other, set):
            return set([s for s in other if s in self])
        return other - self._diff

    def __repr__(self):
        if self._diff == set():
            return "Any"
        else:
            return "Any - %s"%self._diff

    def __or__(self, other):
        S = self.__class__()
        if isinstance(other, set):
            Other = set([s for s in other if s in self])
            S._diff = self._diff - Other
        else:
            S._diff = self._diff - other
        return S

    def __xor__(self, other):
        return (self - other) | (other - self)

    def add(self, elem):
        if elem in self._diff:
            self._diff.remove(elem)

    def update(self, elem):
        self._diff = self._diff - other

    def __ror__(self, other):
        return self.__or__(other)

    def union(self, other):
        return self.__or__(other)

    def difference(self, other):
        return self.__sub__(other)

    def intersection(self, other):
        return self.__and__(other)

    def symmetric_difference(self, other):
        return self.__xor__(other)

    def issubset(self, other):
        if type(other) == set:
            return False
        if issubset(other._diff, self._diff):
            return True
        return False

    def issuperset(self, other):
        if self._diff & other:
            return False
        return True

    def __lt__(self, other):
        return self.issubset(other)

    def __eq__(self, other):
        if type(other) == set:
            return False
        try:
            return self._diff == other._diff
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        return self.issuperset(other)

    def __gt__(self, other):
        return self.issuperset(other) or self == other



class alphabet(univset):
    def __repr__(self):
        if self._diff == set():
            return "Alpha"
        else:
            return "Alpha - %s"%self._diff

    def __contains__(self, c):
        try:
            if c == "_" or str.isalpha(c):
                return not c in self._diff
        except TypeError:
            pass
        return False

class u_alphabet(univset):
    def __repr__(self):
        if self._diff == set():
            return "U_Alpha"
        else:
            return "U_Alpha - %s"%self._diff

    def __contains__(self, c):
        try:
            if c == "_" or unicode.isalpha(c):
                return not c in self._diff
        except TypeError:
            pass
        return False

class whitespace(univset):
    def __repr__(self):
        if self._diff == set():
            return "White"
        else:
            return "White - %s"%self._diff

    def __contains__(self, c):
        try:
            if str.isspace(c):
                return not c in self._diff
        except TypeError:
            pass
        return False

class digit(univset):
    def __repr__(self):
        if self._diff == set():
            return "Digit"
        else:
            return "Digit - %s"%self._diff

    def __contains__(self, c):
        try:
            if str.isdigit(c):
                return not c in self._diff
        except TypeError:
            pass
        return False

Alpha   = alphabet()
White   = whitespace()
U_Alpha = u_alphabet()
Any     = univset()
ANY     = Any
Digit   = digit()

if __name__ == '__main__':
    ANY_BUT_A = Any-set(['a'])
    ANY_BUT_B = Any-set(['b'])

    C = set(['a', 'c', 'd'])
    ANY_BUT_A & C

    print  ANY_BUT_A & ANY_BUT_B
    print 'd' in Alpha
    print Alpha._diff
    '''
    NON_DIGITS = Any - set(range(9))
    assert 8 not in NON_DIGITS
    assert 'a' in NON_DIGITS
    assert 0 in NON_DIGITS | set([0])

    print Alpha - set('a)')

    print 'a' in Alpha - set(['b'])
    print 'b' in Alpha - set(['b'])
    print u'a' in U_Alpha - set([u'b'])
    print u'b' in U_Alpha - set([u'b'])
    '''



