# -*- coding: UTF-8 -*-

import langscape.util.unittest as unittest
from langscape.trail.tokentracer import TokenTracer
from langscape.ls_const import*


E    = 1001
PLUS = 3
MUL  = 2
a    = 1

class obj(object):pass

langlet = obj()
langlet.parse_nfa = obj()
langlet.parse_nfa.nfas = {}
langlet.parse_nfa.expanded = {}
langlet.parse_nfa.start_symbols = (E,)


nfa_E = ["E: a '+' E | a '*' E | 'a'",
    (E,0,E),
    {(E,0,E):[(a,1,E),(a,2,E),(a,3,E)],
     (a,1,E):[(PLUS,4,E)],
     (a,2,E):[(MUL,5,E)],
     (PLUS,4,E):[(E,6,E)],
     (MUL,5,E):[(E,7,E)],
     (a,3,E):[(FIN, FEX, E)],
     (E,6,E):[(FIN, FEX,E)],
     (E,7,E):[(FIN, FEX,E)]}]

nfa_E2 = ["E: a E",
    (E,0,E),
    {(E,0,E):[(a,1,E)],
     (a,1,E):[(E,2,E)],
     (E,2,E):[(FIN, FEX,E)]}]

langlet.parse_nfa.nfas[E] = nfa_E2

tt = TokenTracer(langlet)
tt.selectables()
tt.select(1)
tt.select(1)
tt.select(1)
tt.select(1)
tt.select(1)

