'''
eeoptions.py defines general command line options for langscape.
'''
import pprint
import os
import sys
from langscape.ls_const import*

class DisplayMixin(object):
    '''
    The class DisplyMixin is used to handle ``show_xxx`` options which correspond to command-line
    parameters ::

        -a, --show-cst-after
        -b, --show-cst-before
        -m, --show-marked-node
        -s, --show-source
        -t, --show-token
        --show-scan
        -v, --cst-validation
    '''
    def maybe_show_token(self, tokenstream, filename = None):
        """
        Used to show token-stream created by tokenizer. Call depends on option -t (--show-token).
        @param source: source string to be tokenized
        @param filename: if filename is available the source is read from a file.
        """
        if self.langlet.options.get("show_token"):
            print("[token>")
            display_tokenstream(self.langlet, tokenstream)
            print("<token]")
            print

    def maybe_show_cst_before(self, cst):
        """
        Used to show CST created by the parser *before* transformation. Call depends on option -b (--show-cst-before).
        @param cst: cst to be printed.
        """
        if self.langlet.options.get("show_cst_before"):
            marked = []
            marked_nodes = self.langlet.options.get("show_marked_node")
            if marked_nodes:
                marked = marked_nodes.split(",")
            print("[cst-before-trans>")
            self.langlet.pprint(cst, mark = marked, stop = False)
            print("<cst-before-trans]")

    def maybe_show_cst_after(self, cst):
        """
        Used to show CST created by the parser *after* transformation. Call depends on option -a (--show-cst-after).
        @param cst: cst to be printed.
        """
        if self.langlet.options.get("show_cst_after"):
            marked = []
            marked_nodes = self.langlet.options.get("show_marked_node")
            if marked_nodes:
                marked = marked_nodes.split(",")
            print("[cst-after-trans>")
            self.langlet.target.pprint(cst, mark = marked+["> max(non-terminals)"], stop = False)
            print("<cst-after-trans]")


    def maybe_show_source(self, cst):
        """
        Used to show source code generated transformed cst. Call depends on show-source option -s (--show-source).
        @param cst: cst to be unparsed.
        """
        if self.langlet.options.get("show_source"):
            print ("[unparsed>")
            if isinstance(cst, basestring):
                print cst
            else:
                print self.langlet.unparse(cst)
            print ("<unparsed]")

    def maybe_grammar_check(self, cst):
        """
        Validate cst against grammar. Call depends on option -v ( --cst-validation).
        @param cst: cst to be unparsed.
        """
        if self.langlet.options.get("cst_validation"):
            print("[cst-validation-test>")
            error = self.langlet.target.check_node(cst)
            if not error:
                print "CST o.k."
            print("<cst-validation-test]")

    def maybe_show_scan(self, raw_token):
        """
        Show token stream before it gets passed to the Postlexer. Call depends on option --show-can.
        @param scan: list of token
        """
        if self.langlet.options.get("show_scan"):
            print("[show-scan>")
            pprint.pprint(raw_token)
            print("<show-scan]")


def display_tokenstream(langlet, tokenstream):
    '''
    Create tabular representation for token stream.
    '''

    class Report:
        Line = " %-6s|"
        Columns = " %-8s|"
        TokenValue = " %-20s|"
        TokenId = " %-16s|"
        TokenIdName = " %-16s|"

        def __init__(self):
            self.items = {"Line":" ",
                          "Columns":" ",
                          "TokenValue":" ",
                          "TokenId":" ",
                          "TokenIdName":" "}

        def insert(self, name, value):
            self.items[name] = value

        def write(self):
            print "".join([Report.Line%self.items["Line"],
                    Report.Columns%self.items["Columns"],
                    Report.TokenValue%self.items["TokenValue"],
                    Report.TokenIdName%self.items["TokenIdName"],
                    Report.TokenId%self.items["TokenId"]]
                    )

    print("---------------------------------------------------------------------------.")
    print(" Line  | Columns | Token Value         | Token Name      | Token Id        |")
    print("-------+---------+---------------------+-----------------+-----------------+")

    for item in tokenstream:
        r = Report()
        try:
            tid  = item[0]
            name = langlet.get_node_name(tid)
            r.insert("TokenIdName", ("       INTRON" if tid == 999 else name))
            llid = langlet.langlet_id/10**4
            nid  = tid%LANGLET_ID_OFFSET
            if llid>0:
                r.insert("TokenId", ( "999" if tid == 999 else str(llid)+" -- "+str(nid)))
            else:
                r.insert("TokenId", ( "999" if tid == 999 else str(nid)))
        except KeyError:
            pass
        if item[1] == "\n":
            r.insert("TokenValue","'\\n'")
        elif item[1] == "\t":
            r.insert("TokenValue","'\\t'")
        elif item[1] == "\r":
            r.insert("TokenValue","'\\r'")
        elif item[1] == "\\\n":
            r.insert("TokenValue","'\\'")
        else:
            r.insert("TokenValue",r"'%s'"%item[1])
        if isinstance(item[2], tuple):
            r.insert("Line",item[2][0])
            r.insert("Columns",str(item[2][1])+"-"+str(item[3][1]))
        else:
            r.insert("Line",item[2])
            r.insert("Columns",str(item[3][0])+"-"+str(item[3][1]))
        r.write()
    print("---------------------------------------------------------------------------'")


