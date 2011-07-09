__all__ = ["CodeTemplate", "PyCodeTemplate", "Marker"]

import random
import pprint
from textwrap import dedent

import langscape.csttools.cstrepr as cstrepr
from langscape.csttools.cstsearch import*
from langscape.csttools.cstutil import*
from langscape.trail.tokentracer import TokenTracer
from langscape.trail.nfaparser import TokenStream

class Marker(object):
    def __init__(self, **kwd):
        self.start   = kwd.get("start")
        self.end     = kwd.get("end")
        self.include = kwd.get("include", [])
        if isinstance(self.include, basestring):
            self.include = [self.include]
        self.exclude = kwd.get("exclude", [])
        if isinstance(self.exclude, basestring):
            self.exclude = [self.exclude]
        self.item    = kwd.get("item")
        self.tokensequences = []

    def match(self, tokenstream):
        if self.item:
            self.match_item(tokenstream)
        else:
            assert self.start, "Incomplete Marker: no string to start with. Use keyword argument begin = '...'"
            assert self.end,   "Incomplete Marker: no string to end with. Use keyword argument end = '...'"
            start, end = self.start, self.end
            stack = []
            n = len(self.include)
            for i, tok in enumerate(tokenstream.tokstream):
                if tok[1] == start:
                    stack.append((i, tok))
                elif tok[1] in self.exclude:
                    stack = []
                elif tok[1] == end:
                    while stack:
                        j, start_tok = stack.pop()
                        if n:
                            k = n
                            for t in enumerate(tokenstream[j:i+1]):
                                if t[1] in self.include:
                                    k-=1
                                    if k == 0:
                                        self.tokensequences.append((j,i))
                                        stack = []
                                        break
                            else:
                                continue
                        self.tokensequences.append((j,i))
                        stack = []
                        break

    def match_item(self, tokenstream):
        item = self.item
        for i, tok in enumerate(tokenstream.tokstream):
            if tok[1] == item:
                self.tokensequences.append((i, i))


class CodeTemplate(object):
    _gensymcnt = 1
    _context_bindings = {}
    def __init__(self, langlet, source, start_symbol = None):
        self.langlet      = langlet
        self.source       = dedent(source)
        self.tokstream    = self.langlet.tokenize(self.source)
        self.constants    = langlet.lex_nfa.constants
        self.start_symbol = (start_symbol if start_symbol else langlet.parse_nfa.start_symbols[0])
        # defined using bind() and local_names()
        self.bindings     = {}
        self.unames       = ()

    def gensym(self, name):
        '''
        Function used to mangle local name to avoid capture. The mechanism isn't as sophisticated
        as in Common Lisp and may be replaced if this is required or any kind of clash has been
        observed.
        '''
        newname = name+"_"+("%5s"%CodeTemplate._gensymcnt).replace(" ","0")
        return newname

    def is_free_var(self, name, context):
        bound_names = self.get_bound_names(context)
        return name in bound_names

    def get_bound_names(self, context):
        '''
        This method returns names bound to a specific context. For example:
        the context can be a block of code and bound names are names declared in this block.

        The implementation of this function is up to the language definition. Overwrite this
        method in a subclass of CodeTemplate.
        '''
        raise NotImplementedError

    def local_names(self, *names):
        '''
        Add names which need conversion to unique local names to avoid name capture.
        '''
        self.unames = names

    def subst_locnames(self, tokstream):
        '''
        This function provides a simple renaming scheme. At this level of generality we
        don't have a binding model i.e. lambdas

        The problem we have at this point is the absense of a binding model i.e. lambdas.
        '''
        if isinstance(tokstream, TokenStream):
            tokstream = tokstream.tokstream
        if self.unames:
            symbols = {}
            for name in self.unames:
                symbols[name] = self.gensym(name)
            for tok in tokstream:
                if tok[1] in symbols:
                    tok[1] = symbols[tok[1]]
            CodeTemplate._gensymcnt+=1
        return tokstream

    def bind(self, **kwd):
        for key, value in kwd.items():
            if isinstance(value, Marker):
                marker = value
            elif isinstance(value, basestring):
                marker = Marker(item = value)
            else:
                raise TypeError("Keyword argument must either string or Marker. '%s' found"%type(value))
            marker.match(self.tokstream)
            self.bindings[key] = marker.tokensequences

    def unbind(self, *names):
        for name in names:
            del self.bindings[name]

    def unbind_all(self):
        self.bindings = {}

    def prepare_bindings(self):
        bindings = []
        # flattening bindings
        for key, items in self.bindings.items():
            for item in items:
                bindings.append((key, item))
        # sorts bindings according to occurrence in tokenstream
        bindings = sorted(bindings, key = lambda item: item[1][0])
        used_bindings = []
        j = -1
        # eliminates overlapping bindings
        # TODO: it may be adequate to raise an exception here.
        for bind in bindings:
            _, (idx0, idx1) = bind
            if idx0>j:
                used_bindings.append(bind)
                j = idx1
        return used_bindings

    def from_subst(self, *args, **kwd):
        cst = self.substitute(*args, **kwd)
        instance = self.__class__.__new__(self.__class__)
        instance.start_symbol = self.start_symbol
        instance.langlet    = self.langlet
        instance.source     = self.langlet.unparse(cst)
        instance.constants  = self.constants
        instance.tokstream  = TokenStream(find_all_token(cst))
        instance.unames     = ()
        instance.bindings   = {}
        return instance

    def strict_substitute(self, *args, **kwd):
        if len(args) > 1:
            raise TypeError('Too many positional arguments')
        if not args:
            mapping = kwd
        elif kwd:
            mapping = args[0]
            mapping.update(kwd)
        else:
            mapping = args[0]
        S = set(mapping.keys())
        R = set(self.bindings.keys())
        D_SR = R ^ S
        if len(D_SR)!=0:
            raise KeyError(D_SR.pop())
        elif len(S)!=len(R):
            if len(S)<len(R):
                raise KeyError((R-S).pop())
            else:
                raise KeyError((S-R).pop())
        return self._substitute(mapping)


    def substitute(self, *args, **kwd):
        if len(args) > 1:
            raise TypeError('Too many positional arguments')
        if not args:
            mapping = kwd
        elif kwd:
            mapping = args[0]
            mapping.update(kwd)
        else:
            mapping = args[0]
        return self._substitute(mapping)

    def _substitute(self, mapping):
        tsmap = {}
        for key, value in mapping.items():
            if isinstance(value, str):
                if value == "":
                    tokenseq = []  # delete token
                else:
                    if "\n" in value and value[-1] not in "\r\n":
                        value += "\n"
                    tokenseq = self.langlet.tokenize(value)
                    try:
                        if tokenseq[-1][0] == self.langlet.token.ENDMARKER:
                            tokenseq.tokstream.pop()
                    except AttributeError: # no ENDMARKER available
                        pass
            elif isinstance(value, list) and len(value)>1:
                if type(value[0]) == int:            # assume CST
                   tokenseq = find_all_token(value)
                elif type(value[0]) == list:         # assume tokenstream
                    tokenseq = value
            else:
                raise TypeError("Wrong argument type: '%s'"%type(value))
            tsmap[key] = tokenseq[:]
        tokstream = self.subst_locnames(self.tokstream[:])
        bindings  = self.prepare_bindings()
        res = []
        k = 0
        for key, item in bindings:
            idx0, idx1 = item
            res+=tokstream[k:idx0]
            tokenseq = tsmap.get(key)
            if tokenseq is not None:
                res+=tokenseq
            else:
                res+=tokstream[idx0:idx1+1]
            k = idx1+1
        res+=tokstream[k:]
        try:
            return self.langlet.parse(TokenStream(self._repair(res)))
        except ValueError:
            res = self.langlet.tokenize(self.langlet.untokenize(res))
            return self.langlet.parse(TokenStream(self._repair(res)))

    def _repair(self, tokenstream):
        '''
        Maybe the tokenstream needs some repair? Insert constant token, when needed.
        '''
        n  = len(tokenstream)
        tt = TokenTracer(self.langlet, start = self.start_symbol)
        selectables = tt.selectables()
        repaired = []
        i = 0
        while i<n:
            tok = tokenstream[i]
            # print tok
            if tok[0] in selectables:
                repaired.append(tok)
                selectables = tt.select(tok[0])
            else:
                # find a const token T which can be inserted between token[i] and token[i+1]
                S = []
                for s in selectables:
                    if s in self.constants:
                        _tt = tt.clone()
                        _selectables = _tt.select(s)
                        if i == n-1:
                            if FIN in _selectables:
                                repaired.append([s, self.constants[s]])
                                break
                        else:
                            T = tokenstream[i+1]
                            if T[0] in _selectables:
                                S.append(s)
                                selectables = _selectables
                else:
                    if S == []:
                        if tok[1].strip() == "":  # forgotten a linebreak?
                            i+=1
                            continue
                        # TODO: replace this by an expressive error message
                        self.compute_syntax_error(tokenstream, i)
                    elif len(S) == 1:
                        selectables = _selectables
                        repaired.append([s, self.constants[s]])
            i+=1
        return repaired

    def compute_syntax_error(self, tokenstream, i):
        tok  = tokenstream[i]
        line = tok[2]
        source = self.langlet.untokenize(tokenstream[:i+1])
        n = len(source)
        k = source.rfind("\n")
        if n>k:
            d = n-k-len(tok[1])
        else:
            d = 0
        source+="\n"+" "*d+"^"
        raise SyntaxError("Invalid substitution:\n\n"+source)



class PyCodeTemplate(CodeTemplate):
    def get_bound_names(self, context):
        '''
        Figures out which names get bound in a particular context. The context is presented as a CST.
        '''
        # is binding context available and the names which are bound to it?
        if id(context) in self._context_bindings:
            return self._context_bindings[id(context)]

        bound_names = set()
        symbol = self.langlet.symbol
        token  = self.langlet.token
        expr_stmts = find_all(context, symbol.expr_stmt, exclude = (symbol.classdef, symbol.funcdef))
        for expr_stmt in expr_stmts:
            testlists  = find_all(expr_stmt, symbol.testlist, depth=1)
            yield_expr = find_all(expr_stmt, symbol.yield_expr, depth = 1)
            if yield_expr:
                K = len(testlists)
            else:
                K = len(testlists)-1
            for testlist in testlists[:K]:
                tests = find_all(testlist, symbol.test, depth = 1)
                names = find_all(testlist, token.NAME)
                if len(tests) == len(names):
                    bound_names.update([name[1] for name in names])
        self._context_bindings[id(context)] = bound_names
        return bound_names

'''
Converge Terminology:
    * splicing      -- compile time evaluation of a language expression. The return value of a splice is an AST.

                        $< expr > evaluates expr and returns the AST corresponding to the result. In particular
                        ``expr`` may be a call to a function which returns an AST or a variable holding an AST.

    * quasi-quoting -- language expression which is taken as-is but turned into an AST for further processing

                        [[ expr ]] is the AST corresponding to ``expr``.

    * insertion     -- insertion of an AST into a quasi-quoted expr

                        [[ expr1 $<expr2> expr3 ]] evaluates ``expr2`` and inserts the result ( the AST ) in the
                        quasi-quoted expression.

Macro: a macro is a compile time function which is defined in ordinary source code and produces

Langscape equivalent:
    * splicing      -- Any compile time function which returns source code as a result.

    * quasi-quoting -- No equivalent. Source code is just quoted i.e. used as a string, not quasi-quoted to
                       represent an AST.

    * insertion     -- expressed through CodeTemplate binding and substitution

Major difference: strict separation. No macros in source code.

'''


