import langscape
import random

from langscape.csttools.cstutil import*
from langscape.sourcetools.tokgen import TokenGenerator
from langscape.trail.tokentracer import TokenTracer

ls_grammar = langscape.load_langlet("ls_grammar")


def random_rule(stoplen):
    # some rules to constrain 'interesting' cases
    #
    # 1. Avoid double parens (( ... )) or double square braces [[ ... ]]
    # 2. Avoid use of STRING
    # 3. Avoid sequences of NAME longer than 2 i.e. NAME NAME NAME
    trace = []
    ttracer = TokenTracer(ls_grammar, start = ls_grammar.symbol.rhs)
    STRING = ls_grammar.token.STRING
    NAME   = ls_grammar.token.NAME
    LPAR   = ls_grammar.token.LPAR
    RPAR   = ls_grammar.token.RPAR
    LSQB   = ls_grammar.token.LSQB
    RSQB   = ls_grammar.token.RSQB

    selection = list(ttracer.selectables())

    while True:
        # print len(trace), selection
        if len(trace)>stoplen:
            if None in selection:
                return trace
            elif RSQB in selection:
                trace.append(RSQB)
                selection = ttracer.select(RSQB)
                continue
            elif RPAR in selection:
                trace.append(RPAR)
                selection = ttracer.select(RPAR)
                continue
        while selection:
            k = random.randrange(len(selection))
            item = selection[k]
            selection.remove(item)
            if item is None:
                continue
            if item == STRING:
                continue
            elif item in (NAME, LPAR, LSQB):
                if len(trace)>=2:
                    if trace[-1] == trace[-2] == item:
                        continue
                    if item in (LPAR, LSQB):
                        if trace[-2] in (LPAR, LSQB) and trace[-1] in (LPAR, LSQB):
                            continue

            elif item in (RSQB, RPAR):
                if trace and trace[-1] == item:
                    if item == RSQB:
                        LEFT = LSQB
                    else:
                        LEFT = LPAR
                    RIGHT = item
                    m = len(trace)-2
                    double = False
                    level = -2
                    while m:
                        if trace[m] == RIGHT:
                            level-=1
                        elif trace[m] == LEFT:
                            level+=1
                        if level == 0:
                            if trace[m+1] == LEFT:
                                double = True
                            break
                        m-=1
                    if double:
                        continue
            trace.append(item)
            selection = list(ttracer.select(item))
            break

def get_token_string(langlet, nid):
    if is_keyword(nid):
        return langlet.keywords[nid]
    if nid+SYMBOL_OFFSET in langlet.lex_nfa.constants:
        return langlet.lex_nfa.constants[nid+SYMBOL_OFFSET]
    else:
        return langlet.get_node_name(nid)

if __name__ == '__main__':

    f = open("rulefile.txt", "w")
    for i in range(10000):
        s_rule_token = [get_token_string(ls_grammar, nid) for nid in random_rule(25)]
        j = 0
        for i, item in enumerate(s_rule_token):
            if item == 'NAME':
                c = "abcdefghijkl"[j%12]
                s_rule_token[i] = c
                j+=1
        print >> f, "R: "+" ".join(s_rule_token)

