import binascii

def expanded_transitions(nfadatagen, r):
    class N:n = 0
    nfa = nfadatagen.nfadata.nfas[r]
    transitions = nfa[2]
    exp_trans = {}
    visited = {}

    for L0, T in transitions.items():
        D_T = {}
        for L in T:
            S = D_T.get(L[0], set())
            S.add(L)
            D_T[L[0]] = S
        exp_trans[L0] = D_T

    def get_index(k,S):
        return (k,tuple(sorted([(L[1] if L[1]!='.' else L[2]) for L in S])))

    def new_label(n, k):
        return (k, n, '*')

    def produce(D_T):
        for k, S in D_T.items():
            if len(S) == 1:
                continue
            else:
                I = get_index(k,S)
                if I in visited:
                    continue
                else:
                    D_S = {}
                    N.n+=1
                    for L in S:
                        T_L = exp_trans[L]
                        for m, R in T_L.items():
                            M = D_S.get(m, set())
                            M.update(R)
                            D_S[m] = M
                    NL = new_label(N.n, k)
                    visited[I] = NL
                    exp_trans[NL] = D_S
                    produce(D_S)

    for D_T in exp_trans.values():
        produce(D_T)
    for D_T in exp_trans.values():
        for k, S in D_T.items():
            I = get_index(k,S)
            if I in visited:
                D_T[k] = visited[I]
            else:
                D_T[k] = S.pop()
    return exp_trans


def expand_transitions(nfadatagen):
    for r in nfadatagen.nfadata.nfas.keys():
        if r not in nfadatagen.nfadata.expansion_target:
            nfa = nfadatagen.nfadata.nfas[r]
            D_r = nfadatagen.expanded_transitions(r)
            nfa[2] = D_r

class Densify(object):
    def __init__(self, langlet, outpath = ""):
        self.langlet = langlet
        self.outpath = outpath

    def writeSource(self):
        name =  self.langlet.langlet_name.capitalize()+"ParseTable"
        if self.outpath:
            import os
            name = os.path.join(self.outpath, name)+".py"
        else:
            name = name+".py"
        open(name, "w").write(self.createSource())

    def createTable(self, dct, strings):
        res = {}
        for key, values in dct.items():
            res[key if type(key) == int else strings[key]] = [(v if type(v) == int else strings[v]) for v in values]
        return res

    def createRow(self, values, strings):
        return [(v if type(v) == int else strings[v]) for v in values]


    def createSource(self):
        import pprint
        states = {}
        state_list = []
        start = {}
        trans = {}
        for r, nfa in self.langlet.parse_nfa.nfas.items():
            transitions = nfa[2]
            for key, values in transitions.items():
                i = states.get(key, -1)
                if i==-1:
                    state_list.append(key)
                    states[key] = i = len(state_list)-1
                L = []
                for V in values:
                    j = states.get(V, -1)
                    if j == -1:
                        state_list.append(V)
                        states[V] = j = len(state_list)-1
                    L.append(j)
                trans[i] = L

        for i in range(len(state_list)):
            if i not in trans:
                trans[i] = []

        NAME = self.langlet.offset+1

        strings = {}
        swap_strings = {}

        for i, state in enumerate(state_list[:]):
            nid = state[0]
            idx = state[1]
            if type(nid) == int:
                if type(idx) == int:
                    S = (state[0], i, "", 0, state[2])
                else:
                    S = (state[0], i, state[1], 0, state[3])
                if idx == 0:
                    start[S[-1]] = S
            elif nid is None:
                S = (-1, i, "", 0,  state[2])
            else:
                cs = binascii.crc32(state[0])
                strings[cs] = state[0]
                swap_strings[state[0]] = cs
                if type(state[1]) == int:
                    S = (NAME, i, "", cs, state[2])
                    if idx == 0:
                        start[S[-1]] = S
                else:
                    S = (NAME, i, state[1], cs, state[3])
            state_list[i] = (S, trans[i])

        items = ["state_list = "+pprint.pformat(state_list, width = 10000)]
        items.append("start = "+pprint.pformat(start))
        items.append("keywords = "+pprint.pformat(strings))

        d = self.createTable(self.langlet.parse_nfa.reachables, swap_strings)
        items.append("reachables = "+pprint.pformat(d, width=10000))

        d = self.createRow(self.langlet.parse_nfa.terminals, swap_strings)
        items.append("terminals = "+pprint.pformat(d, width=10000))

        d = self.createTable(self.langlet.parse_nfa.ancestors, swap_strings)
        items.append("ancestors = "+pprint.pformat(d, width=500))

        d = self.createTable(self.langlet.parse_nfa.symbols_of, swap_strings)
        items.append("symbols_of = "+pprint.pformat(d, width=500))

        return "\n\n".join(items)

def nfa2dot(nfa, langlet):
    '''
    Create dot diagram
    '''
    start = nfa[1]
    transitions = nfa[2]
    nodes = []
    nodes.append('    nodeNone[label = "{None|-|%s}"];'%start[0])

    def Node(label):
        if len(label) == 3:
            if label[1] == '?':
                return '    node128[label = "{%s|{%s|%s|%s}}"];'%(node_name(label[0],langlet),label[0],label[1],label[2])
            else:
                return '    node%d[label = "{%s|{%s|%s|%s}}"];'%(label[1],node_name(label[0],langlet),label[0],label[1],label[2])
        else:
            return '    node%d[label = "{%s|{%s|.|%s|%s}}", color = green];'%(label[2], node_name(label[0],langlet),label[0],label[2],label[3])

    def Arrows(label):
        form   = "    node%s -> node%s;"
        idx = (label[2] if label[1] in ('.', '+') else label[1])
        arrows = []
        for f in transitions[label]:
            if f[0] is None:
                arrows.append(form%(idx,"None"))
            else:
                idx2 = (f[2] if f[1] in ('.', '+') else f[1])
                arrows.append(form%(idx,idx2))
        return "\n".join(arrows)

    arrows = []
    for label in transitions:
        nodes.append(Node(label))
        arrows.append(Arrows(label))
    graph = "digraph G {\n    node [shape = record,height=.1];\n"
    graph+="\n".join(nodes)+"\n"
    graph+="\n".join(arrows)
    graph+="\n}\n"
    return graph

def test_nfa2dot():
    import langscape.langlets.infinite_expansion.langlet as langlet
    langlet.init()
    print nfa2dot(langlet.parse_nfa.nfas[28930], langlet)


def test_densify():
    import pprint
    import langscape
    python = langscape.load_langlet("p4d")
    #gen_lextree(python)
    #JavaConverter(python).createSource()
    Densify(python).writeSource()


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

def test_recursive1():
    A = 'A'
    nfa = {(A, 0, A): [(A, '(', 0, A)],
    (A, '(', 0, A): [('<', 1, A), ('a', 4, A)],
    ('<', 1, A): [(A, '(', 0, A)],
    ('>', 3, A): [(A, ')', 0, A)],
    ('a', 4, A): [(A, ')', 0, A)],
    (A, ')', 0, A): [(FIN, FEX, 0, A), ('>', 3, A)]}

    interpreter = NFAInterpreter(nfa)
    print interpreter.run('<<a>>')

def test_recursive2():
    R = 'R'
    a, b, c = 'a', 'b', 'c'
    nfa = {(R, 0, R): [(R, '(', 0, R)],
     (R, '(', 0, R): [(a, 1, R)],
     (a, 1, R): [(b, 2, R)],
     (b, 2, R): [(R, '(', 0, R), (a, 4, R)],
     (a, 4, R): [(c, 5, R)],
     (c, 5, R): [(R, ')', 0, R)],
     (R, ')', 0, R): [(FIN, FEX, 0, R), (a, 4, R)]
    }
    interpreter = NFAInterpreter(nfa)
    assert interpreter.run('abac') == ['R', 'a', 'b', 'a', 'c']
    assert interpreter.run('ababacac') == ['R', 'a', 'b', ['R', 'a', 'b', 'a', 'c'], 'a', 'c']


def test_backmatch():
    S = 'S'
    R = 'R'
    a, b, c = 'a', 'b', 'c'

    nfa_R = {(R, 0, R): [(a, '=W', 0, R)],
             (a, '=W', 0, R): [(b, 1, R)],
             (b, 1, R): [(a, '$W', 3, R)],
             (a, '$W', 3, R):[(FIN, FEX, 0, R)]
    }

    nfa_S = {(S, 0, S): [(a, 0, S), (b, 0, S), (c, 0, S)],
             (a, 0, S): [(FIN, FEX, 0, S)],
             (b, 0, S): [(FIN, FEX, 0, S)],
             (c, 0, S): [(FIN, FEX, 0, S)]}


    interpreter = NFAInterpreter(nfa_R)
    assert interpreter.run('aba') == ['R', 'a', 'b', 'a']



if __name__ == '__main__':
    #test_recursive2()
    #test1()
    test_backmatch()

