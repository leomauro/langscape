import pprint
import os
import sys
from langscape.ls_const import*

class DisplayMixin(object):
    '''
    The class DisplyMixin is used to handle ``show_xxx`` options which correspond to the following
    command-line parameters ::

        -a, --show-cst-after
        -b, --show-cst-before
        -m, --show-marked-node
        -s, --show-source
        -t, --show-token
        --show-scan
        --show-lexer-cst
        -v, --cst-validation
    '''
    def maybe_show_token(self, tokenstream):
        """
        Used to show token stream created by tokenizer. Call depends on option -t (--show-token).
        :param tokenstream: token list to be displayed.
        """
        if self.langlet.options.get("show_token"):
            print("[token>")
            display_tokenstream(self.langlet, tokenstream)
            print("<token]")
            print

    def maybe_show_lexer_cst(self, cst):
        if self.langlet.options.get("show_lexer_cst"):
            marked = []
            marked_nodes = self.langlet.options.get("show_marked_node")
            if marked_nodes:
                marked = marked_nodes.split(",")
            print("[lexer-cst>")
            self.langlet.pprint(cst, mark = marked)
            print("<lexer-cst]")

    def maybe_show_cst_before(self, cst):
        """
        Use this option to show a parse tree **before** it gets transformed.
        Call depends on option -b (--show-cst-before).
        :param cst: cst to be printed.
        """
        if self.langlet.options.get("show_cst_before"):
            marked = []
            marked_nodes = self.langlet.options.get("show_marked_node")
            if marked_nodes:
                marked = marked_nodes.split(",")
            print("[cst-before-trans>")
            self.langlet.pprint(cst, mark = marked)
            print("<cst-before-trans]")

    def maybe_show_cst_after(self, cst):
        """
        Used to show CST **after** langlet transformation.
        Call depends on option -a (--show-cst-after).

        :param cst: cst to be printed.
        """
        if self.langlet.options.get("show_cst_after"):
            marked = []
            marked_nodes = self.langlet.options.get("show_marked_node")
            if marked_nodes:
                marked = marked_nodes.split(",")
            print("[cst-after-trans>")
            self.langlet.target.pprint(cst, mark = marked+["> max(non-terminals)"])
            print("<cst-after-trans]")


    def maybe_show_source(self, cst):
        """
        Used to show source code generated transformed cst.
        Call depends on show-source option -s (--show-source).

        :param cst: unparsed CST.
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
        :param cst: checked CST.
        """
        if self.langlet.options.get("cst_validation"):
            print("[cst-validation-test>")
            no_error = self.langlet.target.check_node(cst)
            if no_error:
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

    for tok in tokenstream:
        r = Report()
        try:
            tid  = tok[0]
            name = langlet.get_node_name(tid)
            r.insert("TokenIdName", ("       INTRON" if tid == 999 else name))
            r.insert("TokenId", str(tid))
        except KeyError:
            pass
        if tok[1] == "\n":
            r.insert("TokenValue","'\\n'")
        elif tok[1] == "\t":
            r.insert("TokenValue","'\\t'")
        elif tok[1] == "\r":
            r.insert("TokenValue","'\\r'")
        elif tok[1] == "\\\n":
            r.insert("TokenValue","'\\'")
        else:
            r.insert("TokenValue",r"'%s'"%tok[1])
        if isinstance(tok[2], tuple):
            r.insert("Line", tok[2][0])
            r.insert("Columns", str(tok[2][1])+"-"+str(tok[3][1]))
        else:
            r.insert("Line", tok[2])
            r.insert("Columns", str(tok[3][0])+"-"+str(tok[3][1]))
        r.write()
    print("---------------------------------------------------------------------------'")


