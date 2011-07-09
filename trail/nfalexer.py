import pprint
import langscape.util
from langscape.ls_const import*
from langscape.trail.nfacursor import*
from langscape.trail.nfareporting import NFAErrorReport

__all__ = ["NFALexer"]

class CharStream(object):
    # Defines character iterator. CharStream needs to care for line and column
    # counts which are important for error display and recovery.

    # TODO: unify shift_read_position() with next()

    def __init__(self, stream):
        self.charstream = stream if stream else '\n'
        self._size = len(stream)
        self.reset()

    def reset(self):
        self.position = 0
        self._line_count = 1
        self._col = 0
        self._nl  = False

    def current_pos(self):
        return (self._line_count, self._col)

    def __iter__(self):
        return self

    def shift_read_position(self):
        self.position+=1
        if self._nl:
            self._line_count+=1
            self._col = 0
            self._nl  = False
        else:
            self._col+=1

    def next(self):
        try:
            c = self.charstream[self.position]
            if c in '\n\r':
                self._nl = True
            return c
        except IndexError:
            raise StopIteration

    def __len__(self):
        return self._size


class CharSet(object):
    def __init__(self, lexer_terminal, keywords):
        self.charset = lexer_terminal
        for c, nid in keywords.items():
            self.charset[nid] = set([c])

    def __setitem__(self, nid, s):
        self.charset[nid] = s

    def __getitem__(self, nid):
        return self.charset.get(nid,"")

    def __contains__(self, nid):
        return self.charset.get(nid)


class NFALexer(object):
    def __init__(self, langlet):
        self.langlet     = langlet
        self.debug       = langlet.options.get("debug_lexer", False)

        # grammar derived entities
        self.nfas       = langlet.lex_nfa.nfas
        self.reachables = langlet.lex_nfa.reachables
        self.keywords   = langlet.lex_nfa.keywords
        self.expanded   = langlet.lex_nfa.expanded
        self.charset    = CharSet(langlet.lex_nfa.lexer_terminal, self.keywords)
        self.parser_kwd = langlet.parse_nfa.keywords
        self.start_symbol = langlet.lex_symbol.token_input

        # caches used and filled by _is_pseudo_reachable()
        self.lexer_terminal = {}
        self.pseudo_reachable = {}

        # special token
        self.ANY        = langlet.lex_token.tokenid.ANY
        self.STOP       = langlet.lex_token.tokenid.STOP
        self.ENDMARKER  = langlet.lex_symbol.ENDMARKER
        self.UNIT       = langlet.lex_symbol.unit
        self.NAME       = langlet.lex_symbol.NAME

        self.cursors    = {}

        # interface between lexer / parser
        self._compute_parser_terminals(langlet.parse_nfa.terminals)

        # if False a parse tree will be returned
        self.do_tokenize = True

        # used for testing
        self._error = False
        self._filename = None

    def _compute_parser_terminals(self, terminals):
        self.parser_terminals = set()
        for s in terminals:
            if type(s) == int:
                self.parser_terminals.add(s+SYMBOL_OFFSET)

    def _init_subtrees(self, sym):
        if sym in self.expanded:
            return []
        else:
            return [sym]

    def _new_cursor(self, sym):
        cursor = self.cursors.get(sym)
        if cursor:
            cursor.reset()
            return cursor
        if sym in self.expanded:
            nfa = self.nfas[sym]
            mtrace  = NFAStateSetSequence(nfa[1], TreeBuilder())
            return NFACursor(nfa, mtrace)
        else:
            cursor = SimpleNFACursor(self.nfas[sym])
        self.cursors[sym] = cursor
        return cursor

    def _next_selection(self, cursor, sym, char, tokstream):
        return char, cursor.move(sym)

    def _store_token(self, sym, cursor, sub_trees, tok, flat):
        if sym in self.expanded:
            if not flat:
                cursor.set_token(tok)
                return
        sub_trees.append(tok)

    def _terminate(self, sym, cursor):
        if sym in self.expanded:
            cursor.terminate()

    def _derive_tree(self, sym, cursor, sub_trees, flat):
        if sym in self.expanded:
            if not flat:
                return cursor.derive_tree(sub_trees)
        return sub_trees

    def dump_error_message(self, tok, selection, rule):
        if tok[1] == '\n':
            tok_string = r"\n"
        else:
            tok_string = tok[1]
        if self._filename:
            s = "\n    Failed to scan input '%s' at (line %d , column %d) in file:\n    %s\n"%(tok_string, tok[2],tok[3]+1, self._filename)
            self._filename = None
        else:
            s = "Failed to scan input '%s' at (line %d , column %d). \n"%(tok_string, tok[2],tok[3]+1)
        raise LexerError(s+rule, **{"token": tok, "selection": selection})

    def _handle_error(self, sym, cursor, sub_trees, tok, selection):
        self._error = True
        if sub_trees:
            cst = sub_trees
        else:
            try:
                cst = self._derive_tree(sym, cursor, sub_trees, False)[:-1]
            except IncompleteTraceError:
                cst = None
        if cst:
            nfareport = NFAErrorReport(self.langlet, "lex")
            if isinstance(cst[0], list):
                rule = nfareport.error_message(cst[-1], tok, selection)
            else:
                rule = nfareport.error_message(cst, tok, selection)
        else:
            rule = ""  # TODO: this is unacceptable
        self.dump_error_message(tok, selection, rule)

    def _is_pseudo_reachable(self, c, s):
        r = self.pseudo_reachable.get((c,s))
        if r is not None:
            return r
        lexer_terminal = self.lexer_terminal.get(s)
        charset = self.charset.charset
        if lexer_terminal is None:
            reach = self.reachables.get(s,[])
            lexer_terminal = [t for t in reach if t in charset]
            self.lexer_terminal[s] = lexer_terminal
        for t in lexer_terminal:
            if c in charset.get(t,""):
                self.pseudo_reachable[(c,s)] = True
                return True
        self.pseudo_reachable[(c,s)] = False
        return False

    def _dbg_info(self, selection, char, T, move):
        selected = "["+', '.join([(self.langlet.get_node_name(s, "lex") if s is not FIN else "FIN") for s in selection ])+"]"
        try:
            if char in '\n':
                char = '\\n'
        except:
            raise ValueError(str(char))
        if move == "step":
            if isinstance(T, str):
                print "char: %s -- select: %s"%char
            else:
                name = self.langlet.get_node_name(T, "lex")
                print "char: %s -- select: %s = "%(char, T)+name
            print " "*21+" "*(len(char)-2)+"next selection: %s"%(selected,)
        else:
            sym, s = T
            name_sym = self.langlet.get_node_name(sym, "lex")
            if isinstance(s, str):
                print "char: %s -- select: %s "%(char,"'"+s+"'")+" (shift: %s)"%name_sym
            else:
                name_s = self.langlet.get_node_name(s, "lex")
                print "char: %s -- select: %s = "%(char, s)+name_s+" (shift: %s)"%name_sym
            print " "*21+" "*(len(char)-2)+"next selection: %s"%(selected,)

    def __dbg_info(self, selection, char, sym):
        if char in '\n':
            char = '\\n'
        print "char: `%s` -- select: %s -- next selection: %s"%(char, sym, selection)
        name = self.langlet.get_node_name(sym, "lex")
        print " "*21+name

    def _update_subtrees(self, sub_trees, item, flat = False):
        if flat:
            sub_trees+=item
        else:
            sub_trees.append(item)

    def _parse(self, tokstream, sym, c, flat = False):
        # TODO: explain the flat kwd argument. Show that it really helps
        # parsing strings, names and comments.
        line, col = tokstream.current_pos()
        if sym in self.parser_terminals:
            flat = True
        cursor = self._new_cursor(sym)
        c, selection = self._next_selection(cursor, sym, c, tokstream)
        if self.debug:
            self._dbg_info(selection, c, sym, "step")
        sub_trees = self._init_subtrees(sym)
        charset = self.charset.charset
        while c:
            for s in selection:
                if s not in (FIN, self.ANY, self.STOP):
                    if s in charset:
                        if c in charset[s]:
                            tokstream.shift_read_position()
                            self._store_token(sym, cursor, sub_trees, c, flat)
                            break
                        continue
                    else:
                        reach = self.reachables.get(s)
                        if reach and (c in reach or self._is_pseudo_reachable(c,s)):
                            res = self._parse(tokstream, s, c, flat)
                            if res:
                                self._update_subtrees(sub_trees, res, flat)
                                break
            else:
                if self.STOP in selection:
                    cursor.move(self.STOP)
                    sub_trees.append([self.STOP, ''])
                    sub_trees = self._derive_tree(sym, cursor, sub_trees, flat)
                    break
                elif FIN in selection:
                    sub_trees = self._derive_tree(sym, cursor, sub_trees, flat)
                    break
                elif self.ANY in selection:
                    line, col = tokstream.current_pos()
                    tokstream.shift_read_position()
                    self._store_token(sym, cursor, sub_trees, c, flat)
                    s = self.ANY
                else:
                    line, col = tokstream.current_pos()
                    self._handle_error(sym, cursor, sub_trees, [self.ANY, c, line, col], selection)
            c, selection = self._next_selection(cursor, s, c, tokstream)
            if self.debug:
                self._dbg_info(selection, c, (sym, s), "shift")
            try:
                c = tokstream.next()
            except StopIteration:
                if self.STOP in selection:
                    cursor.move(self.STOP)
                    sub_trees.append([self.STOP, ''])
                    sub_trees = self._derive_tree(sym, cursor, sub_trees, flat)
                    break
                elif FIN in selection or self.ENDMARKER in selection:
                    sub_trees = self._derive_tree(sym, cursor, sub_trees, flat)
                    break
                else:
                    line, col = tokstream.current_pos()
                    self._handle_error(sym, cursor, sub_trees, [self.ANY, c, line, col], selection)
                c = None
        if sym == self.UNIT and self.do_tokenize:
            return self._make_token(sub_trees, line, col)
        if flat:
            return [sym, sub_trees]
        return sub_trees

    def _getchars(self, lst):
        chars = []
        for item in lst:
            if type(item) == list:
                chars+=self._getchars(item)
            elif type(item) != int:
                chars.append(item)
        return chars

    def _make_token(self, unit, line, col):
        # this function effectively turns NFALexer ( which is a parser, creating parse trees! )
        # into a tokenizer. Trail is a two level parser where non-terminals of
        # one parse are used as terminals of another parse - after some preparation step using
        # _make_token
        self.langlet.display.maybe_show_lexer_cst(unit)
        sub_unit = unit
        nids  = []
        chars = []
        while True:
            if len(sub_unit) == 2:
                if type(sub_unit[1]) == list:
                    nids.append(sub_unit[0])
                    sub_unit = sub_unit[1]
                else:
                    nids.append(sub_unit[0])
                    chars.append(sub_unit[1])
                    break
            else:
                nids.append(sub_unit[0])
                chars = self._getchars(sub_unit)
                break
        for s in nids[::-1]:
            if s in self.parser_terminals:
                if s == self.NAME:
                    name = "".join(chars)
                    kwd_id = self.parser_kwd.get(name)
                    if kwd_id is not None:
                        return [SYMBOL_OFFSET+kwd_id, name, line, col]
                    else:
                        return [s, name, line, col]
                else:
                    return [s, "".join(chars), line, col]
        else:
            return [nids[1], "".join(chars), line, col]

    def _scan(self, charstream, start_symbol = None):
        if start_symbol is None:
            start_symbol = self.start_symbol
        tok = charstream.next()
        tokstream = self._parse(charstream, start_symbol, tok)[1:]
        if charstream.position<len(charstream):
            line, col = charstream.current_pos()
            c = charstream.next()
            if self._filename:
                s = "\n    Failed to scan input '%s' at (line %d , column %d) in file:\n    %s\n"%(c,line,col, self._filename)
            else:
                s = "Failed to scan input '%s' at (line %d , column %d). \n"%(c,line,col)
            raise LexerError(s, **{"token": [self.ANY, c, line, col]})
        return tokstream

    def scan(self, source, filename = "", start_symbol = None):
        '''
        @param source: source code to tokenize
        @return: a sequence of token
        '''
        self._error = False
        self._filename = filename
        cst = self._scan(CharStream(source), start_symbol = start_symbol)
        self._filename = None
        return cst

if __name__ == '__main__':
    grammar = langscape.load_langlet("ls_grammar")
    python = langscape.load_langlet("python")
    import os
    TokenGen = os.path.dirname(python.lex_nfa.__file__)+os.sep+"TokenGen.g"
    grammar.parse(open(TokenGen).read())
    import cProfile
    f = lambda: python.tokenize("'j\nk'"*89)
    cProfile.run("f()")

