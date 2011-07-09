__all__ = ["create_nfa_skeleton", "create_sk_map", "nfa_comp"]

def create_nfa_skeleton(nfa):
    '''
    An nfa-skeleton abstracts away concrete state information but preserves the
    relations between states ( follow sets ). Each state will be reduced to an integer
    number normalized to the range [-1, 0, ... len(nfa) - 1 ]. The number -1 is
    reserved for the single FINAL state.

    NFA-skeletons are used to compare NFAs which usually requires an additional
    Maptracker which is described below.

    An nfa-skeleton will look like ::

        sk_nfa = {0: set([1, 3, 6, -1, 7]),
         1: set([2]),
         2: set([1, 3, 6, -1, 7]),
         3: set([6, 3, 4, 5, -1]),
         4: set([4, 5]),
         5: set([3, 6, -1]),
         6: set([-1]),
         7: set([-1])}
    '''
    trans = nfa[2]
    skeleton = {}
    states   = sorted(trans.keys(), key = lambda state: state[1])
    for s in trans:
        L = []
        follow = trans[s]
        for f in follow:
            if f[0] is None:
                L.append(-1)
            else:
                L.append(states.index(f))
        L.sort()
        skeleton[states.index(s)] = set(L)
    return skeleton


class Maptracker(object):
    '''
    A Maptracker is used to find a bijection between two NFA-skeletons.

    Example: let the following two NFA-skeletons be defined::

        sk1 = {0: set([1, 3, 6, -1, 7]),
         1: set([2]),
         2: set([1, 3, 6, -1, 7]),
         3: set([6, 3, 4, 5, -1]),
         4: set([4, 5]),
         5: set([3, 6, -1]),
         6: set([-1]),
         7: set([-1])}

        sk2 = {0: set([1, 3, 4, -1, 7]),
         1: set([2]),
         2: set([1, 3, 4, -1, 7]),
         3: set([-1]),
         4: set([6, 4, 5, -1, 7]),
         5: set([5, 6]),
         6: set([4, -1, 7]),
         7: set([-1])}

    When we want to figure out if they are equivalent we need to
    find a bijection of the set {0 .. 7} onto itself ::

        >>> mt = Maptracker(sk1, sk2)
        >>> mt.run()
        {0: 0, 1: 1, 2: 2, 3: 4, 4: 5, 5: 6, 6: 7, 7: 3}

    The values 0 and -1 are fixpoints. If a Maptracker fails to find a bijection
    it returns an empty dict.
    '''
    def __init__(self, sk1, sk2):
        self.sk1 = sk1
        self.sk2 = sk2

    def accept(self, value, stack):
        e1, e2 = value  # e1 -> e2
        V1 = self.sk1[e1]
        V2 = self.sk2[e2]
        #
        # e1 -> e2 => v1 -> v2
        #
        # check consistency of the choice of the mapping
        if len(V1)!=len(V2):
            return False
        m = dict(p for (p,q) in stack)
        if e2 in m.values():
            return False
        for v1 in V1:
            if v1 == e1:
                if e2 not in V2:
                    return False
            if v1 in m:
                if m[v1] not in V2:
                    return False
        for s in m:
            if e1 in self.sk1[s]:
                if e2 not in self.sk2[m[s]]:
                    return False
        return True


    def run(self):
        '''
        Creates the NFA-skeleton map as a dict. Returns an empty dict when it can't
        be constructed.
        '''
        stack = []
        if len(self.sk1) != len(self.sk2):
            return {}
        sig1 = sorted(len(v) for v in self.sk1.values())
        sig2 = sorted(len(v) for v in self.sk2.values())
        if sig1!=sig2:
            return {}

        L1 = self.sk1.keys()
        L2 = self.sk2.keys()
        i = j = 0
        while i<len(L1):
            e1 = L1[i]
            while j<len(L2):
                e2 = L2[j]
                if self.accept((e1,e2),stack):
                    stack.append(((e1,e2),(i,j)))
                    j = 0
                    break
                j+=1
            else:
                if stack:
                    _, (i,j) = stack.pop()
                    if j == -1:
                        return {}
                    j+=1
                    continue
                else:
                    return {}
            i+=1
        return dict(elem[0] for elem in stack)


def nfa_comp(nfa1, nfa2):
    '''
    Compares two NFAs by means of their NFA-skeleton.
    '''
    s_nfa1 = create_nfa_skeleton(nfa1)
    s_nfa2 = create_nfa_skeleton(nfa2)
    map = Maptracker(s_nfa1, s_nfa2).run()
    if map:
        return True
    return False


if __name__ == '__main__':
    import pprint
    import langscape
    from langscape.ls_const import*
    python = langscape.load_langlet("python")
    nfa = python.parse_nfa.nfas[python.symbol.varargslist]
    print "RULE", nfa[0]
    #pprint.pprint(nfa)
    #L = create_traces(python, python.symbol.file_input)
    sk1 = {0: set([1, 3, 6, -1, 7]),
     1: set([2]),
     2: set([1, 3, 6, -1, 7]),
     3: set([6, 3, 4, 5, -1]),
     4: set([4, 5]),
     5: set([3, 6, -1]),
     6: set([-1]),
     7: set([-1])}

    sk2 = {0: set([1, 3, 4, -1, 7]),
     1: set([2]),
     2: set([1, 3, 4, -1, 7]),
     3: set([-1]),
     4: set([6, 4, 5, -1, 7]),
     5: set([5, 6]),
     6: set([4, -1, 7]),
     7: set([-1])}

    GR2 = {0: set([1, 3, 6, -1, 7]),
     1: set([2]),
     2: set([1, 3, 6, -1, 7]),
     3: set([6, 3, 4, 5, -1]),
     4: set([4, 5]),
     5: set([3, 6, -1]),
     6: set([-1]),
     7: set([-1])}

    GR1 = {0: set([1, 3, 4, -1, 7]),
     1: set([2]),
     2: set([1, 3, 4, -1, 7]),
     3: set([-1]),
     4: set([6, 4, 5, -1, 7]),
     5: set([5, 6]),
     6: set([4, -1, 7]),
     7: set([-1])}


    phi = {0: 0, 1: 1, 2: 2, 3: 4, 4: 5, 5: 6, 6: 7, 7: 1}
    r = Maptracker(GR1, GR2).run()
    print r
    P = lambda k: (-1 if k == -1 else r[k] )
    print GR2 == dict( (P(key), set(map(P, value))) for (key, value) in GR1.items() )





