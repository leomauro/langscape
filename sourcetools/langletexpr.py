__all__ = ["refine", "LangletExpr", "RuleTemplate"]

import os, pprint
import langscape
from langscape.ls_const import*
from langscape.csttools.cstsearch import*
from langscape.trail.nfaparser import NFAParser, TokenStream
from langscape.trail.nfatools  import compute_span_traces
from langscape.langlets.ls_grammar.grammar_object import GrammarObject
from langscape.sourcetools.sourcegen import SourceGenerator

rule_template = langscape.load_langlet("rule_template")
ls_grammar    = langscape.load_langlet("ls_grammar")


class TraceObject(TokenStream):
    def get_current(self):
        try:
            return self.tokstream[self.position]
        except IndexError:
            raise StopIteration


class TraceChecker(NFAParser):
    def __init__(self, langlet):
        self.langlet    = langlet
        self.rules      = langlet.parse_nfa.nfas
        self.reach      = langlet.parse_nfa.reachables
        self.keywords   = langlet.parse_nfa.keywords
        self.expanded   = langlet.parse_nfa.expanded
        self.terminals  = langlet.parse_nfa.terminals
        self.top        = langlet.parse_nfa.start_symbols[0]
        self.compute_ancestors()

    def compute_ancestors(self):
        _ancestors = {}
        for r, reach in self.langlet.parse_nfa.reachables.items():
            for s in reach:
                S = _ancestors.get(s, set())
                S.add(r)
                _ancestors[s] = S
        self.ancestors = _ancestors

    def checktrace(self, trace, start_symbol = None):
        if start_symbol is None:
            start_symbol = self.top
        item = trace.get_current()
        return self._checktrace(trace, start_symbol, item)


    def _checktrace(self, trace,
                     sym,
                     item,
                     cursor = None,
                     selection = None):

        if cursor is None:
            cursor = self._new_cursor(sym)
            selection = self.next_selection(cursor, sym)
        while item:
            nid = item[0]
            pre = self.ancestors.get(nid, set())
            pre.add(nid)
            S = pre & selection
            if S:
                if len(S) == 1:
                    s = S.pop() # no ambiguity
                    if s == nid:
                        trace.shift_read_position()
                    else:
                        if not self._checktrace(trace, s, item):
                            return False
                else:
                    for s in S:
                        Tr = trace.clone()
                        if self._checktrace(Tr, s, item):
                            trace = Tr
                            break
                    else:
                        return False
            else:
                #
                # trace stops here
                if FIN in selection:
                    return True
                else:
                    return False

            selection = self.next_selection(cursor, s)

            try:
                item = trace.get_current()
            except StopIteration:
                if FIN in selection:
                    return True
                else:
                    return False
        return True


def refine(func):
    func.refined = True
    return func

# 1. Create new LangletObject from a single grammar rule and a list of symbols taken
#    from given langlet L. Build the NFA for this rule.
# 2. Create traces for this NFA and check those traces against L.
# 3. If check was successful create a new langlet object with the data of L and replace
#    the old by the new rule.
# 4. Update the langlet in particular


class LangletExpr(object):
    def __init__(self, langlet):
        self.langlet = langlet
        self.status  = {}
        self.trchecker = TraceChecker(langlet)

    def _linemap(self, lines):
        L = []
        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                continue
            idx  = line.find(":")
            name = line[:idx].strip() if idx>0 else ""
            if name:
                L.append((name,line))
        return L

    def get_token_gen(self):
        lines = open(os.path.join(os.path.dirname(self.langlet.config.__file__), "lexdef", "TokenGen.g")).readlines()
        return self._linemap(lines)

    def get_parse_gen(self):
        lines = open(os.path.join(os.path.dirname(self.langlet.config.__file__), "parsedef", "GrammarGen.g")).readlines()
        return self._linemap(lines)

    def create_refined_grammar(self):
        parser_rules = self.get_parse_gen()
        variables    = {}
        n = 0
        for name in dir(self):
            m = getattr(self, name)
            if hasattr(m, "refined"):
                doc = m.__doc__.strip()
                if doc.startswith(name) and doc[len(name):len(name)+1] in " :":
                    rt = RuleTemplate(self.langlet, doc)
                    for i, (nm, _) in enumerate(parser_rules):
                        if name == nm:
                            parser_rules[i] = (name, rt)
                #variables[names] = m.__call__() or []
        go = self.check_refinement(parser_rules)
        go.variables = variables
        return go

        if n == 0:
            return go
        else:
            rules = []
            for name, R in parser_rules:
                if isinstance(R, RuleTemplate):
                    g_rule = R.get_grammar_rule()
                    rules.append(ls_grammar.tokenize(g_rule))
                    for varname in R.variables:
                        rules.append(ls_grammar.tokenize(varname + ": '$%s$'"%varname))
                else:
                    rules.append(ls_grammar.tokenize(R))
            go = GrammarObject(rules)
            go.set_langlet_id(self.langlet.langlet_id)
            go.langlet.lex_nfa = self.langlet.lex_nfa
            go.langlet.token = go.langlet.parse_token = self.langlet.token
            go.create_grammar(expansion = False)
            go.langlet._load_unparser()
            return go

    def check_refinement(self, parser_rules):
        rules     = []
        templates = []
        for name, R in parser_rules:
            if isinstance(R, RuleTemplate):
                rules.append(ls_grammar.tokenize(R.get_subgrammar_rule()))
                templates.append(R)
            else:
                rules.append(ls_grammar.tokenize(R))
        go = GrammarObject(rules)
        go.set_langlet_id(self.langlet.langlet_id)
        go.langlet.lex_nfa = self.langlet.lex_nfa
        go.langlet.token = go.langlet.parse_token = self.langlet.token
        go.create_grammar(expansion = False)
        go.langlet._load_unparser()
        nfas = go.get_nfas()
        # check that grammars are specialized

        for rt in templates:
            nid = rt.get_nid()
            nfa = nfas[rt.get_nid()]
            traces = compute_span_traces(nfa)
            for tr in traces:
                tro = TraceObject(tr[:-1])
                if not self.trchecker.checktrace(tro, start_symbol = nid):
                    raise GrammarError("Not a refinement: '%s'"%rt.rule_name)
        return go

    def expressions(self, start_symbol = None):
        go = self.create_refined_grammar()
        sg = SourceGenerator(go.langlet, start_symbol)
        return sg.expressions()


class RuleTemplate:
    def __init__(self, langlet, source):
        self.langlet = langlet
        self.cst     = rule_template.transform(source)
        self.variables = rule_template.variables.copy()
        rule_template.variables = {}
        self.subst = {}
        self.rule_name  = find_node(self.cst, rule_template.token.NAME)[1]

    def get_nid(self):
        return getattr(self.langlet.symbol, self.rule_name)

    def get_grammar_rule(self):
        return rule_template.unparse(self.cst)

    def get_subgrammar_rule(self):
        names = find_all(self.cst, rule_template.token.NAME)
        D = {}
        for i, name in enumerate(names):
            if name[1] in self.variables:
                D[i] = name[1]
                name[1] = self.variables[name[1]]
        subgrammar_rule = rule_template.unparse(self.cst)
        # restore CST
        for i, name in D.items():
            names[i][1] = name
        return subgrammar_rule

    def substitute(self, **kwd):
        for varname, S in kwd.items():
            if varname not in self.variables:
                raise KeyError("Undefined variable '%s'" % varname)
            else:
                rule_name = self.variables[varname]
                if hasattr(self.langlet.symbol, rule_name):
                    rule_symbol = getattr(self.langlet.symbol, rule_name)
                    try:
                        self.langlet.parse(S, rule_symbol)
                        self.subst[varname] = S
                    except Exception, e:
                        raise ValueError("Cannot substitute '%s' for symbol '%s'"%(S, varname))
                elif hasattr(self.langlet.token, rule_name):
                    rule_symbol = getattr(self.langlet.token, rule_name) + SYMBOL_OFFSET
                    try:
                        self.langlet.lexer.scan(S, rule_symbol)
                    except Exception, e:
                        raise ValueError("Cannot substitute '%s' for symbol '%s'"%(S, varname))
                else:
                    raise ValueError("Unknown rule '%s' in '$(%s = %s)'"%(rule_name, rule_name, varname))
                self.subst[varname] = S



class PythonExpr(LangletExpr):
    @refine
    def suite(self):
        """
        suite: NEWLINE INDENT (stmt | funcdef | simple_stmt | atom NEWLINE ) DEDENT
        """


    @refine
    def test(self):
        """
        test: or_test ['if' or_test 'else' test] # | lambdef
        """

    @refine
    def decorator(self):
        """
        decorator: '@' (NAME '.'){1,3} NAME [ '(' [arglist] ')' ] NEWLINE
        """

class CFuncallExpr(LangletExpr):
    @refine
    def funcall(self):
        '''
        funcall: NAME '(' [expr (',' expr){0,3}] ')'
        '''

if __name__ == '__main__':
    import langscape as ls
    langlet = ls.load_langlet("sql_select")
    le = CFuncallExpr(langlet)
    for expr in le.expressions(langlet.symbol.sql_select):
        print expr[1:]
        #if expr[0] == langlet.symbol.expr:
        #    print expr[1:]
