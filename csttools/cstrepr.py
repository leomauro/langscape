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


def to_text(node_id, failure_text = True):
    '''
    Returns textual representation of a node id regardless of the langlet.
    '''
    from langscape.base.langlet import langlet_table
    res = langlet_table.get_node_name(node_id, "parse")
    if failure_text:
        return res
    else:
        if res and res.startswith("?("):
            return ""
        else:
            return res

def shave(text):
    '''
    If we have a text of following shape::

        |   foo
        |     bar
        |  baz

    it will be dedented:

        | foo
        |   bar
        |baz
    '''
    res = []
    lines = text.split("\n")
    #print "T-IN", lines
    n = 1000
    for line in lines:
        k = len(line)
        line = line.lstrip()
        if not line:
            res.append((0, ''))
        else:
            res.append((k-len(line), line.rstrip()))
            n = min(n, k-len(line))
    out = [" "*(k-n)+line for (k, line) in res]
    #print "T-OUT", out
    return out

def prepare_source(text):
    return "\n".join(shave(text)).lstrip()

def indent_source(source, k = 4):
    K = " "*k
    sep = "\n"+K
    return K+sep.join(source.split("\n"))

def display_node(langlet_obj, node, mark = [], stop = False, indent = 0):
    INDENT = 2
    langlet_id, _ = divmod(langlet_obj.langlet_id, LANGLET_ID_OFFSET)

    def toText(node_id):
        llid, rest = divmod(node_id, LANGLET_ID_OFFSET)
        if is_symbol(rest):
            if llid!=langlet_id:
                rest = str(rest)+" *"
            name = to_text(node_id, False)
            if name:
                return name+"  -- NT`%d.%s"%(llid, rest)
            return langlet_obj.get_node_name(node_id)+"  -- NT`%s"%(rest,)
        else:
            if llid!=langlet_id:
                rest = str(rest)+" *"
            name = to_text(node_id, False)
            if name:
                return name+"  -- T`%d.%s"%(llid, rest)
            return langlet_obj.get_node_name(node_id)+"  -- T`%s"%(rest,)

    def node2text(node, indent = 0):
        if not node:
            return " "*(indent+INDENT)+str(node)+"  <----------    ???    <---------  \n\n"

        nid = node[0]%LANGLET_ID_OFFSET
        if node[0] in mark or langlet_obj.get_node_name(node[0]) in mark:
            s = " "*indent+toText(node[0])+"       <-------  \n"
            if stop == True:
                s+=" "*(indent+INDENT)+".... \n\n"
                return s
        else:
            if hasattr(node, "__message__"):
                msg = node.__message__()
            else:
                msg = ""
            ln = node[-1]
            if isinstance(ln, int):
                s = " "*indent+toText(node[0])+"     L`%s     %s"%((node[-1]),msg)+"\n"
            else:
                s = " "*indent+toText(node[0])+"   %s\n"%msg
        for item in node[1:]:
            if isinstance(item, list):
                s+=node2text(item, indent+INDENT)
            elif isinstance(item, str):
                if item in string.whitespace:
                    k = ("' '"   if item == ' '  else
                         "'\\n'" if item == '\n' else
                         "'\\t'" if item == '\t' else
                         "'\\r'" if item == '\r' else
                         "'\\'"  if item == '\\' else
                         "''")
                else:
                    k = item
                s+=" "*(indent+INDENT)+k+"\n"
        if indent == 0:
            return "\n"+s+"\n"
        else:
            return s
    return node2text(node, indent = indent)

def pprint(langlet_obj, node, mark = [], stop = True, indent = 0):
    print display_node(langlet_obj, node, mark = mark, stop = stop, indent = indent),



