'''
TODO: In order to improve Maybe treatment we consider the following two cases

o -> x -> [y]
 \        /
  '------'

1) x in diagram1 and x2 in diagram2 don't have any branching points.

Seq(Maybe(x), y)


        y1---y2
       /      \
o -> x1       x2 ->[z]
 \     \      /    /
  \     y3---y4   /
   \             /
    '-----------'


2) if x,y,z are branching points of o and z in future(x) and z in future(y). We have following cases:

    1) y in future(x):

        Seq(Maybe([X]-[Y]),Maybe([Y]-[Z]),[Z])

    2) Seq(Maybe(Alt([X]-[Z], [Y]-[Z])), [Z])

       Here X-Z and Y-Z are the x and y branches of o delimited by z but not containing z.

In any case it has to be ensured that there is exactly one predecessor of Y in future(X). So let Pred(Y)
the set of predecessors of Y, then len(future(X) & Pred(Y)) == 1.

'''

import pprint
import langscape
from langscape.csttools.cstutil import*
from langscape.trail.nfamaps import nfa_comp, create_nfa_skeleton
from langscape.langlets.ls_grammar.grammar_object import GrammarObject

__DEBUG__ = False

def check(trans):
    for S in trans:
        follow = trans[S]
        if not follow:
            pprint.pprint(trans)
            raise ValueError("Follow set of %s is empty"%(S,))
        for F in follow:
            if F[0] is not FIN:
                try:
                    trans[F]
                except KeyError:
                    pprint.pprint(trans)
                    raise
    for S in trans:
        if S[1] == 0:
            continue
        for F in trans:
            if S in trans[F]:
                break
        else:
            pprint.pprint(trans)
            raise ValueError("%s cannot be found on the RHS"%(S,))

def check_consistency(f):
    def call(self, trans, *args):
        D = {}
        for s, v in trans.items():
            D[s] = v[:]
        r = f(self, trans, *args)
        try:
            check(trans)
        except KeyError:
            print "-"*40
            pprint.pprint(D)
            raise
        return r
    call.__name__ = f.__name__
    return call


def get_follow(n, S, trans):
    if n == 0:
        return set()
    elif n == 1:
        return set(trans[S])
    else:
        C = get_follow(n-1, S, trans)
        R = set()
        for s in C:
            if s[0]!=FIN:
                R = R.union(get_follow(1, s, trans))
        return R

def get_follow_closure(S, trans, visited = None):
    if visited is None:
        visited = set()
    visited.add(S)
    follow = trans[S]
    R = set(follow)
    for f in follow:
        if f[0] is not FIN and f not in visited:
            R.update(get_follow_closure(f, trans, visited))
    return R

def get_follow_closure_set(S, trans):
    R = set()
    for s in S:
        if s[0]!=FIN:
            R.update(get_follow_closure(s, trans, set()))
    return R


def follow_from_set(state_set, trans):
    R = set()
    for s in state_set:
        if s[0] is not FIN:
            R.update(trans[s])
    return R

def find_node_from(S, N, trace, trans, visited):
    if not trace:
        trace = [S]
    F = trace[-1]
    for f in trans[F]:
        if f == N:
            trace.append(f)
            return trace
        elif f[0] is FIN:
            continue
        elif f in visited:
            continue
        else:
            visited.add(f)
            T = find_node_from(S, N, trace+[f], trans, visited)
            if T:
                return T
    return []

def predecessors(state, trans):
    P = set()
    for F in trans:
        if state in trans[F]:
            P.add(F[1])
    return P

def completion(state, future):
    return future[state] | set([state])

def find_partition(future):
    '''
    We are looking for a partition i.e. future[0] must be split into two or more sets with a disjoint
    future
    '''
    follow = future[0]
    partition = {}
    for f in follow:
        partition[f] = future[f].union(set([f]))
        if len(partition[f]) == len(follow):
            return [] # no partition found
    # eliminate entry f in domain when f is subdomain of g
    for f in follow:
        fi = partition[f]
        for g in partition:
            if g!=f:
                if fi.issubset(partition[g]):
                    del partition[f]
                    break
    m = len(follow)
    R = {}
    Idx = set()
    P = partition.values()
    n = len(P)
    for i in range(n):
        pi = P[i]
        if i in Idx:
            continue
        R[i] = pi
        for j in range(i+1, n):
            qj = P[j]
            if R[i] & qj:
                R[i] = R[i].union(qj)
                Idx.add(j)
                break
    return R.values()


def futures(start, trans):
    F = {}

    def _future(state, visited):
        visited.add(state)
        R = set()
        for f in trans[state]:
            if f in F:
                R = R.union(F[f])
            elif f[0] is not FIN and f not in visited:
                R = R.union(_future(f, visited))
            R.add(f)
        F[state] = R
        return R
    for s in trans:
        _future(s, set())
    D = {}
    for s, follow in F.items():
        D[s[1]] = set([f[1] for f in follow  if f[1]!='-'])
    return D

def new_state(start, n):
    state = (start[0]+1000+2*n, 2*n+1, start[0])
    return state

def node_by_index(trans, idx):
    for S in trans:
        if S[1] == idx:
            return S

def create_span(state, nfa, future, memo):
    _, start, trans = nfa
    D = {}
    future_F = future[state[1]]
    for S in trans:
        if S[1] in future_F:
            D[S] = trans[S]
    D[start] = [state]
    D[state] = trans[state]
    return TreeRule(["", start, D], memo)


############  SimpleReduction   ##########################

class SimpleReduction(object):
    def __init__(self, nfa):
        _, start, trans = nfa
        self.fin = (FIN, "-", start[-1])

    def _find_maybe(self, start, trans, visited):
        visited.add(start)
        follow_1 = set(trans[start])
        follow_2 = get_follow(2, start, trans)
        C = follow_1 & follow_2
        if C:
            if __DEBUG__:
                print "C", C
            return (S,C)
        for F in follow_1:
            if F[0] is not FIN and F not in visited:
                R = self._find_maybe(F, trans, visited)
                if R:
                    return R

    def maybe_reduction(self, nfa, memo):
        _, start, trans = nfa
        res = self._find_maybe(start, nfa, set())
        if res:
            S, follow = res
            X = new_state(start, len(memo))
            memo[X] = "?"
            trans_S = trans[S]
            trans_S.append(X)
            for f in follow:
                trans_S.remove(f)
            trans[X] = list(follow)
            return True
        return False

    def _find_seq(self, start, trans, visited):
        visited.add(start)
        L = []
        follow = trans[start]
        if len(follow) == 1:
            F = follow[0]
            if F[0] is FIN:
                if len(L)>=2:
                    return L
            else:
                if len(L) == 0 and start[1]!=0:
                    L.append(S)
                for T in trans:
                    if T!=start and F in trans[T]:
                        break
                else:
                    L.append(F)
                    if F not in visited:
                        R = self._find_seq(F, trans, visited, L)
                        if len(R)>=2:
                            return R
                    if len(L)>=2:
                        return L
        elif len(L)>=2:
            return L
        for F in follow:
            if F[0] is not FIN and F not in visited:
                R = self.find_simple_seq(F, trans, visited, [])
                if len(R)>=2:
                    return R
        return []


    def seq_reduction(self, nfa, memo):
        _, start, trans = nfa
        L = self._find_seq(start, trans, set())
        if L:
            X = new_state(start, len(memo))
            memo[X] = Seq(L[0], L[1:], memo)
            Last = L[-1]
            First = L[0]
            follow = trans[Last]
            for m in L:
                del trans[m]
            trans[X] = follow
            for S in trans:
                F = trans[S]
                if First in F:
                    F.remove(First)
                    F.append(X)
            return True
        return False


    def _find_alt(self, start, trans, visited):
        _, start, trans = nfa
        visited.add(start)
        follow = trans[start]
        if len(follow)>1:
            if self.fin in follow:
                return

    def alt_reduction(self, nfa, memo):
        pass


    def terminate(nfa):
        _, start, trans = nfa
        if len(trans) <= 2:
            for v in trans.values():
                if len(v)>1:
                    return False
            return True
        return False

    def reduction(self, nfa, memo):
        while True:
            if self.maybe_reduction(nfa, memo):
                if self.terminate(nfa):
                    return True
            elif self.seq_reduction(nfa, memo):
                if self.terminate(nfa):
                    return True
            elif self.alt_reduction(nfa, memo):
                if self.terminate(nfa):
                    return True
            else:
                return False




############  maybe, alt, seq, cyc  ##########################

class RuleObj: pass

class Maybe(RuleObj):
    def __init__(self, rule):
        self.rule = rule

    def __eq__(self, other):
        if isinstance(other, Maybe):
            return self.rule == other.rule
        return False

    def __repr__(self):
        return "["+str(self.rule)+"]"

class ReqCycle(RuleObj):
    def __init__(self, rule):
        self.rule = rule

    def __eq__(self, other):
        if isinstance(other, ReqCycle):
            return self.rule == other.rule
        return False

    def __repr__(self):
        return "("+str(self.rule)+")+"

class OptCycle(RuleObj):
    def __init__(self, rule):
        self.rule = rule

    def __eq__(self, other):
        if isinstance(other, OptCycle):
            return self.rule == other.rule
        return False

    def __repr__(self):
        return "("+str(self.rule)+")*"

class Seq(RuleObj):
    def __init__(self, item, rule, memo):
        self.lst = []
        if isinstance(item, RuleObj):
            if isinstance(item, Seq):
                self.lst+=item.lst
            else:
                self.lst.append(item)
        else:
            self.lst.append(memo[item])
        if isinstance(rule, Seq):
            self.lst+=rule.lst
        elif isinstance(rule, list):
            self.lst+=rule
        else:
            self.lst.append(rule)
        self.memo = memo

    def __eq__(self, other):
        if isinstance(other, Seq):
            return self.lst == other.lst
        return False


    def __repr__(self):
        return (" ".join(str(item) for item in self.lst)).strip()

class Alt(RuleObj):
    def __init__(self, rules, memo):
        self.rules = rules

    def __eq__(self, other):
        if isinstance(other, Alt):
            return self.rules == other.rules
        return False

    def __repr__(self):
        return "("+ " | ".join(str(rule) for rule in self.rules)+")"

class End(RuleObj):
    def __eq__(self, other):
        if isinstance(other, ReqCycle):
            return True
        return False

    def __repr__(self):
        return ""

class TreeRule(object):
    def __init__(self, nfa, memo):
        self.nfa   = nfa
        self.memo  = memo
        self.start = nfa[1]
        self.trans = nfa[2]
        self.fin   = (FIN, "-", self.start[-1])

    def run(self):
        follow = self.trans[self.start]
        if self.fin in follow:
            if len(follow) == 1:
                return End()
            follow.remove(self.fin)
            rule = TreeRule(self.nfa, self.memo)
            return Maybe(rule.run())
        future = futures(self.start, self.trans)
        if len(follow) == 1:
            F = follow[0]
            D = {}
            for T in self.trans:
                if T!=F:
                    D[T] = self.trans[T]
            D[self.start] = self.trans[F]
            rule = TreeRule(["", self.start, D], self.memo)
            return Seq(F, rule.run(), self.memo)
        partition = find_partition(future)
        #print "PARTITION", pprint.pformat(partition)
        #print "FOLLOW", [f[1] for f in follow]
        s_follow = set(f[1] for f in follow)
        if len(partition)>1:
            alt = []
            for p in partition:
                p_follow = [f for f in follow if f[1] in s_follow & p]
                if len(p_follow) == 1:
                    rule = self.create_span(p_follow[0], future)
                    alt.append(rule.run())
                else:
                    D = {}
                    D.update(self.trans)
                    D[self.start] = p_follow
                    alt.append(TreeRule(["", self.start, D], self.memo).run())
            return Alt(alt, self.memo)
        else:

            F = set(self.trans[follow[0]])
            for f in follow[1:]:
                if set(self.trans[f]) != F:
                    break
            else:
                X = new_state(self.start, len(self.memo))
                self.memo[X] = Alt([Seq(f, End(), self.memo) for f in follow], self.memo)
                D = {}
                for s in self.trans:
                    if s not in follow:
                        D[s] = self.trans[s]
                D[self.start] = [X]
                D[X] = self.trans[follow[0]]
                return TreeRule(["", self.start, D], self.memo).run()

            #R = self.handle_tail(future)
            #if R:
            #    return R
            P = []
            for F in follow:
                rule = self.create_span(F, future)
                P.append(rule.run())
            #print "ALT"
            #pprint.pprint(self.trans)
            #print "-"*170
            return Alt(P, self.memo)


    def handle_tail(self, future):
        follow = self.trans[self.start][:]
        f_futures    = [(i,future[f[1]].union(set([f[1]]))) for (i,f) in enumerate(follow)]

        # we can eliminate each state F from follow = trans[start]
        # when it is included within the future of all other states in follow

        inclusion = []
        visisted = set()

        while len(f_futures)>1:
            for (i,future_i) in f_futures:
                for (j,future_j) in f_futures:
                    if i!=j:
                        if not future_i.issubset(future_j):
                            break
                else:
                    # future_i is subset of all future_j sets with i!=j
                    inclusion.insert(0,i)
                    f_futures.remove((i,future_i))
                    break
            else:
                break

        seq = []
        state = None
        k   = -1
        # the n-th topmost future is included in all (n-1)-th futures
        removables = set([follow[i] for i in inclusion])

        while inclusion:
            i = inclusion.pop()
            if k == -1:
                rule = self.create_span(follow[i], future)
                # print "RULE-1", rule.run()
                seq.insert(0,rule.run())
            else:
                P = predecessors(follow[k], self.trans)
                if len(future[i] & P) == 1:
                    rule = self.create_diff_span(follow[i], follow[k][1], future)
                    # print "RULE-2", rule.run()
                    if not set(self.trans[follow[i]]).issubset(removables):
                        R = seq[0]
                        if not isinstance(R, Maybe):
                            seq[0] = Maybe(R)
                    seq.insert(0, rule.run())
                else:
                    return
            k = i

        state = follow[k]
        # print "REMOVABLES", removables
        for f in removables:
            follow.remove(f)
        if k>=0:
            P = predecessors(state, self.trans)
            y = state[1]
            alt = []
            for F in follow:
                if len(completion(F[1], future) & P) == 1:
                    rule = self.create_diff_span(F, y, future)
                    # print "RULE-3", rule.run(), self.trans[F]
                    follow_F = self.trans[F]

                    if not set(self.trans[F]).issubset(removables):
                        R = seq[0]
                        if not isinstance(R, Maybe):
                            seq[0] = Maybe(R)
                    alt.append(rule.run())
                else:
                    return
            if len(alt)>1:
                seq.insert(0, Maybe(Alt(alt, self.memo)))
            else:
                seq.insert(0, Maybe(alt[0]))
            R = Seq(seq[0], seq[1:], self.memo)
            return R


    def create_span(self, state, future):
        D = {}
        future_F = future[state[1]]
        for S in self.trans:
            if S[1] in future_F:
                D[S] = self.trans[S]
        D[self.start] = [state]
        D[state] = self.trans[state]
        return TreeRule(["", self.start, D], self.memo)

    def create_diff_span(self, X, y, future):
        '''
        Creates span of x but subtracting future_x by Y. So we replace each y in Y by Fin.
        '''
        D = {}
        Y = future[y] | set([y])
        future_x = future[X[1]]
        for S in self.trans:
            s = S[1]
            if s in future_x:
                if s not in Y:
                    D[S] = self.trans[S]
        D[self.start] = [X]
        D[X] = self.trans[X]
        for s in D.keys():
            F = []
            follow = D[s]
            for f in follow:
                if f[1] not in Y and f not in F:
                    F.append(f)
                else:
                    if self.fin not in F:
                        F.append(self.fin)
            D[s] = F
        return TreeRule(["", self.start, D], self.memo)


#########################  simple cycle  ###################################

class SimpleCycleTranslator(object):

    def find_in_transitive_follow(self, S, F, trans, visited):
        visited.add(F)
        follow = trans[F]
        if S in follow:
            return True
        else:
            for f in follow:
                if f[0] is FIN or f in visited:
                    continue
                else:
                    R = self.find_in_transitive_follow(S, f, trans, visited)
                    if R:
                        return R
        return False


    def find_simple_cycle(self, S, trans, visited = None):
        if visited is None:
            visited = set()
        visited.add(S)
        follow = trans[S]
        if S in follow:
            # check that S is not in follow^n(S)
            follow_follow = set()
            for F in follow:
                if F[0] is FIN or F in follow_follow or F == S:
                    continue
                else:
                    R = self.find_in_transitive_follow(S, F, trans, follow_follow)
                    if R:
                        break
            else:
                return S
        for F in follow:
            if F[0] is FIN or F == S or F in visited:
                continue
            C = self.find_simple_cycle(F, trans, visited)
            if C:
                return C

    @check_consistency
    def replace_simple_cycle(self, trans, S, X, memo):
        if __DEBUG__:
            print "-"*76+"."
            print "Cycle", S ," --> ",X
        follow = trans[S]
        follow_S = follow[:]
        follow.remove(S)
        del trans[S]
        is_plus = False

        for T in trans:
            follow_T = trans[T]
            if S in follow_T:
                K = set(follow) & set(follow_T)
                if K == set():
                    is_plus = True
                    break
                if not set(follow_S).issubset(follow_T):
                    is_plus = True
                    break

        for T in trans:
            F = trans[T]
            if S in F:
                F.remove(S)
                if not is_plus:
                    for a in follow:
                        if a in F:
                            F.remove(a)
                F.append(X)
        trans[X] = follow
        return is_plus

    def transform_simple_cycle(self, nfa, memo):
        start = nfa[1]
        trans = nfa[2]
        C = self.find_simple_cycle(start, trans)
        if C:
            X = new_state(start, len(memo))
            if self.replace_simple_cycle(trans, C, X, memo):
                memo[X] = ReqCycle(memo[C])
            else:
                memo[X] = OptCycle(memo[C])
            return True
        return False

######################### complex cycle  #####################################

class CycleData(object):
    '''
    Let C(x) be a cycle:

    1. F(x)     = {s|x in follow(s)}.
    2. Pre(x)   = {s in F(x)| s not in follow^n(x)}
    3. Fin(x)   = F(x) - Pre(x)
    4. Post(x)  = {s in follow(Fin(x))| x not in follow^n(s)}
    5. Init(x)  = follow(Pre(x)) - Post(x)
    6. Bundle(x)= {s in follow^n(Pre(x))| s not in Post(x) and s not in Post^n(x)}
    '''

    def __init__(self, x, trans):
        self.x = x
        self.trans = trans
        self.follow_closure = get_follow_closure(x, trans)
        self.Enter = None
        self.Pre   = None
        self.Fin   = None
        self.Post  = None
        self.Init  = None
        self.Bundle = None
        self.create()

    def create(self):
        self.Enter = set()

        # compute Enter
        for s in self.trans:
            if self.x in self.trans[s]:
                self.Enter.add(s)

        # compute Pre
        self.Pre = self.Enter - self.follow_closure

        # compute Fin
        self.Fin = self.Enter - self.Pre

        # compute Post
        self.Post = set()
        for f in self.Fin:
            if f[0] is not FIN:
                follow = self.trans[f]
                for s in follow:
                    if s[0] is FIN:
                        self.Post.add(s)
                        continue
                    follow_closure_s = get_follow_closure(s, self.trans)
                    if self.x not in follow_closure_s:
                        self.Post.add(s)
            else:
                self.Post.add(f)

        Fin = set()
        for f in self.Fin:
            follow = set(self.trans[f])
            if self.Post.issubset(follow):
                Fin.add(f)
        self.Fin = Fin

        # compute Init
        self.Init = (self.follow_closure & follow_from_set(self.Pre, self.trans)) - \
                                           (self.Post|self.Pre|get_follow_closure_set(self.Post, self.trans))

        # compute Bundle
        self.Bundle = set()
        for s in self.Pre:
            self.Bundle.update(get_follow_closure(s, self.trans))
        self.Bundle-=(self.Post|self.Pre)
        for p in self.Post:
            if p in self.Bundle:
                self.Bundle.remove(p)
            elif p[0] is not FIN:
                self.Bundle-=get_follow_closure(p, self.trans)
        self.Bundle &= self.follow_closure


class ComplexCycleTranslator(object):
    def __init__(self, translator):
        self.translator = translator

    def reduce_cycle(self, cycle_data):
        trans = {}
        for s in cycle_data.trans:
            trans[s] = list(cycle_data.trans[s])
        D = cycle_data.Fin - cycle_data.Init
        if D:
            for s in D:
                follow = trans[s]
                for f in cycle_data.Init:
                    if f in follow:
                        follow.remove(f)
            if not follow or follow == [s]:
                return {}
        else:
            # select one F in Fin s.t. reduction by Init satisfies following conditions:
            # 1. follow(F)-Init != {}
            # 2. With follow(F) = follow(F)-Init, F is still endpoint
            #
            if cycle_data.Init == cycle_data.Fin:
                for p in cycle_data.Fin:
                    if p[0] is not FIN:
                        follow = trans[p]
                        for q in cycle_data.Fin:
                            if q in follow:
                                follow.remove(q)
                        if follow == []:
                            trans[p] = cycle_data.trans[p]
                            continue
            else:
                for p in cycle_data.Fin:
                    if p[0] is not FIN:
                        follow = trans[p]
                        for q in cycle_data.Init:
                            if q in follow:
                                follow.remove(q)
                        # check cycle data
                        if follow == []:
                            trans[p] = cycle_data.trans[p]
                            continue
                        S = set()
                        for q in follow:
                            if q[0] is not FIN and q not in cycle_data.Post:
                                S.update(trans[q])

                        if S.issubset(cycle_data.Post):
                            break
                        else:
                            trans[p] = cycle_data.trans[p]
                else:
                    raise RuntimeError("Unable to reduce cycle")
        for p in trans.keys():
            if p[1] == 0:
                start = p
            elif p not in cycle_data.Bundle:
                del trans[p]
        trans[start] = list(cycle_data.Init)
        exit_symbol = (FIN, '-', start[0])
        for q in trans:
            follow = trans[q]
            for p in cycle_data.Post:
                if p in follow:
                    follow.remove(p)
                    if exit_symbol not in follow:
                        follow.append(exit_symbol)
        return trans

    def is_complex_cycle(self, cycle_data):
        if cycle_data.Fin == cycle_data.Init and len(cycle_data.Fin) == 1:
            return False
        return True


    @check_consistency
    def replace_complex_cycle(self, trans, cycle_data, start, memo):
        reduced_trans = self.reduce_cycle(cycle_data)
        if not reduced_trans:
            return False
        if __DEBUG__:
            print "[replace_complex_cycle: CYCLE]", cycle_data.x
            print "[replace_complex_cycle: INIT]", cycle_data.Init
            print "[replace_complex_cycle: FINAL]", cycle_data.Fin
            print "[replace_complex_cycle: POST]", cycle_data.Post
            print "[replace_complex_cycle: PRE]", cycle_data.Pre
            print "[replace_complex_cycle: BUNDLE]", cycle_data.Bundle
            print
            pprint.pprint(reduced_trans)
            print "[replace_complex_cycle: Cycle Redux] START"
        check(reduced_trans)
        rep = self.translator.reduce_nfa(["", start, reduced_trans], memo)
        if __DEBUG__:
            print "[replace_complex_cycle: Cycle Redux]", rep
        X = new_state(start, len(memo))
        memo[X] = rep
        for p in cycle_data.Pre:
            follow = trans[p]
            for q in cycle_data.Init:
                if q in follow:
                    follow.remove(q)
            follow.append(X)
        trans[X] = list(cycle_data.Post)
        trans[X].append(X)
        for p in cycle_data.Bundle:
            del trans[p]
        return True

    def find_cycle(self, S, trans, visited):
        visited.add(S)
        for F in trans[S]:
            if F[0] is FIN:
                continue
            cycle = find_node_from(F, F, None, trans, set())
            if cycle:
                cycle_data = CycleData(cycle[0], trans)
                if self.is_complex_cycle(cycle_data):
                    return cycle_data
        for F in trans[S]:
            if F[0] is FIN or F in visited:
                continue
            cycle_data = self.find_cycle(F, trans, visited)
            if cycle_data:
                return cycle_data

    def transform_complex_cycle(self, nfa, memo):
        start = nfa[1]
        trans = nfa[2]
        cycle_data = self.find_cycle(start, trans, set())
        if not cycle_data:
            return False
        if __DEBUG__:
            print "-"*76+"."
            print "COMPLEX CYCLE"
        return self.replace_complex_cycle(trans, cycle_data, start, memo)


#################### test ###############################


class NFA2GrammarTranslator(object):
    def __init__(self, langlet):
        self.langlet = langlet
        self.trans_simcycle = SimpleCycleTranslator()
        self.trans_comcycle = ComplexCycleTranslator(self)

    # the following two methods are needed to let ad hoc langlets overwrite them for
    # testability
    def get_constants(self):
        return self.langlet.lex_nfa.constants

    def get_node_name(self, nid):
        return self.langlet.get_node_name(nid)

    def maybe_show(self, trans, memo):
        if __DEBUG__:
            print "-"*76
            print "------------------ NFA --------------------------"
            pprint.pprint(trans)
            print
            print "------------------ MEMO -------------------------"
            pprint.pprint(memo)
            print "-"*76+"'\n"


    def terminate(self, trans):
        if len(trans) <= 2:
            for v in trans.values():
                if len(v)>1:
                    return False
            return True
        return False

    #  the basic reduction algorithm works in two steps
    #
    #  1. Eliminate cycles
    #  2. After cycle elimination automata can be described using Alt and Seq. Maybe describes
    #     a special case.

    def reduce_nfa(self, nfa, memo):
        _, start, trans = nfa
        while True:
            if self.trans_comcycle.transform_complex_cycle(nfa, memo):
                self.maybe_show(trans, memo)
                if self.terminate(trans):
                    break
            elif self.trans_simcycle.transform_simple_cycle(nfa, memo):
                self.maybe_show(trans, memo)
                if self.terminate(trans):
                    break
            else:
                return TreeRule(nfa, memo).run()

        if len(trans[start]) == 2:
            for item in trans[start]:
                if item[0] is not FIN:
                    rep = Maybe(memo[item])
        elif len(trans) == 1:
            rep = memo[start]
        else:
            rep = memo[trans[start][0]]
        return rep


    def translate(self, nfa, memo = {}):
        _nfa = [nfa[0], nfa[1], {}]
        for key, value in nfa[2].items():
            _nfa[2][key] = value[:]

        trans = _nfa[2]
        start = _nfa[1]
        constants = self.get_constants()
        memo.clear()

        for S in trans:
            if S[0] in constants:
                c = constants[S[0]]
                if c and not c.isspace():
                    memo[S] = "'"+constants[S[0]]+"'"
                else:
                    memo[S] = self.get_node_name(S[0])
            elif is_keyword(S[0]):
                memo[S] = "'"+self.get_node_name(S[0])+"'"
            else:
                memo[S] = self.get_node_name(S[0])
        rep = self.reduce_nfa(_nfa, memo)
        return memo[start] +": "+str(rep)

    def check_translation(self, nfa, dbg=True):
        global __DEBUG__
        __DEBUG__ = dbg
        if __DEBUG__:
            print "----------------------------------------------"
            pprint.pprint(nfa)
            print "----------------------------------------------"
        R = self.translate(nfa)
        if __DEBUG__:
            print "[check-translation : Rule]", R
        go = GrammarObject.grammar_from_rule(R)
        nfa_R = go.get_nfas()[go.get_start_symbol()]
        __DEBUG__ = False
        return R, nfa_comp(nfa, nfa_R)




# can we identify loops by futures? Does every element in a loop has the same future?

def test2():
    langlet = langscape.load_langlet("nfa2gra_test")
    nfa2gra = NFA2GrammarTranslator(langlet)
    n = 0
    for i in range(1, 68):
        try:
            print "-"*70
            print str(i)
            nfa = langlet.parse_nfa.nfas[getattr(langlet.symbol, "stmt"+str(i))]
            R, res = nfa2gra.check_translation(nfa, False)
            assert res #, nfa2gra.check_translation(nfa)
        except Exception:
            print "FAIL", i, R
            n+=1
        print "-"*70
    print "FAILURES", n


    nfa = langlet.parse_nfa.nfas[langlet.symbol.stmt9]
    print nfa2gra.check_translation(nfa, False)

def test3():
    from langscape.langlets.ls_grammar.grammar_object import GrammarObject

    class NFA2GrammarObjTranslator(NFA2GrammarTranslator):
        def __init__(self, langlet):
            self.langlet = langlet
            nfas = self.langlet.nfagenerator.nfas
            self.names = {}
            for r in nfas:
                name = nfas[r][0].split(":")[0]
                self.names[r] = name
            super(NFA2GrammarObjTranslator, self).__init__(langlet)

        def get_constants(self):
            return  {} #self.langlet.nfagenerator.nfadata.constants

        def get_node_name(self, nid):
            return self.names[nid]

    rules = []
    rules = open("tests/rulefile.txt").readlines()
    for i, rule in enumerate(rules):
        print "RULE", rule
        go = GrammarObject.grammar_from_rule(rule)
        nfa = go.nfagenerator.nfas[go.get_start_symbol()]
        nfa2gra = NFA2GrammarObjTranslator(go)
        if not nfa2gra.check_translation(nfa, False):
            print (i, rule)
        if i == 10:
            break


if __name__ == '__main__':
    test3()



