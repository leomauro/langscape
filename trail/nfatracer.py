from langscape.trail.nfadef import*
import langscape.util

__all__ = ["NFATracer", "NFATracerDetailed", "NFATracerUnexpanded"]


class NFATracer(object):
    def __init__(self, nfas):
        self.nfas  = nfas
        self.nfa   = None
        self.state      = None   # can be shared by more than one node with same nid
        self.selectable = []

    def clone(self):
        rt = self.__class__(self.nfas)
        rt.selectable = self.selectable[:]
        rt.state = self.state[:]
        rt.nfa = self.nfa
        return rt

    def get_nid(self, state):
        return state[0][0]

    def initialize(self, nid):
        nfa = self.nfas[nid]
        self.nfa   = nfa[2]
        self.state = [nfa[1]]

    def select(self, nid, *other):
        try:
            if self.state is None:
                self.initialize(nid)
                return self._next()
            if nid is None:
                raise NonSelectableError(str(nid))
            self.state = [s for s in self.selectable if s[0] == nid]
            for n in other:
                self.state += [s for s in self.selectable if s[0] == n]
            if self.state:
                return self._next()
            raise NonSelectableError(nid)
        except KeyError:
            raise NonSelectableError(nid)

    move = select

    def _selection(self):
        return tuple(set(s[0] for s in self.selectable))

    def _get_next_state(self, state, visited):
        states = set()
        if len(state) == 1:
            if state[0][0] is None:
                states.add(state[0])
                return states
            trans = self.nfa[state[0]]
            for item in trans:
                if item[1] in CONTROL:
                    if item in visited:
                        continue
                    visited.add(item)
                    sub_states = self._get_next_state([item], visited)
                    states.update(sub_states)
                else:
                    states.add(item)
        else:
            for S in state:
                if S in visited:
                    continue
                visited.add(S)
                sub_states = self._get_next_state([S], visited)
                states.update(sub_states)
        return states

    def _next(self):
        visited = set()
        states = self._get_next_state(self.state, visited)
        self.selectable  = tuple(states)
        return self._selection()


class NFATracerDetailed(NFATracer):
    def get_nid(self, state):
        return state[0]

    def _selection(self):
        return self.selectable


class NFATracerUnexpanded(NFATracer):
    def __init__(self, nfa_mod):
        self.nfa_mod    = nfa_mod
        self.state      = None   # can be shared by more than one node with same nid
        self.selectable = []
        self.nfa = None

    def clone(self):
        rt = self.__class__(self.nfa_mod)
        rt.selectable = self.selectable[:]
        rt.state = self.state[:]
        rt.nfa = self.nfa
        return rt


    def initialize(self, nid):
        if nid in self.nfa_mod.expanded:
            self.nfa   = self.nfa_mod.expanded[nid][2]
            self.state = [self.nfa_mod.expanded[nid][1]]
        else:
            self.nfa   = self.nfa_mod.nfas[nid][2]
            self.state = [self.nfa_mod.nfas[nid][1]]


class _TokenTracer(NFATracer):
    def __init__(self, langlet, nfas, expanded, kind):
        self.langlet  = langlet
        self.expanded = expanded
        self.nfas     = nfas
        self.state    = []   # can be shared by more than one node with same nid
        self.initial  = None
        self.tracers  = {}
        self.trans    = {}
        self.parent   = None
        self.start    = None
        self.kind     = kind


    def clone(self, cloned):
        # TODO: needs testing
        cl = cloned.get(self)
        if cl:
            return cl
        rt = _TokenTracer(self.langlet, self.nfas, self.expanded, self.kind)
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
        for s, tracers in self.tracers.items():
            ct = []
            for T in tracers:
                ct.append((cloned.get(T) if cloned.get(T) else T.clone(cloned)))
            rt.tracers[s] = ct
        return rt


    def select(self, nid, follow_tracers = None):
        if follow_tracers is None:
            follow_tracers = {}
        selection = set()
        if self.tracers:
            tracers = [(state, self.tracers.get(state)) for state in self.state if state[0] == nid]
            if tracers == []:
                raise NonSelectableError(nid)
            for state, tracer in tracers:
                for T in tracer:
                    selection.update(T._next_selection(state, follow_tracers))
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
            return self.select(nid, follow_tracers)


    def _next_selection(self, state, follow_tracers):
        follow = self.trans[state]
        selection = set()
        for S in follow:
            if S[0] is None:
                if self.parent is None:
                    selection.add(S)
                if self.initial:
                    selection.update(self.parent._next_selection(self.initial, follow_tracers))
            elif is_token(S[0]):
                selection.add(S)
                T = follow_tracers.get(S)
                if T:
                    T.append(self)   # first/first - conflict
                else:
                    follow_tracers[S] = [self]
            else:
                subtracer = _TokenTracer(self.langlet, self.nfas, self.expanded, self.kind)
                subtracer.parent  = self
                subtracer.initial = S
                subtracer.select(S[0], follow_tracers)
                selection.update(subtracer.state)
        return selection

    def selectables(self):
        return set(S[0] for S in self.state)

    def __repr__(self):
        return "_TokenTracer<%s, %s>"%(self.start, self.initial)

class TokenTracer(_TokenTracer):
    def __init__(self, langlet, start = None, kind = "parse"):
        if kind == "parse":
            nfas  = langlet.parse_nfa.nfas
            expanded = langlet.parse_nfa.expanded
            if start is None:
                start = langlet.parse_nfa.start_symbols[0]
        else:
            nfas  = langlet.lex_nfa.nfas
            expanded = langlet.lex_nfa.expanded
            if start is None:
                start = langlet.lex_nfa.start_symbols[0]
        try:
            super(TokenTracer, self).__init__(langlet, nfas, expanded, kind)
        except TypeError:
            print self
            raise
        self.select(start)

    def check(self, tokstream):
        for i, tok in enumerate(tokstream):
            try:
                self.select(tok[0])
            except NonSelectableError:
                return (False, i)
        if None in self.selectables():
            return (True, i)
        else:
            return (False, i)


    def clone(self):
        return super(TokenTracer, self).clone({})



if __name__ == '__main__':
    import langscape
    ls_grammar = langscape.load_langlet("ls_grammar")
    stream = ls_grammar.tokenize("a:( b )\n")
    tracer = TokenTracer(ls_grammar)
    print tracer.check(stream)
    print [S for S in tracer.state if S[0] is None]

    python = langscape.load_langlet("python")
    stream = python.tokenize("def foo():\n print 42\ndef bar():\n print 47\n")

    tracer = TokenTracer(python, start = python.parse_symbol.funcdef)

    for tok in stream:
        try:
            selection = tracer.select(tok[0])
            print tok
        except NonSelectableError:
            pass



