import pprint
import warnings
import copy
import sys

import langscape
import langscape.util
import langscape.trail.nfatools as nfatools
from langscape.csttools.cstutil import is_token, is_keyword
from langscape.trail.nfatracer import NFATracerDetailed

from langscape.trail.nfadef import*

__all__ = ["NFAExpansionParser", "NFAExpansionLexer"]

START_SHIFTER = MAX_ALLOWED_STATES

class LeftRecursionWarning(Warning):
    def __init__(self,*args, **kwd):
        super(LeftRecursionWarning, self).__init__(*args, **kwd)
        self.rules = []

class NeedsMoreExpansionWarning(Warning): pass
class RightExpansionWarning(Warning): pass
class DriftingExpansionWarning(Warning): pass

warnings.simplefilter("always",LeftRecursionWarning)
warnings.simplefilter("always",NeedsMoreExpansionWarning)
warnings.simplefilter("always",RightExpansionWarning)

@langscape.util.psyco_optimized
def combinations(l):
    if l == ():
        return ((),)
    else:
        return [(x,)+y for x in l[0] for y in combinations(l[1:]) if (y and x<y[0] or y==())]

def lower_triangle(lst):
    '''
    Converts list of integers ( or ordered values of another type ) into a list of pairs belonging
    to a lower triangle matrix.

    Example:

        >>> L = [1, 2, 3]
        >>> lower_triangle(L)
        [(1,2),(1,3),(2,3)]

    There is no sorting involved so when you keep a rotated list the result will differ:

        >>> L = [2, 1, 3]
        >>> lower_triangle(L)
        [(2,3),(1,2),(1,3)]

    Doubles will not be erased:

        >>> L = [3, 1, 3]
        >>> lower_triangle(L)
        [(1,3),(1,3)]

    '''
    _lst = list(lst)
    L = (_lst,_lst)
    return combinations(L)

class AbstractExpansionStatusReport(object):
    def __init__(self, type = "Parser"):
        pass

    def print_rule(self, status, name, nid, states):
        pass

    def print_header(self):
        pass

    def print_trailer(self):
        pass



class ExpansionStatusReport(AbstractExpansionStatusReport):
    '''
    Class used to format NFA expansion messages in a tabular way.
    '''
    def __init__(self, type = "Parser"):
        self.type = type
        self.ok_cnt  = 0
        self.fail_cnt  = 0

    def print_rule(self, status, name, nid, states):
        if status == "OK":
            self.ok_cnt+=1
        else:
            self.fail_cnt+=1
        print "%-8s| %-40s| %-10s| %-14s|"%(status, name, nid, states)
        print "--------+-----------------------------------------+-----------+---------------+"

    def print_header(self):
        print
        print "======================."
        print "%s Expansion"%self.type,
        print " "*5 if len(self.type) == 5 else " "*4,
        print "|"
        print "======================+=======================================================."
        print "Status  | Expanded rule                           | Node Id   | Nbr of states |"
        print "========+=========================================+===========+===============+"

    def print_trailer(self):
        if self.ok_cnt == 1:
            print "1 NFA expanded"
        else:
            print "%s NFAs expanded"%self.ok_cnt
        if self.fail_cnt>0:
            if self.fail_cnt == 1:
                print "1 NFA expansion failed -> NFA%s uses backtracking"%self.type
            else:
                print "%s NFA expansions failed -> NFA%s uses backtracking"%(self.fail_cnt, self.type)
        print


#################################################################################################
#
#
#  NFAExpansion
#
#
#################################################################################################

class NFAExpansion(object):
    # TODO: maxdepth needs improved reasoning. What are the error cases and how can they be
    #       detected early?
    '''
    Base class for Lexer / Parser specific expansions.
    '''
    def __init__(self, langlet, nfadata):
        self.nfadata = nfadata
        self.max_depth = max(self.nfadata.depths.values())
        self.warn_cnt = 0
        self.size = 0
        self.offset_factor = 2  # used
        self.report = ExpansionStatusReport(self.get_type())

    def expand(self, rule = 0, visited = set()):
        raise NotImplementedError

    def get_type(self):
        raise NotImplementedError

    def node_name(self, item):
        raise NotImplementedError

    def _get_next_state(self, transitions, state, stack):
        if len(stack)>10*self.max_depth:
            raise RuntimeError
        stack.append(state[0])
        next_states = []
        states = transitions[state]
        for S in states:
            if S[1] in CONTROL:
                follow = self._get_next_state(transitions, S, stack)
                next_states+=follow
            else:
                next_states.append(S)
        return next_states

    def _all_selections(self, r):
        '''
        This method creates all possible state sets for a given NFA. Form those sets all selections
        can be derived easily by projection i.e. set(s[0] for s in states).
        '''
        selections = []
        transitions_redux = {}
        transitions = self.nfadata.nfas[r][2]
        for state in transitions:
            if state[1] in CONTROL:
                continue
            follow = self._get_next_state(transitions, state, [])
            transitions_redux[state] = follow
            selections.append(follow)

        # So far we have only determined the follow sets of individual states S that are keys of NFA transitions.
        # But suppose a state set contains a subset {S1, S2, ..., Sk} with
        # a = nid(S1) = nid(S2) = ... = nid(Sk). A parser would apply a selection tracer.select(a) and this
        # yields a unification of the follow sets of all the Si. Those need to be computed and it has to be
        # taken care that each of those sets is computed only once.

        index_set = set()
        stack = selections[:]
        while stack:
            selection = stack.pop()
            S = set(s[0] for s in selection if s[0]!=None)
            for s in S:
                multiple = [L for L in selection if L[0] == s]
                if len(multiple)>1:
                    multiindex = tuple(sorted([L[1] for L in multiple]))
                    if multiindex in index_set:
                        continue
                    else:
                        index_set.add(multiindex)
                    new_selections = set()
                    for L in multiple:
                        new_selections.update(transitions_redux[L])
                    new_selections = list(new_selections)
                    selections.append(new_selections)
                    stack.append(new_selections)
        return selections

    def _cyclefree_traces(self):
        cfree_traces = {}
        spanned = nfatools.span_traces(self.nfadata.nfas, self.nfadata.nonterminals)
        for r, (sym, lst) in spanned.items():
            cfree_traces[r] = lst
        return cfree_traces

    def _compute_follow_sets(self, start):
        follow = []
        for T in self._all_selections(start[0]):
            K = [state for state in T if state[0] is not None]
            if len(K)>1:
                follow.append(K)
        return follow


    #@langscape.util.psyco_optimized
    def expand_all(self):
        '''
        Expand each rule that requires expansion.
        '''
        self.size    = sum(len(nfa[2]) for nfa in self.nfadata.nfas.values())
        self.shifter = MAX_ALLOWED_STATES
        visited = set()
        self.report.print_header()
        rule_data = {}
        expanded = set()
        for r in self.nfadata.nfas:
            if r not in visited:
                try:
                    self.expand(r, visited)
                except (LeftRecursionWarning, OverflowError), e:
                    self.report.print_rule("Failed", self.node_name(r), r, 0)
                    exp = self.nfadata.expansion_target.get(r)
                    if exp:
                        self.nfadata.nfas[r] = exp
                        del self.nfadata.expansion_target[r]
                    continue
                for s in set(self.nfadata.expansion_target)-expanded:
                    n = len(self.nfadata.nfas[s][2])
                    expanded.add(s)
                    self.report.print_rule("OK", self.node_name(s), s, n)
        self.report.print_trailer()


    def maybe_expand(self, r, visited):
        if r and r not in visited and not is_token(r):
            self.expand(r, visited)

    def embedd_nfa(self, state, target_rule):
        '''
        Let S -> {L1, L2, ..., Ln} be a transition and L1 be a state. We want to replace L1 by an
        NFA with nid(NFA) == L1[0].

        We have to care for following conditions to be satisfied ::

            1) The target NFA has to be `shifted` which means that all indizes have to be re-enumerated.
               This is because an NFA can be embedded at several different locations in the target NFA.
               There must not be an overlap.

            2) If the target NFA has not been expanded yet, a copy of the original NFA will be stored.

            3) If L1 = (A, index, S) we create L1` = (A, '.', index, S). Furthermore let First_A be defined
               by First_A = NFA_A[Start_A].

               i)   On each occurence of L1 on the RHS of the NFA_Z we replace L1 by First_A.
               ii)  We replace L1 as a key of NFA_Z by L1`.
               iii) The terminal (None, '-', A) of NFA_A will be replaced by L1`. This way we can link
                    the endpoint of NFA_A with with NFA_Z via L1`.
        '''
        # TODO: the shift-index computation is still crap. Sometimes consistency checks fails and manipulation
        #       of shift-index seems to work.

        #print "embedd_nfa(self, state: %s, at: %s)"%(state, target_rule)
        nid_A     = state[0]
        shifted_A = state[1]
        Z = self.nfadata.nfas[target_rule]
        A = self.nfadata.nfas[nid_A]
        if nid_A == target_rule:
            raise LeftRecursionWarning
        elif nid_A == state[-1] and shifted_A>START_SHIFTER:
            raise LeftRecursionWarning

        # store reminder
        if not target_rule in self.nfadata.expansion_target:
            self.nfadata.expansion_target[target_rule] = copy.deepcopy(Z)

        # shifted NFA will be embedded in top level NFA
        # ...
        start_A, trans_A = self._shift_nfa_index(A)
        trans_Z    = Z[2]
        follow_A = trans_A[start_A]

        # this will replace the exit symbol (None, '-', nid_A) in the shifted NFA.
        transit  = (state[0], SKIP, self.shifter, state[-1])
        if state[0] == state[-1]:
            R_NAME = A[1].split(":")[0]
            raise RuntimeError("no expansion of `%s` possible in `%s`!"%(R_NAME, Z[1]))

        #self.shifter+=1

        trans_Z[transit] = trans_Z[state][:]
        del trans_Z[state]
        del trans_A[start_A]

        for follow in trans_Z.values():
            if state in follow:
                follow.remove(state)
                follow.extend(follow_A)

        for follow in trans_A.values():
            for L in follow:
                if L[0] is None:
                    follow.remove(L)
                    if transit not in follow:
                        follow.append(transit)

        trans_Z.update(trans_A)
        self._check_consistency(trans_Z, state, target_rule)

    def _check_consistency(self, trans_Z, state, target_rule):
        # used to check consistency of embedding
        follow_set = set()
        for key, follow in trans_Z.items():
            follow_set.update(follow)
            for f in follow:
                if f[0]!=None:
                    trans = trans_Z.get(f)
                    if not trans:
                        raise RuntimeError, "Failed embedding: embedd_nfa(self, state: %s, at: %s)"%(state, target_rule)
        for key in trans_Z:
            if key[1] == 0:
                continue
            if key not in follow_set:
                pprint.pprint(trans_Z)
                raise RuntimeError, "Failed embedding: embedd_nfa(self, state: %s, at: %s). Unreachable: %s"%(state, target_rule, key)

    def _shift_nfa_index(self, nfa):
        '''
        @param nfa: single nfa to be shifted
        @return: (start-state, shifted transitions)

        Description ::
            When embedding transitions of an NFA A into transitions of another NFA Z one
            has to take care for not-overwriting transitions of a previous embedding of A into Z.
            This is done by adding a value V to each index IDX of a state L:

                 (nid, IDX, link) -> (nid, IDX+V, link)
        '''
        shift  = self.shifter
        start  = nfa[1]
        trans  = nfa[2]
        states = trans.keys()
        state_map = {}
        states.sort(key = lambda state: ( state[1] if state[1] not in CONTROL else state[2]))
        for state in states:
            if state[1] in CONTROL:
                state_map[state] = (state[0], state[1], shift, state[3])
            else:
                state_map[state] = (state[0], shift, state[2])
            shift+=1
        self.shifter += START_SHIFTER

        new_trans = {}
        for key, follow in trans.items():
            new_follow = []
            for state in follow:
                new_follow.append(state_map.get(state, state))
            new_trans[state_map[key]] = new_follow
        return state_map[start], new_trans

    def check_expanded(self, nfamodule, rule = None, print_warning = False):

        def check(r, state, tracer, visited):
            must_trace = False
            states    = tracer.select(state[0])
            selection = list(set(s[0] for s in states if s and s[0]!=None))
            R = set()
            C = {}
            msg = ""
            for i,s in enumerate(selection):
                if is_token(s):
                    S = set([s])
                else:
                    S = nfamodule.reachables[s]
                if R&S:
                    for u in C:
                        if C[u]&S:
                            if is_token(s):
                                msg = "%s : %s -> FirstSet(%s) /\\ {%s} = %s\n"%(r, state, u, s, C[u]&S)
                            elif is_token(u):
                                msg = "%s : %s -> {%s} /\\ FirstSet(%s) = %s\n"%(r, state, u, s, C[u]&S)
                            else:
                                msg = "%s : %s -> FirstSet(%s) /\\ FirstSet(%s) = %s\n"%(r, state, u, s, C[u]&S)
                            lineno = sys._getframe(0).f_lineno +1
                            if print_warning:
                                warnings.warn_explicit(msg, NeedsMoreExpansionWarning, "nfadatagen.py", lineno)
                            backtracking.add(r)
                    break
                else:
                    R.update(S)
                    C[s] = S

            for state in states:
                if state[0] is not None and state not in visited:
                    visited.add(state)
                    subtracer = tracer.clone()
                    check(r, state, subtracer, visited)

        backtracking = set()
        if rule is None:
            rules = self.nfadata.nfas.keys()
        else:
            rules = [rule]
        for r in rules:
            nfa = self.nfadata.nfas[r]
            visited = set()
            tracer = NFATracerDetailed(nfamodule.nfas)
            start = nfa[1]
            check(r, start, tracer, visited)
        return backtracking


    def check_rightexpand(self):
        '''
        Dumps an unconditional RightExpansionWarning when warning case is detected.

        Description ::
            This method checks for `horizontal ambiguities`. By this we mean ambiguities that occur
            in grammars like

               G: A* B
               B: A

            If 'AA' is given one can derive G -> A B or G -> A A.
        '''
        last_sets  = self.nfadata.compute_last_set()
        fin_cycles = self.nfadata.compute_fin_cycles()

        warned = set()

        def format_stream(T, k):
            stream = []
            for t in [t for t in T[:k+2]]:
                if isinstance(t, int):
                    stream.append(self.node_name(t))
                else:
                    stream.append("'"+t+"'")
            return stream[0]+': '+' '.join(stream[1:])

        for r, traces in self._cyclefree_traces().items():
            for T in traces:
                for i in range(1,len(T)-1):
                    A = T[i]
                    B = T[i+1]
                    if (r,A,B) in warned or A == B:
                        continue
                    if is_token(B):
                        if B in last_sets.get(A, set()):
                            if B in fin_cycles[A]:
                                warn_text = "%s -> LastSet(%s) /\\ set([%s]) != {}"%(self.node_name(r),self.node_name(A),self.node_name(B)) #, format_stream(T,i))

                                warnings.warn_explicit(warn_text, RightExpansionWarning, "nfadatagen.py", sys._getframe(0).f_lineno-1)
                                warned.add((r,A,B))
                                break
                    else:
                        S = last_sets.get(A, set()) & self.nfadata.reachables.get(B, set())
                        if S:
                            C = S & fin_cycles[A]
                            if C:
                                warn_text = warn_text = "%s -> LastSet(%s) /\\ FirstSet(%s) != {}"%(self.node_name(r), self.node_name(A),self.node_name(B)) #,format_stream(T,i))

                                warnings.warn_explicit(warn_text, RightExpansionWarning, "nfadatagen.py", sys._getframe(0).f_lineno-1)
                                warned.add((r,A,B))
                                print "                  /\\", set([self.node_name(c) for c in C])
                                break


#################################################################################################
#
#
#  NFAExpansionParser
#
#
#################################################################################################

class NFAExpansionParser(NFAExpansion):
    def __init__(self, langlet, nfadata):
        super(NFAExpansionParser, self).__init__(langlet, nfadata)
        self.start_symbol = nfadata.start_symbols[0]
        self.offset    = langlet.langlet_id
        self.sym_name  = langlet.parse_symbol.sym_name
        self.tok_name  = langlet.parse_token.tok_name

    def get_type(self):
        return "Parser"

    def node_name(self, item):
        if type(item) == str:
            return item
        return self.sym_name.get(item,"")+self.tok_name.get(item,"")

    def expand(self, rule = 0, visited = set()):
        '''
        Let K be the reduced NFA[r]. For each transition ::

            S -> {L1, ..., Ln}

        with at least two follow states L1, L2 and Li!=None we determine
        the corresponding selection ::

            sel = {s1, ..., sk}

        From sel we build Ri = s1.reach \/ s2.reach \/ .... si.reach successively.

        If Ri intersects with s(i+1) find the first sj, j=1,...,i with ::

                sj.reach /\ s(i+1).reach

        Now embedd the smaller of both NFAs into K.

        Repeat this procedure for each transition T until Rn-1 /\ sn.reach = {}.
        '''
        if not rule:
            rule = self.start_symbol

        visited.add(rule)
        more = True
        must_select = False
        while more:
            more = False
            selections = self._all_selections(rule)

            if len(selections)>MAX_ALLOWED_STATES:
                raise OverflowError("NFA size > MAX_ALLOWED_STATES. Cannot expand rule `%s : %s`"%(rule, self.node_name(rule)))
            if self.warn_cnt>10:
                raise OverflowError("More than ten expansion warnings issued. Expansion is terminated!")

            for follow in selections:
                selectable = sorted(list(set(s[0] for s in follow if s and s[0]!=None)))
                if len(selectable)<=1:
                    continue
                R = set()
                C = {}
                for i,s in enumerate(selectable):
                    tok_s = False
                    if is_token(s):
                        tok_s = True
                        S = set([s])
                    else:
                        S = self.nfadata.reachables[s]
                    if R&S:
                        for u in selectable[:i]:
                            tok_u,U = C[u]
                            if U&S:
                                if tok_s:
                                    k = u
                                elif tok_u:
                                    k = s
                                else:
                                    N_s = self.nfadata.nfas[s][2]
                                    N_u = self.nfadata.nfas[u][2]
                                    k = (s if len(N_s)<=len(N_u) else u)
                                break
                        for state in (state for state in follow if state[0] == k):
                            self.maybe_expand(state[0], visited)
                            self.embedd_nfa(state, rule)
                            more = True
                            break
                        break
                    else:
                        R.update(S)
                        C[s] = (tok_s, S)
                else:
                    continue
                break
            else:
                break


#################################################################################################
#
#
#  NFAExpansionLexer
#
#
#################################################################################################

class LexerTerminalSet(dict):
    max_tid = 0
    def __init__(self, dct={}):
        dict.__init__(self, dct)

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        LexerTerminalSet.max_tid = max(LexerTerminalSet.max_tid, key)

    def __repr__(self):
        d = {}
        for tid, pt in self.items():
            d[tid] = pt.charset
        return pprint.pformat(d)


class LexerTerminal(object):
    def __init__(self, tid, charset, name = ""):
        if tid == -1:
            LexerTerminalSet.max_tid +=1
            self.tid = LexerTerminalSet.max_tid
        else:
            self.tid = tid
        self.name    = name
        self.charset = charset  # a set-like object

    def __repr__(self):
        return "<PT: %s , %-16s, %s>"%(self.tid, self.name, self.charset)


class NFAExpansionLexer(NFAExpansion):
    def __init__(self, langlet, nfadata):
        super(NFAExpansionLexer, self).__init__(langlet, nfadata)
        self.start_symbol = langlet.lex_symbol.token_input
        self.sym_name  = langlet.lex_symbol.sym_name
        self.tok_name  = langlet.lex_token.tok_name
        self.token_map = langlet.lex_token.token_map
        self.charset   = langlet.lex_token.charset
        self.lexer_terminal = LexerTerminalSet()
        self.offset = langlet.langlet_id
        self.kwd_index = max(self.nfadata.keywords.values())+1
        self.initial_lexer_terminal()

    def get_type(self):
        return "Lexer"

    def node_name(self, item):
        return self.sym_name.get(item,"")

    def is_token(self, s):
        return ( s in self.nfadata.terminals or \
                 s in self.lexer_terminal)

    def initial_lexer_terminal(self):
        for name, val in self.charset.__dict__.items():
            tid = self.token_map[name]
            self.lexer_terminal[tid] = LexerTerminal(tid, val, name)
        for c, val in self.nfadata.keywords.items():
            self.lexer_terminal[val] = LexerTerminal(val, set([c]), c)


    def expand_all(self):
        super(NFAExpansionLexer, self).expand_all()
        self.nfadata.lexer_terminal = self.lexer_terminal
        LexerTerminalSet.max_tid = 0

    def expand(self, rule = 0, visited = set()):
        if not rule:
            rule = self.start_symbol
        start = self.nfadata.nfas[rule][1]
        nfa = self.nfadata.nfas[rule][2]
        self.expand_nt(rule, start, nfa, visited)
        self.expand_charset(rule, start, nfa)
        if self.check_expanded(self.nfadata, rule):
            self.expand_nt(rule, start, nfa, visited)
            self.expand_charset(rule, start, nfa)

    def replace_keywords(self, nids):
        for i, n in enumerate(nids):
            if type(n)!=int:
                k = self.nfadata.keywords.get(n)
                if k is None:
                    k = self.kwd_index
                    self.nfadata.keywords[n] = self.kwd_index
                    self.kwd_index+=1
                nids[i] = k
        return nids


    def expand_charset(self, rule, start, nfa):
        more = True
        while more:
            more = False
            kicked = []
            selections = self._all_selections(start[0])
            for trans in selections:
                follow = [f for f in trans if f[0]!=None and f not in kicked]
                if len(follow)<2:
                    continue
                lexer_terminal = self.split(follow)
                for state, sets in lexer_terminal.items():
                    # LS_state has been split into several sets, we check if the set is already a Charset of another
                    # LexerTerminal. If this is not the case we create a new LexerTerminal from this set.
                    nids = []
                    for S in sets:
                        if len(S) == 1:
                            nids.append(list(S)[0])
                            continue
                        for P in self.lexer_terminal.values():
                            if P.charset == S:
                                nids.append(P.tid)
                                break
                        else:
                            pt = LexerTerminal(-1, S)
                            self.lexer_terminal[pt.tid] = pt
                            nids.append(pt.tid)
                            # print "NEW pt", pt

                    # State substitution.
                    #
                    # Let S be a state with charset(S) = charset(S1) \/ ... \/ charset(Sk) and {S,S1, ..., Sk} < follow.
                    # The set {S1,...,Sk} is computed using the split() method. We create new states S1', ..., Sk'
                    # with nid(Si') = nid(Si) and replace S:
                    #
                    #   1) if S occurs on the RHS of a transition replace it by {S1', ..., Sk'}
                    #   2) insert Si' as a key with the transitions of S as a value
                    #
                    follow = nfa[state]
                    del nfa[state]
                    kicked.append(state)
                    new_states = []
                    nids = self.replace_keywords(nids)
                    for n in nids:
                        i = 0
                        new_state = (n, state[1]+i, state[-1])
                        while nfa.get(new_state):
                            i+=1
                            new_state = (n, state[1]+i, state[-1])
                        nfa[new_state] = follow
                        new_states.append(new_state)
                    for trans in nfa.values():
                        if state in trans:
                            trans.remove(state)
                            trans+=new_states
                    more = True

    def split(self, states):
        # If for two lexer token A, B the corresponding charsets intersect i.e.
        # K = A.charset /\ B.charset != {} we split those sets into A.charset-K, K, B.charset-K.
        # An important special case is K = A.charset or K = B.charset
        #   Suppose K = B.charset, then we have lexer_terminal[A] = [A.charset - B.charset, B.charset].
        #   For A.charset - B.charset we eventually need a new LexerTerminal.
        pt_list, np_list = [],[]
        ok = False
        for state in states:
            if state[0] in self.lexer_terminal:
                pt_list.append(state)
            else:
                np_list.append(state)
        res = []
        lexer_terminal = {}
        for i,A in enumerate(pt_list):
            CS_A = self.lexer_terminal[A[0]].charset
            for B in pt_list[1+i:]:
                if A[0]!=B[0]:
                    CS_B = self.lexer_terminal[B[0]].charset
                    K = CS_A & CS_B
                    if K:
                        if K!=CS_A:
                            pt = lexer_terminal.get(A,[])
                            pt.append(K)
                            lexer_terminal[A] = pt
                        if K!=CS_B:
                            pt = lexer_terminal.get(B,[])
                            pt.append(K)
                            lexer_terminal[B] = pt
            for t in np_list:
                if t[0] in CS_A:
                    pt = lexer_terminal.get(A,[])
                    pt.append(set([t[0]]))
                    lexer_terminal[A] = pt
        if lexer_terminal:
            # print lexer_terminal
            i = 1
            for A, sets in lexer_terminal.items():
                R = [self.lexer_terminal[A[0]].charset]
                for S in sets:
                    K = []
                    for T in R:
                        for r in T & S, T-S, S-T:
                            if r and r not in K:
                                K.append(r)
                    R = K
                lexer_terminal[A] = R
        return lexer_terminal


    def has_intersection(self, R_A, R_B):
        for t in R_A:
            if t in self.lexer_terminal:
                CS_t = self.lexer_terminal[t].charset
                for u in R_B:
                    if u in self.lexer_terminal:
                        CS_u = self.lexer_terminal[u].charset
                        if CS_t & CS_u:
                            return True
                    else:
                        if u in CS_t:
                            return True
        return False

    def try_expansion(self, nids, follow, rule, visited, embedded):
        for state in (state for state in follow if state[0] in nids):
            self.maybe_expand(state[0], visited)
            if not (state, rule) in embedded:
                self.embedd_nfa(state, rule)
            embedded.add((state, rule))
        return True

    def expand_nt(self, rule, start, nfa, visited):
        visited.add(rule)
        expanded = set()
        embedded = set()
        while True:
            more = False
            #pprint.pprint(nfa)
            follow_sets = self._compute_follow_sets(start)
            #if __DEBUG__:
            #    print "DEBUG - follow_sets", follow_sets
            for follow in follow_sets:
                follow = list(follow)
                selectable = [s[0] for s in follow if s]
                pairs = lower_triangle( selectable )
                for A,B in pairs:
                    rc = 0
                    if (A,B) in expanded:
                        continue
                    elif A in self.nfadata.terminals and not A in self.lexer_terminal:
                        #elif is_token(A) and not A in self.lexer_terminal:
                        if self.is_token(B):
                            pass
                        elif A in self.nfadata.reachables[B]:
                            rc = self.try_expansion([B], follow, rule, visited, embedded)
                    elif self.is_token(B) and not B in self.lexer_terminal:
                        if A in self.lexer_terminal:
                            continue   # special case of two intersecting PT entities
                                       # is handled in expand_charset method
                        elif B in self.nfadata.reachables[A]:
                            rc = self.try_expansion([A], follow, rule, visited, embedded)
                    elif A in self.lexer_terminal:
                        if B in self.lexer_terminal:
                            continue
                        R_B = self.nfadata.reachables[B]
                        if self.has_intersection([A],R_B):
                            rc = self.try_expansion([B], follow, rule, visited, embedded)
                    elif B in self.lexer_terminal:
                        R_A = self.nfadata.reachables[A]
                        if self.has_intersection([B],R_A):
                            rc = self.try_expansion([A], follow, rule, visited, embedded)
                    elif self.nfadata.reachables[A] & self.nfadata.reachables[B]:
                        rc = self.try_expansion([A,B], follow, rule, visited, embedded)
                    else:
                        R_A = self.nfadata.reachables[A]
                        R_B = self.nfadata.reachables[B]
                        if self.has_intersection(R_A, R_B) or self.has_intersection(R_B, R_A):
                            rc = self.try_expansion([A,B], follow, rule, visited, embedded)
                    if rc:
                        expanded.add((A,B))
                        more = True
            if not more:
                #pprint.pprint(nfa)
                break


if __name__ == '__main__':
    import langscape
    langscape.load_langlet("Breeed")
