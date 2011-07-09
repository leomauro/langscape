__all__ = ["SourceGenerator"]

import pprint
import langscape
from langscape.csttools.cstsegments import SegmentTree, proj_segment
from langscape.csttools.cstutil import*
from langscape.trail.nfa2grammar import futures
from langscape.trail.tokentracer import TokenTracer
from langscape.trail.nfatools import compute_tr_with_target, compute_state_traces, compute_all_tr
from langscape.sourcetools.tokgen import TokenGenerator

def compute_with_target_gen(target, nfa):
    _, start, trans = nfa
    trace = compute_tr_with_target(start, target, nfa)
    for S in trace[1:]:
        yield S
    while True:
        trace = compute_tr_with_target(target, target, nfa)
        for S in trace[1:]:
            yield S

def compute_in_cycle(nfa):
    _, start, trans = nfa
    in_cycle = []
    for idx, S in futures(start, trans).items():
        if idx in S:
            for state in trans:
                if state[1] == idx:
                    in_cycle.append(state)
                    break
    return in_cycle


def compute_minimal_state_traces(nfa):
    _, start, trans = nfa
    states = set()
    traces = []
    for S in trans:
        if S == start:
            continue
        T1 = compute_tr_with_target(start, S, nfa)
        if (FIN, '-', start[0]) in trans[S]:
            traces.append(T1[1:])
        else:
            T2 = compute_tr_with_target(S, (FIN, FEX, 0, start[0]), nfa)
            T = T1[1:]+T2[1:-1]
            traces.append(T)
    return traces

def rule_ids(langlet, nid, rules = None):
    if rules is None:
        rules = set([nid])
    else:
        rules.add(nid)
    for s in langlet.parse_nfa.reachables[nid]:
        if is_symbol(s):
            if s not in rules:
                rule_ids(langlet, s, rules)
    for s in langlet.parse_nfa.symbols_of[nid]:
        if is_symbol(s):
            if s not in rules:
                rule_ids(langlet, s, rules)
    return rules

def _compute_flat_tr(nid, state_traces, flat_traces, visited):
    if nid in flat_traces:
        return
    trace = []
    visited.add(nid)
    # find optimal trace
    K  = 10000
    tr = []
    for T in state_traces[nid]:
        if K == 0:
            break
        k = 0
        for S in T:
            if is_symbol(S[0]):
                if S[0] not in flat_traces:
                    k+=1
                if S[0] == nid:  # avoid cycles
                    k+=10
        if k == 0:
            tr = T
            break
        elif k<K:
            K = k
            tr = T
    for S in tr:
        s = S[0]
        if is_symbol(s):
            if s in flat_traces:
                trace+=flat_traces[s]
            elif s not in visited:
                rt = _compute_flat_tr(s, state_traces, flat_traces, visited)
                if rt:
                    trace+=rt
                else:
                    if len(state_traces[nid]) == 1:
                        raise RuntimeError("Cannot construct flat trace for '%s'"%s)
                    else:
                        # repeat with another trace
                        ST = state_traces.copy()
                        ST[nid] = ST[nid][:]
                        ST[nid].remove(tr)
                        visited.remove(nid)
                        visited.remove(s)
                        return _compute_flat_tr(nid, ST, flat_traces, visited)
            else:
                return
        else:
            trace.append(s)
    flat_traces[nid] = trace
    return trace


def compute_flat_tr(langlet, unused_symbols):
    state_traces = {}
    flat_traces  = {}
    for s, nfa in langlet.parse_nfa.nfas.items():
        if s not in unused_symbols:
            state_traces[s] = sorted(compute_minimal_state_traces(nfa),
                              key = lambda item: (len(item) if len(item)>1 else -1/(item[0][0]+1.0)))
    visited = set()
    for s in state_traces:
        _compute_flat_tr(s, state_traces, flat_traces, set())
    assert len(state_traces) == len(flat_traces)
    return flat_traces


class SourceGenerator(object):
    Varnames = "abcdestuxyz"
    def __init__(self, langlet, start_symbol = None):
        self.langlet = langlet
        self.start_symbol = start_symbol
        self.state_traces = {}
        self.unused_symbols = set()
        self.compute_unused_symbols()
        self.segtree = SegmentTree(langlet)
        self.segtree.create()
        self.token_traces = {}
        self.expr_types   = set([self.start_symbol])
        self.compute_expr_types()
        self.tokgen = TokenGenerator(langlet, stdlen = 1)
        self._cnt   = 1
        self._id    = 0
        self._expressions = []


    def compute_expr_types(self):
        symbols = [s for s in self.langlet.parse_nfa.symbols_of[self.start_symbol] if is_symbol(s)]
        symbols.insert(0, self.start_symbol)
        for s in self.langlet.parse_nfa.nfas:
            if s not in self.unused_symbols:
                for sym in symbols:
                    seg = self.segtree[sym: s]
                    if seg:
                        self.expr_types.add(s)

    def compute_unused_symbols(self):
        if self.start_symbol is None:
            self.start_symbol   = self.langlet.parse_nfa.start_symbols[0]
            self.unused_symbols = self.langlet.parse_nfa.start_symbols[1]
            self.unused_symbols.remove(self.start_symbol)
        else:
            rules = rule_ids(self.langlet, self.start_symbol)
            self.unused_symbols = set()
            for r in self.langlet.parse_nfa.nfas:
                if r not in rules:
                    self.unused_symbols.add(r)

    def expressions(self):
        if self._expressions:
            return self._expressions
        self._compute_all_state_traces()
        self._insert_non_expr_state_traces()
        self._compute_all_token_traces()
        self._remove_duplicates()
        for s in self.expr_types:
            name = self.langlet.get_node_name(s)
            for tr in self.token_traces[s]:
                self._expressions.append((s, name, self.langlet.untokenize(tr)))
        return self._expressions

    def _remove_duplicates(self):
        S = set()
        for s in self.expr_types:
            traces = self.token_traces[s]
            new_traces = []
            for i, trace in enumerate(traces[:]):
                tup = tuple(s[0] for s in trace)
                if tup not in S:
                    new_traces.append(trace)
                    S.add(tup)
            self.token_traces[s] = new_traces

    def _compute_all_state_traces(self):
        for s, nfa in self.langlet.parse_nfa.nfas.items():
            if s is self.start_symbol or s not in self.unused_symbols:
                traces = compute_all_tr(1, nfa)
                for tr in traces:
                    del tr[-1]
                self.state_traces[s] = traces


    def _compute_all_token_traces(self):
        Tr   = []
        rest = []
        for s, traces in self.state_traces.items():
            for trace in traces:
                Tr.append((s, trace))
        n = 0
        while True:
            if Tr:
                s, trace = Tr.pop()
            else:
                if len(rest) == n:
                    break
                else:
                    n  = len(rest)
                    Tr = rest[::-1]
                    rest = []
            visited = set([s])
            tokentrace = self._compute_token_trace(trace, visited)
            if tokentrace:
                tt = self.token_traces.get(s,[])
                tt.append(tokentrace)
                self.token_traces[s] = tt
            else:
                rest.append((s, trace))


    def _insert_non_expr_state_traces(self):
        non_expr_types = set()
        for s in self.state_traces:
            if s not in self.expr_types:
                non_expr_types.add(s)

        def insert(s, nids):
            for e in nids:
                if e == s:
                    continue
                for tr in self.state_traces[e][:]:
                    for i, state in enumerate(tr):
                        if state[0] == s:
                            for T in self.state_traces[s]:
                                self.state_traces[e].append(tr[:i]+T+tr[i+1:])
                            return e

        inserted = set()
        for s in non_expr_types:
            e = s
            while True:
                if not insert(e, self.expr_types):
                    f = insert(e, non_expr_types)
                    if f and f in inserted:
                        # repeat insertion
                        e = f
                    else:
                        break
                else:
                    inserted.add(e)
                    break


    def _compute_token_trace(self, state_trace, visited):
        tokstream = []
        for state in state_trace:
            nid = state[0]
            if is_keyword(nid):
                tokstream.append([nid, self.langlet.get_node_name(nid)[4:]])
            elif is_token(nid):
                if nid == self.langlet.token.NAME:
                    name = self.Varnames[self._id%len(self.Varnames)]
                    tokstream.append([nid, name])
                    self._id+=1
                else:
                    tokstream.append([nid, self.tokgen.gen_token_string(nid+SYMBOL_OFFSET)])
            else:
                seg = self.segtree[nid:self.langlet.token.NAME]
                if seg:
                    S, P = proj_segment(seg)
                    for t in P:
                        if t == self.langlet.token.NAME:
                            tokstream.append([t, self.langlet.get_node_name(S if S!=0 else nid)])
                        elif is_keyword(t):
                            tokstream.append([t, self.langlet.get_node_name(t)[4:]])
                        else:
                            tokstream.append([t, self.tokgen.gen_token_string(t+SYMBOL_OFFSET)])
                else:
                    nt_traces = self.token_traces.get(nid, [])
                    if nt_traces:
                        idx = self._cnt % len(nt_traces)
                        self._cnt+=1
                        tokstream+=nt_traces[idx]
                    else:
                        if nid in visited:
                            return
                        else:
                            visited.add(nid)
                            for i, st in enumerate(self.state_traces[nid][:]):
                                tr = self._compute_token_trace(st, visited)
                                if tr:
                                    tokstream+=tr
                                    del self.state_traces[nid][i]
                                    tt = self.token_traces.get(nid,[])
                                    tt.append(tr)
                                    self.token_traces[nid] = tt
                                    break
                                else:
                                    return
                            visited.remove(nid)
        return tokstream




def _compute_embedd_tr(langlet, tr, r, nid, segtree, start_symbols):
    nfas = langlet.parse_nfa.nfas
    for X in nfas:
        if X in start_symbols:
            continue
        if r in langlet.parse_nfa.symbols_of[X]:
            (start_X, _, _) = nfa_X = nfas[X]
            for _tr_X in compute_state_traces(nfa_X):
                for i, S in enumerate(_tr_X):
                    if S[0] == r:
                        tr_X = _tr_X[:i]+tr+_tr_X[i+1:]
            segment = segtree[nid: X]
            if segment:
                sg = proj_segment(segment)[:]
                for j, item in enumerate(sg):
                    if not is_symbol(item):
                        sg[j] = (item, 1, nid)
                i = sg.index(X)
                return sg[:i]+tr_X+sg[i+1:]
            else:
                trace = _compute_embedd_tr(langlet, tr_X, X, nid, segtree, start_symbols)
                return trace
    return []


def _compute_next_tr(langlet, state, state_traces, segtree, start_symbols):
    nid = state[0]
    for r in state_traces:
        if r not in start_symbols:
            tr = state_traces[r].pop()
            if state_traces[r] == []:
                del state_traces[r]
            return _compute_embedd_tr(langlet, tr, r, nid, segtree, start_symbols)


def compute_super_tr(langlet,
                     start_state,
                     state_traces,
                     segtree,
                     running_cycle,
                     start_symbols = None):
    nid = start_state[0]
    nfa = langlet.parse_nfa.nfas[nid]
    cyclic = compute_in_cycle(nfa)
    trace  = []
    if not start_symbols:
        start_symbols = langlet.parse_nfa.start_symbols[1]
    for S in cyclic:
        if is_symbol(S[0]):
            cycle_gen = compute_with_target_gen(S, nfa)
            while True:
                state = cycle_gen.next()
                if is_symbol(state[0]):
                    tr = _compute_next_tr(langlet, state, state_traces, segtree, start_symbols)
                    if tr:
                        trace+=tr
                    else:
                        trace.append(state)
                        if state == S:
                            # compute tail
                            trace+=compute_tr_with_target(S, (FIN, FEX, 0, nid), nfa)[1:-1]
                            break
                else:
                    trace.append(state)
    return trace


def compute_langlet_expr(langlet, start_symbol = None):
    running_cycle = set()
    state_traces = {}
    for s, nfa in langlet.parse_nfa.nfas.items():
        if s is start_symbol or s not in start_symbols:
            state_traces[s] = compute_state_traces(nfa)
    _, start, _ = langlet.parse_nfa.nfas[start_symbol]

    segtree = SegmentTree(langlet)
    segtree.create()
    supertrace = compute_super_tr(langlet, start, state_traces, segtree, running_cycle, start_symbols)
    flat_traces = compute_flat_tr(langlet)
    langlet_trace  = []
    for t in supertrace:
        if is_symbol(t[0]):
            langlet_trace.extend(flat_traces[t[0]])
        else:
            langlet_trace.append(t[0])
    # for item in langlet_trace:
    #    print item, langlet.get_node_name(item)
    tgen = TokenGenerator(langlet, stdlen = 1)
    tokstream = []
    letters = "abcdefg"
    i = 0
    for tid in langlet_trace:
        if tid == langlet.token.NAME:
            tokstream.append([tid, letters[i%len(letters)]])
            i+=1
        elif is_keyword(tid):
            tokstream.append([tid, langlet.get_node_name(tid)[4:]])
        else:
            tokstream.append([tid, tgen.gen_token_string(tid+SYMBOL_OFFSET)])
    return langlet.unparse([1000]+tokstream)



if __name__ == '__main__':
    python = langscape.load_langlet("python")

    sg = SourceGenerator(python)
    for expr in sg.expressions():
        pass #print expr






