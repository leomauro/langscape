##
##  This module contains mostly experimental stuff. Instead of cleaning it up
##  some of the functions might be extracted into own modules
##

import langscape
from langscape.trail.nfadef import*
from langscape.trail.nfatracer import*
from langscape.util import flatten_list
import pprint
import copy

class NFAInterpreter(object):
    '''
    Small interpreter for NFAs. Used to checkout new ideas.
    '''
    def __init__(self, nfa):
        for state in nfa:
            if state[1] == 0:
                self.start = state
                break
        else:
            raise ValueError("Incorrect NFA - start state not found")
        self.nfa = ["", self.start, nfa]

    def run(self, tokstream):
        from nfacursor import TreeBuilder, NFAStateSetSequence, NFACursor
        mtrace = NFAStateSetSequence(self.nfa[1], TreeBuilder())
        cursor = NFACursor(self.nfa, mtrace)
        selection = cursor.move(self.start[0])
        for t in tokstream:
            cursor.set_token(t)
            cursor.move(t)
        return cursor.derive_tree([])


def pprint_nfa(nfa, langlet):
    this_nfa = copy.deepcopy(nfa)
    trans = this_nfa[2]
    for label, follow in trans.items():
        del trans[label]
        if type(label[0]) == str:
            new_label = label[:-1]+(langlet.get_node_name(label[-1]),)
        elif len(label) == 4:
            new_label = (langlet.get_node_name(label[0]),
                         label[1],
                         label[2],
                         langlet.get_node_name(label[3]))
        else:
            new_label = (langlet.get_node_name(label[0]),
                         label[1],
                         langlet.get_node_name(label[2]))
        new_F = []
        for label in follow:
            if type(label[0]) == str or label[0] is None:
                new_L = label[:-1]+(langlet.get_node_name(label[-1]),)
            elif len(label) == 4:
                new_L = (langlet.get_node_name(label[0]),
                         label[1],
                         label[2],
                         langlet.get_node_name(label[3]))
            else:
                new_L = (langlet.get_node_name(label[0]),
                         label[1],
                         langlet.get_node_name(label[2]))
            new_F.append(new_L)
        trans[new_label] = new_F
    pprint.pprint(this_nfa)


def compute_follow_states(transitions, state):
    follow = []
    states = transitions[state]
    for s in states:
        if s[1] in CONTROL:
            follow+=compute_follow_states(transitions, s)
        else:
            follow.append(s)
    return follow

def compute_pre_states(transitions, state):
    # Other than 'compute_follow_states' only transitory states will be
    # returned
    pre = []
    for S, F in transitions.items():
        if state in F:
            pre.append(S)
    return pre


# TODO: let N be a sub-NFA of M. We call N 'branched' if there are states S0,S1,S2 in N and S1, S2 <- Follow(S0)
#       with S1 ~ S2. In that case we call S0 a branch point.
#       We are interested in all un-ramified sub NFAs of M. We call them also 'branch-free'.
#
#       Algorithm: if S is a state and S a predecessor of a branch point P it is also a point in a non
#       branch-free sub-NFA. So we try to find out all branch points {BP1, ..., BPk} first and then determine
#       all of their predecessors ( and recursively their predecessors down to the start ).

def compute_branch_points(nfa):
    branch_points = set()
    trans = nfa[2]
    for S in trans:
        if S[1] not in CONTROL and S[0]!=None:
            follow = compute_follow_states(trans, S)
            nids = {}
            for F in follow:
                if nids.get(F[0]):
                    branch_points.add(S)
                    break
                else:
                    nids[F[0]] = True
    stack = list(branch_points)
    branch_points = set()
    while stack:
        S = stack.pop()
        branch_points.add(S)
        for P in compute_pre_states(trans, S):
            if P not in branch_points:
                stack.append(P)
    return branch_points

def compute_reachable_depths(reachables):
    depths = {}
    visited = set()

    def compute_depth(r):
        S = reachables[r]
        K = 0
        visited.add(r)
        for s in S:
            if s in depths:
                K = max(K, 1+depths[s])
            elif is_token(s):
                K = max(K,1)
            elif s in visited:
                raise NodeCycleError, "Cyclic references in grammar found at node %s. Trail can't build parse tables."%s
            else:
                compute_depth(s)
                K = max(K, 1+depths[s])
        depths[r] = K

    for r in reachables:
        compute_depth(r)
    return depths


def compute_subnfa(nfa, state):
    trans     = nfa[2]
    sub_trans = {state: trans[state]}
    sub_nfa   = ['', state, sub_trans]
    visited   = set()
    follow    = set(trans[state])
    while follow:
        S = follow.pop()
        if S[0] is None:
            continue
        F = trans[S]
        sub_trans[S] = F
        for f in F:
            if f not in sub_trans:
                follow.add(f)
    return sub_nfa


def compute_fibration(nfa):
    '''
    Let Pre(EXIT) the set of predecessors of the EXIT symbol (None, '-', nid)
    for some NFA. For each p in Pre(EXIT) we compute a sub NFA p(NFA)
    '''
    start   = nfa[1]
    trans   = nfa[2]
    traces  = {}
    visited = set()

    def compute_next(state, trans, traces, visited):
        visited.add(state)
        S_trace = []
        for F in trans[state]:
            if F[0] is None:
                S_trace.append([state, F])
            elif F in traces:
                for T in traces[F]:
                    S_trace.append([state]+T)
            elif F not in visited:
                compute_next(F, trans, traces, visited)
                for T in traces[F]:
                    S_trace.append([state]+T)
            else:  # cycle - do nothing
                continue
        traces[state] = S_trace

    compute_next(start, trans, traces, visited)
    return traces[start]

def span_traces(nfas, nonterminals):

    def exhaust(nt):
        rtd = NFATracerDetailed(nfas)
        visited = set()
        symbols = set()

        def get_selections(rt, state):
            tree = [state]
            selection = rt.select(state)
            for s in selection:
                if s in visited or s[0] is None:
                    continue
                visited.add(s)
                symbols.add(s[0])
                cloned = rt.clone()
                tree.append(get_selections(cloned, s[0]))
            return tree

        tree = get_selections(rtd, nt)
        return tree, symbols

    spanned = {}
    for nt in list(nonterminals):
        tree, symbols = exhaust(nt)
        flt = flatten_list(tree)
        if not isinstance(flt[0], list):
            flt = [flt]
        spanned[nt] = (symbols, flt)
    return spanned


def compute_constants(nfas, lexer_token, keywords):
    constants = {}
    for r in nfas:
        tracer = NFATracer(nfas)
        s = r
        l = []
        while True:
            selection = tracer.select(s)
            if len(selection)>1:
                break
            if None in selection:
                constants[r] = ''.join(l)
                break
            else:
                s = selection[0]
                if is_token(s):
                    if is_keyword(s):
                        l.append(keywords[s])
                    else:
                        z = lexer_token.default.get(s, None)
                        if z is not None:
                            l.append(z)
                        else:
                            break
                else:
                    break
    return constants


def test_fibration():
    import langscape.langlets.python.parsedef.parse_nfa as parse_nfa
    for nfa in parse_nfa.nfas.values():
        pprint.pprint(compute_fibration(nfa))

def test_subnfa():
    python = langscape.load_langlet("python")
    for nfa in python.parse_nfa.nfas.values():
        trans = list(nfa[2])
        state = trans[len(trans)/2]
        pprint_nfa(compute_subnfa(nfa, state), python)
        break

def test_branchpoints():
    python = langscape.load_langlet("python")
    nfa = python.lex_nfa.nfas[1003]
    pprint_nfa(nfa, python)
    print len(nfa[2])
    return compute_branch_points(nfa)

if __name__ == '__main__':
    test_subnfa()
    test_branchpoints()
    test_fibration()
