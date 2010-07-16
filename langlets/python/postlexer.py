###############  langlet Postlexer + Interceptor definitions ############

from langlet_config import parent_langlet
from langscape.base.postlexer import postlex
from langscape.base.loader import BaseClass
from langscape.trail.nfadef import INTRON_NID
from langscape.ls_const import*

class LangletPostlexer(BaseClass("Postlexer", parent_langlet)):
    '''
    Defines a langlet specific token stream post-processor.
    '''
    def run(self, scanned):
        self.reset()
        self.set_refactor_mode()
        self.scan = scanned
        sym_left  = self.langlet.lex_nfa.reachables[self.lex_symbol.LEFT]
        sym_right = self.langlet.lex_nfa.reachables[self.lex_symbol.RIGHT]
        for pos, tok in enumerate(self.scan):
            tid = tok[0]
            if tid in sym_left:
                self.LEFT(pos, tok)
            elif tid in sym_right:
                self.RIGHT(pos, tok)
            else:
                handler = self._post_handler.get(tid)
                if handler:
                    handler(pos, tok)
                else:
                    self.add_token(tok)
        self.dedent_to(0)
        self.terminate_stream()
        self.indents = []
        self.parenlevl = 0
        return self.stream

    @postlex
    def dot_start(self, pos, tok):
        "dot_start: '.' | '.' A_DIGIT+ [Exponent] ['j'|'J']"
        # dot_start is an optimization hack in the Token definition. It helps preventing a bloated
        # `unit` NFA.
        if tok[1] == '.':
            self.add_token([self.lex_symbol.DOT]+tok[1:])
        else:
            self.add_token([self.lex_symbol.NUMBER]+tok[1:])

    @postlex
    def INTRON(self, pos, tok):
        if self._refactor_mode:
            intron = tok[:]
            # print "INTRON-PRE", intron
            intron[0] = INTRON_NID + SYMBOL_OFFSET
            # print "INTRON_POST", intron
            self.add_token(intron)
        if self.parenlev>0:   # no action inside expression
            return
        else:
            # extract INDENT and NEWLINE token
            S = tok[1]
            nl_termination = S[-1] in ("\n", "\r")
            nl_inserted = False
            if S in ("\n", "\r"):
                 self.add_token([self.lex_symbol.NEWLINE]+tok[1:])
                 if self.indents and nl_termination:
                     self.dedent_to(0)
                 return
            line, col = tok[2], tok[3]
            _indent = 0
            for c in S:
                if c in ("\n", "\r"):
                    if not nl_inserted:
                        self.add_token([self.lex_symbol.NEWLINE, c, line, col])
                        nl_inserted = True
                    if self.indents and nl_termination:
                        self.dedent_to(0)
                    _indent = 0
                    line+=1
                    col = -1
                elif c == " ":
                    if col == 0:
                        _indent = 1
                    elif _indent>0:
                        _indent+=1
                elif c == '\t':
                    if col == 0:
                        _indent = TABWIDTH
                    elif _indent>0:
                        _indent += TABWIDTH
                elif c == '#':
                    _indent = 0
                col+=1
            if _indent>0:
                k = 0
                while self.indents:
                    last_indent = self.indents[-1]
                    n = len(last_indent[1])
                    if _indent > n:
                        if k>0:
                            raise IndentationError("(Line %d, column %d): Unindent does not match any outer indentation level."%(line, col))
                        else:
                            indent_tok = [self.lex_symbol.INDENT, " "*_indent, line, 0]
                            self.add_token(indent_tok)
                            self.indents.append(indent_tok)
                            return
                    elif _indent < n:
                        self.indents.pop()
                        self.add_token([self.lex_symbol.DEDENT, "", line, 0])
                    else:
                        break
                else:
                    indent_tok = [self.lex_symbol.INDENT, " "*_indent, line, 0]
                    self.add_token(indent_tok)
                    self.indents.append(indent_tok)


    def dedent_to(self, k):
        if not self.stream:
            return
        line = self.stream[-1][2]+1
        while self.indents:
            n = self.indents[-1]
            if n>k:
                self.indents.pop()
                self.add_token([self.lex_symbol.DEDENT, '', line, 0])
            elif n == k:
                break

    @postlex
    def LEFT(self, pos, tok):
        self.parenlev+=1
        self.add_token(tok)

    @postlex
    def RIGHT(self, pos, tok):
        self.parenlev-=1
        self.add_token(tok)



