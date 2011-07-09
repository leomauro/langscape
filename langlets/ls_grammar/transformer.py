###############  langlet transformer definition ##################

import pprint
from langlet_config import parent_langlet
from langscape.base.loader import BaseClass
from langscape.csttools.cstutil import*
from langscape.csttools.cstsearch import*
from langscape.base.transformer import transform, transform_dbg, t_dbg

from rules import*

class LangletTransformer(BaseClass("Transformer", parent_langlet)):
    '''
    Defines langlet specific CST transformations.
    '''
    def __init__(self, *args, **kwd):
        super(LangletTransformer, self).__init__(*args, **kwd)
        self.rules = {}
        self.cnt     = 0
        self.nullidx = 0

    @transform
    def rule(self, node):
        "rule: NAME ':' rhs NEWLINE"
        self.cnt     = 0
        self.nullidx = 0
        rule_name = find_node(node, self.token.NAME)[1]
        rhs = self.rhs(find_node(node, self.symbol.rhs))
        if isinstance(rhs, SequenceRule):
            rhs.lst.append(ConstRule([(FIN, FEX)]))
        else:
            rhs = SequenceRule([rhs, ConstRule([(FIN, FEX)])])
        self.rules[rule_name] = (Rule([(rule_name, 0), rhs]), self.langlet.unparse(node))

    def rhs(self, node):
        "rhs: alt ( '|' alt )*"
        altnodes = [self.alt(N) for N in find_all(node, self.symbol.alt, depth=1)]
        if len(altnodes)>1:
            return AltRule(altnodes)
        else:
            return altnodes[0]

    def alt(self, node):
        "alt: item+"
        items = [self.item(it) for it in find_all(node, self.symbol.item, depth=1)]
        if len(items)>1:
            return SequenceRule(items)
        else:
            return items[0]


    def item(self, node):
        "item: '[' rhs ']' | atom [ '*' | '+' ]"
        rhs = find_node(node, self.symbol.rhs, depth = 1)
        if rhs:
            self.nullidx+=1
            return AltRule([EmptyRule([(FIN, self.nullidx)]), self.rhs(rhs)])
        else:
            atom = self.atom(find_node(node, self.symbol.atom))
            if find_node(node, self.token.STAR, depth=1):
                self.nullidx+=1
                return AltRule([EmptyRule([(FIN, self.nullidx)]), atom, SequenceRule([atom, atom])])
            elif find_node(node, self.token.PLUS, depth=1):
                return AltRule([atom, SequenceRule([atom, atom])])
            else:
                return atom

    def atom(self, node):
        "atom: '(' rhs ')' | NAME | STRING"
        rhs = find_node(node, self.symbol.rhs, depth=1)
        if rhs:
            return self.rhs(rhs)
        else:
            self.cnt+=1
            item = node[1][1]
            return ConstRule([(item, self.cnt)])

__superglobal__ = []
