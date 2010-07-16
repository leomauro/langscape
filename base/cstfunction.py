__all__ = ["CSTFunctionBase"]

import langscape.base.loader
from langscape.csttools.cstsearch import find_node, find_token_gen

class CSTFunction(object):
    def __init__(self, langlet):
        self.langlet = langlet
        self.__dict__.update(langscape.base.loader.load_cstbuilder(langlet.config.langlet_name))

    def split(self, node):
        '''
        Let N = build_a(N1, N2, ..., Nk) = [a, N1, N2, ..., Nk], then

        split(N) = [build_a(n) for n in N[1:] if n!=NEWLINE and n!=ENDMARKER]

        If build_a(Ni) fails to create a value for one i, then N is returned.
        '''
        if len(node)<=2:
            return [node]
        nid = node[0]
        name = self.langlet.get_node_name(nid)
        nd_builder = getattr(self, name)
        parts = []
        for item in node[1:]:
            try:
                parts.append(nd_builder(item))
            except Exception, e:
                if self.langlet.unparse(item).strip() !="":
                    raise
                else:
                    return [node]
        return parts

    def map(self, node, target_symbol):
        '''
        If N = build_a(N1, N2, ..., Nk) then ::

            map(N, b) = build_b(N1, ..., Nk)
        '''
        name = self.langlet.get_node_name(target_symbol)
        nd_builder = getattr(self, name)
        return nd_builder(*node[1:])

    def fit(self, node, target_symbol):
        '''
        Attempts to fit node to target_symbol.

        First try to v-interpolate node using target_symbol. If this fails try to
        find subnode of type target_symbol in node. If both attempts fail raise an exception.
        '''
        name = self.langlet.get_node_name(target_symbol)
        nd_builder = getattr(self, name)
        try:
            return nd_builder(node)
        except Exception, e:
            nd = find_node(node, target_symbol)
            if nd is None:
                raise

    def normalize(self, node, A_symbol, Z_symbol):
        A_node = find_node(node, A_symbol)
        if A_node:
            Z_builder = self.langlet.get_node_builder(Z_symbol)
            Z_node = Z_builder(A_node)
            nd_builder = self.langlet.get_node_builder(node[0])
            return nd_builder(Z_node)
        else:
            raise ValueError("Subnode of type '%s' could not be found"% self.langlet.get_node_name(A_symbol))

    def match_token_seq(self, node, token_seq):
        token_seq = token_seq[::-1]
        gen = find_token_gen(node)
        while token_seq:
            s = token_seq.pop()
            try:
                t = gen.next()
            except StopIteration:
                return False
            if t[1] != s:
                return False
        return True





