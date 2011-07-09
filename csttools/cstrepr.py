#! /usr/bin/env python
#
# URL:      http://www.fiber-space.de
# Author:   Kay Schluehr <kay@fiber-space.de>
# Creation: 17 Oct 2009

# Unlike other services displaying nodes does not depend on an individual
# langlet but the set of all active langlets.
# Only this enables printing parse trees in a mixed langlet state during
# transformation.

from langscape.csttools.cstutil import*
import string

def indent_source(source, k = 4):
    K = " "*k
    sep = "\n"+K
    return K+sep.join(source.split("\n"))

class CSTDisplay(object):
    def __init__(self, langlet, *args, **kwd):
        self.langlet       = langlet
        self.langlet_id, _ = divmod(langlet.langlet_id, LANGLET_ID_OFFSET)

class CSTTextualDisplay(CSTDisplay):
    def __init__(self, langlet, *args, **kwd):
        super(CSTTextualDisplay, self).__init__(langlet, *args, **kwd)
        self.INDENT = kwd.get("indent", 2)
        self.marked = {}

    def nid_to_text(self, nid):
        llid, S = divmod(nid, LANGLET_ID_OFFSET)
        name = self.langlet.get_node_name(nid)
        if is_symbol(nid):
            return name+"  -- NT`%d.%d\n"%(llid, S)
        else:
            return name+"  -- T`%d.%d\n"%(llid, S)

    def is_marked(self, nid, mark):
        marked = self.marked.get(nid)
        if marked is None:
            if nid in mark or self.langlet.get_node_name(nid) in mark:
                self.marked[nid] = True
                return True
            else:
                self.marked[nid] = False
                return False
        return marked

    def wrap_whitespace(self, S):
        if S in string.whitespace:
            return ("' '"   if S == ' '  else
                    "'\\n'" if S == '\n' else
                    "'\\t'" if S == '\t' else
                    "'\\r'" if S == '\r' else
                    "'\\'"  if S == '\\' else
                    "''")
        return "'"+S+"'"


    def node_to_text(self, node, indent = 0, depth = 10000, mark = ()):
        if node is None:
            return " "*(indent+self.INDENT)+"(None)  <----------    ???    <---------  \n\n"
        nid = node[0]
        nid_text = self.nid_to_text(nid)
        if self.is_marked(nid, mark):
            s = " "*indent+nid_text+"       <-------  \n"
        else:
            col = node[-1]
            if isinstance(col, tuple):
                line = node[-2]
                s = " "*indent+nid_text.rstrip()+" at (L`%s, C`%s)\n"%(line, col)
            else:
                s = " "*indent+nid_text
        for item in node[1:]:
            if isinstance(item, list):
                if depth > 0:
                    s+=self.node_to_text(item, indent = indent+self.INDENT, depth = depth-1, mark = mark)
                elif depth == 0:
                    # use flat = 2 to indicate that no further nesting shall be applied
                    s+=self.node_to_text(item, indent = indent+self.INDENT, depth = -1, mark = mark)
                else:
                    pass
            elif isinstance(item, str):
                s+=" "*(indent+self.INDENT)+self.wrap_whitespace(item)+"\n"
        if indent == 0:
            return "\n"+s+"\n"
        else:
            return s

    def pformat(self, node, depth = 10000, mark = ()):
        return self.node_to_text(node, indent = 0, depth = depth, mark = mark)

    def pprint(self, node, depth = 10000, mark = (), line = -1):
        #if line:
        print self.pformat(node, depth = depth, mark = mark)

if __name__ == '__main__':
    import langscape
    langlet = langscape.load_langlet("python")
    cst = langlet.parse("1+1")
    import pprint
    langlet.pprint(cst, depth=100)
