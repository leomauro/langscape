from langscape.ls_const import*

__all__ = ["NFATracer", "NFATracerDetailed", "NFATracerUnexpanded"]


class NFATracer(object):
    def __init__(self, nfas):
        self.nfas  = nfas
        self.nfa   = None
        self.trans = None
        self.state = None   # can be shared by more than one node with same nid
        self.selectable = []

    def clone(self):
        rt = self.__class__(self.nfas)
        rt.selectable = self.selectable[:]
        rt.state = self.state[:]
        rt.nfa   = self.nfa
        rt.trans = self.trans
        return rt

    def get_nid(self, state):
        return state[0][0]

    def initialize(self, nid):
        self.nfa   = self.nfas[nid]
        self.trans = self.nfa[2]
        self.state = [self.nfa[1]]

    def select(self, nid, *other):
        try:
            if self.state is None:
                self.initialize(nid)
                return self._next()
            if nid is FIN:
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
            if state[0][0] is FIN:
                states.add(state[0])
                return states
            follow = self.trans[state[0]]
            for item in follow:
                if item[1] in TRAIL_CONTROL:
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
        self.nfa_mod    = nfa_mod  # langlet.lex_nfa or langlet.parse_nfa module
        self.state      = None     # can be shared by more than one node with same nid
        self.selectable = []
        self.nfa = None
        self.trans = None

    def clone(self):
        rt = self.__class__(self.nfa_mod)
        rt.selectable = self.selectable[:]
        rt.state = self.state[:]
        rt.nfa = self.nfa
        rt.trans = self.trans
        return rt


    def initialize(self, nid):
        if nid in self.nfa_mod.expanded:
            self.nfa = self.nfa_mod.expanded[nid]
        else:
            self.nfa = self.nfa_mod.nfas[nid]
        self.trans = self.nfa[2]
        self.state = [self.nfa[1]]


