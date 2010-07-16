import pprint

import langscape
import langscape.util
from langscape.trail.nfadef import*
from langscape.trail.nfacursor import*
from langscape.ls_exceptions import ParserError

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
        return "<TokenStream: "+str(self.tokstream)+" >"

    def clone(self):
        ts = TokenStream(self.tokstream)
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
        p   = self.position
        if p<len(self):
            tok = self[p]
        else:
            tok = self[-1]
        lno = tok[2]
        l = p-1
        r = p+1
        left = []
        right = []
        while l>=0:
            T = self[l]
            if T[2] == lno:
                left.insert(0, T)
                l-=1
            else:
                break
        while r<self.size:
            T = self[r]
            if T[2] == lno:
                right.append(T)
                r+=1
            else:
                break
        stream = []
        col_end = 0
        for T in left+[tok]+right:
            k = T[3][0]-col_end
            if k:
                stream.append(' '*k)
            stream.append(T[1])
            col_end = T[3][1]
        return ''.join(stream)



#
#
#  NFAParser  --  general form of NFA trace parser
#
#

class TreeCache(object):
    def __init__(self):
        self._cache = {}

    def add(self, pos_start, nid, tree, pos_end):
        self._cache[(pos_start, nid)] = (pos_end, tree)

    def get(self, position, nid):
        return self._cache.get((position, nid),(None, None))

    def clear(self):
        self._cache = {}


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
        self._tree_cache = TreeCache()
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
        if self.contextual_keywords:
            return
        parse_token = self.langlet.parse_token
        try:
            CONTEXT_KWD = parse_token.CONTEXT_KWD
            for S, nid in parse_token.token_map.items():
                if nid == CONTEXT_KWD:
                    self.contextual_keywords.update(S.split("|"))
            NAME = parse_token.NAME
            self.nameset = self.ancestors.get(NAME, set())
            self.nameset.add(NAME)
        except AttributeError:
            pass


    def _dbg_info(self, selection, tok, T, move):
        t = str(tok)
        if move == "step":
            if isinstance(T, str):
                print "token: %s -- rule: %s"%(t, T)
            else:
                name = self.langlet.get_node_name(T)
                print "token: %s -- rule: %s = "%(t, T)+name
            print "                   "+" "*(len(t)-2)+"next selection: %s"%(selection,)
        elif move == "tracefork-start":
            print "\ntracefork-parse: start forking traces with symbols %s\n"%selection
        elif move == "next-trace":
            name = self.langlet.get_node_name(T)
            print "trace next symbol: %s = %s\n"%(T, name)
        elif move == "tracefork-success":
            name = self.langlet.get_node_name(T)
            print "tracefork-succeeded: selected symbol: %s = %s\n"%(T, name)
        elif move == "tarcefork-failed":
            print "tracefork-failed"
        elif move == "tracefork-cancel":
            name = self.langlet.get_node_name(T)
            print "trace cancelled: symbol: %s = %s\n"%(T, name)
        else:
            sym, s = T
            name_sym = self.langlet.get_node_name(sym)
            if isinstance(s, str):
                print "token: %s -- rule: %s "%(t,"'"+s+"'")+" (shift: %s)"%name_sym
            else:
                name_s = self.langlet.get_node_name(s)
                print "token: %s -- rule: %s = "%(t, s)+name_s+" (shift: %s)"%name_sym
            print "                   "+" "*(len(t)-2)+"next selection: %s"%(selection,)

    def format_error_msg(self, sym, cursor, sub_trees, tok, selection, tokstream):
        if sub_trees:
            cst = sub_trees
        else:
            try:
                cst = self._derive_tree(sym, cursor, sub_trees)[:-1]
            except IncompleteTraceError:
                cst = None
        if cst:
            if isinstance(cst[0],list):
                rule = rule_error(self.langlet, cst[-1], selection, self.keywords, type = "parse")
            else:
                rule = rule_error(self.langlet, cst, selection, self.keywords, type = "parse")
        else:
            rule = ""
        word = tok[1]
        if tok[1] == '\n':
            word = r"\n"
        line = "    "+tokstream.untokenize_current_line()
        error_line = "\n"+line+'\n'+" "*(tok[3][0]+4)+"^"*(tok[3][1]-tok[3][0])+"\n"
        s = "Failed to parse input '%s' at (line %d , column %d)."%(word,tok[2],tok[3][0]+1)
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
        if kwds:
            s.append("    Keywords")
            for k in kwds:
                s.append("             %s"%k)
        if symbols:
            s.append("    Symbols")
            for k in symbols:
                s.append("             %s"%k)
        return "\n".join(s)


    def handle_error(self, sym, cursor, sub_trees, tok, selection, tokstream):
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
            return NFACursor(nfa, mtrace)
        else:
            return SimpleNFACursor(self.rules[sym])

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


    def next_selection(self, cursor, sym, tok, tokstream):
        return cursor.move(sym)

    # Parsing methods:
    #
    #  parse:  API function
    #  _parse: implements TBP algorithm
    #  _parse_all: backtracking support
    #

    def parse(self, tokstream, start_symbol = None, filename = ""):
        if start_symbol is None:
            start_symbol = self.top
        self._filename = filename
        tok = tokstream.get_token()
        p = self._parse(tokstream, start_symbol, tok)
        # pprint.pprint(p)
        return p

    def _parse_all(self, cursor, tokstream, S, tok, sym, sub_trees):
        tracks = []
        if self.debug:
            self._dbg_info(S, tok, sym, "tracefork-start")
        errors = []
        for s in S:
            try:
                if self.debug:
                    self._dbg_info(S, tok, s, "next-trace")
                cloned_cursor    = cursor.clone()
                cloned_tokstream = tokstream.clone()
                trees = self._parse(cloned_tokstream, sym, tok, cursor = cloned_cursor,
                                    selection = set([s]), sub_trees = sub_trees[:])
                tracks.append((cloned_cursor, cloned_tokstream, trees, s))
            except ParserError, e:
                errors.append((cloned_tokstream.position, e))
                if self.debug:
                    self._dbg_info(S, tok, s, "tracefork-cancel")
        if tracks == []:
            errors.sort()
            raise ParserError, errors[-1][1]
        else:
            # print "TRACK-LEN", len(tracks) -- tracks of length>1 have been experienced -> no reduction possible
            tracks.sort( key = lambda item: -item[1].position)
            c_cursor, c_tokstream, trees, s = tracks[0]
            tokstream.position = c_tokstream.position
            if self.debug:
                self._dbg_info(S, tok, s, "tracefork-success")
            cursor.stateset = c_cursor.stateset
            cursor.mtrace = c_cursor.mtrace
            return trees


    def _parse(self, tokstream,
                     sym,
                     tok,
                     parent = 0,
                     cursor = None,
                     selection = None,
                     sub_trees = None,
                     full_error = True):

        p0 = tokstream.position
        if self._backtrack_level>0:
            end_pos, trees = self._tree_cache.get(p0, sym)
            if end_pos:
                tokstream.position = end_pos
                return trees
        if cursor is None:
            cursor = self._new_cursor(sym)
            selection = self.next_selection(cursor, sym, tok, tokstream)
            sub_trees = self._init_subtrees(sym)
        if self.debug:
            self._dbg_info(selection, tok, sym, "step")
        while tok:
            token_type = tok[0]
            #
            # ignore INTRON token for further parsing
            # but store INTRON information content for unparsing
            if token_type == INTRON_NID:
                self._intron.append(tok)
                tokstream.shift_read_position()
                try:
                    tok = tokstream.get_token()
                except StopIteration:
                    if None in selection:
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
            # map contextual keywords to NAME token
            if not S and tok[1] in self.contextual_keywords:
                S = self.nameset & selection
                token_type = self.offset+1  # TODO - verify!
            try:
                if S:
                    if len(S)>1:
                        #
                        # ambiguity - use some sort of continuation here
                        self._backtrack_level+=1
                        res = self._parse_all(cursor, tokstream, S, tok, sym, sub_trees)
                        self._backtrack_level-=1
                        if self._backtrack_level == 0:
                            self._tree_cache.clear()
                        if type(res[0]) == int:
                            return res
                        else:
                            return self._derive_tree(sym, cursor, res)
                    else:
                        #
                        # no ambiguity
                        s = S.pop()
                        if s == token_type:
                            tokstream.shift_read_position()
                            if self._intron:
                                self._store_token_and_intron(sym, cursor, sub_trees, tok)
                            else:
                                self._store_token(sym, cursor, sub_trees, tok)
                        else:
                            res = self._parse(tokstream, s, tok, parent=sym, full_error = full_error)
                            if res:
                                sub_trees.append(res)
                else:
                    #
                    # trace stops here
                    if None in selection:
                        return self._derive_tree(sym, cursor, sub_trees)
                    else:
                        self.handle_error(sym, cursor, sub_trees, tok, selection, tokstream)
            except IncompleteTraceError:
                if None in selection:
                    return self._derive_tree(sym, cursor, sub_trees)
                else:
                    self.handle_error(sym, cursor, sub_trees, tok, selection, tokstream)

            selection = self.next_selection(cursor, s, tok, tokstream)

            if self.debug:
                self._dbg_info(selection, tok, (sym, s), "shift")
            try:
                tok = tokstream.get_token()
            except StopIteration:
                if None in selection or self.offset in selection:
                    return self._derive_tree(sym, cursor, sub_trees)
                else:
                    self.handle_error(sym, cursor, sub_trees, tokstream.last(), selection, tokstream)
        if self._backtrack_level:
            self._tree_cache.add(p0, sym, sub_trees, tokstream.position)
        return sub_trees



