import warnings
import sys
from   langscape.trail.nfatracer import NFATracerUnexpanded
from   langscape.csttools.cstutil import*

# Warnings

class GrammarConformanceWarning(Warning): pass

warnings.simplefilter("always",GrammarConformanceWarning)

error_msg = "<====  No grammar conformance!\n\n  ---->  Expected node(s): %s"
error_msg_terminal = "<====  No grammar conformance! More nodes required. Expected node(s): %s"

# NodeChecker

class NodeChecker(object):
    def __init__(self, langlet):
        self.langlet = langlet

    def run(self, node, **kwd):
        if not self.check_node(node):
            self.langlet.pprint(node)

            warnings.warn_explicit("CST doesn't match target langlet grammar.", GrammarConformanceWarning, "csttools.py", lineno = sys._getframe(0).f_lineno)
            return False
        return True

    def check_node(self, node, nid = None, tracer = None):
        if nid is None:
            nid = node[0]
        if tracer is None:
            tracer = NFATracerUnexpanded(self.langlet.parse_nfa)
        try:
            selection = tracer.select(nid)
        except NonSelectableError:
            selection = ["Node(s) of target langlet '%s'"%self.langlet.config.langlet_name]
            self.annotate_error_node(node, [], error_msg, selection)
        for sub in node[1:]:
            sub_nid = sub[0]
            if isinstance(sub, list):
                if sub_nid in selection:
                    if is_symbol(sub_nid):
                        new_tracer = NFATracerUnexpanded(self.langlet.parse_nfa)
                        rc = self.check_node(sub, nid = sub_nid, tracer = new_tracer)
                        if rc is False:
                            return False
                    selection = tracer.select(sub_nid)
                else:
                    self.annotate_error_node(node, sub, error_msg, selection)
                    return False
        if None not in selection:
            self.annotate_error_node(node, sub, error_msg_terminal, selection)
            return False
        return True

    def annotate_error_node(self, node, sub, msg, selection):
        select_txt = "{ "
        for s in selection:
            if isinstance(s, int):
                name = self.langlet.get_node_name(s)
                if is_token(s):
                    select_txt+="\n                "+name+" -- T'%d"%s
                else:
                    select_txt+="\n                "+name+" -- NT'%d"%s
            else:
                select_txt+="%s, "%s
        msg = msg%select_txt[:-2]+" \n        }\n"
        if isinstance(sub, cstnode):
            sub.msg = msg
        elif isinstance(sub, list):
            n = cstnode(sub)
            n.msg = msg
            sid = id(sub)
            for i,item in enumerate(node):
                if id(item) == sid:
                    node[i] = n
                    break
        elif isinstance(node[-1], cstnode):
            node[-1] = cstnode(node[-1])
            node[-1].msg = msg
        else:
            raise TypeError("Cannot annotate object of type '%s'"%type(sub))



