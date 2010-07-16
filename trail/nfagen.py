'''
nfagen module. Used to create characterstic finite automata for grammar rules
'''
__all__ = ["create_lex_nfa",
           "create_parse_nfa",
           "create_nfa_from_source",
           "GrammarError",
           "parse_grammar",
           "NFAGenerator",
           "NFAData"]

import pprint

USE_EE = False

import langscape
import langscape.util
import langscape.trail.nfaexpansion as nfaexpansion
from langscape.trail.nfadef import*

if USE_EE:
    from EasyExtend.langlets.grammar_langlet.rules import*
else:
    from langscape.langlets.ls_grammar.rules import*

from langscape.ls_const import*
from langscape.util import flip

class NFAData:
    def __init__(self, nfas):
         self.nfas       = nfas       # state-machine table
         self.keywords   = set()      # langlet keywords
         self.reachables = {}         # first-set ( == self.first_set )
         self.ancestors  = {}         # set of NT which derive T
         self.first_set  = {}
         self.used_symbols = set()    # all nids and keywords
         self.terminals    = set()    # terminals of the grammar
         self.nonterminals = set()    # non-terminals of the grammar
         self.symbols_of   = {}       # T and NT found in rule
         self.expansion_target = {}   # rules before expansion
         self.depths = {}             # rule depth
         self.fin_cycles = {}         # -> see compute_fin_cycles()
         self.last_set = {}           # first-set dual
         self.max_depth = 0
         self.lexer_terminal = None   # lexer terminals - available for lexers only
         self.start_symbols = ()      # all possible start symbols

    def compute_terminals(self):
        '''
        Computed ::
            self.terminals
            self.nonterminals

        Required ::
            self.used_symbols
            self.keywords
        '''
        assert self.used_symbols
        #assert self.keywords

        for s in list(self.used_symbols):
            if s in self.keywords:
                self.terminals.add(s)
            elif is_token(s):
                self.terminals.add(s)
            else:
                self.nonterminals.add(s)

    def compute_used_symbols(self):
        '''
        Computed ::
            self.used_symbols   --  all nids and keywords
            self.symbols_of     --  for each nfa compute the symbols of the particular nfa
        Required ::
            None
        '''
        self.used_symbols = set()  # reset
        for k, nfa in self.nfas.items():
            S = set([label[0] for label in nfa[2]]) - set([None, k])
            self.used_symbols.update(S)
            self.symbols_of[k] = S

    def compute_predecessor(self, nfa, label):
        '''
        For a set of transitions and a label compute the predecessors of the label.
        If a preceding label L is skipable compute a non-skipable label recursively from L.

        @param nfa: an NFA
        @param label: a label of the NFA.
        '''
        transitions = nfa[2]
        pre = []
        for L, T in transitions.items():
            if label in T:
                if L[1] in CONTROL:
                    pre+=self.compute_predecessor(nfa, L)
                else:
                    pre.append(L)
        return pre

    def compute_successor(self, nfa, label):
        '''
        For a set of transitions and a label compute the successors of the label.
        If a successor label L is skipable compute a non-skipable label recursively from L.

        @param nfa: an NFA
        @param label: a label of the NFA.
        '''
        transitions = nfa[2]
        succ = []
        T = transitions[label]
        for L in T:
            if L[1] == '.':
                succ+=self.compute_successor(nfa, L)
            else:
                succ.append(L)
        return succ

    def compute_fin_cycles(self):
        '''
        Computed ::
            self.fin_cycles
        Required ::
            self.last_set
        Description ::
            Let K be a non-terminal and Esc = Pre((None, '-', K)) the set of states that can escape
            the NFA of K. The transitions of Esc shall be denoted by Next(Esc). Now consider the set
            BaseFinCycle(K) = nids-of ( Next(Esc) /\ Esc ).

            Example: a non-empty BaseFinCycle is created by rules

                     I)  R: A+      -> BaseFinCycle = {A}  -- A is in Esc and in Next(Esc)
                     II) R: A [B]   -> BaseFinCycle = {B}  -- A,B are in Esc and B is in Next({A})

            We define FinCycle(K) recusively by

                FinCycle(K) = \/ (FinCycle(s)) \/ BaseFinCycle(K)
                            s in LastSet(K)
                              and s in NT

            This function computes the FinCycle(K) for each NT K.
        '''
        assert self.last_set

        fin_cycles = {}
        for r, nfa in self.nfas.items():
            T = set()
            fin_set = set(self.compute_predecessor(nfa, (None, '-', r)))
            transitions = nfa[2]
            for L in fin_set:
                T.update(transitions[L])
            fin_cycles[r] = set([L[0] for L in (fin_set & T) if L[0]!=None])

        visited = set()
        def compute_fin_set(r):
            S = self.last_set[r]
            self.fin_cycles[r] = fin_cycles[r]
            visited.add(r)
            for s in S:
                if not is_token(s):
                    if s in self.fin_cycles:
                        self.fin_cycles[r].update(self.fin_cycles[s])
                    elif s not in visited:
                        compute_fin_set(s)
                        self.fin_cycles[r].update(self.fin_cycles[s])
        for r in self.nfas:
            compute_fin_set(r)
        return self.fin_cycles


    def compute_last_set(self):
        '''
        Computed ::
            self.last_set
        Required ::
            None
        Description ::
            Let K be a non-terminal and Esc = Pre((None, '-', K)) the set of labels that can escape
            the NFA of K. We define BaseLastSet(K) = nids-of ( Esc ) and then recursively

                 LastSet(K) = \/ (LastSet(s)) \/ BaseLastSet(K)
                            s in BaseLastSet(K)
                              and s in NT

            This function computes the LastSet(K) for each NT K.
        '''

        def end_trans(r):
            nfa = self.nfas[r]
            labels = self.compute_predecessor(nfa, (None, '-', r))
            return set([L[0] for L in labels])

        end_transitions = {}
        for r in self.nfas:
            end_transitions[r] = end_trans(r)

        visited = set()
        last_sets = {}

        def _compute_last_set(r):
            end_t = end_transitions[r]
            visited.add(r)
            S = set()
            for s in end_t:
                S.add(s)
                if not is_token(s):
                    if s in last_sets:
                        S.update(last_sets[s])
                    elif s not in visited:
                        _compute_last_set(s)
                        S.update(last_sets[s])

            last_sets[r] = S

        for r in end_transitions:
            if r not in last_sets:
                _compute_last_set(r)
        self.last_set = last_sets
        return last_sets


    def compute_first_set(self):
        '''
        Computed ::
            self.first_set
            self.reachables ( self.reachables == self.first_set )
        Required ::
            None
        Description ::
            Let K be a non-terminal and Start = Succ((K,0,K)) the set of labels following the start label
            in the transititions of K. We define BaseFirstSet(K) = nids-of ( Start ) and then recursively

                FirstSet(K) = \/ (FirstSet(s)) \/ BaseFirstSet(K)
                            s in BaseFirstSet(K)
                              and s in NT

            This function computes the LastSet(K) for each NT K.
        '''
        assert self.nfas
        self.reachables = {}  # reset
        visited = set()

        def _reachables(NT):
            reach = self.reachables.get(NT)
            if reach:
                return reach
            if NT in visited:
                raise NodeCycleError, "Immediate left recusion in grammar detected at node %s. Trail can't build parse tables."%NT
            visited.add(NT)
            nfa = self.nfas[NT]
            selection = set([s[0] for s in self.compute_successor(nfa, (NT,0,NT)) if s[0]!=None])
            self.reachables[NT] = set()
            for s in selection:
                if not is_token(s) and s!=NT:
                    self.reachables[NT].update(_reachables(s))
            self.reachables[NT].update(selection)
            return self.reachables[NT]

        for r in self.nfas:
            _reachables(r)
        self.first_set = self.reachables


    def compute_ancestors(self):
        '''
        Computed ::
            self.ancestors
        Required ::
            self.reachables
        Description ::
            Inverse function of compute_first_set(). For each terminal symbol T the non-terminals NT that
            `derive T` ( i.e. T is in FirstSet(NT) ) are computed.
        '''
        _ancestors = {}
        for r, reach in self.reachables.items():
            for s in reach:
                if is_token(s):
                    S = _ancestors.get(s, set())
                    S.add(r)
                    _ancestors[s] = S
        self.ancestors = _ancestors

    def compute_reachable_depths(self):
        '''
        Computed ::
            self.depths
        Required ::
            self.reachables
        Description ::

        '''
        depths = {}
        visited = set()

        def compute_depth(r):
            S = self.reachables[r]
            K = 0
            visited.add(r)
            for s in S:
                if s in depths:
                    K = max(K, 1+depths[s])
                elif is_token(s):
                    K = max(K,1)
                elif s in visited:
                    raise NodeCycleError("Cyclic references in grammar found at node %s. Trail can't build parse tables."%s)
                else:
                    compute_depth(s)
                    K = max(K, 1+depths[s])
            depths[r] = K

        for r in self.reachables:
            compute_depth(r)
        self.depths = depths
        return depths

    def compute_toplevel(self):
        '''
        Computed ::
            self.top
        Required ::
            self.symbols_of
        Description ::
            Computes one or more start symbols.
        '''
        def create_referrer():
            referrer = {}
            for r, sym in symbols.items():
                for s in sym:
                    if is_token(s):
                        continue
                    R = referrer.get(s,set())
                    R.add(r)
                    referrer[s] = R
            return referrer

        symbols  = {}
        symbols.update(self.symbols_of)
        layer    = []
        rules    = symbols.keys()

        referrer = create_referrer()

        top = set()
        for r in rules:
            S = referrer.get(r, set([]))
            if len(S) == 0:
                top.add(r)
        default, k = 0,0
        for T in top:
            n = len(self.reachables[T])
            if n>k:
                k = n
                default = T
        self.start_symbols = (default, top)
        return self.start_symbols


class GrammarError(Exception):
    def __init__(self, symbols, typ):
        self.symbols = symbols
        self.parser_type = typ

    def __str__(self):
        S = tuple(self.symbols)[0]
        if self.parser_type == "Token":
            return "Unreferenced symbol `%s` in Token.gen file detected."%S
        else:
            return "Unreferenced symbol `%s` in Grammar.gen file detected."%S

def get_nid(item, langlet):
    nid = langlet.symbol.__dict__.get(item)
    if nid is not None:
        return nid
    nid = langlet.token.token_map.get(item)
    if nid is not None:
        return nid
    else:
        return item

def contractible(X):
    if isinstance(X, EmptyRule):
        return True
    elif isinstance(X, ConstRule):
        return False
    elif isinstance(X, AltRule):
        return any(contractible(S) for S in X.lst)
    else:
        return all(contractible(S) for S in X.lst)

def begin(X):
    if not X.lst:
        return set()
    elif isinstance(X, (ConstRule, EmptyRule)):
        return set([X])
    elif isinstance(X, AltRule):
        return reduce(lambda x, y: x.union(y), [begin(R) for R in X.lst])
    else:
        S = X.lst[0]
        if contractible(S):
            return begin(S).union(begin(SequenceRule(X.lst[1:])))
        else:
            return begin(S)

def end(X):
    if not X.lst:
        return set()
    if isinstance(X, (ConstRule, EmptyRule)):
        return set([X])
    elif isinstance(X, AltRule):
        return reduce(lambda x, y: x.union(y), [end(R) for R in X.lst])
    else:
        S = X.lst[-1]
        if contractible(S):
            return end(S).union(end(SequenceRule(X.lst[:-1])))
        else:
            return end(S)

def build_nfa(rule, start = None, nfa = None):
    if not start:
        nfa = {}
        # rule.lst[0] == (rule name, 0)
        # rule.lst[1] == SequenceRule(...)
        start = set([ConstRule([rule.lst[0]])])
        return build_nfa(rule.lst[1], start, nfa)
    if isinstance(rule, SequenceRule):
        for i, R in enumerate(rule.lst):
            build_nfa(R, start, nfa)
            start = end(R)
    elif isinstance(rule, AltRule):
        for R in rule.lst:
            build_nfa(R, start, nfa)
    else: # ConstRule or EmptyRule
        r = rule.lst[0]
        for s in start:
            state = s.lst[0]
            follow = nfa.get(state, set())
            follow.add(r)
            nfa[state] = follow
    return nfa


def nfa_reduction(nfa):
    removable = []
    for (K, idx) in nfa:
        if K is None and idx!="-":
            F = nfa[(K, idx)]
            for follow in nfa.values():
                if (K, idx) in follow:
                    follow.remove((K, idx))
                    follow.update(F)
            removable.append((K, idx))
    for R in removable:
        del nfa[R]
    return nfa

def parse_grammar(source):
    if USE_EE:
        from EasyExtend.langlets.grammar_langlet.langlet import parse_grammar_rule
        return parse_grammar_rule(source)
    else:
        ls_grammar = langscape.load_langlet("ls_grammar")
        return ls_grammar.compile(source)


class NFAGenerator(object):
    '''
    Creates NFAs from grammar files, expands them and writes NFA data to a parse_nfa ( lex_nfa ).
    '''
    def __init__(self, langlet, parser_type = "Parser"):
        self.langlet = langlet
        self.parser_type = parser_type
        self.unknown = set()
        self.used_strings = set()
        self.nfas = {}
        self.keywords = {}
        self.nfadata = None
        self.kwd_index = langlet.langlet_id + KEYWORD_OFFSET

    def from_ebnf(self, ebnf_str, default = 0):
        rules = parse_grammar(ebnf_str)
        for rule_name, (rule, ebnf) in rules.items():
            table  = nfa_reduction(build_nfa(rule))
            r, nfa = self.insert_nids(rule_name, table, default)
            return [ebnf.strip(), (r, 0, r), nfa]

    def create_all(self, source):
        '''
        Creates all nfas for an existing langlet.
        '''
        rules = parse_grammar(source)
        for rule_name, (rule, ebnf) in rules.items():
            nfa = build_nfa(rule)
            table  = nfa_reduction(nfa)
            r, nfa = self.insert_nids(rule_name, table)
            self.nfas[r] = [ebnf.strip(), (r, 0, r), nfa]
        S = self.unknown - self.used_strings
        if S:
            raise GrammarError(S, self.parser_type)
        return self.nfas


    def insert_nids(self, rule_name, table, default = None):
        def map_state(state, nid):
            name = state[0]
            if name is None:
                return (None, "-", nid)
            elif name[0] in ("'", '"'):
                name = name[1:-1]
                self.used_strings.add(name)
            S = self.get_nid(name, symbol, token)
            if type(S)!=int:
                k = self.keywords.get(S)
                if k is None:
                    k = self.kwd_index
                    self.keywords[S] = self.kwd_index
                    self.kwd_index+=1
                return (k, state[1], nid)
            else:
                return (S, state[1], nid)

        if self.parser_type == "Parser":
            token  = self.langlet.parse_token
            symbol = self.langlet.parse_symbol
        elif self.parser_type == "Lexer":
            token  = self.langlet.lex_token
            symbol = self.langlet.lex_symbol

        nid = self.get_nid(rule_name, symbol, token, default)
        nfa = {}
        for state, follow in table.items():
            nfa[map_state(state, nid)] = [map_state(F, nid) for F in follow]
        return nid, nfa

    def get_nid(self, item, symbol, token, default = None):
        default = default if default else item
        nid = symbol.__dict__.get(item)
        if nid is not None:
            return nid
        nid = token.token_map.get(item) or token.__dict__.get(item)
        if nid is not None:
            return nid
        else:
            self.unknown.add(item)
            return default

    def derive_properties(self):
        self.nfadata = NFAData(self.nfas)
        self.nfadata.keywords = self.keywords
        self.nfadata.compute_used_symbols()
        self.nfadata.compute_terminals()
        self.nfadata.compute_first_set()
        self.nfadata.compute_ancestors()
        self.nfadata.compute_reachable_depths()
        self.nfadata.compute_toplevel()
        if self.parser_type == "Lexer":
            from langscape.trail.nfatools import compute_constants
            self.nfadata.constants = compute_constants(self.nfadata.nfas, self.langlet.lex_token, flip(self.nfadata.keywords))

    def expand_nfas(self, report = True, check_right_expand = True):
        if self.parser_type == "Lexer":
            nfaexp = nfaexpansion.NFAExpansionLexer(self.langlet, self.nfadata)
        else:
            nfaexp = nfaexpansion.NFAExpansionParser(self.langlet, self.nfadata)
        if report is False:
            nfaexp.report = nfaexpansion.AbstractExpansionStatusReport()
        nfaexp.expand_all()
        if check_right_expand:
            nfaexp.check_rightexpand()

    def write_to_file(self):
        from langscape.util.path import path
        if self.parser_type == "Parser":
            fPyTrans = open(self.langlet.path.joinpath("parsedef", "parse_nfa.py"),"w")
        else:
            fPyTrans = open(self.langlet.path.joinpath("lexdef", "lex_nfa.py"),"w")
        if self.langlet.config.encoding:
            print >> fPyTrans, langscape.util.get_encoding_str(self.langlet.config.encoding)

        print >> fPyTrans, "# %s" % ("_" * 70)
        print >> fPyTrans, "# This was automatically generated by nfagen.py."
        print >> fPyTrans, "# Hack at your own risk."
        print >> fPyTrans
        print >> fPyTrans, "# LANGLET ID\n"
        print >> fPyTrans, "LANGLET_ID = %s"%self.langlet.langlet_id
        print >> fPyTrans
        print >> fPyTrans, "from langscape.util.univset import ANY\n"
        print >> fPyTrans
        print >> fPyTrans, "# trail NFAs:"
        print >> fPyTrans
        print >> fPyTrans, "nfas = "+pprint.pformat(self.nfadata.nfas)
        print >> fPyTrans
        print >> fPyTrans, "# expansion targets:"
        print >> fPyTrans
        print >> fPyTrans, "expanded  = "+pprint.pformat(self.nfadata.expansion_target, width=120)
        print >> fPyTrans
        print >> fPyTrans, "# reachables:"
        print >> fPyTrans
        print >> fPyTrans, "reachables = "+pprint.pformat(self.nfadata.reachables, width=120)
        print >> fPyTrans
        print >> fPyTrans, "# terminals:"
        print >> fPyTrans
        print >> fPyTrans, "terminals  = "+pprint.pformat(self.nfadata.terminals, width=120)
        print >> fPyTrans
        print >> fPyTrans, "# terminal ancestors:"
        print >> fPyTrans
        print >> fPyTrans, "ancestors  = "+pprint.pformat(self.nfadata.ancestors, width=120)
        print >> fPyTrans
        print >> fPyTrans, "# last set:"
        print >> fPyTrans
        print >> fPyTrans, "last_set  = "+pprint.pformat(self.nfadata.last_set, width=120)
        print >> fPyTrans
        print >> fPyTrans, "# symbols of:"
        print >> fPyTrans
        print >> fPyTrans, "symbols_of  = "+pprint.pformat(self.nfadata.symbols_of, width=120)
        print >> fPyTrans
        print >> fPyTrans, "# keywords:"
        print >> fPyTrans
        print >> fPyTrans, "keywords  = "+pprint.pformat(self.nfadata.keywords, width=120)
        print >> fPyTrans
        print >> fPyTrans, "# start symbols:"
        print >> fPyTrans
        print >> fPyTrans, "start_symbols  = "+pprint.pformat(self.nfadata.start_symbols, width=120)
        print >> fPyTrans


        if self.nfadata.lexer_terminal:
            print >> fPyTrans, "# lexer_terminal:"
            print >> fPyTrans
            print >> fPyTrans, "lexer_terminal  = "+pprint.pformat(self.nfadata.lexer_terminal, width=80)
            print >> fPyTrans
            print >> fPyTrans, "# constants:"
            print >> fPyTrans
            print >> fPyTrans, "constants  = "+pprint.pformat(self.nfadata.constants, width=120)
            print >> fPyTrans

        fPyTrans.close()

        if self.parser_type == "Parser":
            print "*** GrammarGen.g + parse_nfa.py generated in %s.parsedef\n"%self.langlet.config.langlet_name
        else:
            print "*** TokenGen.g + lex_nfa.py generated in %s.lexdef\n"%self.langlet.config.langlet_name

        return self.nfadata.nfas

def create_nfa_from_source(langlet, source, parser_type = "Parser"):
    nfagenerator = NFAGenerator(langlet, parser_type)
    nfagenerator.create_all(source)
    if nfagenerator.nfas:
        nfagenerator.derive_properties()
        nfagenerator.expand_nfas()
    return nfagenerator

def create_lex_nfa(langlet):
    return create_nfa(langlet, "Lexer")

def create_parse_nfa(langlet):
    return create_nfa(langlet, "Parser")

def create_nfa(langlet, parser_type = "Parser"):
    from langscape.base.grammar_gen import find_langlet_grammar
    grammar_type = "GrammarGen.g" if parser_type == "Parser" else "TokenGen.g"
    source = find_langlet_grammar(langlet, grammar_type)
    nfagenerator = create_nfa_from_source(langlet, source, parser_type)
    nfagenerator.write_to_file()


def test1():
    grammar = """
    print_stmt: 'print' ( [ test (',' test)* [','] ] |
                      '>>' test [ (',' test)+ [','] ] )
    """
    rules = parse_grammar(grammar)
    rule  = rules.values()[0][0]
    print rule
    pprint.pprint( nfa_reduction(build_nfa(rule)))

def test2():
    import langscape
    langlet = langscape.load_langlet("python")

    from langscape.base.grammar_gen import find_langlet_grammar
    grammar_type = "GrammarGen.g"
    source = find_langlet_grammar(langlet, grammar_type)

    nfagen = NFAGenerator(langlet)
    rules  = nfagen.create_all()
    for r, nfa in langlet.parse_nfa.nfas.items():
        table = rules[r][2]
        for state, follow in nfa[2].items():
            F = table.get(state,[])
            if sorted(follow)!=sorted(F):
                print "NFAs are different"
                print rules[r][0]
                pprint.pprint(table)
                print "-----------------"
                pprint.pprint(nfa[2])
                print
                break

def test3():
    "print_stmt : 'print' ( [test (',' test )* [',' ] ]| '>>' test [ (',' test )+ [',' ] ] )"
    import langscape
    langlet = langscape.load_langlet("python")
    nfagen = NFAGenerator(langlet)
    rule = nfagen.from_ebnf("if_stmt: 'if' test [ as_name] ':' suite ('elif' test [ as_name] ':' suite)* ['else' ':' suite]")
    print rule[0]


if __name__ == '__main__':
    test3()

