from cstutil import*
import cstrepr
import cstsearch
import cstsegments
import langscape.trail.nfatools as nfatools
from langscape.util import flip
import sys

__all__ = ["CSTBuilder"]

def shallow_lift(args, langlet_id):
    for arg in args:
        if type(arg) == list:
            arg[0] = arg[0]%LANGLET_ID_OFFSET + langlet_id


class CSTBuilder(object):
    def __init__(self, langlet):
        langlet._load_parse_tables()
        self.NFATracer = nfatools.NFATracerUnexpanded
        self.langlet   = langlet
        self.nfas      = langlet.parse_nfa.nfas
        self.lnlt_id   = langlet.parse_nfa.LANGLET_ID
        self.segments  = cstsegments.SegmentTree(langlet)
        self.token     = langlet.parse_token
        self.symbol    = langlet.parse_symbol
        self.keywords  = langlet.parse_nfa.keywords
        self.create_constant_token(langlet.lex_nfa.constants)
        self.segments.create()

    def create_constant_token(self, constants):
        self.constants = {}
        for r, value in constants.items():
            self.constants[r-SYMBOL_OFFSET] = (r-SYMBOL_OFFSET, value)

    def to_token(self, item):
        if type(item) == str:
            return self.langlet.tokenize(item)[0]
        else:
            return item

    def build_segment(self, segment, node):
        start = segment[0]
        node = self.to_token(node)
        if segment == []:
            raise ValueError("Cannot build node '%s' from node '%s'"%(self.langlet.get_node_name(start),self.langlet.get_node_name(node[0])))
        nid = node[0]
        for item in segment[::-1]:
            if nid == item:
                res = node
            elif type(item) == int:
                if res:
                    if type(res[0]) == int:
                        res = [item, res]
                    else:
                        res = [item]+res
                else:
                    res.append(item)
            else:
                S = []
                for r in item:
                    if is_token(r):
                        S.append(list(self.constants[r]))
                    elif r == nid:
                        S.append(node)
                    else:
                        S.append([r, res])
                res = S
        return res


    def builder(self, nid, name, doc):
        '''
        Generic CST builder function.
        '''
        def cstbuilder(*args):
            # shallow_lift(args, self.lnlt_id)
            return self.build_cst(nid, *args)

        cstbuilder.__doc__ = doc
        cstbuilder.__name__= name
        return cstbuilder

    def factory(self, indent=16, target=sys.stdout):
        funcs = {}
        for name in dir(self.symbol):
            val = getattr(self.symbol, name)
            if isinstance(val, int):
                doc = self.langlet.parse_nfa.nfas[val][0]
                print >> target, ("    %%-%d"%indent+"s = cstbuilder.builder(%s, '%s', \"%s\")")%(name, val, name, doc)


    def completion(self, nodelist, item, expected, track_data):
        if type(item) == str:
            if item in expected:
                node = self.langlet.tokenize(item)[0]
                nodelist.append(node)
                return (item, None)
            else:
                node = self.langlet.tokenize(item)[0]
        elif isinstance(item, list):
            node = item
        else:
            node = self.langlet.tokenize(str(item))[0]
        nid = node[0]
        if nid in expected:
            nodelist.append(node)
            return (nid, None)
        else:
            if len(expected) == 2 and None in expected:
                if expected[0] is None:
                    expected = (expected[1],)
                else:
                    expected = (expected[0],)
            # try keyword  ( TBD )
            if len(expected) == 1 and is_keyword(expected[0]):
                nodelist.append([expected[0],self.langlet.keywords[expected[0]]])
                return (expected[0], item)

            # try vertical interpolation
            S = set()
            for s in expected:
                segment = self.segments[s:nid]
                if segment:
                    nodelist.append(self.build_segment(segment, node))
                    return (s, None)
                S.add(s)

            # try constant extension
            const = [self.constants[r] for r in expected if r in self.constants]
            if len(const) == 1:
                nodelist.append(list(const[0]))
                return (const[0][0], item)

            # error
            target = self.langlet.get_node_name(nodelist[0])
            n = len(nodelist)
            if track_data:
                n-=track_data["cnt"]
                expected = track_data["expected"]
            rule = getattr(self.langlet.fn, target).__doc__
            if nid == -1:
                names = ', '.join(["'"+self.langlet.get_node_name(item)+"'" for item in expected if item!=None])
                raise ValueError("Not enough arguments to build rule '%s'. "
                                 "Expected rule(s) at position %i are: "%(target, n)+names+ \
                                 ".\n\nSee also rule:\n\n    %s"%rule)
            else:
                # print "EXPECTED", expected
                insert = self.langlet.get_node_name(item[0])
                names = ', '.join(["'"+self.langlet.get_node_name(s)+"'" for s in expected if s!=None])
                raise ValueError("Cannot insert node of type '%s' (%s)"
                                 " at position %i in node '%s' (%s).\n"
                                 "            Expected rule(s) at position %i are: %s"%(insert, item[0], n, target, nodelist[0], n, names)+ \
                                 "\n\nSee also rule:\n\n    %s"%rule)


    def build_cst(self, nid, *args):
        tree = [nid]
        tracer = self.NFATracer(self.langlet.parse_nfa)
        s = nid
        it = iter(args)
        track_data = {}
        try:
            arg = it.next()
            while True:
                expected = tracer.select(s)
                try:
                    (s, arg) = self.completion(tree, arg, expected, track_data)
                except Exception, e:
                    if len(args) == 1 and arg[0] == nid:
                        return arg
                    else:
                        raise
                if arg is None:
                    arg = it.next()
                    track_data = {}
                else:
                    if not track_data:
                        track_data = {"expected": expected, "cnt": 1}
                    else:
                        track_data["cnt"]+=1
        except StopIteration:
            while True:
                expected = tracer.select(s)
                if None in expected:
                    return tree
                else:
                    last_set = self.langlet.parse_nfa.last_set[nid]
                    S = [s for s in expected if s in last_set]
                    if S:
                        (s, arg) = self.completion(tree, [-1], S, {})
                    else:
                        (s, arg) = self.completion(tree, [-1], expected, {})




if __name__ == '__main__':
    import langscape
    import pprint
    python = langscape.load_langlet("python")
    symbol = python.parse_symbol
    builder = CSTBuilder(python)
    from cstsearch import*

    #python.pprint( builder.build_cst(symbol.simple_stmt, a1[0], ';', a1[0]) )

    p4d  = langscape.load_langlet("p4d")
    st = p4d.parse("1+a\n")
    '''
    a1 = find_node(st, p4d.parse_symbol.atom)

    for simple_stmt in find_all(p4d.transform(p4d.parse("elm x:\n y\n")), python.parse_symbol.simple_stmt):
        print python.unparse(simple_stmt)
        python.check_node(simple_stmt)
        for n in simple_stmt[1:]:
            print "%-6s"%n[0], python.get_node_name(n[0])
        print "--------------"
    ND = p4d.fn.del_stmt(a1)
    p4d.pprint(ND)
    #S = python.projection(ND)
    p4d.check_node(ND)

    p4d.fn.lambdef(p4d.fn.varargslist("x", ",", "y"), "y")
    p4d.fn.or_test("x", "y")
    p4d.fn.atom("(", "foo", ")")
    '''
    tl = find_node(st, p4d.symbol.testlist)
    p4d.fn.atomize(tl)






