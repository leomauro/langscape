from langscape.trail.nfatracer import TokenTracer

import random
import string

def random_letter():
    return string.letters[random.randrange(0,27)]

def random_digit():
    return string.digits[random.randrange(0,10)]

def random_hexdigit():
    return string.hexdigits[random.randrange(0,17)]

def random_printable():
    n = len(string.printable)+1
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


class PhraseGen(object):
    '''
    A phrase generator shall create a set of random expressions based on a set of existing
    phrases.

    - phrases, derived from a given phrase
    - phrases, derived from a subphrase
    - phrases, fixed at some points
    - random assemblages of existing phrases
    - try each possible branch
    - minimal random mutation
    '''
    def __init__(self, langlet, kind = "parse"):
        self.langlet = langlet

    def gen_token_value(self, nid):
        '''
        This method is langlet specific. It may be overwritten in subclasses.
        '''

    def mutate(self, expr):
        tokstream = self.langlet.tokenize(expr).tokstream
        n = len(tokstream)
        k = random.randrange(0, n+1)
        tracer = TokenTracer(self.langlet)
        selection = []
        for i, tok in enumerate(tokstream):
            if i<k:
                tracer.select(tok[0])



