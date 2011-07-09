import langscape
import random
from langscape.ls_const import*
from langscape.csttools.cstutil import is_keyword
from langscape.sourcetools.sourcegen import GPSourceGen
from langscape.sourcetools.tokgen import TokenGenerator
from lexdef import lex_symbol
from langscape.trail.nfagen import NFAGenerator, GrammarError
from langscape.base.langlet import BaseLanglet
from langscape.base.grammar_gen import SymbolObject
import math

ls_grammar = langscape.load_langlet("ls_grammar")

class RuleObject(object):
    def __init__(self, langlet, rule):
        try:
            self.rule = rule.tokstream
        except AttributeError:
            self.rule = rule
        self.nfagenerator = NFAGenerator(langlet, "Parser")
        R = [s[1] for s in self.rule]
        self.nfa = self.nfagenerator.from_ebnf(" ".join(R))

class ReverseGen(GPSourceGen):
    def __init__(self, langlet, nfa):
        super(ReverseGen, self).__init__(ls_grammar)
        self.rule_langlet = langlet
        self.nfa = nfa
        self.strings = []
        self.names = []
        trans = nfa[2]
        start = nfa[1]
        self.rule_name = langlet.get_node_name(start[0])
        for T in trans:
            if is_keyword(T[0]):
                self.strings.append(langlet.keywords[T[0]])
            else:
                if T!=start:
                    self.names.append(langlet.get_node_name(T[0]))
        self.K = 0
        for S in self.nfa[2]:
            self.K+=len(self.nfa[2][S])


    def get_right_par(self, nid):
        if nid == lex_symbol.LPAR:
            return lex_symbol.RPAR
        elif nid == lex_symbol.LSQB:
            return lex_symbol.RSQB

    def get_left_par(self, nid):
        if nid == lex_symbol.RPAR:
            return lex_symbol.LPAR
        elif nid == lex_symbol.RSQB:
            return lex_symbol.LSQB

    def gen_token_string(self, nid):
        if nid == lex_symbol.NAME:
            return self.names[random.randrange(0, len(self.names))]
        elif nid == lex_symbol.STRING:
            if len(self.strings):
                return self.strings[random.randrange(0, len(self.strings))]
            else:
                return '"FOO"'
        else:
            return self.tokgen.gen_token_string(nid)


    def fitness(self, individual):
        trans_1 = individual.nfa[2]
        trans_2 = self.nfa[2]
        s_1 = set(trans_1.keys())
        s_2 = set(trans_2.keys())
        K = 0
        for s in trans_1:
            if s in trans_2:
                K+=50
                K+=10*len(set(trans_1[s]) & set(trans_2[s]))
            elif s[0] is None:
                k-=100
        return K

    def init_population(self, size):
        R = ls_grammar.tokenize(self.rule_name+":"+" ".join(self.names)+"\n")
        while len(self.population)<size:
            ro  = RuleObject(self.rule_langlet, R)
            rox = self.mutate(ro)
            if rox:
                self.population.append((rox,-1))

    def display_results(self):
        individual, fit = self.population[0]
        self.display_individual(individual, fit)

    def display_individual(self, individual, fit):
        k = 0
        for r, nfa in individual.nfagenerator.nfas.items():
            k = max(len(nfa[2]),k)

        print "Fitness:", fit
        print "Max Rule:", k
        print "-------------------------------------------------------------------"
        print ' '.join([s[1] for s in individual.rule])
        pprint.pprint(individual.nfa)

    def terminate(self, fit_val):
        return False

    def mutate(self, individual):
        try:
            R = individual.rule
            op = ["insert", "subst", "delete"][random.randrange(0,3)]
            fn = getattr(self, op)
            print ' '.join([s[1] for s in fn(R)])
            ro = RuleObject(self.rule_langlet, fn(R))
            return ro
        except (GrammarError, NodeCycleError):
            pass
        except (KeyError, RuntimeError):
            self.display_individual(ro, 0)
            raise


if __name__ == '__main__':
    python = langscape.load_langlet("python")
    nfagen = NFAGenerator(python)
    import pprint
    nfa = nfagen.from_ebnf("file_input: (NEWLINE | stmt)* ENDMARKER")
    pprint.pprint(nfa)

    rgen = ReverseGen(python, nfa)
    print rgen.names
    rgen.evolve(size = 20, generations = 250)


