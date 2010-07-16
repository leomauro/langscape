###############  langlet transformer definition ##################

from langlet_config import parent_langlet
from langscape.base.loader import BaseClass
from langscape.csttools.cstutil import*
from langscape.csttools.cstsearch import*
from langscape.base.transformer import transform, transform_dbg, t_dbg

from evalutils import*
from p4dbase import*
from bytelet import*

Hex.format = Hex.F_0x

class LangletTransformer(BaseClass("Transformer", parent_langlet)):
    '''
    Defines langlet specific CST transformations.
    '''

    @transform
    def subscript(self, node):
        sub = node[1:]
        for i, item in enumerate(sub):
            if is_node(item, self.token.DOUBLECOLON):
                del sub[i]
                sub.insert(i, [self.token.COLON, ':', item[-1]])
                sub.insert(i, [self.token.COLON, ':', item[-1]])
                break

    @transform
    def SPECNUM(self, node):
        binnum = find_node(node, self.token.Binnumber)
        if binnum:
            return self.fn.atomize(self.fn.CallFunc("Bin",[self.fn.Number(binnum[1][2:])]))
        else:
            hexnum = self.fn.String(' '.join([item[1][2:] for item in find_all(node, self.token.Hexnumber)]))
            return self.fn.atomize(self.fn.CallFunc("Hex", [hexnum]))

    @transform
    def p4d_attr_access(self, node):
        "p4d_attr_access: '@' ( NAME | '*') ->  attribute(NAME) | attributes() "
        name = find_node(node, self.token.NAME)
        if name:
            return self.fn.CallFunc("attribute", [self.fn.String(name[1])])
        else:
            return self.fn.CallFunc("attributes", [])

    def p4d_string(self, p4dnode):
        return "'''"+str(p4dnode)+"'''"

    def build_p4d_compound_stmt(self, node, xmlnode = None):
        "p4d_compound_stmt: [NAME '='] p4d_element ':' p4d_suite"
        element = self.build_p4d_element(find_node(node, self.symbol.p4d_element))
        nodes    = self.build_p4d_suite(find_node(node, self.symbol.p4d_suite), element)
        if xmlnode:
            xmlnode.children.extend(nodes)
        else:
            xmlnode = nodes[0]
        return xmlnode

    def build_p4d_name(self, node):
        "p4d_name: NAME (':' NAME)*"
        return ":".join([name[1] for name in find_all(node, self.token.NAME) ])

    def build_p4d_element(self, node):
        "p4d_element: p4d_name ['(' [p4d_attribute_list] ')']"
        tag = self.build_p4d_name(find_node(node, self.symbol.p4d_name))
        xmlnode = P4DNode(tag, attrs = {})
        _attrlist = find_node(node, self.symbol.p4d_attribute_list)
        if _attrlist:
            _attributes = find_all(_attrlist, self.symbol.p4d_attribute, depth = 1)
            attrs = {}
            for attr in _attributes:
                attr_name, attr_value = self.build_p4d_attribute(attr)
                attrs[attr_name] = attr_value
            xmlnode.attrs.update(attrs)
        return xmlnode

    def build_p4d_attribute(self, node):
        "p4d_attribute: p4d_name '=' ['&'] test"
        attr_name  = self.build_p4d_name(find_node(node, self.symbol.p4d_name))
        n_value    = find_node(node, self.symbol.test)
        if find_node(node, self.token.AMPER, depth = 1):
            attr_value = "evaltostr_%s"%self.langlet.unparse(n_value)
        elif is_supersimple(n_value):
            S = find_node(n_value, self.token.STRING)
            if S:
                attr_value = S[1][1:-1]
            else:
                S = find_node(n_value, self.token.NUMBER)
                if S:
                    attr_value = "evaltostr_%s"%self.langlet.unparse(n_value)
                else:
                    _specnum = find_node(n_value, self.symbol.SPECNUM)
                    if _specnum:
                        attr_value = "evaltoobj_%s"%self.langlet.unparse(self.SPECNUM(_specnum))
                    else:
                        raise SyntaxError("P4D attribute value `%s` must be prefixed with &-operator for evaluation."%self.langlet.unparse(n_value))
        else:
            print "N_VALUE", n_value
            raise SyntaxError("P4D attribute value of `%s` must be prefixed with &-operator for evaluation."%self.langlet.unparse(node))
        return attr_name, attr_value

    def build_p4d_simple_stmt(self, node):
        "p4d_simple_stmt: (p4d_element | p4d_expr) NEWLINE"
        _p4d_element = find_node(node, self.symbol.p4d_element, depth = 1)
        if _p4d_element:
            return self.build_p4d_element(_p4d_element)
        else:
            return self.build_p4d_expr(find_node(node, self.symbol.p4d_expr))

    def build_p4d_stmt(self, node, xmlnode):
        "p4d_stmt: p4d_simple_stmt | p4d_compound_stmt"
        if is_node(node[1], self.symbol.p4d_simple_stmt):
            res = self.build_p4d_simple_stmt(node[1])
            if isinstance(res, P4DNode):
                xmlnode.children.append(res)
                return [xmlnode]
            elif res.startswith("evaltoobj_"):
                xmlnode.children.append(res)
                return [xmlnode]
            else:
                xmlnode.text = res
                return [xmlnode]
        else:
            xmlnode = self.build_p4d_compound_stmt(node[1], xmlnode)
            return [xmlnode]

    def build_p4d_suite(self, node, xmlnode):
        "p4d_suite: p4d_expr | NEWLINE INDENT p4d_stmt+ DEDENT"
        if is_node(node[1], self.symbol.p4d_expr):
            return self.build_p4d_stmt([self.symbol.stmt, [self.symbol.p4d_simple_stmt]+node[1:]], xmlnode)
        else:
            nodes = []
            _stmts = find_all(node, self.symbol.p4d_stmt, depth = 1)
            for _stmt in _stmts:
                self.build_p4d_stmt(_stmt, xmlnode)
            return [xmlnode]

    def build_p4d_expr(self, node):
        "p4d_expr: '&' ['&'] test | '(' [ p4d_expr (',' p4d_expr)] ')' | STRING | NUMBER | SPECNUM | P4D_Comment"
        _test = find_node(node, self.symbol.test, depth = 1)
        if _test:
            if node[2][0] == self.token.AMPER:
                name = find_node(_test, self.token.NAME)[1]
                return "deferredeval_lambda %s: %s"%(name, self.langlet.unparse(_test))
            return "evaltoobj_"+self.langlet.unparse(_test)
        _expr_list = find_all([self.symbol.p4d_simple_stmt]+node[1:], self.symbol.p4d_expr, depth = 1)
        if _expr_list:
            return "evaltoobj_"+str([self.build_p4d_expr(item) for item in _expr_list])
        p4d_comment = find_node(node, self.token.P4D_Comment, depth = 1)
        if p4d_comment:
            comment = self.langlet.unparse(node)[2:-2]
            if comment[0] == '*' and comment[-1] == '*':
                comment = "restringify_"+hide_bad_chars(comment[1:-1])
                p4d_node = P4DNode("**")
            else:
                p4d_node = P4DNode("*")
                comment = "restringify_"+hide_bad_chars(comment)
            p4d_node.text = comment
            return p4d_node
        _str = find_node(node, self.token.STRING, depth = 1)
        if _str:
            return "restringify_"+hide_bad_chars(node[1][1])
        _specnum = find_node(node, self.symbol.SPECNUM,depth=1)
        if _specnum:
            return "evaltoobj_%s"%self.langlet.unparse(self.SPECNUM(_specnum))
        _number = find_node(node, self.token.NUMBER,depth=1)
        if _number:
            return "evaltonum_"+node[1][1]
        raise TypeError("no P4D object content or attribute: `%s`."%self.langlet.unparse(node))

    @transform
    def NAME(self, node):
        name = node[1]
        if '-' in name:
            chain = self.node_stack(node)
            nd, chain = chain.step()
            nid = nd[0]
            if nid in (self.symbol.p4d_attr_access,
                       self.symbol.p4d_name,
                       self.symbol.p4d_accessor):
                return
            elif nid == self.symbol.atom:
                difference = ' - '.join(name.split('-'))
                chain = self.node_stack(node)
                nd, chain = chain.step()  # power
                nd, chain = chain.step()  # factor
                nd, chain = chain.step()  # term
                nd, chain = chain.step()  # arith_expr
                txt = self.langlet.unparse(nd)
                txt = txt.replace(name, difference)
                return find_node(self.langlet.parse(txt), self.symbol.arith_expr)
            else:
                raise SyntaxError("invalid syntax. No hyphenation permitted in Python names.")
        elif '::' in name:
            chain = self.node_stack(node)
            _trailer, chain = chain.step() # trailer
            if _trailer[0]!=self.symbol.trailer:
                raise SyntaxError("invalid use of accessor symbol '::'")
            nd, chain = chain.step() # power
            prefix, local_name = name.split("::")
            accessor = cstnode([self.symbol.p4d_accessor,
                               [self.token.DOUBLECOLON, '::'],
                               [self.token.NAME, local_name]])
            id_trailer = id(_trailer)
            for i, item in enumerate(nd):
                if id(item) == id_trailer:
                    del nd[i]
                    nd.insert(i,[self.symbol.trailer, accessor])
                    nd.insert(i, self.fn.trailer(".", self.fn.Name(prefix)))
                    break
            self.mark_node(nd)
            return nd


    @transform
    def p4d_accessor(self, node):
        "p4d_accessor: '.' p4d_attr_access | '::' NAME | '.' '(' ['.'] test ')'"
        _attr = find_node(node, self.symbol.p4d_attr_access, depth = 1)
        if _attr:
            self.unmark_node(_attr)
            _call = self.p4d_attr_access(_attr)
            name  = find_node(_call, self.token.NAME)[1]
            return self.fn.trailer(".", name), find_node(_call, self.symbol.trailer)
        elif find_node(node, self.token.LPAR, depth = 1):
            # .(@x == A)  ==> lambda this: this.attribute("x") == str(A)
            # .(x == A)   ==> lambda this: any(x.text() == A for x in this.x)
            # .(X op Y)   ==> lambda this: T(X) op T(Y)
            # .(x.X == A) ==> lambda this: any(x.X == A for x in this.x)
            # .(x::y == A) ==> lambda this: any(item.text() == A for item in this.children("x:y"))
            # .(@x::y == A) ==> lambda this: this.attribute("x:y") == str(A)
            if is_node(node[3], self.token.DOT):
                _test = find_node(node, self.symbol.test)  # child node
                _test[:] = find_node(self.langlet.parse("_."+self.langlet.unparse(_test)), self.symbol.test)
                filter_type = 3
            else:
                filter_type = 2  # this node
            body = find_node(node, self.symbol.test)
            self.unmark_node(body, self.token.NAME)
            _not_tests = find_all(body, self.symbol.not_test, depth = 3)
            for nt in _not_tests:
                _comparison = find_node(nt, self.symbol.comparison)
                n = len(_comparison)
                if n>4:
                    raise SyntaxError("Invalid filter `.(%s)`"%self.langlet.unparse(_comparison))
                _expr_1 = _comparison[1]
                if find_node(_expr_1, self.token.DOUBLECOLON):
                    _pow = find_node(_expr_1, self.symbol.power)
                    for i,item in enumerate(_pow):
                        if isinstance(item, list):
                            if find_node(item, self.token.DOUBLECOLON):
                                _name = find_node(_pow[i-1], self.token.NAME)
                                _name[1] = _name[1]+':'+find_node(item, self.token.NAME)[1]
                                del _pow[i]
                                break
                self.run(_expr_1)
                name = find_node(_expr_1, self.token.NAME)[1]
                if n>2:
                    s_comp   = self.langlet.unparse(_comparison[2])
                    s_expr_2 = self.langlet.unparse(_comparison[3])
                s_expr_1 = self.langlet.unparse(_expr_1)
                if name == "attribute":
                    filter_type = 1  # attribute
                    if n == 4:
                        _expr = find_node(self.langlet.parse("(this.%s %s str(%s))"%(s_expr_1, s_comp, s_expr_2)), self.symbol.expr)
                    else:
                        _expr = find_node(self.langlet.parse("(this.%s)"%(s_expr_1,)), self.symbol.expr)
                else:
                    if s_expr_1 == name:
                        if n == 4:
                            if name != '_':
                                _expr = find_node(self.langlet.parse("(this.text() %s %s and this.tag == '%s')"%(s_comp, s_expr_2, name)), self.symbol.expr)
                            else:
                                _expr = find_node(self.langlet.parse("(this.text() %s %s)"%(s_comp, s_expr_2)), self.symbol.expr)
                        else:
                            _expr = find_node(self.langlet.parse("(this.tag == '%s')"%(name,)), self.symbol.expr)
                    else:
                        s_expr_1 = s_expr_1.replace(name, "this", 1)
                        if n == 4:
                            if name !='_':
                                _expr = find_node(self.langlet.parse("(%s %s %s and this.tag == '%s')"%(s_expr_1, s_comp, s_expr_2, name)), self.symbol.expr)
                            else:
                                _expr = find_node(self.langlet.parse("(%s %s %s)"%(s_expr_1, s_comp, s_expr_2)), self.symbol.expr)
                        else:
                            if name !='_':
                                _expr = find_node(self.langlet.parse("(%s and this.tag == '%s')"%(s_expr_1, name)), self.symbol.expr)
                            else:
                                _expr = find_node(self.langlet.parse("(%s)"%(s_expr_1,)), self.symbol.expr)
                del _comparison[1:]
                _comparison.append(_expr)
                _inner = self.fn.Lambda(body, ["this"])
            _lambda = self.fn.Lambda( self.fn.Tuple(filter_type, _inner),[])
            return self.fn.trailer(".", "search"), \
                   self.fn.trailer("(", self.fn.arglist(self.fn.argument(self.fn.test(_lambda))),")")
        elif find_node(node, self.fn.token.DOUBLECOLON):
            # .X :: Y
            locname = find_node(node, self.fn.token.NAME)[1]
            chain = self.node_stack(node)
            nd, chain = chain.step() # trailer
            nd, chain = chain.step() # power
            j = 1000
            for i, item in enumerate(nd[1:]):
                if find_node(item, self.fn.token.DOUBLECOLON):
                    break
                if find_node(item, self.fn.symbol.arglist):
                    j = i

            if j == i-1:
                _str = find_node(nd, self.fn.token.STRING)
                _str[1] = "'"+_str[1][1:-1]+":"+locname+"'"
                del nd[i+1]
            else:
                prefix  = find_node(nd[i], self.fn.token.NAME)[1]
                nd[i]   = self.fn.trailer(".", "child")
                nd[i+1] = self.fn.trailer("(",
                            self.fn.arglist(
                                self.fn.argument(
                                    self.fn.test(
                                        self.fn.String(prefix+":"+locname)))),
                                        ")")
            return nd


    @transform #_dbg("sn")
    def p4d_compound_stmt(self, node):
        "p4d_compound_stmt: ['elm' | NAME '='] p4d_element ':' p4d_suite"
        self.unmark_node(node)
        # transform this into a comma separated list of items if two or more entries are found
        # otherwise return just this entry
        # chain = self.node_stack(node)

        p4d_node = self.build_p4d_compound_stmt(node)
        S = self.p4d_string(p4d_node)

        if p4d_node.tag.startswith("bl:"):
            tagwrapper = self.fn.test(
                                self.fn.CallFunc("Bytelet",
                                    [self.fn.CallFunc("mapeval",[
                                            [self.token.STRING,S],
                                                self.fn.CallFunc("globals",[]),
                                                self.fn.CallFunc("locals",[])])]))

        elif p4d_node.tag.startswith("bl-schema:"):
            tagwrapper = self.fn.test(
                            self.fn.CallFunc("ByteletSchema",
                                    [self.fn.CallFunc("mapeval",[
                                        [self.token.STRING,S],
                                            self.fn.CallFunc("globals",[]),
                                            self.fn.CallFunc("locals",[])])]))
        else:
            tagwrapper = self.fn.test(
                            self.fn.CallFunc("P4D",
                                [self.fn.CallFunc("mapeval",[
                                    [self.token.STRING,S],
                                    self.fn.CallFunc("globals",[]),
                                    self.fn.CallFunc("locals",[])])]))

        _name = find_node(node, self.token.NAME, depth = 1)
        if _name:
            return self.fn.stmt(self.fn.Assign(_name, tagwrapper))
        if find_node(node, self.keyword["elm"], depth = 1):
            name_fragments = find_all(find_node(node, self.symbol.p4d_name), self.token.NAME)
            if len(name_fragments) == 1:
                obj_name = name_fragments[0][1]
            else:
                prefix, obj_name = name_fragments[0][1],name_fragments[1][1]
            if obj_name in self.keyword:
                raise SyntaxError("invalid syntax. Keyword cannot be used as name. Use explicit assignment instead.")
            if '-' in obj_name:
                raise SyntaxError("invalid syntax. Hyphenated name cannot be used as Python name. Use explicit assignment instead.")
            assignment = self.fn.Assign(obj_name, tagwrapper)
            return self.fn.stmt(assignment)
        else:
            return self.fn.stmt(tagwrapper)


class InteractiveTransformer(LangletTransformer):
    def p4d_string(self, p4dnode):
        return str(p4dnode)


__superglobal__ = ["mapeval", "P4DNode", "P4D", "P4DList", "P4DName", "P4DNamespace", "P4DAccessError", "P4DContentList", "Bytelet", "ByteletSchema", "LEN", "Hex", "Bin", "VAL", "RAWLEN"]

