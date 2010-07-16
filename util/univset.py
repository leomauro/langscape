class univset(object):
    def __init__(self):
        self._diff = set()

    def __sub__(self, other):
        S = univset()
        if type(other) == set:
            S._diff = self._diff | other
            return S
        else:
            S._diff = self._diff | other._diff
            return S

    def __rsub__(self, other):
        return other & self._diff

    def __contains__(self, obj):
        return not obj in self._diff

    def __and__(self, other):
        return other - self._diff

    def __rand__(self, other):
        return other - self._diff

    def __repr__(self):
        if self._diff == set():
            return "ANY"
        else:
            return "ANY - %s"%self._diff

    def __or__(self, other):
        S = univset()
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


ANY = univset()

if __name__ == '__main__':
    ANY_BUT_A = ANY-set(['a'])
    ANY_BUT_B = ANY-set(['b'])

    C = set(['a', 'c', 'd'])
    ANY_BUT_A & C

    print  ANY_BUT_A & ANY_BUT_B

    NON_DIGITS = ANY - set(range(9))
    assert 8 not in NON_DIGITS
    assert 'a' in NON_DIGITS
    assert 0 in NON_DIGITS | set([0])


