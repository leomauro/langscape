# -*- coding: UTF-8 -*-
import sys
from p4dutils import pprinter
import xml.parsers.expat

class Parser(object):
    def __init__(self):
        self.stack = []

    def parse(self, s):
        parser = self._create_parser()
        parser.Parse(s, 1)
        assert len(self.stack) == 1, len(self.stack)
        root = self.stack[0][1]
        self.stack = []
        return root

    def start_element(self, name, attrs):
        self.stack.append(('T', name))
        self.stack.append(('A',attrs))

    def char_data(self, data):
        self.stack.append(('S',data))

    def end_element(self, name):
        element  = [name, {}, None, '']
        children = []
        while self.stack:
            item = self.stack.pop()
            t, obj = item
            if t == 'E':
                children.append(obj)
            if t == 'S':
                #children.append(["_T", {}, [], obj])
                element[-1] = obj+element[-1]
            elif t == 'A':
                element[1] = obj
            elif t == 'T':
                assert obj == name, name
                element[2] = children[::-1]
                self.stack.append(('E', element))
                break

    def default(self, data):
        print "Default", [data]

    def start_cdata(self):
        self.stack.append(('T', '**'))

    def end_cdata(self):
        self.end_element('**')

    def comment(self, data):
        self.stack.append(('E',['*', {}, [], data]))

class ExpatParser(Parser):

    def _create_parser(self):
        parser = xml.parsers.expat.ParserCreate()
        parser.StartElementHandler      = self.start_element
        parser.EndElementHandler        = self.end_element
        parser.CharacterDataHandler     = self.char_data
        parser.StartCdataSectionHandler = self.start_cdata
        parser.EndCdataSectionHandler   = self.end_cdata
        parser.CommentHandler           = self.comment
        return parser


class xmlprinter(pprinter):
    def filter(self, *args, **kwd):
        return args


    def pprint(self, xml_declaration = True, strip_p4d = False):
        self._indentw = 1

        def indent(txt):
            return " "*self._indentw*level+txt

        def strip_endtag(end_tag):
            if strip_p4d and 'p4d:' in end_tag:
                return end_tag.replace('p4d:', '')
            else:
                return end_tag

        def autoinsert(begin_tag, attrs):
            if begin_tag.startswith("bl:"):
                if "bl" not in autoinserted:
                    attrs["xmlns:bl"] = "http://fiber-space.de/blns"
                    autoinserted.add("bl")
            elif begin_tag.startswith("bl-schema:"):
                if "bl-schema" not in autoinserted:
                    attrs["xmlns:bl-schema"] = "http://fiber-space.de/bl-schemans"
                    autoinserted.add("bl-schema")

        def handle_begintag(begin_tag, has_p4d_ns, multiline):
            if begin_tag == "_T":
                begin_tag = ""
                endtags.append("")
            elif begin_tag == "*":
                begin_tag = "!--"
                if multiline:
                    endtags.append('\n'+indent("-->\n"))
                else:
                    endtags.append("-->\n")
            elif begin_tag == "**":
                begin_tag = "![CDATA["
                if multiline:
                    endtags.append('\n'+indent("]]>\n"))
                else:
                    endtags.append("]]>\n")
            else:
                endtags.append(indent("</%s>\n"%begin_tag))
            if begin_tag.startswith("p4d:"):
                if strip_p4d:
                    begin_tag = begin_tag[4:]
                    prefixed.add(begin_tag)
                elif not has_p4d_ns:
                    attrs["xmlns:p4d"] = "http://fiber-space.de/p4dns"
                    has_p4d_ns = True
            else:
               autoinsert(begin_tag, attrs)
            return begin_tag, has_p4d_ns

        if xml_declaration:
            self.stream.write('<?xml version="1.0" encoding="UTF-8" ?> \n')
        walker  = self.walker()
        endtags = []
        prefixed = set()
        autoinserted = set()
        level   = 0
        has_p4d_ns = False
        while 1:
            try:
                element,level = walker.next()
                begin_tag, attrs, children, text = element
                text = str(text)
                n = text.count('\n')
                k = n
                if n:
                    text = text.rstrip()
                    k = n - text.count('\n')
                    if k>0:
                        text+='\n'*(k-1)
                while level<len(endtags):
                    end_tag = strip_endtag(endtags.pop())
                    self.stream.write(end_tag)
                s_element = "\n\n"
                begin_tag, has_p4d_ns = handle_begintag(begin_tag, has_p4d_ns, k)
                if begin_tag == "":
                    _t = text
                    if _t:
                        self.stream.write(_t)
                    endtags.pop()
                    continue
                s_attrs = self.formatAttributes(attrs, strip_p4d, prefixed)
                if children == [] and text == '':
                    s_element = indent("<%s%s/>\n"%(begin_tag,s_attrs))
                    endtags.pop()
                elif children == [] and text:
                    begin_tag, s_attrs, text = self.filter(begin_tag, s_attrs, text, **{"level":level})
                    end_tag = strip_endtag(endtags.pop())
                    if begin_tag[0] == "!":
                        s_element = indent("<%s%s%s%s"%(begin_tag,s_attrs,text,end_tag))
                    else:
                        if k == 0:
                            end_tag = end_tag.lstrip()
                        s_element = indent("<%s%s>%s%s"%(begin_tag,s_attrs,text,end_tag))
                elif text:
                    args = self.filter(begin_tag, s_attrs, text, **{"level":level})
                    s_element = indent("<%s%s>%s\n"%args)
                else:
                    begin_tag, s_attrs, text = self.filter(begin_tag, s_attrs, text, **{"level":level})
                    s_element = indent("<%s%s>\n"%(begin_tag,s_attrs))
                self.stream.write(s_element)
            except StopIteration:
                while len(endtags):
                    self.stream.write(strip_endtag(endtags.pop()))
                if prefixed:
                    print "xmlutils.py: Following tags were stripped from `p4d` prefix: %s"%(list(prefixed),)
                break

    def formatAttributes(self,attr, strip_p4d, prefixed):
        if not attr:
            return ""
        else:
            lAttr = []
            for key,val in attr.items():
                if strip_p4d and key.startswith("p4d:"):
                    key = key[4:]
                    prefixed.add(key)
                if val:
                    if val[0] == '"':
                        val = val.strip('"')
                    if val[0] == "'":
                        val = val.strip("'")
                lAttr.append('%s="%s"'%(key,val))
        sAttr = " ".join(lAttr)
        return " "+sAttr



