import langscape
import random
from langscape.ls_const import*
from langscape.sourcetools.sourcegen import GPSourceGen
from langscape.sourcetools.tokgen import TokenGenerator
from lexdef import lex_symbol
from langscape.trail.nfagen import NFAGenerator, GrammarError
from langscape.base.langlet import BaseLanglet
from langscape.base.grammar_gen import SymbolObject
import math

ls_grammar = langscape.load_langlet("ls_grammar")

'''
1. Given a set of textual grammar rules.
2. Create a GrammarObject from those rules and expand the rules.
3. Evaluate the fitness of each Grammar object.
4. Take the best GrammarObjects, extract their rule sets, mutate the rule sets and create
   a new generation of GrammarObjects.
'''

class GrammarLanglet(BaseLanglet):
    def __init__(self):
        self.options = {}
        self.parse_token    = ls_grammar.parse_token
        self.parse_symbol   = None
        self.langlet_id     = ls_grammar.langlet_id

class GrammarObject(object):
    def __init__(self, rules):
        self.rules = rules
        self.langlet = GrammarLanglet()
        self.nfagenerator = None

    def create_grammar(self):
        symobject = SymbolObject(ls_grammar.langlet_id)
        R = [' '.join([g[1] for g in R1]).strip() for R1 in self.rules]
        symobject.create(R)
        self.langlet.parse_symbol = symobject
        self.nfagenerator = NFAGenerator(self.langlet, "Parser")
        self.nfagenerator.create_all("\n".join(R)+"\n")
        if self.nfagenerator.nfas:
            self.nfagenerator.derive_properties()
            self.nfagenerator.expand_nfas()

class GGen(GPSourceGen):
    def __init__(self, *args):
        super(GGen, self).__init__(*args)
        self.desired_rule_size = 0
        self.rule_cnt = 0
        self.rule_ids = []

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

    def new_rule(self):
        self.rule_cnt+=1
        self.rule_ids.append(self.rule_cnt)
        return ls_grammar.tokenize("r%d : 'A%d'\n"%(self.rule_cnt,self.rule_cnt)).tokstream

    def gen_token_string(self, nid):
        if nid == lex_symbol.NAME:
            n = len(self.rule_ids)
            return "r%d"%self.rule_ids[random.randrange(0, n)]
        elif nid == lex_symbol.STRING:
            n = len(self.rule_ids)
            return "'A%d'"%self.rule_ids[random.randrange(0, n)]
        else:
            return self.tokgen.gen_token_string(nid)


    def fitness(self, individual):
        '''
        We seek for the smallest rule set with the biggest expansion.

        n = len(rules)

        m = average length of a rule ::

            m = sum(length(rule) for rule in rules) / len(rules)

        k = nbr of states of the biggest expanded rule

        However, we do not want rules with a number of states signficantly exceeding 1000.
        So we are dumping k:

            def scale(N, k):
                if k<=N:
                    return k**2
                else:
                    return math.exp(-0.02*(k-N))*(k**2)

        Our formular becomes ::
                         !
            scale(N, k)/m*n = max
        '''
        k = 0
        for r, nfa in individual.nfagenerator.nfas.items():
            k = max(len(nfa[2]),k)
        if k <= self.desired_rule_size:
            K = float(k**2)
        else:
            K = math.exp(-0.02*(k-self.desired_rule_size))*(k**2)
        m = sum(len(R) for R in individual.rules)
        return m/50.0 + K / m


    def init_population(self, size):
        R = [self.new_rule() for i in range(7)]
        while len(self.population)<size:
            go  = GrammarObject(R)
            gox = self.mutate(go)
            if gox:
                self.population.append((gox,-1))

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
        print "\n".join([' '.join([g[1] for g in R1]).strip() for R1 in individual.rules])

    def terminate(self):
        return False # controlled by evolve main loop

    def mutate(self, individual):
        rules = individual.rules[:]
        ops = ["insert", "subst", "delete"]
        while True:
            op = ops[random.randrange(0,3)]
            if op == "new_rule":
                k = random.randrange(0,3)
                if k == 0:
                    rules.append(self.new_rule())
                    break
            else:
                i = random.randrange(0, len(rules))
                R = rules[i]
                fn = getattr(self, op)
                rules[i] = fn(R)
                break
        try:
            go = GrammarObject(rules)
            go.create_grammar()
            return go
        except (GrammarError,NodeCycleError):
            pass
        except (KeyError, RuntimeError):
            self.display_individual(go, 0)
            raise

def test1():
    ggen = GGen(ls_grammar)
    R1 = ggen.new_rule()
    R2 = ggen.new_rule()
    R3 = ggen.new_rule()
    for i in range(10):
        R1 = ggen.insert(R1)
    #print ' '.join([g[1] for g in R1]).strip()
    for i in range(1):
        R1 = ggen.delete(R1)
        print R1
    print ' '.join([g[1] for g in R1]).strip()
    for i in range(3):
        R1 = ggen.subst(R1)
    print ' '.join([g[1] for g in R1]).strip()

if __name__ == '__main__':
    ggen = GGen(ls_grammar)
    ggen.desired_rule_size = 1000
    ggen.evolve(size = 20, generations = 400)

