# Module used to translate a BNF grammar into an EBNF grammar using
# left recusion elimination

__all__ = ["convertbnf", "eliminate_left_recursion"]

import pprint
import langscape
from langscape.csttools.cstsearch import find_node, find_all
from langscape.csttools.cstutil import*
from langscape.trail.nfagen import NFAGenerator
from langscape.trail.nfa2grammar import NFA2GrammarTranslator
from langscape.base.grammar_gen import SymbolObject
from langscape.util import flip

bnfreader  = langscape.load_langlet("bnfreader")
ls_grammar = langscape.load_langlet("ls_grammar")

def transform_recursion(nfa, state = None):
    '''
    :param nfa: NFA containing ``state``.
    :param state: state of kind (S,..., T) where S is the nid of the nfa.

    Description ::
        Let L be the state passed to this function.

        1) We map L using ShiftNested: (S, idx, T) -> (S, '(', idx, T)
        2) We replace L by ShiftNested(L) in the NFA. If A -> [L, X, Y, ...] is a transition we collect
           X, Y, ... within a separate list called Cont.
        3) Replace (FIN, '-', S) by (S, ')', IDX, S) on each occurence.
        4) Add the following transition:
           (S, ')', IDX, S) -> [(FIN, '-', S)]+Cont
    '''
    trans = nfa[2]
    nid   = nfa[1][0]
    # if (CLOSING, '?', nid) in trans:
    #    return
    if state is None:
        for L in trans:
            if L[0] == nid:
                if L[1] == '(':
                    return # recusion eliminated
                elif L[1] != 0:
                    state = L
                    break
        else:
            raise RuntimeError("No recursion to eliminate in rule `%s`"%self.node_name(nid))
    # assert state[0] == S, "Unable to embedd state: %s %s"%(state, S)
    LEFT    = (nid, '(', state[1], state[2])
    RIGHT   = (nid, ')', state[1], state[2])
    EXIT    = (FIN, '-', nid)
    CONT    = trans[state][:]
    FIRST   = trans[nfa[1]]
    # print "TRANSIT", state, transit
    # print "...................."
    if not EXIT in CONT:
        CONT.append(EXIT)
    del trans[state]
    trans[LEFT] = FIRST
    for follow in trans.values():
        if state in follow:
            follow.remove(state)
            follow.append(LEFT)
        if EXIT in follow:
            follow.remove(EXIT)
            follow.append(RIGHT)
    trans[RIGHT] = CONT


def eliminate_left_recursion(nfa):
    '''
    Eliminates A in rules of the form ::

        A: A x ... | B
    '''
    trans = nfa[2]
    start = nfa[1]
    nid   = nfa[1][0]

    while True:
        first_follow = trans[start]
        for f in first_follow:
            if f[0] == nid:
                LEFT = (f[0],"(",f[1], f[2])
                RIGHT = (f[0],")",f[1], f[2])
                transform_recursion(nfa, f)
                break
        else:
            return
        # remove LEFT
        del trans[LEFT]
        first_follow.remove(LEFT)
        # subst right
        rest = trans[RIGHT]
        del trans[RIGHT]
        for follow in trans.values():
            if RIGHT in follow:
                follow.remove(RIGHT)
                follow.extend(rest)


class LangletObject(object):
    '''
    This defines a minimal langlet. It contains just enough attributes for the NFA2GrammarTranslator.
    '''
    def __init__(self, langlet_id, symbol_obj, lexer_obj):
        self.parse_token    = self.token  = lexer_obj
        self.parse_symbol   = self.symbol = symbol_obj
        self.langlet_id     = langlet_id
        self.nfas           = {}
        self.keywords       = {}

class NFA2GrammarLangletObjTranslator(NFA2GrammarTranslator):
    def __init__(self, langlet, constants):
        self.langlet   = langlet
        self.constants = constants
        self.keywords  = flip(langlet.keywords)
        self.token_map = flip(langlet.parse_token.token_map)
        self.names     = langlet.parse_symbol.sym_name
        self.names.update(langlet.parse_token.tok_name)
        super(NFA2GrammarLangletObjTranslator, self).__init__(langlet)

    def get_constants(self):
        return  {} # self.langlet.nfagenerator.nfadata.constants

    def get_node_name(self, nid):
        #print "NID", nid, is_keyword(nid)
        if nid in self.keywords:
            return self.keywords[nid]
        name = self.names.get(nid, "???")
        if is_token(nid):
            if nid in self.token_map:
                value = self.token_map[nid]
                for c in value:
                    if c.isalnum():
                        return name
                return "'"+value+"'"
        return name

def create_bnf_langlet(bnf_grammar_file, lexer_file):
    '''
    Construct an ad-hoc langlet from a BNF grammar file.
    '''
    # parser-rules
    cst = bnfreader.parse_file(bnf_grammar_file)
    parser_rules = []
    # do some normalization of rules of the grammar file
    for rule in find_all(cst, bnfreader.symbol.rule):
        ls_rule = " ".join(bnfreader.unparse(rule)[:-1].split())+"\n"
        parser_rules.append(ls_rule)
    bnf_grammar  = "".join(parser_rules)
    langlet_id   = 1000*100
    parse_symbol = SymbolObject(langlet_id)
    parse_symbol.create(parser_rules)

    # lexer-rules
    with open(lexer_file) as f_lex:
        lexer_rules = ls_grammar.unparse(ls_grammar.parse(f_lex.read())).split("\n")
    lex_symbol  = SymbolObject(langlet_id, 100)
    lex_symbol.create(lexer_rules)
    # create NFAs but don't compute properties. This won't work because
    # left recursion prevents first-sets ( reachables ) to be derived.
    langlet = LangletObject(langlet_id, parse_symbol, lex_symbol)
    nfagen  = NFAGenerator(langlet)
    nfas    = nfagen.create_all(bnf_grammar)
    langlet.nfas = nfas
    langlet.keywords = nfagen.keywords
    return langlet


def convertbnf(bnf_grammar_file, lexer_file):
    langlet    = create_bnf_langlet(bnf_grammar_file, lexer_file)
    translator = NFA2GrammarLangletObjTranslator(langlet, {})
    rules = []
    for i, (r, nfa) in enumerate(sorted(langlet.nfas.items())):
        eliminate_left_recursion(nfa)
        #pprint.pprint(nfa)
        rules.append(translator.translate(nfa))
        #pprint.pprint(nfa)
        #break
    return "\n".join(sorted(rules)[::-1])




