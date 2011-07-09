import langscape
import langscape

from langscape.ls_const import*
from langscape.sourcetools.tokgen import TokenGenerator
from langscape.trail.nfagen import NFAGenerator, GrammarError
from langscape.base.langlet import BaseLanglet
from langscape.base.grammar_gen import SymbolObject

from lexdef import lex_symbol

ls_grammar = langscape.load_langlet("ls_grammar")

class GrammarLanglet(BaseLanglet):
    def __init__(self):
        self.options = {}
        self.parse_token    = self.token  = ls_grammar.parse_token
        self.parse_symbol   = self.symbol = None
        self.langlet_id     = -1
        self.keywords       = {}

    def _load_symbols(self):
        return self.parse_symbol

class GrammarObject(object):
    def __init__(self, rules):
        '''
        @param rules: a list of grammar rules in tokenized form i.e. grammar rules as token streams.
        '''
        self.rules = rules
        self.langlet = GrammarLanglet()
        self.nfagenerator = None
        self.langlet.langlet_id = ls_grammar.langlet_id
        self.grammar      = ""

    def set_langlet_id(self, ll_id):
        self.langlet.langlet_id = ll_id

    def create_grammar(self, report = False, expansion = True):
        symobject = SymbolObject(self.langlet.langlet_id)
        R = [' '.join([g[1] for g in R1]).strip() for R1 in self.rules]
        symobject.create(R)
        self.langlet.parse_symbol = self.langlet.symbol = symobject
        self.nfagenerator = NFAGenerator(self.langlet, "Parser")
        self.grammar = "\n".join(R)+"\n"
        # print grammar
        self.nfagenerator.create_all(self.grammar)
        if self.nfagenerator.nfas:
            self.nfagenerator.derive_properties()
            if expansion:
                self.nfagenerator.expand_nfas(report = report)
        self.langlet.parse_nfa = self.nfagenerator.nfadata
        self.langlet.keywords  = self.langlet.parse_nfa.keywords

    def get_nfas(self):
        return self.nfagenerator.nfas

    def get_start_symbol(self):
        return self.nfagenerator.nfadata.start_symbols[0]


    @classmethod
    def grammar_from_rule(cls, grammar_rule, report = False):
        rules = []
        R = ls_grammar.tokenize(grammar_rule)
        rules.append(R)
        names = set()
        strings = set()
        for t in R[2:]:
            if t[0] == ls_grammar.parse_token.NAME:
                names.add(t[1])
            elif t[0] == ls_grammar.parse_token.STRING:
                strings.add(t[1])
        for i,name in enumerate(names):
            n = 1
            k = str(i)*n
            while (name+k in names or "'"+name+k+"'" in strings):
                n+=1
                k = str(i)*n

            rules.append(ls_grammar.tokenize("%s: '%s'"%(name, name+k)))
        go = GrammarObject(rules)
        go.create_grammar(report = report)
        return go


if __name__ == '__main__':
    import pprint
    rules = []
    rules = open("rulefile.txt").readlines()
    for i, rule in enumerate(rules):
        go = GrammarObject.grammar_from_rule(rule)
        pprint.pprint( go.nfagenerator.nfas )
        pprint.pprint( go.get_start_symbol() )
        if i == 0:
            break

