import warnings
import sys
from langscape.trail.nfatracer import NFATracerUnexpanded
from langscape.csttools.cstutil import*
from langscape.csttools.cstsearch import find_token_gen, find_node

# Warnings

class GrammarConformanceWarning(Warning): pass

warnings.simplefilter("always", GrammarConformanceWarning)

# NodeChecker

class NodeChecker(object):
    def __init__(self, langlet):
        self.langlet = langlet
        self._error  = None

    def check_node(self, node, **kwd):
        self._error = None
        rc = self._check_node(node)
        if rc == False:
            self.print_error_msg()
        return rc


    def _check_node(self, node, tracer = None):
        nid = node[0]
        if tracer is None:
            tracer = NFATracerUnexpanded(self.langlet.parse_nfa)
        try:
            selection = tracer.select(nid)
        except NonSelectableError:
            self._error = (node, 0, [])
            return False

        for i, sub in enumerate(node[1:]):
            sub_nid = sub[0]
            if isinstance(sub, list):
                if sub_nid in selection:
                    if is_symbol(sub_nid):
                        rc = self._check_node(sub, tracer = NFATracerUnexpanded(self.langlet.parse_nfa))
                        if rc is False:
                            if self._error:
                                _, pos, _ = self._error
                                if pos == 0:
                                    self._error = (node, i+1, selection)
                            return False

                    selection = tracer.select(sub_nid)
                else:
                    self._error = (node, i+1, selection)
                    return False
        if None not in selection:
            self._error = (node, len(node)+1, selection)
            return False
        return True

    # error display methods

    def get_text(self, node):
        try:
            text = self.langlet.unparse(node)
            k = text.find("\n")
            if k>0:
                text = text[:k+1].replace("\n", '\\n')
        except Exception:
            text = "??? -- Could not unparse node."
        return "'"+text+"'"

    def nid_to_text(self, nid):
        llid, S = divmod(nid, LANGLET_ID_OFFSET)
        name = self.langlet.get_node_name(nid)
        if is_symbol(nid):
            return name+"  -- NT`%d.%d"%(llid, S)
        else:
            return name+"  -- T`%d.%d"%(llid, S)

    def get_line_info(self, node):
        token_gen = find_token_gen(node)
        tok = token_gen.next()
        return (tok[2], tok[3][0])

    def format_node(self, node, k):
        snode  = []
        indent = " "*2
        S = indent+"%-52s # %s"
        name = self.nid_to_text(node[0])
        snode.append(S%(name+" at (L`%s, C`%s)"%self.get_line_info(node), self.get_text(node)))
        if k == 0:
            snode.append(indent+"~"*len(name)+"\n")
        indent = " "*4
        for i, sub in enumerate(node[1:]):
            S = indent+"%-50s # %s"
            name = self.nid_to_text(sub[0])
            snode.append(S%(name+" at (L`%s, C`%s)"%self.get_line_info(sub), self.get_text(sub)))
            if i+1 == k:
                snode.append(indent+"~"*len(name))
        if k>len(node):
            snode.append(indent+"None")
            snode.append(indent+"~~~~")
        return "\n".join(snode)

    def format_selection(self, selection):
        symbols = []
        llid    = self.langlet.langlet_id/LANGLET_ID_OFFSET
        for s in selection:
            if s is None:
                symbols.append("None")
            else:
                symbols.append("(%d.%s, %s)"%(llid, s, self.langlet.get_node_name(s)))
        s = ["One of the following symbols must be used:\n"]
        indent = " "*2
        if symbols:
            for S in symbols:
                s.append(indent+S)
            return "\n".join(s)+"\n"
        return ""

    def print_error_msg(self):

        warnings.warn_explicit("CST doesn't match grammar of target langlet.", GrammarConformanceWarning, "langscape.csttools.cstcheck", lineno = sys._getframe(0).f_lineno)
        node, idx, selection = self._error
        print
        print self.format_node(node, idx)
        print
        print self.format_selection(selection)

if __name__ == '__main__':
    import langscape
    langlet = langscape.load_langlet("python")
    cst = langlet.parse("def foo(x, y):\n  print 89\n  print 'a'")
    print_stmt = find_node(cst, langlet.symbol.print_stmt)
    print_stmt[0]+=3
    nc = NodeChecker(langlet)
    nc.check_node(cst)



