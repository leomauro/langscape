import pprint

import langscape.util
from langscape.ls_const import*
from langscape.trail.nfadef import rule_error
from langscape.trail.nfacursor import*

__all__ = ["NFALexer"]

class CharStream(object):
    '''
    Defines character iterator.
    '''
    def __init__(self, stream):
        self.tokstream = stream if stream else '\n'
        self.position = 0
        self._size = len(stream)
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
            tok = self.tokstream[self.position]
            if tok in '\n\r':
                self._nl = True
            return tok
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
        self.langlet    = langlet
        self.debug      = langlet.options.get("debug_lexer", False)
        # grammar derived entities
        self.rules      = langlet.lex_nfa.nfas
        self.reachables = langlet.lex_nfa.reachables
        self.keywords   = langlet.lex_nfa.keywords
        self.expanded   = langlet.lex_nfa.expanded
        self.charset    = CharSet(langlet.lex_nfa.lexer_terminal, self.keywords)
        self.start_symbol = langlet.lex_symbol.token_input
        self.parser_kwd = langlet.parse_nfa.keywords
        self.lexer_terminal = {}
        self.pseudo_reachable = {}
        # special token
        self.ANY        = self.langlet.lex_token.tokenid.ANY
        self.STOP       = self.langlet.lex_token.tokenid.STOP
        self.ENDMARKER  = self.langlet.lex_symbol.ENDMARKER
        self.UNIT       = self.langlet.lex_symbol.unit
        self.NAME       = self.langlet.lex_symbol.NAME
        self.cursors    = {}
        # the lexer hack
        self._register_hooks()
        # interface between lexer / parser
        self._compute_parser_terminals(langlet.parse_nfa.terminals)

    def _register_hooks(self):
        self._hooks = {}
        if hasattr(self.langlet, "LangletInterceptor"):
            for c, f in self.langlet.interceptor.interceptors.items():
                self._hooks[c] = f(self.langlet.interceptor) # register an interceptor at some character

    def _compute_parser_terminals(self, terminals):
        self.parser_terminals = set()
        for s in terminals:
            if type(s) == int:
                self.parser_terminals.add(s+SYMBOL_OFFSET)

    def _init_subtrees(self, sym, flat):
        if sym in self.expanded:
            return []
        else:
            return [sym]

    @langscape.util.psyco_optimized
    def _new_cursor(self, sym):
        cursor = self.cursors.get(sym)
        if cursor:
            cursor.reset()
            return cursor
        if sym in self.expanded:
            nfa = self.rules[sym]
            mtrace  = NFAStateSetSequence(nfa[1], TreeBuilder())
            return NFACursor(nfa, mtrace)
        else:
            cursor = SimpleNFACursor(self.rules[sym])
        self.cursors[sym] = cursor
        return cursor

    def _next_selection(self, cursor, sym, char, tokstream):
        if self._hooks:
            handler = self._hooks.get(char)
            if handler:
                return handler(cursor, sym, char, tokstream)
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

    def _handle_error(self, sym, cursor, sub_trees, tok, selection):
        if sub_trees:
            cst = sub_trees
        else:
            try:
                cst = self._derive_tree(sym, cursor, sub_trees, False)[:-1]
            except IncompleteTraceError:
                cst = None
        if cst:
            if isinstance(cst[0],list):
                rule = rule_error(self.langlet, cst[-1], selection, self.keywords, type = "lex")
            else:
                rule = rule_error(self.langlet, cst, selection, self.keywords, type = "lex")
        else:
            rule = ""
        word = tok[1]
        if tok[1] == '\n':
            word = r"\n"
        s = "Failed to scan input '%s' at (line %d , column %d). \n"%(word,tok[2],tok[3]+1)
        raise LexerError(s+rule, **{"token": tok, "selection": selection})


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
        selected = "["+', '.join([(self.langlet.get_node_name(s, "lex") if s is not None else "None") for s in selection ])+"]"
        try:
            if char in '\n':
                char = '\\n'
        except:
            raise ValueError(str(char))
        if move == "step":
            if isinstance(T, str):
                print "char: %s -- rule: %s"%char
            else:
                name = self.langlet.get_node_name(T, "lex")
                print "char: %s -- rule: %s = "%(char, T)+name
            print "                   "+" "*(len(char)-2)+"next selection: %s"%(selected,)
        else:
            sym, s = T
            name_sym = self.langlet.get_node_name(sym, "lex")
            if isinstance(s, str):
                print "char: %s -- rule: %s "%(char,"'"+s+"'")+" (shift: %s)"%name_sym
            else:
                name_s = self.langlet.get_node_name(s, "lex")
                print "char: %s -- rule: %s = "%(char, s)+name_s+" (shift: %s)"%name_sym
            print "                   "+" "*(len(char)-2)+"next selection: %s"%(selected,)


    def __dbg_info(self, selection, char, sym):
        if char in '\n':
            char = '\\n'
        print "char: `%s` -- rule: %s -- next selection: %s"%(char, sym, selection)
        name = self.langlet.get_node_name(sym, "lex")
        print "                   %s"%name

    def _update_subtrees(self, sub_trees, item, flat = False):
        if flat:
            sub_trees.extend(item)
        else:
            sub_trees.append(item)


    def _parse(self, tokstream, sym, c, flat = False):
        line, col = tokstream.current_pos()
        if sym in self.parser_terminals:
            flat = True
        cursor = self._new_cursor(sym)
        c, selection = self._next_selection(cursor, sym, c, tokstream)
        if self.debug:
            self._dbg_info(selection, c, sym, "step")
        sub_trees = self._init_subtrees(sym, flat)
        charset = self.charset.charset
        while c:
            for s in selection:
                if s not in (None, self.ANY, self.STOP):
                    if s in charset:
                        if c in charset[s]:
                            line, col = tokstream.current_pos()
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
                elif None in selection:
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
                elif None in selection or self.ENDMARKER in selection:
                    sub_trees = self._derive_tree(sym, cursor, sub_trees, flat)
                    break
                else:
                    line, col = tokstream.current_pos()
                    self._handle_error(sym, cursor, sub_trees, [self.ANY, c, line, col], selection)
                c = None
        if sym == self.UNIT:
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
            s = "Failed to scan input '%s' at (line %d , column %d). \n"%(c,line,col)
            raise LexerError(s, **{"token": c})
        return tokstream

    def scan(self, source, filename = ""):
        '''
        @param source: source code to parse
        @return: a sequence of token
        '''
        cst = self._scan(CharStream(source))
        return cst


def test2():
    import cProfile as profile
    source = open(__file__).read()
    python = langscape.load_langlet("python")
    f = lambda: python.tokenize(source)
    profile.runctx("f()", globals(), locals())

def test3():
    import tokenize
    import cProfile as profile
    f = lambda: list(tokenize.generate_tokens(open(__file__).readline))
    profile.runctx("f()", globals(), locals())


if __name__ == '__main__':
    python = langscape.load_langlet("python")
    print python.tokenize("'jjsk'")

