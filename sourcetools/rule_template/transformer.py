###############  langlet transformer definition ##################

from langlet_config import parent_langlet
from langscape.base.loader import BaseClass
from langscape.csttools.cstutil import*
from langscape.csttools.cstsearch import*
from langscape.base.transformer import transform, transform_dbg, t_dbg

class LangletTransformer(BaseClass("Transformer", parent_langlet)):
    '''
    Defines langlet specific CST transformations.
    '''
    def __init__(self, *args, **kwd):
        super(LangletTransformer, self).__init__(*args, **kwd)

    @transform
    def repeated(self, node):
        s = self.langlet.unparse(node).strip()[1:-1]
        n0 = 0
        n1 = 0
        if str.isdigit(s):
            n0 = int(s)
            n1 = n0
        else:
            f1, f2 = s.split(",")
            if f1:
                n0 = int(f1)
            else:
                n0 = 0
            if f2:
                n1 = int(f2)
            else:
                n1 = 0
        chain = self.node_stack(node)
        item, _ = chain.step()
        atom = find_node(item, self.symbol.atom)
        satom = self.langlet.unparse(atom)
        if n0 == n1:
            return self.langlet.parse("("+" ".join([satom]*n0) + ")", start_symbol = self.symbol.item)
        elif n1 == 0:  # min = n0, max = infinity
            return self.langlet.parse("("+" ".join([satom]*n0) + " "+satom+"*"+")", start_symbol = self.symbol.item)
        elif n1>n0:
            return self.langlet.parse("("+" ".join([satom]*n0) + " "+("["+satom+"]")*(n1-n0)+")", start_symbol = self.symbol.item)
        else:
            raise SyntaxError("Bad repeat interval: {"+s+"}")

    @transform
    def variable(self, node):
        dest, varname = find_all(node, self.token.NAME)
        self.langlet.variables[varname[1]] = dest[1]
        return self.langlet.fn.atom(varname)


__superglobal__ = []
