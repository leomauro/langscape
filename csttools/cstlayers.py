'''
Layers
------

We say R1 refers to R2 or R1 -> R2, if R2 is on the rhs of R1.

Let us successively split the set of available nodes into disjoints sets L1, L2 with:

    For each R1 in L1 there is an R2 in L2 with R1 -> R2, but there is no R2 in L2 with
    R2 -> R1, for all R1 in L1.

We also write L1 => L2.

The algorithm implemented in this module determines a sequence of node sets
(L0, L1,..., Lk) with ::

    L0 => L1 => ... => Lk

The Li sets are our *layers*. A layer can be flat or contain circles i.e. sequences of nodes ::

    R1 => R2 => ... => Rk => R1

Purpose of building layers ::

    layers can be used to optimize search processes. We do not have to seek for a node M as
    a subnode of N, if Layer(M) => Layer(N).

'''

from langscape.csttools.cstutil import is_token

def create_referrer(symbols):
    '''
    The referrer is a dictionary
    '''
    referrer = {}
    for r, sym in symbols.items():
        for s in sym:
            if is_token(s):
                continue
            R = referrer.get(s,set())
            R.add(r)
            referrer[s] = R
    return referrer

def create_toplevel(rules, referrer, layer):
    top = set()
    for r in rules:
        S = referrer.get(r, set([]))
        if len(S) == 0:
            top.add(r)
    for t in top:
        rules.remove(t)
    layer.append(top) if top else None
    return top

def clean_up(top, referrer):
    snd_layer_candidates = set()
    for r in list(referrer):
        for s in top:
            if s in referrer[r]:
                referrer[r].remove(s)
                if r not in top:
                    snd_layer_candidates.add(r)
        if not referrer[r] and r in top:
            del referrer[r]
    # pprint.pprint(referrer)
    return snd_layer_candidates

def detect_circle(referrer, c, trace = []):
    R = referrer[c]
    for r in R:
        # circle detected
        if r in trace:
            return r
        else:
            C = detect_circle(referrer, r, trace+[c])
            if C:
                return C

def span(referrer, c, S):
    S.add(c)
    R = referrer[c]
    for r in R:
        if r not in S:
            S = span(referrer, r, S)
    return S


def layers(nfamod):
    '''
    Creates a layer hierarchy
    '''
    symbols  = {}
    symbols.update(nfamod.symbols_of)
    referrer = create_referrer(symbols)

    layer    = []
    rules    = symbols.keys()
    top = create_toplevel(rules, referrer, layer)

    while True:
        while top:
            snd_layer_candidates = clean_up(top, referrer)
            top = create_toplevel(snd_layer_candidates, referrer, layer)
        for c in snd_layer_candidates:
            p = detect_circle(referrer, c)
            if p:
                top = span(referrer, p,set())
                layer.append(top)
                # print "TOP", top
                break
        else:
            if referrer:
                snd_layer_candidates = set([referrer.keys()[0]])
            else:
                break
    d_layer = {}
    referrer = create_referrer(symbols)
    for S in layer:
        R = set()
        for s in S:
            R.update(referrer.get(s, set()))
        if len(R) == 0:
            for s in S:
                d_layer[s] = 0
        else:
            k = max(d_layer.get(r,0) for r in R)+1
            for s in S:
                d_layer[s] = k
    return d_layer


if __name__ == '__main__':
    import pprint
    import langscape.langlets.python.parsedef.parse_nfa as parse_nfa

    pprint.pprint(layers(parse_nfa))


