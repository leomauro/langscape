from __future__ import with_statement

__all__ = ["ParserGrammar", "LexerGrammar", "SymbolObject", "ParserObject", "find_langlet_grammar"]

import pprint
import re
import langscape

from langscape.util.path import path
from langscape.util import more_recent
from langscape.base.display import DisplayMixin

alphanum = re.compile("\w")

class LineList:
    """
    Implements a readline-style interface to a string or list of lines.
    """
    def __init__ (self, s_or_l):
        self.index = 0
        if isinstance(s_or_l, list):
            self.lineList = s_or_l
        else:
            self.lineList = s_or_l.splitlines()

    def __iter__(self):
        return self

    def next(self):
        if self.index>=len(self.lineList):
            raise StopIteration
        return self()

    def __call__ (self):
        retVal = ''
        if self.index < len(self.lineList):
            retVal = self.lineList[self.index] + "\n"
            self.index += 1
        return retVal


def find_langlet_grammar(langlet, grammar_type):
    if grammar_type == "GrammarGen.g":
        return langlet.path.joinpath("parsedef", grammar_type).open().read()
    else:
        return langlet.path.joinpath("lexdef", grammar_type).open().read()

class GrammarRuleGenerator(object):
    def rule_extension(self, rest):
        i = 0
        while i<rest:
            c = rest[i]
            if c!=" ":
                if c == ".":
                    while True:
                        i+=1
                        if rest[i] != ".":
                            return True, rest[i+1:]
                else:
                    return False, rest
            i+=1
        return False, rest

    def create_rules(self, lines):
        k = 1
        rule = ""
        rules = {}
        for nextline in lines:
            line = nextline.strip()
            if not line:
                continue
            if line.find("#")>=0:
                single = 0
                double = 0
                for i,c in enumerate(line):
                    if c == '"':
                        single+=1
                    elif c == "'":
                        double+=1
                    elif c == '#':
                        if single%2==0 and double%2==0:
                            line = line[:i]
                            break
                if not line:
                    continue
            colidx = line.find(":")
            if colidx>=0:
                rule_name = line[:colidx]
                if nextline[0].isalnum():
                    rule = rule_name
                    rc, ext = self.rule_extension(line[colidx+1:])
                    if rc:
                        rules[rule] = (k, ext, line)
                    else:
                        rules[rule] = (k, "", line)
                    k+=1
                else:
                    rule_name = rule
                    idx, ext, rule_text = rules[rule_name]
                    rules[rule_name] = (idx, "", rule_text + " "+ line.strip())
            else:
                (idx, ext, l) = rules[rule_name]
                rules[rule_name] = (idx, ext, l+line)
        return rules



class GrammarUpdater(object):
    def __init__(self, langlet_name, pth, options = {}):
        self.grammar_gen  = GrammarRuleGenerator()
        self.langlet_name = langlet_name
        self.recreate     = options.get("build_nfa")
        self.pth_langlet  = self.langlet_path(pth)
        self.langlet_id   = self.read_langlet_id()
        self.offset       = self.read_offset()

    def langlet_path(self, pth):
        base = pth = path(pth).dirname()
        while pth:
            if pth.files("langlet.py"):
                return pth
            root = path(pth).dirname()
            if root == pth:
                return base
            pth = root
        raise RuntimeError("Unable to determine langlet path")

    def read_langlet_id(self):
        for line in open(self.pth_langlet.joinpath("langlet_config.py")).readlines():
            if line.startswith("LANGLET_ID"):
                return int(line.split("LANGLET_ID = ")[1])
        raise RuntimeError("LANGLET_ID not found")

    def track_change(self):
        if self.langlet_name == "ls_grammar":  # don't update grammar automatically!
            return False
        pth_nfa = self.nfa_path()
        pth_sym = self.symbol_path()
        if more_recent(self.grammar_base_path(), pth_nfa) or \
                more_recent(self.grammar_ext_path(), pth_nfa) or \
                self.recreate or \
                pth_sym.size<10:
            return True
        else:
            return False

    def load_grammar(self):
        '''
        Function used to create ext-language specific grammarObjects that contain
        dfa parser tables. These grammar objects will be created using lifted nodes of the
        the used langlets.

        @note: The grammarObj will be replaced by a newer version if the Grammar file
               is more recent than the parsetable.py module.
        '''
        # is parsetable.py file module more recent than the Grammar file or small than return the
        # grammarObj immediately ...
        if not self.track_change():
            return False
        else:
            gram_lines = self._merge_ext()
        # create symbols
        with open(self.symbol_path(),"w") as f_symbol:
            self.map_symbols(f_symbol, gram_lines)
        return True


    def _merge_ext(self):
        '''
        Create a new set of lines reading Grammar + Grammar.ext.
        If Grammar.ext contains a rule R of the same name as Grammar replace R of
        Grammar with R of Grammar.ext
        '''
        global_lines = open(self.grammar_base_path()).readlines()
        ext_lines    = open(self.grammar_ext_path()).read().splitlines()
        global_rules = self.grammar_gen.create_rules(global_lines)
        ext_rules    = self.grammar_gen.create_rules(ext_lines)
        n = len(global_rules)
        i = 1
        ext_rules = sorted(ext_rules.items(), key = lambda r: r[1][0])
        for r, v in ext_rules:
            line, rule_ext, rule_def = v
            rule = global_rules.get(r)
            if rule:
                # overwrite existing rule
                if rule_ext:
                    rule_def = rule[-1]+" "+rule_ext
                global_rules[r] = (rule[0], "", rule_def)
            else:
                # new rule
                global_rules[r] = (n+i, "", rule_def)
                i+=1

        grammar = [line for (k,ext,line) in sorted(global_rules.values(), key = lambda rule: rule[0])]
        self.map_extended(global_rules)
        self.write_merged_grammar(grammar)
        return LineList(grammar)


    def write_merged_grammar(self, grammar):
        with open(self.grammar_gen_path(),"w") as G:
            for l in grammar:
                l = self.post_process_line(l)
                print >> G, l

    def map_symbols(self, f_symbol, gram_lines):
        '''
        Create new langlet specific xxx_symbol.py file.
        '''
        print >> f_symbol, "#  This file is automatically generated; change it on your own risk!"
        print >> f_symbol
        print >> f_symbol, "#--begin constants--"
        print >> f_symbol
        i = 0
        for line in gram_lines:
            if line and line[0].isalpha():
                NT = line.split(":")[0].strip()  # split rule name from rule
                if NT:
                    print >> f_symbol, "%s = %s"%(NT, self.langlet_id+self.offset+i)
                    i+=1

        print >> f_symbol
        print >> f_symbol, "#--end constants--"
        print >> f_symbol
        print >> f_symbol, "tok_name = sym_name = {}"
        print >> f_symbol, "for _name, _value in globals().items():"
        print >> f_symbol, "    if type(_value) is type(0):"
        print >> f_symbol, "        sym_name[_value] = _name\n"
        print >> f_symbol, "del _name"
        print >> f_symbol, "del _value"

        self._write_extended(f_symbol)

    def grammar_gen_path(self):
        raise NotImplementedError

    def grammar_base_path(self):
        raise NotImplementedError

    def grammar_ext_path(self):
        raise NotImplementedError

    def symbol_path(self):
        raise NotImplementedError

    def nfa_path(self):
        raise NotImplementedError

    def map_extended(self, rules):
        raise NotImplementedError

    def post_process_line(self, line):
        raise NotImplementedError

    def _write_extended(self, f_symbol):
        raise NotImplementedError

    def read_offset(self):
        raise NotImplementedError


class ParserGrammar(GrammarUpdater, DisplayMixin):
    '''
    Class used to handle creation / updates of Grammar.base + Grammar.ext specific files ::

            parse_symbol.py
            parse_nfa.py
    '''
    def read_offset(self):
        return 1000

    def grammar_gen_path(self):
        return self.pth_langlet.joinpath("parsedef","GrammarGen.g")

    def grammar_ext_path(self):
        return self.pth_langlet.joinpath("parsedef","Grammar.ext")

    def grammar_base_path(self):
        return self.pth_langlet.joinpath("parsedef","GrammarBase.g")

    def nfa_path(self):
        return self.pth_langlet.joinpath("parsedef","parse_nfa.py")

    def symbol_path(self):
        return self.pth_langlet.joinpath("parsedef","parse_symbol.py")

    def map_extended(self, rules):
        return rules

    def post_process_line(self, line):
        return line

    def _write_extended(self, f_symbol):
        pass

class LexerGrammar(GrammarUpdater, DisplayMixin):
    '''
    Class used to handle creation / updates of Token.base + Token.ext specific files ::

            lex_symbol.py
            lex_nfa.py

    but also ::

            parse_token.py
    '''
    def read_offset(self):
        return 1000

    def grammar_gen_path(self):
        return self.pth_langlet.joinpath("lexdef", "TokenGen.g")

    def grammar_ext_path(self):
        return self.pth_langlet.joinpath("lexdef", "Token.ext")

    def grammar_base_path(self):
        return self.pth_langlet.joinpath("lexdef", "TokenBase.g")

    def nfa_path(self):
        return self.pth_langlet.joinpath("lexdef","lex_nfa.py")

    def symbol_path(self):
        return self.pth_langlet.joinpath("lexdef","lex_symbol.py")


    def map_extended(self, rules):
        self.token_map = {}
        for i,ext,rule in sorted(rules.values()):
        #for i,ext,rule in rules.values():
            rhs = rule[rule.index(":")+1:].strip()
            r = "".join(rhs.split())
            r = "".join(r.split("'"))
            self.token_map[r] = self.offset+i+self.langlet_id
        return rules

    def post_process_line(self, line):
        '''
        Rules in Token.base + Token.ext may contain strings of the kind ::

            R: A B 'xyz' C

        The strings will be splitted and the resulting rule looks like ::

            R: A B 'x' 'y' 'z' C
        '''
        fragments = []
        n = len(line)
        i = 0
        while i<n:
            k1 = line.find("'",i)
            k2 = line.find('"',i)
            if k1 == k2 == -1:
                fragments.append(line[i:])
                break
            k = min(k for k in (k1,k2) if k>0)
            quote = "'" if k== k1 else '"'
            l = line.find(quote, k+1)
            if l==-1:
                raise ValueError("line = '%s', index = %d"%(line, k))
            if l>2+k:
                fragments.append(line[i:k])
                if line[k+1] == '\\':
                    fragments.append(quote+line[k+1:l]+quote+" ")
                else:
                    for c in line[k+1:l]:
                        fragments.append(quote+c+quote+" ")
            else:
                fragments.append(line[i:l+1])
            i = l+1
        return "".join(fragments)


    def _write_extended(self, f_symbol):
        print >> f_symbol
        print >> f_symbol, "token_map = "+pprint.pformat(self.token_map, width=120)


    def map_to_parse_token(self):
        '''
        The files lex_symbol.py and parse_token.py contain the same symbols but use different node ids.

        The general rule is ::

            Nid(lex_symbol.S) == Nid(parse_token.S) - offset

        Since lex_symbol.py is created first this function creates parse_token.py from lex_symbol.py.
        '''
        import langscape.base.loader as loader
        tok_path   = self.pth_langlet.joinpath("parsedef", "parse_token.py")
        lex_symbol = loader.find_module(self.langlet_name, "lexdef.lex_symbol")[1]
        # print "_p", lex_symbol.__dict__
        with open(tok_path, "w") as fPToken:
            print >> fPToken, "#  This file is automatically generated; change it on your own risk!"
            print >> fPToken
            print >> fPToken, "#--begin constants--"
            print >> fPToken
            symbols = sorted((val, key) for (key, val) in lex_symbol.__dict__.items() if isinstance(val, int))
            for val, key in symbols:
                # print "%s = %s"%(key, val - 256)
                print >> fPToken, "%s = %s"%(key, val-self.offset)

            print >> fPToken
            print >> fPToken, "#--end constants--"
            print >> fPToken
            print >> fPToken, "tok_name = sym_name = {}"
            print >> fPToken, "for _name, _value in globals().items():"
            print >> fPToken, "    if type(_value) is type(0):"
            print >> fPToken, "        sym_name[_value] = _name\n"
            print >> fPToken, "del _name"
            print >> fPToken, "del _value"

            new_tok_map = {}
            for k, v in lex_symbol.token_map.items():
                new_tok_map[k] = v - self.offset-1
            print >> fPToken
            print >> fPToken, "token_map = "+pprint.pformat(new_tok_map, width=120)
            print >> fPToken
            inv_tok_map = {}
            for s, i in new_tok_map.items():
                if alphanum.search(s) is None:
                    inv_tok_map[i] = s
            print >> fPToken
            print >> fPToken, "symbol_map = "+pprint.pformat(inv_tok_map, width=120)
            print >> fPToken
            fPToken.close()

    def load_grammar(self):
        if super(LexerGrammar, self).load_grammar():
            self.map_to_parse_token()
            return True
        return False


class _RulesObject(object):
    def __init__(self, langlet_id, offset = 1000):
        self._langlet_id = langlet_id
        self._offset  = offset
        self.tok_name = {}
        self.sym_name = {}

class SymbolObject(_RulesObject):
    def create(self, grammar_lines):
        i = 0
        symbols = {}
        for line in grammar_lines:
            if line and line[0].isalpha():
                NT = line.split(":")[0].strip()  # split rule name from rule
                if NT:
                    symbols[NT] = self._langlet_id + i + self._offset
                    i+=1
        for name, value in symbols.items():
            self.sym_name[value] = name
        self.tok_name = self.sym_name
        self.__dict__.update(symbols)
        if self._offset == 0:
            self.add_maps(grammar_lines)

    def add_maps(self, grammar_lines):
        token_map = {}
        symbol_map = {}
        rule_gen  = GrammarRuleGenerator()
        rules = rule_gen.create_rules()
        for i,ext,rule in sorted(rules.values()):
            rhs = rule[rule.index(":")+1:].strip()
            r = "".join(rhs.split())
            r = "".join(r.split("'"))
            token_map[r] = i+self._langlet_id
            if alphanum.search(r) is None:
                symbol_map[i+self._langlet_id] = rule
        setattr(self, "token_map", token_map)
        setattr(self, "symbol_map", symbol_map)

