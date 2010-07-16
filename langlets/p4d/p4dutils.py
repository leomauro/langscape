# -*- coding: UTF-8 -*-

import sys
from parsedef.parse_nfa import keywords
import warnings
import pprint

class TagIsKeywordWarning(Warning): pass

warnings.simplefilter("always", TagIsKeywordWarning)

def ignore_whitespace(S):
    return '\n'.join(shave(S.strip()))

def softrstrip(S):
    k = 0
    Sl = S.rstrip()
    for i in range(len(Sl), len(S), 1):
        if S[i] != ' ':
            break
        k+=1
    if k:
        Sl += " "*k
    return Sl

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

def indentk(text, k, lbra = '', rbra = ''):
    ltext = shave(text)
    if lbra:
        ltext.insert(0, lbra)
    if rbra:
        ltext.append(rbra)
    return '\n'.join(' '*k+line for line in ltext)

class pprinter(object):
    def __init__(self,tree, stream = None):
        '''
        @param tree: p4d-root node.
        @param stream: output stream.
        '''
        self.tree = tree
        self.stream = (stream if stream else sys.stdout)
        self._indentw = 4

    def walker(self,*tree,**kw):
        from p4dbase import P4D
        if not tree:
            _tree = self.tree
        else:
            _tree = tree[0]
        if kw:
            yield _tree,kw["level"]
        else:
            yield _tree,0
        t = type(_tree[2])
        if len(_tree[2])>0:
            _subtree = [(item._tree if isinstance(item, P4D) else item) for item in _tree[2]]
            if len(_subtree)>0 and isinstance(_subtree[0], list):
                for element in _subtree:
                    if isinstance(element, list):
                        if kw:
                            walker = self.walker(element,level=kw["level"]+1)
                        else:
                            walker = self.walker(element,level=1)
                        while 1:
                            try:
                                yield walker.next()
                            except StopIteration:
                                break

class p4dprinter(pprinter):
    def check_tag(self, tag, convert_kwd = False, prefixed = set()):
        if tag in keywords:
            if convert_kwd:
                prefixed.add(str(tag))
                return "p4d:"+tag
            lineno = sys._getframe(0).f_lineno +1

            warnings.warn_explicit('Used tag `%s` is P4D keyword.\n\t\tUse --p4d:kwd option to wrap keyword tags with p4d namespace.\n'%(tag, ), TagIsKeywordWarning, "p4dutils.py", lineno)
        return tag


    def pprint(self, prefix_keyword = False):
        def indent(txt):
            s = " "*self._indentw*level+txt
            return s
        walker = self.walker()
        level  = 0
        prefixed = set()
        while 1:
            try:
                element, level = walker.next()
                tag, attrs, children, text  = element
                tag  = self.check_tag(tag, prefix_keyword, prefixed)
                text = str(text)
                if text.isspace():
                    text = ''
                text = softrstrip(text)
                c = text.count('\n')
                if tag == "*":
                    if c:
                        s_element = indent("{*\n")
                        s_element+= self.formatText(text, level+1)
                        if s_element[-self._indentw:] == " "*self._indentw:
                            s_element = s_element[:-self._indentw]+'\n'+indent("*}")
                        else:
                            s_element+='\n'+indent("*}")
                    else:
                        s_element = s_element = indent("{*%s*}"%text)
                elif tag == "**":
                    if c:
                        s_element = indent("{**")
                        s_element+= self.formatText(text, level+1)
                        if s_element[-self._indentw:] == " "*self._indentw:
                            s_element = s_element[:-self._indentw]+'\n'+indent("**}")
                        else:
                            s_element+='\n'+indent("**}")
                    else:
                        s_element = s_element = indent("{**%s**}"%text)
                else:
                    s_attrs = self.formatAttributes(attrs, tag, level, prefix_keyword, prefixed)
                    if text:
                        if c:
                            level = level+1
                            s_text = "\n"+indent('"""')+self.formatText(softrstrip(text)+'\n', level)+'"""'
                            level = level-1
                        else:
                            s_text = '"'+text+'"'
                        if children:
                            s_element = indent("%s%s:"%(tag, s_attrs))
                            s_element+= s_text
                        else:
                            s_element = indent("%s%s: %s"%(tag, s_attrs, s_text))
                    elif children:
                        s_element = indent("%s%s:"%(tag, s_attrs))
                    else:
                        s_element = indent("%s%s"%(tag, s_attrs))
                self.stream.write(s_element.rstrip()+'\n')
            except StopIteration:
                if prefixed:
                    print "p4dutils.py: Following tags were prefixed by `p4d` : %s"%(list(prefixed),)
                break

    def formatText(self, S, level, comment = False, double_comment = False):
        K  = self._indentw*level
        return indentk(S, K)

    def formatAttributes(self,attr, elem, level, prefix_keyword, prefixed):
        n = 0
        if not attr:
            return ""
        else:
            lAttr = []
            for key,val in attr.items():
                if prefix_keyword and key in keywords:
                    prefixed.add(str(key))
                    key = "p4d:"+key
                lAttr.append(' %s="%s"'%(key,val))
                n+=len(lAttr[-1])
        if n>80 and elem and len(lAttr)>1:
            lAttrBreak = [lAttr[0]]
            for txt in lAttr[1:]:
                lAttrBreak.append(" "*(self._indentw*level+len(elem)+1)+txt)
            sAttr = "\n".join(lAttrBreak)
        else:
            sAttr = ",".join(lAttr)
        return "( "+sAttr[1:]+" )"


if __name__ == '__main__':
    library = """<library path="library.swf">
        <script name="mx/core/mx_internal" mod="1146526998000">
            <txt>
                One line.
                    And another one.
            </txt>
            <mx:script>
                <![CDATA[
                    import foo.bar;
                ]]>
                cdata-section
                    end
            </mx:script>
            <def id="mx.core:mx_internal">def-section </def>
            <dep type="n" id="AS3"/>
        </script>
    </library>"""


    import p4dbase
    p4d_lib = p4dbase.P4D.from_xml(library)
    #pprint.pprint( p4d_lib._tree )
    printer = p4dprinter(p4d_lib._tree, sys.stdout)
    printer.pprint()
