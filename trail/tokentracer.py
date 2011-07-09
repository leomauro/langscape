'''
TODO:

(NFA, {(S1, F1), (S2, F2), ..., (Sk, Nk)})



The basic problem of NFAs is that the continuation of (FIN, '-', R) is context dependent. Depending
on how R gets entered ( in which NFA R is embedded ) we find nodes R1, ..., Rk which continue R. However
those nodes are all well known and associated to states.

So let's say we have an originial set of states S0

Suppose T is a token. FOLLOW(T) may be the set of terminals/nonterminals following T across all NFAs.
With FIRST(N) we characterize the set of token which are in the first-set of N. Building

For each token T we determine the follow-set Follow(T). If nid = T[0] we can also consider the joint
follow FOLLOW(nid). The joint first set for F in FOLLOW(nid) is FIRST(FOLLOW(nid)).

The parse-tree is the reified context information for the sequence of token. However for token-traces
we can forget about being in several contexts at the same time.

###################################################################################################
'''
from langscape.csttools.cstutil import*
from langscape.trail.nfatracer import NFATracer
import pprint

__all__ = ["TokenTracer"]

class _TokenTracer(NFATracer):
    def __init__(self, langlet, nfas, expanded, kind, cache):
        self.langlet  = langlet
        self.expanded = expanded
        self.nfas     = nfas
        self.state    = []   # can be shared by several nodes with same nid
        self.initial  = None
        self.tracers  = {}
        self.trans    = {}
        self.parent   = None
        self.start    = None
        self.kind     = kind
        self.cache    = cache

    def clone(self, cloned = None):
        # TODO: needs testing
        if cloned is None:
            cloned = {}
        cl = cloned.get(self)
        if cl:
            return cl
        rt = _TokenTracer(self.langlet, self.nfas, self.expanded, self.kind, self.cache)
        cloned[self] = rt
        rt.initial = self.initial
        rt.state = self.state[:]
        rt.start = self.start
        rt.kind  = self.kind
        rt.trans = self.trans
        pt = cloned.get(self.parent)
        if pt:
            rt.parent = pt
        elif self.parent:
            rt.parent = self.parent.clone(cloned)
            cloned[self.parent] = rt.parent
        for s, tracers in self.tracers.items():
            ct = []
            for T in tracers:
                C = cloned.get(T)
                if C is None:
                    C = T.clone(cloned)
                ct.append(C)
            rt.tracers[s] = ct
        return rt


    def select(self, nid, follow_tracers = None, visited = None):
        if follow_tracers is None:
            follow_tracers = {}
        if visited is None:
            visited = set()
        selection = set()
        if self.tracers:
            tracers = [(state, self.tracers[state]) for state in self.state if state[0] == nid]
            if tracers == []:
                raise NonSelectableError(nid)
            for state, tracer in tracers:
                for T in tracer:
                    next_selection = T._next_selection(state, follow_tracers, visited)
                    selection.update(next_selection)
            self.tracers = follow_tracers
            self.state = list(selection)
            return set(s[0] for s in selection)
        else:
            if nid in self.expanded:
                nfa   = self.expanded[nid]
            elif nid in self.nfas:
                nfa   = self.nfas[nid]
            else:
                raise NonSelectableError(nid)
            self.trans = nfa[2]
            self.start = nfa[1]
            self.state = [self.start]
            self.tracers = {self.start: [self]}
            return self.select(nid, follow_tracers, visited)


    def _next_selection(self, state, follow_tracers, visited):
        follow = self.trans[state]
        selection = set()
        if type(state[1]) == str:
            for S in follow:
                selection.update(self._next_selection(S, follow_tracers, visited))
            return selection
        for S in follow:
            if S[0] is FIN:
                if self.parent is None:
                    selection.add(S)
                if self.initial:
                    selection.update(self.parent._next_selection(self.initial, follow_tracers, visited))
            elif is_token(S[0]):
                selection.add(S)
                T = follow_tracers.get(S)
                if T:                        # first/first - conflict
                    for t in T:
                        if t.initial!=self.initial or t.state!=self.state:  # TODO: explore the application of this
                            T.append(self)                                  #       this condition
                            break
                else:
                    follow_tracers[S] = [self]
            else:
                subtracer = _TokenTracer(self.langlet, self.nfas, self.expanded, self.kind, self.cache)
                subtracer.parent  = self
                subtracer.initial = S
                subtracer.select(S[0], follow_tracers, visited)
                selection.update(subtracer.state)
        return selection

    def selectables(self):
        return set(S[0] for S in self.state)

    def __repr__(self):
        return "_TokenTracer<%s, %s>"%(self.start, self.initial)


class TokenTracer(_TokenTracer):
    def __init__(self, langlet, start = None, kind = "parse", jump_to_state = None, without_expansion = True):
        expanded = {}
        if kind == "parse":
            nfas  = langlet.parse_nfa.nfas
            if without_expansion:
                expanded = langlet.parse_nfa.expanded
            if start is None:
                start = langlet.parse_nfa.start_symbols[0]
        else:
            nfas  = langlet.lex_nfa.nfas
            if without_expansion:
                expanded = langlet.lex_nfa.expanded
            if start is None:
                start = langlet.lex_nfa.start_symbols[0]
        try:
            super(TokenTracer, self).__init__(langlet, nfas, expanded, kind, {})
        except TypeError:
            print self
            raise
        self.select(start)
        if jump_to_state:
            self.jump_to(jump_to_state)

    def jump_to(self, jump_to_state):
        if isinstance(jump_to_state, list):
            self.state = jump_to_state
        else:
            self.state = [jump_to_state]
        self.tracers = {}
        for S in self.state:
            assert S in self.trans, "State '%s' is not a state of NFA '%s'"%(S, start)
            self.tracers[S] = [self]

    def check(self, tokstream):
        for i, tok in enumerate(tokstream):
            try:
                self.select(tok[0])
            except NonSelectableError:
                return (False, i)
        if FIN in self.selectables():
            return (True, i)
        else:
            return (False, i)

    def clone(self):
        return super(TokenTracer, self).clone({})

    def random_trace(self):
        tracers = [(self, [])]
        while True:
            tt, trace = tracers.pop()
            selectables = tt.selectables()
            print selectables, len(tracers)
            if FIN in selectables:
                return trace
            else:
                for s in selectables:
                    cloned = tt.clone()
                    cloned.select(s)
                    tracers.insert(0, (cloned, trace+[s]))


if __name__ == '__main__':
    import langscape
    ls_grammar = langscape.load_langlet("ls_grammar")
    stream = ls_grammar.tokenize("a:( b )\n")
    tracer = TokenTracer(ls_grammar)
    print tracer.check(stream)
    print [S for S in tracer.state if S[0] is FIN]

    python = langscape.load_langlet("python")
    stream = python.tokenize("def foo():\n print 42\ndef bar():\n print 47\n")

    tracer = TokenTracer(python, start = python.parse_symbol.funcdef)

    for tok in stream:
        try:
            selection = tracer.select(tok[0])
            print tok
        except NonSelectableError:
            pass



