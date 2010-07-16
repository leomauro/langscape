#from langscape.util import psyco_optimized
from langscape.trail.nfadef import*
import langscape.util

__all__ = ["TreeBuilder", "NFAStateSetSequence", "NFACursor", "SimpleNFACursor"]

class NFAState:
    def __init__(self, state, follow, tok = None):
        '''
        :param follow: A list [[S11, ..., S1n], [S21, ..., S2m],...] of state lists.

            Statelists containing more than one state have the form ::

                [(a1, '.', i1, b1), (b1, '.', i2, b2), ..., (bk, ik, ck)]

            They are linked lists of states where all but the last one is transitional.
        '''
        self.state  = state
        self.follow = follow
        self.token  = tok

    def __repr__(self):
        return "State(%s ; %s)"%(self.state, self.token)


class TreeBuilder(object):
    '''
    Creates tree from a list of states and sub_trees.
    '''
    def create(self, states, sub_trees):
        root   = states[0][0][0]
        tree   = []
        rule   = [root]
        cycle  = []

        for state, tok in states[1:]:
            nid  = state[0]
            link = state[-1]
            IDX  = state[1]

            if IDX == SKIP:
                rule.pop()
                for i in xrange(len(tree)-1, -1, -1):
                    if tree[i] == nid:
                        tree, T = tree[:i], tree[i:]
                        if link!=rule[-1]:
                            tree.append(link)  # int
                            rule.append(link)
                        tree.append(T)  # sublist-of_tree
                        break
                else:
                    raise ValueError("Failed to derive tree."
                                     "Cannot build node [%s, ...]"%root)
            elif IDX == '(':
                tree.append(state)
                cycle.append(state)
            elif IDX == ')':
                if cycle:
                    rec = cycle.pop()
                    if (rec[0], rec[2], rec[3]) != (state[0], state[2], state[3]):
                        raise ValueError("Failed to derive tree."
                                         "Cannot build node [%s, ...]"%root)
                else:
                    raise ValueError("Failed to derive tree."
                                     "Cannot build node [%s, ...]"%root)
                for i in xrange(len(tree)-1, -1, -1):
                    t_i = tree[i]
                    if type(t_i) == tuple:
                        if t_i[1] == '(':
                            tree, T = tree[:i], tree[i+1:]
                            if tree:
                                T.insert(0, link)
                                tree.append(T)
                            else:
                                tree = T
                            break
                else:
                    raise ValueError("Failed to derive tree. Cannot build node [%s, ...]"%root)
            elif nid is None:
                if cycle:
                    raise ValueError("Failed to derive tree. Cannot build node [%s, ...]"%root)
                if type(tree[0]) == int:
                    return tree
                else:
                    tree.insert(0, link)  # int
                    return tree
            else:
                if link!=rule[-1]:
                    tree.append(link)
                    rule.append(link)
                if tok:
                    tree.append(tok)      # token
                else:
                    sub = (sub_trees[0] if sub_trees else None)
                    if sub and (sub[0] == nid or sub[1] == nid):
                        sub_trees.pop(0)
                        tree.append(sub)
                    else:
                        raise ValueError("No sub-tree available")
        else:
            if len(states)>1:
                raise ValueError("Exit label `(None, ..)` missing in: %s"%states)
            else:
                raise ValueError("No trace available")


class NFAStateSetSequence:
    def __init__(self, start, builder):
        # print "DEBUG - start", start
        self.start  = start
        self.states = []
        self.new_states = []
        self.builder = builder

    def reset(self):
        self.states = []
        self.new_states = []

    def clone(self):
        '''
        A shallow copy is sufficient to fork a trace.
        '''
        mt = NFAStateSetSequence(self.start, self.builder)
        mt.states = self.states[:]
        mt.new_states = self.new_states[:]
        return mt

    def set_token(self, tok):
        for state in self.states[-1]:
            state.token = tok

    def update(self, state, follow):
        self.new_states.append(NFAState(state, follow))

    def commit(self):
        self.states.append(self.new_states)
        self.new_states = []

    def unwind(self, trace_stop=0):
        '''
        We iterate the list of state sets as follows ::

            Let N1 be an NFAState and ``S = N1.state``. Consider the set ``prev`` of predeecessors.
            If there is an ``N0`` in ``prev`` and an F in ``N0.follow`` with ``F[-1] == S`` we can
            link ``N0`` with ``N1`` by means of F.

        :param trace_stop: stops state set unwinding after ``trace_stop`` steps. If ``trace_stop`` is
                           0 no stop is applied.
        '''
        trace = []
        trace.append([(None, '-', self.states[0][0].state[0]),[]])
        S = trace[0][0]
        while self.states:
            prev = self.states.pop()
            for P in prev:
                for F in P.follow:
                    if S == F[-1]:
                        if P.token:                  # re-link token from predecessor
                            trace[-1][1] = P.token
                        if len(F)>1:
                            trace+=[[f,[]] for f in F[:-1][::-1]]
                        trace.append([P.state, []])
                        S = P.state
                        break
                else:
                    continue
                break
            else:
                raise IncompleteTraceError
            if trace_stop and len(trace)>=trace_stop:
                break
        return trace[::-1]

    def derive_tree(self, sub_trees):
        '''
        Derives parse tree fragment from statelist and sub trees.
        '''
        states = self.unwind()
        return self.builder.create(states, sub_trees)


class NFACursor:
    '''
    Class used by the lexer/parser to step through an NFA. A session that involves NFACursor
    objects works as follows ::

        NFACursor            NFAParser
           |    __init__(nfa)   |
           |   ------------>    |
           |    move(nid)       |
           |   <-----------     |
           |    selection       |
           |   ------------>    |
           |    move(nid)       |
           |   <-----------     |
           |    ...             |
           |                    |
           |    derive_tree()   |
           |   <-----------     |
           |    CST             |
           |   ----------->     |

    '''
    def __init__(self, nfa, mtrace):
        self.nfa = nfa
        self.cache  = {}
        self.mtrace = mtrace
        self.transitions = nfa[2]
        self.stateset   = set([mtrace.start])
        self.terminated = False

    def reset(self):
        self.mtrace.reset()
        self.stateset = set([self.nfa[1]])

    def clone(self):
        # Creates a clone of the NFACursor. Used for backtracking.
        cursor = NFACursor(self.nfa)
        cursor.stateset = set()
        cursor.stateset.update(self.stateset)
        cursor.mtrace = self.mtrace.clone()
        cursor.cache = self.cache
        return cursor

    def derive_tree(self, sub_trees):
        if len(self.mtrace.states) == 1:
            return sub_trees
        return self.mtrace.derive_tree(sub_trees)

    def set_token(self, tok):
        self.mtrace.set_token(tok)

    def move(self, nid):
        next_stateset = set()
        for state in self.stateset:
            if state[0] == nid:
                follow = self.cache.get(state)
                if follow is None:
                    follow = self.follow_states(state)
                    self.cache[state] = follow
                self.mtrace.update(state, follow)
                for F in follow:
                    next_stateset.add(F[-1])
        self.mtrace.commit()
        self.stateset = next_stateset
        return set([s[0] for s in next_stateset])

    @langscape.util.psyco_optimized
    def follow_states(self, state):
        follow = []
        for S in self.transitions[state]:
            if S[1] in CONTROL:
                for F in self.follow_states(S):
                    follow.append([S]+F)
            else:
                follow.append([S])
        return follow

    def remove_state(self, nid, link = 0):
        '''
        This method is used for state set "surgery".
        '''
        for S in list(self.stateset):
            if S[0] == nid:
                if link:
                    if S[-1] == link:
                        self.stateset.remove(S)
                else:
                    self.stateset.remove(S)


class SimpleNFACursor(NFACursor):
    '''
    Simplified version of NFACursor that doesn't hook into NFAStateSetSequence and won't derive trees.

    SimpleNFACursors are used for unexpanded rules and they are faster.
    '''
    def __init__(self, nfa, start = None, mtrace = None):
        self.nfa = nfa
        self.transitions = nfa[2]
        if start is None:
            start = nfa[1]
        self.stateset   = set([start])
        self.cache = {}
        self.mtrace = mtrace

    def reset(self):
        self.stateset = set([self.nfa[1]])

    def clone(self):
        cursor = SimpleNFACursor(self.nfa)
        cursor.stateset = set()
        cursor.stateset.update(self.stateset)
        cursor.cache = self.cache
        return cursor

    def move(self, nid):
        stateset = set()
        for state in self.stateset:
            if state[0] == nid:
                follow = self.cache.get(state)
                if follow is None:
                    follow = [S[-1] for S in self.follow_states(state)]
                    self.cache[state] = follow
                stateset.update(follow)
        self.stateset = stateset
        selection = set([s[0] for s in stateset])
        return selection




