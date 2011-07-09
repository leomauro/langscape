from langscape.util import split_list
from langscape.ls_const import*
from langscape.csttools.cstutil import*
from langscape.trail.nfacursor import*
from langscape.trail.nfareporting import NFAErrorReport
from langscape.trail.tokentracer import TokenTracer

try:
    import cTrail
except ImportError:
    cTrail = None

class NFACursorP(NFACursor):
    cache = {}

class SimpleNFACursorP(SimpleNFACursor):
    cache = {}

__DEBUG__ = False

class TokenStream(object):
    def __init__(self, stream):
        self.tokstream = stream
        self.position = 0
        self.size = len(stream)

    def __iter__(self):
        return self

    def __len__(self):
        return self.size

    def __repr__(self):
        return "<"+self.__class__.__name__+": "+str(self.tokstream)+" >"

    def clone(self):
        # provides a shallow copy of the token stream
        # it is assumed that the token stream is constant
        ts = self.__class__(self.tokstream)
        ts.position = self.position
        ts.size = self.size
        return ts

    def __getitem__(self, idx):
        return self.tokstream[idx]

    def last(self):
        return self.tokstream[-1]

    def shift_read_position(self):
        self.position+=1

    def next(self):
        try:
            t = self.tokstream[self.position]
            self.position +=1
            return t
        except IndexError:
            raise StopIteration


    def get_token(self):
        try:
            return self.tokstream[self.position]
        except IndexError:
            raise StopIteration

    def untokenize_current_line(self):
        '''
        Method used to reconstruct current line from tokenstream for highlighting errors.

        Point of analysis is the position of the current token.
        '''
        p = self.position
        if p<len(self):
            tok = self[p]
        else:
            tok = self[-1]
        lno = tok[2]
        token = []
        for T in self.tokstream[:p+1][::-1]:
            if T[2] == lno:
                token.append(T)
            else:
                break
        stream = []
        col_end = 0
        for T in token[::-1]:
            k = T[3][0]-col_end
            if k:
                stream.append(' '*k)
            stream.append(T[1])
            col_end = T[3][1]
        return ''.join(stream)


class NFAParser(object):
    def __init__(self, langlet):
        self.langlet    = langlet
        self.debug      = langlet.options.get("debug_parser", False) or __DEBUG__
        self.offset     = langlet.parse_nfa.LANGLET_ID
        self.rules      = langlet.parse_nfa.nfas
        self.reach      = langlet.parse_nfa.reachables
        self.ancestors  = langlet.parse_nfa.ancestors
        self.keywords   = langlet.parse_nfa.keywords
        self.expanded   = langlet.parse_nfa.expanded
        self.terminals  = langlet.parse_nfa.terminals
        self.top        = langlet.parse_nfa.start_symbols[0]
        # CtxKwd attributes
        self.nameset    = set()
        self.contextual_keywords = set()
        self._cache     = {}
        self._intron    = []
        self.read_contextual_keywords()
        self._backtrack_level = 0
        self._filename   = ""
        self._last_scan_point = None
        # self.NEWLINE    = self.offset+4
        # self.nl_ignore  = self.NEWLINE not in langlet.parse_nfa.terminals

    def reset(self):
        pass

    def read_contextual_keywords(self):
        #
        # For further explanation of contextual keywords
        # read the following article:
        #
        #     http://fiber-space.de/wordpress/?p=194
        #
        if self.contextual_keywords:  # already present
            return
        parse_token = self.langlet.parse_token
        if hasattr(parse_token, "CONTEXT_KWD"):
            assert parse_token.NAME, "Contextual keywords require a NAME token to be available."
            CONTEXT_KWD = parse_token.CONTEXT_KWD
            for S, nid in parse_token.token_map.items():
                if nid == CONTEXT_KWD:
                    self.contextual_keywords.update(S.split("|"))
            NAME = parse_token.NAME
            self.nameset = self.ancestors.get(NAME, set())
            self.nameset.add(NAME)


    def _dbg_info(self, selection, tok, T, move):
        selected = "["+', '.join([(self.langlet.get_node_name(s) if s is not FIN else "FIN") for s in selection ])+"]"
        t = "["+self.langlet.get_node_name(tok[0])+", '"+tok[1].replace("\n", "\\n")+"']"
        if move == "step":
            if isinstance(T, str):
                print "token: %s -- select: %s"%(t, T)
            else:
                name = self.langlet.get_node_name(T)
                print "token: %s -- select: %s = "%(t, T)+name
            print "                     "+" "*(len(t)-2)+"next selection: %s"%(selected,)
        elif move == "shift":
            sym, s = T
            name_sym = self.langlet.get_node_name(sym)
            if isinstance(s, str):
                print "token: %s -- select: %s "%(t,"'"+s+"'")+" (match -> %s.next)"%name_sym
            else:
                name_s = self.langlet.get_node_name(s)
                if is_token(s):
                    print "token: %s -- select: %s = "%(t, s)+name_s+" (match -> %s.next)"%name_sym
                else:
                    print "token: %s -- select: %s = "%(t, s)+name_s+" (FIN -> %s.next)"%name_sym
            print "                     "+" "*(len(t)-2)+"next selection: %s"%(selected,)
        else:
            raise ValueError

    def format_error_msg(self, sym, cursor, sub_trees, tok, selection, tokstream):
        if sub_trees:
            cst = sub_trees
        else:
            try:
                cst = self._derive_tree(sym, cursor, sub_trees)[:-1]
            except IncompleteTraceError:
                cst = None
        if cst:
            report = NFAErrorReport(self.langlet, "parse")
            if isinstance(cst[0],list):
                rule = report.error_message(cst[-1], tok, selection)
            else:
                rule = report.error_message(cst, tok, selection)
        else:
            rule = ""
        word = tok[1]
        if tok[1] == '\n':
            word = r"\n"
        line = tokstream.untokenize_current_line().rstrip()
        prefix = "line[%s]: "%tok[2]
        error_line = "\n"+"    \n    "+prefix+"'"+line+"'"+'\n\n'+" "*(tok[3][0]+5+len(prefix))+"^"*(tok[3][1]-tok[3][0])+"\n"
        nmt = "Parser needs more token to finish. " if tok[1] == "<EOF>" else ""
        if self._filename:
            s = "\n\n    "+nmt+"Failed to parse input '%s' at (line %d , column %d) in file:\n\n       %s\n"%(word,tok[2],tok[3][0]+1,self._filename)
            self._filename = None
        else:
            s = nmt+"Failed to parse input '%s' at (line %d , column %d)."%(word,tok[2],tok[3][0]+1)
        terminals = set()
        for item in selection:
            if item in self.terminals:
                terminals.add(item)
            else:
                terminals.update(self.reach[item] & self.terminals)
        return s+error_line+rule+self.format_terminals(terminals)

    def format_terminals(self, terminals):
        kwds = []
        symbols = []
        for t in terminals:
            if is_keyword(t):
                kwds.append(self.langlet.get_node_name(t))
            else:
                token = self.langlet.parse_token
                symbols.append(token.symbol_map.get(t, token.sym_name.get(t, str(t))))
        s = ["\nOne of the following symbols must be used:\n"]
        indent = " "*13
        if kwds:
            s.append("    Keywords")
            for L in split_list(kwds, 8):
                s.append(indent+" ".join(L))
        if symbols:
            s.append("    Symbols")
            for L in split_list(symbols, 8):
                s.append(indent+" ".join(L))
        return "\n".join(s)


    def handle_error(self, sym, cursor, sub_trees, tok, selection, tokstream):
        if self._last_scan_point:
            (sym, p, tok, selection) = self._last_scan_point
        formatter = lambda: self.format_error_msg(sym, cursor, sub_trees, tok, selection, tokstream)
        raise ParserError(**{"token": tok, "selection": selection, "formatter": formatter})

    #
    # Several methods used to hide the difference between expanded NFAs ( NFACursor ) and
    # unexpanded NFAs ( SimpleNFACursor ).
    #

    def _init_subtrees(self, sym):
        if sym in self.expanded:
            return []
        else:
            return [sym]

    def _new_cursor(self, sym):
        if sym in self.expanded:
            nfa = self.rules[sym]
            mtrace  = NFAStateSetSequence(nfa[1], TreeBuilder())
            return NFACursorP(nfa, mtrace)
        else:
            return SimpleNFACursorP(self.rules[sym])

    def _store_token(self, sym, cursor, sub_trees, tok):
        if sym in self.expanded:
            cursor.set_token(tok)
        else:
            sub_trees.append(tok)

    def _store_token_and_intron(self, sym, cursor, sub_trees, tok):
        S = ''.join([intron[1] for intron in self._intron])
        self._intron = []
        tok[1] = tokenstring(tok[1], S)
        self._store_token(sym, cursor, sub_trees, tok)

    def _derive_tree(self, sym, cursor, sub_trees):
        if sym in self.expanded:
            return cursor.derive_tree(sub_trees)
        else:
            return sub_trees

    def next_selection(self, cursor, sym):
        return cursor.move(sym)


    def parse(self, tokstream, start_symbol = None, filename = ""):
        if start_symbol is None:
            start_symbol = self.top
        self._filename = filename
        if cTrail:
            cTrail.select_langlet(self)
            cTrail.parse(tokstream, start_symbol)
        else:
            tok = tokstream.get_token()
            p = self._parse(tokstream, start_symbol, tok)
        self._filename = None
        return p

    def _get_states(self, nid, sym):
        nfa = self.rules[sym]
        trans = nfa[2]
        states = []
        for state in trans:
            if state[0] == nid:
                states.append(state)
        return states

    def _lookahead(self, tokstream, S, sym):
        tokstream = tokstream.clone()
        tracer_data = {}
        tts = []
        for s in S:
            if is_symbol(s):
                tt = TokenTracer(self.langlet, s)
            else:
                # jump to state with nid = s within the current NFA
                states = self._get_states(s, sym)
                if not states:
                    return -1
                tt = TokenTracer(self.langlet, sym, jump_to_state = states, without_expansion = False)
            tts.append(tt)
            tracer_data[tt] = (s, -1)
        n = len(tokstream)
        p = tokstream.position
        m = -1
        while p<n:
            nid = tokstream[p][0]
            if nid == INTRON_NID:
                p+=1
                continue
            removable = []
            for tt in tts:
                selection = tt.selectables()
                if FIN in selection:
                    s, _ = tracer_data[tt]
                    tracer_data[tt] = (s, p)
                    m = p
                if nid not in selection:
                    removable.append(tt)
                else:
                    tt.select(nid)
            for tt in removable:
                tts.remove(tt)
            if len(tts) == 1:
                s, q = tracer_data[tts[0]]
                if q>=0:
                    return (tracer_data[tts[0]][0], p, None)
            elif len(tts) == 0:
                if p > m:
                    ttcancel = removable[-1]
                    s, _ = tracer_data[ttcancel]
                    self._last_scan_point = (s, p, tokstream[p], ttcancel.selectables())
                if m >= 0:
                    for tt, (s, i) in tracer_data.items():
                        if i == m:
                            return (s, p, None)
                selectable = set()
                for tt in removable:
                    selectable.update(tt.selectables())
                return (-1, p, selectable)
            p+=1
        return (-1, p, set())

    def parse(self, tokstream, start_symbol = None, filename = ""):
        if start_symbol is None:
            start_symbol = self.top
        self._filename = filename
        tok = tokstream.get_token()
        p = self._parse(tokstream, start_symbol, tok)
        self._filename = None
        if self.debug:
            print "-- OK --\n"
        # print "COUNT", NFACursor.cnt
        return p

    def _parse(self, tokstream,
                     sym,
                     tok,
                     cursor = None,
                     selection = None,
                     sub_trees = None,
                     full_error = True):

        if cursor is None:
            cursor = self._new_cursor(sym)
            selection = self.next_selection(cursor, sym)
            sub_trees = self._init_subtrees(sym)
        if self.debug:
            self._dbg_info(selection, tok, sym, "step")
        while tok:
            token_type = tok[0]
            #
            # (NFAP.Intron) ignore INTRON token for further parsing
            # but store INTRON information content for unparsing
            if token_type == INTRON_NID:
                self._intron.append(tok)
                tokstream.shift_read_position()
                try:
                    tok = tokstream.get_token()
                except StopIteration:
                    if FIN in selection:
                        return self._derive_tree(sym, cursor, sub_trees)
                    else:
                        self.handle_error(sym, cursor, sub_trees, tok, selection, tokstream)
                continue
            #
            # determine all terminals and non terminals in the current selection that derive
            # the given token type.
            pre = self.ancestors.get(token_type, set())
            pre.add(token_type)
            S = pre & selection
            #
            # map contextual keywords to the NAME token
            if not S and tok[1] in self.contextual_keywords:
                S = self.nameset & selection
                token_type = self.langlet.parse_token.NAME
            try:
                if S:
                    if len(S) == 1:
                        s = S.pop() # no ambiguity
                    else:
                        # print "AMBIGUITY", sym
                        # print "SET", S
                        # print "-"*70
                        s, p, selectable = self._lookahead(tokstream, S, sym)
                        if s == -1:
                            # print "HERE"
                            self.handle_error(sym, cursor, sub_trees, tokstream[p], selectable, tokstream)
                    if s == token_type:
                        tokstream.shift_read_position()
                        if self._intron:
                            self._store_token_and_intron(sym, cursor, sub_trees, tok)
                        else:
                            self._store_token(sym, cursor, sub_trees, tok)
                    else:
                        res = self._parse(tokstream, s, tok, full_error = full_error)
                        if res:
                            sub_trees.append(res)
                else:
                    #
                    # trace stops here
                    if FIN in selection:
                        return self._derive_tree(sym, cursor, sub_trees)
                    else:
                        self.handle_error(sym, cursor, sub_trees, tok, selection, tokstream)
            except IncompleteTraceError:
                if FIN in selection:
                    return self._derive_tree(sym, cursor, sub_trees)
                else:
                    self.handle_error(sym, cursor, sub_trees, tok, selection, tokstream)

            selection = self.next_selection(cursor, s)

            try:
                if self.debug:
                    T = tok

                tok = tokstream.get_token()

                if self.debug:
                    if T[0] == s:
                        self._dbg_info(selection, T, (sym, s), "shift")
                    else:
                        self._dbg_info(selection, tok, (sym, s), "shift")
            except StopIteration:
                if self.debug:
                    self._dbg_info(selection, tok, (sym, s), "shift")
                if FIN in selection or self.offset in selection:
                    return self._derive_tree(sym, cursor, sub_trees)
                else:
                    if tokstream.position == len(tokstream):
                        last = tokstream.last()
                        try:
                            T = [self.langlet.parse_token.ENDMARKER, '<EOF>', last[2], (last[3][1], last[3][1])]
                        except AttributeError:
                            T = [0, '<EOF>', last[2], (last[3][1], last[3][1])]
                        self.handle_error(sym, cursor, sub_trees, T, selection, tokstream)
        return sub_trees



class NFAPartialParser(NFAParser):
    def __init__(self, langlet):
        super(NFAPartialParser, self).__init__()
        self._serialized = None
        self._tokstream  = None

    def parse(self, tokstream, start_symbol = None, filename = ""):
        pass

    def resume(self, tokstream):
        pass

if __name__ == '__main__':
    import langscape
    import cProfile
    langlet = langscape.load_langlet("p4d")
    f = lambda: langlet.parse_file(r"c:\lang\Python27\Lib\site-packages\langscape\langlets\p4d\tests\test_p4d.p4d")
    cProfile.run("f()")
    #f()


