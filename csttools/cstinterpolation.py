# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <kay@fiber-space.de>
# Date:    2009-17-10
#--------------------------------------------------------------------------------------


# TODO: implementation is incomplete. Finish or perish.
#

import pprint

class CSTInterpolation(object):
    def __init__(self, langlet):
        self.langlet = langlet

    def interpolate(self, nid, *args):
        # turn arguments into proper nodes
        nodes = []
        nids  = set()
        seg_nid = {}
        for arg in args:
            if isinstance(arg, str):
                node = self.langlet.tokenize(arg)[0]
                nids.add(node[0])
                seg_nid[node[0]] = set([node[0]])
                nodes.append(node)
            else:
                nodes.append(arg)
                nids.add(arg[0])
                seg_nid[arg[0]] = set([arg[0]])
        segments = self.langlet.segments
        for r, (table, seglist) in segments.items():
            for n in nids:
                if n in table:
                    seg_nid[n].add(r)
        R = []
        table, seglist = segments[nid]
        for r, Symbols in self.langlet.parse_nfa.symbols_of.items():
            for S in seg_nid.values():
                D = Symbols & S
                if not D:
                    break
            else:
                if r in table:
                    R.append(r)
        return [self.langlet.get_node_name(r) for r in R]


if __name__ == '__main__':
    import langscape
    from cstsearch import*

    langlet = langscape.load_langlet("python")
    st = langlet.parse("1+a\n")
    a1, a2 = find_all(st, langlet.parse_symbol.atom)
    interpolator = CSTInterpolation(langlet)
    pprint.pprint( interpolator.interpolate(langlet.parse_symbol.stmt, a1, ';', a2) )



