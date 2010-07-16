import random
import string
from langscape.ls_const import*
from langscape.trail.nfatracer import TokenTracer

def random_letter():
    return string.letters[random.randrange(0,27)]

def random_digit():
    return string.digits[random.randrange(0,10)]

def random_hexdigit():
    return string.hexdigits[random.randrange(0,17)]

def random_printable():
    n = len(string.printable)
    return string.printable[random.randrange(0,n)]

def random_name(num_letters):
    return ''.join([random_letter() for i in range(num_letters)])

def random_string(num_chars):
    return '"'+''.join([random_printable() for i in range(num_chars)])+'"'

def random_int(num_digits):
    x = random_digit()
    while x == '0':
        x = random_digit()
    return x + ''.join(random_digit() for i in range(num_digits-1))

def random_float(num_digits):
    k = random.randrange(3)
    if k == 0:
        return "."+random_int(num_digits)
    elif k == 1:
        return random_int(num_digits)+"."
    else:
        j = random.randrange(1, num_digits)
        return random_int(j)+"."+random_int(num_digits-j)

class TokenGenerator(object):
    def __init__(self, langlet, stdlen = 3):
        self.langlet = langlet
        self.stdlen = stdlen
        self.lexer_terminal = langlet.lex_nfa.lexer_terminal

    def gen_token_string(self, nid):
        tracer = TokenTracer(self.langlet, nid, "lex")
        selection = list(tracer.selectables())
        S = []
        while True:
            n = len(selection)
            if selection == [None]:
                return ''.join(S)
            if len(S)>20:
                return self.gen_token_string(nid)
            while True:
                m = random.randrange(0, n)
                t = selection[m]
                if t is None:
                    continue
                try:
                    chars = list(self.lexer_terminal[t])
                except KeyError:
                    return ''
                if not chars:
                    other_chars = reduce(lambda S, T: S.union(T), [self.lexer_terminal.get(r, set()) for r in selection if r!=t])
                    while True:
                        c = random_printable()
                        if c == '\\':
                            continue
                        if c not in other_chars:
                            break
                    S.append(c)
                else:
                    c = chars[random.randrange(0, len(chars))]
                    S.append(c)
                selection = list(tracer.select(t))
                break

            if len(S) >= self.stdlen:
                if None in selection:
                    if S[0] in ('"', "'"):
                        if len(S)>=4:
                            return ''.join(S)
                    if S[0] in string.digits:
                        if len(S)>=4:
                            return ''.join(S)
                    if random.randrange(0,2) == 0:
                        return ''.join(S)

if __name__ == '__main__':
    import langscape
    from langscape.trail.nfatracer import TokenTracer
    python = langscape.load_langlet("python")
    tracer = TokenTracer(python, python.lex_symbol.Single3, "lex")

    tokgen = TokenGenerator(python)
    for i in range(1000):
        s = tokgen.gen_token_string(python.lex_symbol.NAME)
        print s
        #print "NUM", "%-8s %s"%(s, eval(s))





