'''
1. Segments ::

    Whenever two CST nodes N, M are given we want to know whether N can be wrapped by M.
    This means we want a minimal path from N to M.

    We start using following definition:

    A segment S is defined recursively using following rules
      -------

        1. [nid(N), M] is a section between N and M if it a valid CST node.
        2. [nid(N), S] is a section if S is a segment and the list is a valid CST node.

    We call N the initial point of the segment and M the endpoint. Since segments are oriented
    we write [N->M].

    The empty segment shall be denoted by []. If for N, M there is no segment we say that [N->M] = [].

    Our goal is twofold.

    1. Define a function segment(N,M) that returns a segment [N->M].

    2. Create a tree from which segments can be constructed, called the segmenttree.

    Tree structure:

        A : (N1, N2, ... Nk)

2. Generalized Segments ::

   For Python we can find many useful non-empty segments, e.g. [expr->atom] or [test->atom].
   Other important segments like [file_input->test] are empty though. If we analyze this case
   we find that we get stuck at simple_stmt and simple_stmt can only be the lower end of a segment
   but never an upper one. This is because the minimum size of a simple_stmt node is always 3
   instead of the required 2 for a segment.

   When we analyze simple_stmt in more detail we find a valid node having following form:

           [symbol.simple_stmt, N, NEWLINE]

   Not only is NEWLINE a token but also one with a `fixed content` C. A token T is defined by
   T = [nid, content, line, (col1,col2)] and `fixed content` means that T[1] = C for all T.
   The variable part is therefore still just N.

    A generalized segment S is defined recursively using following rules
      -------------------

        1. [nid(N), M1,..,M,...,Mk] is a section between N and M if it a valid CST node and
           M1,...,Mk / M are fixed content token and M is an arbitrary node.

        2. [nid(N), M1,...,S,...,Mk] is a section if S is a generalized segment, the list is a valid
           CST node and M1,...,Mk / S are fixed content token and M is an arbitrary node.

3. Deterministic Interpolation ::

    For any two nodes M,N there can be more than one generalized segment connecting them.
    We denote the set of generalized segments {N->M} with N at the start and M at the end.

    A generalized segment K = [nid(N), M1,...,S,...,Mk] is minimal iff

        (i)  K is the shortest generalized segment starting with nid(N)
        (ii) S is minimal.

    If min{N->M} is the set of minimal generalized segments and len(min{N->M}) = 1 we write
    [[N->M]] for the generalized segment.

3. Implementation ::

    For each N we know the set reachable(N).
'''
from langscape.ls_const import SYMBOL_OFFSET, FIN
from cstutil import is_token, is_keyword, is_symbol
from langscape.trail.nfatracer import NFATracer, NFATracerUnexpanded

class SegmentNode(object):
    def __init__(self, nid, simple_segments, reachables):
        self.nid   = nid
        self.table = {}
        self.simple_segments  = simple_segments
        for i, L in enumerate(simple_segments):
            s = L[0]
            if is_token(s):
                self.table[s] = i
            else:
                self.table[s] = i
                for rx in reachables[s]:
                    self.table[rx] = i

    def __repr__(self):
        return "%s -> %s"%(self.nid, self.simple_segments)



class SegmentTree(object):
    def __init__(self, langlet):
        self._cache = {}
        self.simple_segments = {}
        self.langlet = langlet
        self.nodes = {}

    def _has_fixed_content(self, nid):
        try:
            return nid+SYMBOL_OFFSET in self.langlet.lex_nfa.constants
        except TypeError:
            return True

    def _min_span(self, S, tracer, visited):
        s = S[-1]
        if type(s) == list:
            s = s[0]
        selection = tracer.select(s)
        if FIN in selection:
            return S
        else:
            T = []
            for t in selection:
                if self._has_fixed_content(t):
                    T.append(t)
                elif is_keyword(t):
                    T.append(t)
            if len(T):
                minR = [0]*10
                minT = None
                for t in T:
                    if t not in visited:
                        V = set([t])
                        V.update(visited)
                        R = self._min_span(S+[t], tracer.clone(), V)
                        if R and len(R)<len(minR):
                            minR = R
                            minT = t
                if minT:
                    S.append(minT)
                    return minR
        return []

    def _create_simple_segments(self):
        for r in self.langlet.parse_nfa.reachables:
            tracer = NFATracerUnexpanded(self.langlet.parse_nfa)
            prefix = []

            r1 = r
            while True:
                selection = tracer.select(r1)
                if len(selection) == 1 and is_keyword(selection[0]):
                    prefix.append(selection[0])
                    r1 = selection[0]
                else:
                    break

            nodes = []
            for s in selection:
                if s is FIN:
                    continue
                S = []
                S.append(s)
                R = self._min_span(S, tracer.clone(), set())
                if R:
                    nodes.append(prefix+R)
            self.simple_segments[r] = nodes

    def create(self):
        self._create_simple_segments()
        for r in self.simple_segments:
            self.nodes[r] = SegmentNode(r, self.simple_segments[r], self.langlet.parse_nfa.reachables)

    def __getitem__(self, item):
        return self.segment(item.start, item.stop)

    def segment(self, begin, end):
        segm = self._cache.get((begin, end))
        if segm:
            return segm
        elif begin == end:
            return [begin]
        else:
            segm = [begin]
            r = begin
            while True:
                nd = self.nodes.get(r)
                if nd is None:
                    return []
                idx = nd.table.get(end)
                if idx is None:
                    return []
                else:
                    simple_segm = nd.simple_segments[idx]
                    if len(simple_segm) == 1:
                        r = simple_segm[0]
                        segm.append(r)
                        if r == end:
                            self._cache[(begin, end)] = segm
                            return segm
                    else:
                        r = simple_segm[0]
                        segm.append(simple_segm)
                        if r == end:
                            self._cache[(begin, end)] = segm
                            return segm

def fold_segment(segment):
    res = []
    for item in segment[::-1]:
        if type(item) == int:
            if res:
                if type(res[0]) == int:
                    res = [item, res]
                else:
                    res = [item]+res
            else:
                res.append(item)
        else:
            S = []
            for r in item:
                if is_token(r):
                    S.append([r])
                else:
                    S.append([r, res])
            res = S
    return res

def proj_segment(segment):
    '''
    Let S = [a -> b] a generalized segment. For a simple segment we can substitute 'a' by 'b' but in the
    general case we need to add also a few constant token.
    '''
    P = []
    S = 0
    for item in segment[::-1]:
        if P == []:
            if type(item) == int:
                P = [item]
            else:
                P = item
        elif type(item) != int:
            for i,s in enumerate(item):
                if is_symbol(s):
                    S = s
                    P = item[:i]+P+item[i+1:]
    return S, P


if __name__ == '__main__':
    import pprint
    import langscape
    langlet = langscape.load_langlet("python")
    st = SegmentTree(langlet)
    st.create()
    #pprint.pprint( st.nodes )
    seg =  st[langlet.parse_symbol.stmt: langlet.parse_symbol.test]
    print "Segment[stmt: test] = ", seg
    print "proj_segment(seg)   = ", proj_segment(seg)
    print "fold_segment(seg)   = ", fold_segment(seg)






