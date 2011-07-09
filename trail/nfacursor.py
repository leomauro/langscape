from langscape.ls_const import*
import langscape.util

__all__ = ["TreeBuilder", "NFAStateSetSequence", "NFACursor", "SimpleNFACursor"]

class NFAState:
    def __init__(self, state, follow, tok = None):
        '''
        :param follow: A list [[S11, ..., S1n], [S21, ..., S2m],...] of state lists.

            Statelists containing more than one state have the form ::

                [(a1, i1, TRAIL_SKIP, b1), (b1, i2, TRAIL_SKIP, b2), ..., (bk, ik, 0, ck)]

            They are linked lists of states where all but the last one is transitional.
        '''
        self.state  = state
        self.follow = follow

class NFAStates:
    def __init__(self, nfastates):
        self.nfastates = nfastates
        self.token = None

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
            nid, IDX, ext, link  = state

            if ext == TRAIL_SKIP:
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
            elif ext == TRAIL_OPEN:
                tree.append(state)
                cycle.append(state)
            elif ext == TRAIL_CLOSE:
                if cycle:
                    rec = cycle.pop()
                    if (rec[0], rec[1], rec[3]) != (state[0], state[1], state[3]):
                        raise ValueError("Failed to derive tree."
                                         "Cannot build node [%s, ...]"%root)
                else:
                    raise ValueError("Failed to derive tree."
                                     "Cannot build node [%s, ...]"%root)
                for i in xrange(len(tree)-1, -1, -1):
                    t_i = tree[i]
                    if type(t_i) == tuple:
                        if t_i[1] == TRAIL_OPEN:
                            tree, T = tree[:i], tree[i+1:]
                            if tree:
                                T.insert(0, link)
                                tree.append(T)
                            else:
                                tree = T
                            break
                else:
                    raise ValueError("Failed to derive tree. Cannot build node [%s, ...]"%root)
            elif nid is FIN:
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
                raise ValueError("Final state `(FIN, ..)` missing in: %s"%states)
            else:
                raise ValueError("No trace available")


class NFAStateSetSequence:
    def __init__(self, start, builder):
        # print "DEBUG - start", start
        self.start  = start
        self.states = []
        self.new_states = {}
        self.builder = builder

    def reset(self):
        self.states = []
        self.new_states = {}

    def clone(self):
        '''
        A shallow copy is sufficient to fork a trace.
        '''
        mt = NFAStateSetSequence(self.start, self.builder)
        mt.states = self.states[:]
        mt.new_states = self.new_states.copy()
        return mt

    def set_token(self, tok):
        nfastates = self.states[-1]
        nfastates.token = tok

    def update(self, nfastates):
        self.new_states.update(nfastates)

    def commit(self):
        self.states.append(NFAStates(self.new_states))
        # reset and wait for new updates
        self.new_states = {}

    def compute_state_sequence(self):
        '''
        We iterate the list of state sets as follows ::

            Let N1 be an NFAState and ``S = N1.state``. Consider the set ``prev`` of predeecessors.
            If there is an ``N0`` in ``prev`` and an F in ``N0.follow`` with ``F[-1] == S`` we can
            link ``N0`` with ``N1`` by means of F.

        '''
        trace = []
        nfastates = self.states[0]
        nid = nfastates.nfastates.itervalues().next().state[0]
        S = (FIN, FEX, 0, nid)
        trace.append([S,[]])
        for prev in self.states[::-1]:
            try:
                P = prev.nfastates[S]
                if P:
                    if prev.token:     # re-link token from predecessor
                        trace[-1][1] = prev.token
                    if len(P.follow)>1:
                        trace.extend([[f,[]] for f in P.follow[1:]])
                    trace.append([P.state, []])
                    S = P.state
            except KeyError:
                raise IncompleteTraceError
        return trace[::-1]

    def derive_tree(self, sub_trees):
        '''
        Derives parse tree fragment from statelist and sub trees.
        '''
        states = self.compute_state_sequence()
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
    cache  = {}
    def __init__(self, nfa, mtrace):
        self.nfa = nfa
        self.mtrace = mtrace
        self.transitions = nfa[2]
        self.stateset   = set([mtrace.start])
        self.terminated = False

    def reset(self):
        self.mtrace.reset()
        self.stateset = set([self.nfa[1]])

    def clone(self):
        # Creates a clone of the NFACursor. Used for backtracking.
        mtrace = self.mtrace.clone()
        cursor = NFACursor(self.nfa, mtrace)
        cursor.stateset = set()
        cursor.stateset.update(self.stateset)
        return cursor

    def derive_tree(self, sub_trees):
        if len(self.mtrace.states) == 1:
            return sub_trees
        return self.mtrace.derive_tree(sub_trees)

    def set_token(self, tok):
        self.mtrace.set_token(tok)

    def move(self, nid):
        '''
        For a given set of states and nid the follow states corresponding to that nid
        is determined i.e. the joint follow sets of states with that nid.
        '''
        next_stateset = set()
        for state in self.stateset:
            if state[0] == nid:
                nfastates = self.cache.get(state, {})
                if not nfastates:
                    follow = self.follow_states(state)
                    for F in follow:
                        nfastates[F[0]] = NFAState(state, F)
                    self.cache[state] = nfastates
                self.mtrace.update(nfastates)
                next_stateset.update(nfastates.keys())
        self.mtrace.commit()
        self.stateset = next_stateset
        return set([s[0] for s in next_stateset])


    def follow_states(self, state):
        '''
        Computes a list F of follow states of a given state S.
        '''
        # this looks like we are doing too much because not all possible
        # transitions have to be considered. But since we have to examine
        # skipped states, it is not avoidable. On the bonus side: the
        # function is pure and its value can be cached.
        follow = []
        for S in self.transitions[state]:
            if S[2] in TRAIL_CONTROL:
                for F in self.follow_states(S):
                    follow.append(F+[S])
            else:
                follow.append([S])
        return follow


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
        self.mtrace = mtrace

    def reset(self):
        self.stateset = set([self.nfa[1]])

    def clone(self):
        cursor = SimpleNFACursor(self.nfa)
        cursor.stateset = set()
        cursor.stateset.update(self.stateset)
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




