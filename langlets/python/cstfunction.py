from langlet_config import parent_langlet
from langscape.base.loader import BaseClass
from langscape.csttools.cstutil import*
from langscape.csttools.cstsearch import*


class LangletCSTFunction(BaseClass("CSTFunction", parent_langlet)):
    '''
    Implements langlet specific functions operating on CSTs which are accessed through the
    Langlet object via the ``self.fn`` attribute.
    '''
    def __init__(self, langlet):
        super(LangletCSTFunction, self).__init__(langlet)
        self.symbol = self.langlet.parse_symbol
        self.token  = self.langlet.parse_token

    def is_atomic(self, node):
        try:
            nid = node[0]
            if nid in ( self.symbol.atom,
                        self.token.STRING,
                        self.token.NAME,
                        self.token.NUMBER):
                return True
            else:
                if len(node) >= 3:
                    return False
                else:
                    return self.is_atomic(node[1])
        except TypeError:
            raise

    def atomize(self, node):
        if node[0] == self.symbol.atom:
            return node
        elif node[0] in (self.token.STRING,
                         self.token.NAME,
                         self.token.NUMBER):
            return self.atom(node)
        return self.atom("(", node, ")")

    def maybe_projection(self, node):
        '''
        This is a variant of the projection() function. It projects on a Python cst only
        when the first node can be projected.
        '''
        if node[0]>SYMBOL_OFFSET+MAX_PY_SYMBOL:
            node[0] = node[0]%LANGLET_ID_OFFSET
            for item in node[1:]:
                if isinstance(item, (list, tuple)):
                    self.langlet.projection(item)
        return node

    def left_distribute(self, a_atom, a_test, func = None):
        '''
        Suppose a_test is a predicate of the form `A == X or B > Y`. Then we map a_atom against the boolean
        expressions s.t. we yield `a_atom.A == X or a_atom.B > Y`.

        If func is available we distribute as `func(a_atom, A) == X or func(a_atom, B) > Y`.
        '''
        # Implementation:
        # 1) We seek for all not_test nodes in test down to depth 3. For each not_test node we seek the comparison
        #    node without limitations of depth.
        # 2) The comparison node has the structure `expr (comp_op expr)*` If func is available we transform like
        #        any_expr(CallFunc([[func]], [a_atom, expr])) (comp_op expr)*.
        # Otherwise we apply
        #        any_expr(CallFunc("getattr", [a_atom, expr])) (comp_op expr)*.
        _not_tests = find_all(a_test, self.symbol.not_test,depth = 3)
        for nt in _not_tests:
            _comparison = find_node(nt, self.symbol.comparison)
            _expr = _comparison[1]
            _cloned = clone_node(_expr)
            if func:
                if func == ".":
                     _power    = find_node(_expr, self.symbol.power)
                     _trailer  = find_all(_power, self.symbol.trailer,depth = 1)
                     _name     = find_node(_power, self.token.NAME)
                     _power[1] = self.atomize(a_atom)
                     _power.insert(2, self.trailer(".", _name))
                else:
                    replace_node(_expr, self.expr(self.CallFunc(func, [a_atom, _cloned])))
            else:
                _cloned = clone_node(_expr)
                replace_node(_expr, self.expr(self.CallFunc("getattr", [a_atom, _cloned])))


    def varargs2arglist(self, varargs):
        """
        This function is used to turn the arguments of a function defintion into that of a function
        call.

        Motivation ::

             Let

                def f(x,y,*args):
                        ...

             be a given function. We want to define a second function

                def g(*args,**kwd):
                        ...

             that shall be called with the arguments of f in the body of f:

                def f(x,y,*args):
                    ...
                    g(x,y,*args)
                    ...

            To call g with the correct arguments of f we need to transform the varargslist node according to
            f into the arglist of g.
        """

        if not varargs:
            raise ValueError, "No varargs found"
        self.maybe_projection(varargs)
        arguments = []
        i = 1
        while i<len(varargs):
            arg = varargs[i]
            if arg[0] == self.symbol.fpdef:
                if i+1 < len(varargs):
                    tok = varargs[i+1][0]
                    if tok == self.token.EQUAL:
                        i+=3
                    elif tok == self.token.COMMA:
                        i+=2
                    arguments.append(self.argument(arg[1]))
                else:
                    arguments.append(self.argument(arg[1]))
                    break
            elif arg[0] == self.token.STAR:
                arguments.append("*")
                arguments.append(test(varargs[i+1][1]))
                i+=2
            elif arg[0] == self.token.DOUBLESTAR:
                arguments.append("**")
                arguments.append(test(varargs[i+1]))
                i+=2
            elif arg[0] == self.token.COMMA:
                i+=1
            else:
                raise ValueError,"Unexpected node %s"%(self.token.tok_name[arg[0]])
        return arglist(*arguments)

    def func_name(self, funcdef):
        if funcdef[1][0] == self.symbol.decorators:
            return funcdef[3][1]
        else:
            return funcdef[2][1]

    def to_signature(self, varargs):
        """
        Creates a dictionary from a node of type symbol.varargslist.

        @param varargs: node of type varargslist.
        @return: dict of following structure:
                 {'args': dict, 'defaults': dict, 'star_args': dict, 'dstar_args': dict}
        """
        #assert proj_nid(varargs) == self.symbol.varargslist, self.symbol.sym_name[proj_nid(varargs)]
        signature = {'args':{}, 'defaults':{}, 'star_args': {}, 'dstar_args':{}, 'arglist': [] }
        n = len(varargs)-2
        i = 0
        current_name = ""
        while i<=n:
            item = varargs[1:][i]
            if proj_nid(item) == self.symbol.fpdef:
                if find_node(item, self.symbol.fplist):
                    raise SyntaxError("Does not support tuple-structured arguments")
                else:
                    current_name = item[1][1]
                    signature['arglist'].append(current_name)
                    signature['args'][current_name] = ()
            elif proj_nid(item) == self.symbol.test:
                signature['defaults'][current_name] = item
            elif proj_nid(item) == self.token.STAR:
                i+=1
                signature['star_args'][find_node(varargs[1:][i], self.token.NAME)[1]] = ()
            elif proj_nid(item) == self.token.DOUBLESTAR:
                i+=1
                signature['dstar_args'][find_node(varargs[1:][i], self.token.NAME)[1]] = {}
            i+=1
        return signature


    def power_merge(self, nodeA, nodeB):
        '''

        This function merges a pair of power nodes in the following way::

              nodeA = atomA + trailerA   \\
                                         | =>   atomB + trailerB + trailerA
              nodeB = atomB + trailerB   /
        '''
        nodeA = self.maybe_projection(nodeA)
        nodeB = self.maybe_projection(nodeB)
        if nodeA[0] == self.symbol.power and nodeB[0] == self.symbol.power:
            trailerA = find_all(nodeA, self.symbol.trailer,depth = 1)
            if not trailerA:
                trailerA = []
            trailerB = find_all(nodeB, self.symbol.trailer,depth = 1)
            if not trailerB:
                trailerB = []
            atomB    = find_node(nodeB, self.symbol.atom)
            return self.power(atomB, *(trailerB+trailerA))


    def concat_funcalls(self, funA, funB):
        '''
        Two function calls funA(argsA), funB(argsB) are merged to one call funA(args).funB(argsB).
        '''
        if funA[0] == self.symbol.power and funB[0] == self.symbol.power:
            trailerA = find_all(funA, self.symbol.trailer,depth = 1)
            trailerB = find_all(funB, self.symbol.trailer,depth = 1)
            atomA    = find_node(funA, self.symbol.atom)
            atomB    = find_node(funB, self.symbol.atom)
            return self.power(atomA, *(trailerA+[trailer(".",atomB[1])]+trailerB))


    def parens(self, node):
        '''
        Like atomize but default for enforced parentheses is true.
        '''
        return self.atomize(node, enforce = True)


    def split_expr(self, node):
        "splits an expr of the kind a.b(x).c(). ... into factors a, b, (x), c, (), ..."
        pw = find_node(node, self.symbol.power)
        at = find_node(pw, self.symbol.atom)
        tr = find_all(pw, self.symbol.trailer,depth = 1)
        return [at]+tr


    def add_to_suite(self, _suite, _stmt, pos=-1):
        '''
        Inserts statement into suite node.
        @param _suite: suite node in which stmt node is inserted.
        @param _stmt: stmt node to be inserted into suite
        @param pos: optional argument used to characterize the insert
                    position. default value is -1 i.e. stmt node
                    will be appended.
        '''
        n = find_node(_suite, self.symbol.simple_stmt,depth = 1)
        if n:
            _args = [self.stmt(n)]
            if pos==0:
                _args.insert(0, _stmt)
            else:
                _args.append(_stmt)
            return replace_node(_suite, self.suite(*_args))
        else:
            nodes = find_all(_suite, self.symbol.stmt, depth=1)
            if pos == -1:
                nodes.append(_stmt)
            else:
                nodes.insert(pos, _stmt)
            return replace_node(_suite, self.suite(*nodes))


    def pushstmt(self, stmt1, stmt2):
        '''
        If stmt1 has following structure ::

            EXPR1:
                STMT11
                ...
                STMT1k
                EXPR2:
                    STMT21
                    ...
                    STMT2m

        then we insert the second argument stmt2 at the end ::

            EXPR1:
                STMT11
                ...
                STMT1k
                EXPR2:
                    STMT21
                    ...
                    STMT2m
          -->       stmt2
        '''
        SUITE = find_node(stmt1, self.symbol.suite)
        while True:
            _stmts = find_all(SUITE, self.symbol.stmt, depth = 1)
            _stmt  = _stmts[-1]
            _suite = find_node(_stmt, self.symbol.suite)
            if not _suite:
                _stmts.append(stmt2)
                return stmt1
            else:
                SUITE = _suite

    def Name(self, s):
        return [self.token.NAME, s]

    def Number(self, s):
        return [self.token.NUMBER, str(s)]

    def String(self, s):
        if s:
            if s[0] not in ("'", '"'):
                s = '"'+s+'"'
        else:
            s = '""'
        return [self.token.STRING, s]


    def Add(self, fst, snd, *args):
        "Add: term ('+' term)+ -> arith_expr"
        addargs = []
        allargs = [fst,snd]+list(args)
        for item in allargs[:-1]:
            addargs.append(self.fit(item, self.symbol.term))
            addargs.append("+")
        addargs.append(self.fit(allargs[-1], self.symbol.term))
        return self.arith_expr(*addargs)

    def Assign(self, name, value):
        "Assign: expr (',' expr)* '=' expr (',' expr)*  -> expr_stmt"
        if isinstance(name, str):
            arg1 = self.testlist(self.test(self.Name(name)))
        else:
            arg1 = self.testlist(self.test(name))
        arg2 = self.testlist(self.test(value))
        return self.expr_stmt(arg1,'=',arg2)

    def AugAssign(self, var, augass, val):
        "AugAssign: expr augassign expr   -> expr_stmt"
        if type(var) == str:
            v1 = self.testlist(self.test(self.Name(var)))
        else:
            v1 = self.testlist(self.test(var))
        v2 = self.testlist(self.test(val))
        if isinstance(augass, list):
            op = augass
        else:
            op = self.augassign(augass)
        return self.expr_stmt(v1,op,v2)

    def Comparison(self, arg1, op, arg2):
        "Comparison: expr comp_op expr -> test"
        expr1 = find_node(self.expr(arg1), self.symbol.expr)
        expr2 = find_node(self.expr(arg2), self.symbol.expr)
        return self.test(self.comparison(expr1, self.comp_op(op), expr2))

    def Power(self, a, n):
        "Power: atom factor -> power"
        return self.power(self.fit(a, self.symbol.atom), self.fit(n, self.symbol.factor))

    def Sub(self, fst, snd, *args):
        "Sub: term ('-' term)+ -> arith_expr"
        addargs = []
        allargs = [fst,snd]+list(args)
        for item in allargs[:-1]:
            addargs.append(self.fit(item, self.symbol.term))
            addargs.append("-")
        addargs.append(self.fit(allargs[-1], self.symbol.term))
        return self.arith_expr(*addargs)


    def Mul(self, fst, snd, *args):
        "Mul: factor ('+' factor)+ -> term"
        addargs = []
        allargs = [fst,snd]+list(args)
        for item in allargs[:-1]:
            addargs.append(self.fit(item, self.symbol.factor))
            addargs.append("*")
        addargs.append(self.fit(allargs[-1], self.symbol.factor))
        return self.term(*addargs)


    def Div(self, fst, snd, *args):
        "Div: factor ('/' factor)+ -> term"
        addargs = []
        allargs = [fst,snd]+list(args)
        for item in allargs[:-1]:
            addargs.append(self.fit(item, self.symbol.factor))
            addargs.append("/")
        addargs.append(self.fit(allargs[-1], self.symbol.factor))
        return self.term(*addargs)

    def FloorDiv(self, *args):
        "FloorDiv: expr ( '//' expr)+ -> expr"
        addargs = []
        allargs = args
        for item in allargs[:-1]:
            addargs.append(self.fit(item, self.symbol.factor))
            addargs.append("//")
        addargs.append(self.fit(allargs[-1], self.symbol.factor))
        return self.term(*addargs)

    def BitAnd(self, *args):
        "BitAnd: expr ( '&' expr)+ -> expr"
        allargs = [self.fit(arg, self.symbol.shift_expr) for arg in args]
        return self.and_expr(*allargs)

    def BitOr(self, *args):
        "BitOr: expr ( '|' expr)+ -> expr"
        allargs = [self.fit(arg, self.symbol.xor_expr) for arg in args]
        return self.expr(*allargs)

    def BitXor(self, *args):
        "BitXor: expr ( '^' expr)+ -> expr"
        allargs = [self.fit(arg, self.symbol.and_expr) for arg in args]
        return self.xor_expr(*allargs)

    def If(self, *args, **kwd):
        # TODO: to be finished
        #_else = kwd.get("_else")
        _ifargs = []
        for _t,_s in zip(args[::2],args[1::2]):
            _ifargs.append(test(_t))

    def Not(self, expr):
        "Not: 'not' expr -> not_test"
        return self.not_test("not", self.fit(expr, self.symbol.not_test))

    def And(self, fst,snd,*args):
        "And: expr ( 'and' expr)+ -> and_test"
        allargs = [self.fit(arg, self.symbol.not_test) for arg in [fst,snd]+list(args)]
        return self.and_test(*allargs)

    def Or(fst,snd,*args):
        "And: expr ( 'or' expr)+ -> or_test"
        allargs = [self.fit(arg, self.symbol.and_test) for arg in [fst,snd]+list(args)]
        return self.test(self.or_test(*allargs))

    def Del(self, *args):
        _args = []
        for arg in args:
            _args.append(self.fit(arg, self.symbol.expr))
        return self.del_stmt(self.exprlist(*_args))

    def GetItem(self, name, arg):
        if isinstance(name, str):
            name = self.Name(name)
        return self.power(self.atom(name),
                          self.trailer("[",self.subscriptlist(self.subscript(self.expr(arg))),"]"))

    def CallFuncWithArglist(self, name_or_atom, arglist):
        _params = self.trailer("(",arglist,")")
        if isinstance(name_or_atom, list):
            if name_or_atom[0]%LANGLET_ID_OFFSET == self.symbol.atom:
                _args = [name_or_atom]+[_params]
            elif name_or_atom[0]%LANGLET_ID_OFFSET == self.token.NAME:
                _args = [self.atom(name_or_atom)]+[_params]
            else:
                raise ValueError("Cannot handle function name %s"%name_or_atom)
            return self.power(*_args)
        elif name_or_atom.find(".")>0:
            names = name_or_atom.split(".")
            _args = [self.atom(self.Name(names[0]))]+[self.trailer(".",n) for n in names[1:]]+[_params]
            return self.power(*_args)
        else:
            return self.power(self.atom(self.Name(name_or_atom)),_params)


    def CallFunc(self, name_or_atom, args = [], star_args = None, dstar_args = None):
        '''
        Instead of a name an atom is allowed as well.
        '''
        _arglist = []
        for arg in args:
            if isinstance(arg, tuple):
                assert len(arg)==3, arg
                _param = [self.symbol.argument, self.test(self.Name(arg[0])),[self.token.EQUAL, '=']]
                _param.append(self.test(arg[2]))
                _arglist.append(_param)
            else:
                _arglist.append(self.argument(self.test(arg)))

        "arglist: (argument ',')* (argument [',']| '*' test [',' '**' test] | '**' test) "
        if star_args:
            if type(star_args) == str:
                star_args = self.Name(star_args)
            _arglist.append('*')
            _arglist.append(self.test(star_args))
        if dstar_args:
            if type(dstar_args) == str:
                dstar_args = self.Name(dstar_args)
            _arglist.append('**')
            _arglist.append(self.test(dstar_args))
        if _arglist:
            _params = self.trailer("(",self.arglist(*_arglist),")")
        else:
            _params = self.trailer("(",")")
        if isinstance(name_or_atom, list):
            if name_or_atom[0] == self.symbol.atom:
                _args = [name_or_atom]+[_params]
            elif name_or_atom[0] == self.token.NAME:
                _args = [self.atom(name_or_atom)]+[_params]
            else:
                raise ValueError("Cannot handle function name %s"%name_or_atom)
            return self.power(*_args)
        elif name_or_atom.find(".")>0:
            names = name_or_atom.split(".")
            _args = [self.atom(self.Name(names[0]))]+[self.trailer(".",n) for n in names[1:]]+[_params]
            return self.power(*_args)
        else:
            return self.power(self.atom(self.Name(name_or_atom)),_params)


    def GetAttr(self, expr, *args):
        '''
        (A(EXPR), B, C(EXPR), ...) -> CST (A(EXPR1).B.C(EXPR). ... ) of power
        '''
        if isinstance(expr, str):
            expr = self.Name(expr)
        trailers = []
        for arg in args:
            if isinstance(arg, str):
                trailers.append(trailer(".",self.Name(arg)))
            elif arg[0]%LANGLET_ID_OFFSET == 101:
                trailers.append(self.trailer(".", arg))
            else:
                call = find_node(arg, self.symbol.power)[1:]
                assert is_node(call[0], self.symbol.atom)
                trailers.append(".")
                trailers.append(call[0][1])
                for item in call[1:]:
                    assert is_node(item, self.symbol.trailer)
                    trailers.insert(0,item)
        return self.power(self.atom("(", self.testlist_comp(self.test(expr)),")"),*trailers)

    def List(self, *args):
        '''
        List: '[' ']' | '[' expr (',' expr)* ']'   -> atom
        '''
        if not args:
            return self.atom("[","]")
        else:
            return self.atom("[",self.listmaker(*[self.expr(arg) for arg in args]),"]")

    def Tuple(self, *args):
        '''
        Tuple: '(' ')' | '(' expr (',' expr)* ')'   -> atom
        '''
        if not args:
            return self.atom("(",")")
        else:
            return self.atom("(", self.testlist_comp(*([self.expr(arg) for arg in args]+[","])),")")

    def Dict(self, pairs = None, **dct):
        '''
        Dict: '{' '}' | '{' expr ':' expr (',' expr ':' expr )* '}'   -> atom
        '''
        if dct:
            pairs = dct.items()
        if pairs is None:
            return self.atom("{","}")
        args = []
        for key, value in pairs:
            args.append(self.expr(key))
            args.append(self.expr(value))
        return self.atom("{", self.dictmaker(*args),"}")

    def ParametersFromSignature(self, sig):
        return self.FuncParameters(sig['args'],
            defaults = sig['defaults'],
            star_args=sig['star_args'],
            dstar_args=sig['dstar_args'])

    def Lambda(self, body, argnames, defaults = {}, star_args=None, dstar_args=None):
        if argnames:
            _param = find_node(self.FuncParameters(argnames, defaults, star_args, dstar_args),
                               self.symbol.varargslist)
            if _param:
                return self.lambdef(_param, self.test(body))
        return self.lambdef(self.test(body))

    def FuncParameters(self, argnames, defaults = {}, star_args=None, dstar_args=None):
        _argnames = [self.fpdef(arg) for arg in argnames]
        _star_args= []
        if star_args:
            _star_args = ['*', star_args]
        _dstar_args= []
        if dstar_args:
            _dstar_args = ['**', dstar_args]
        _defaults = []
        for key,val in defaults.items():
            _defaults+=[self.fpdef(self.Name(key)), self.expr(val)]
        _all = _argnames+_defaults+_star_args+_dstar_args
        if _all:
            return self.parameters(self.varargslist(*_all))
        else:
            return self.parameters()


    def Function(self, name, BLOCK, argnames, defaults={}, star_args=None, dstar_args=None):
        def _wrap_name(name):
            if isinstance(name, str):
                return self.Name(name)
            return name
        return self.stmt(self.funcdef("def", _wrap_name(name),
                         self.FuncParameters(argnames, defaults, star_args, dstar_args), BLOCK))

    def Subscript(self, expression, sub, *subs):
        '''
        Maps to expr[sub1,sub2,...,subn] only
        '''
        SUBSCR = [self.symbol.subscriptlist,
                  self.subscript(self.expr(sub))]+[self.subscript(self.expr(arg)) for arg in subs]
        return self.power(self.atom('(', self.testlist_comp(self.expr(expression)),')'),
                          self.trailer('[',SUBSCR,']'))

    def Return(self, *args):
        '''
        (EXPR, EXPR, ... ) -> CST ( return_stmt )
        '''
        return self.return_stmt(self.testlist(*[self.expr(arg) for arg in args]))

    def Eval(self, arg):
        return self.eval_input(self.fit(arg, self.symbol.testlist))

    def Except(self, arg1, arg2 = None):
        if arg2:
            return self.except_clause(self.expr(arg1), self.expr(arg2))
        else:
            return self.except_clause(self.expr(arg1))

    def TryExcept(self, try_suite, else_suite = None, *args):
        assert len(args)%2 == 0, "pairs of (except_clause, suite) expected"
        try_except_args = [try_suite]
        for i in range(len(args))[::2]:
            arg = args[i]
            if isinstance(arg, list):
                if arg[0] == self.symbol.except_clause:
                    try_except_args.append(arg)
                else:
                    try_except_args.append(self.Except(arg))
            try_except_args.append(args[i+1])
        if else_suite:
            try_except_args.append(else_suite)
        return self.try_stmt(*try_except_args)


    def TryFinally(self, try_suite, finally_suite):
        return self.try_stmt(try_suite, 'finally', finally_suite)

    def Import(self, module):
        return self.import_name(self.dotted_as_names(self.dotted_as_name(self.dotted_name(*[mod for mod in module.split(".")]))))

    def ImportFrom(self, from_module, *names):
        path = self.dotted_name(*[self.Name(mod) for mod in from_module.split(".")])
        if names[0] == "*":
            return self.import_from(path, '*')
        else:
            return self.import_from(path, self.import_as_name(*names))

    def While(self, *args):
        arg = self.expr(args[0])
        return self.while_stmt(*((arg,)+args[1:]))

    def For(self, *args):
        raise NotImplementedError

    def ListComp(self, *args):
        return self.atom("[", self.listmaker( self.expr(args[0]), args[1]),"]")


    def Subscript(self, expression, *subs):
        assert len(subs)>1
        return self.power( self.atom('(', expression, ')'), self.trailer('[', self.subscriptlist(*subs),']') )


    def Tuple(self, *args):
        if not args:
            return self.atom("(",")")
        else:
            exprs = self.testlist_comp(*list(args)+[","])
            return self.atom("(", exprs ,")")

    def Binary(self, outnode, op, *args):
        assert len(args)>=2
        allargs = []
        for arg in args[:-1]:
            allargs.append(arg)
            allargs.append(op)
        allargs.append(args[-1])
        return outnode(*allargs)

    def Or(self, *args):
        return self.test(self.or_test(*args))


