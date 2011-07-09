###############  langlet transformer definition ##################

from langlet_config import parent_langlet
from langscape.base.loader import BaseClass
from langscape.csttools.cstutil import*
from langscape.csttools.cstsearch import*
from langscape.base.transformer import transform, transform_dbg, t_dbg

import random
import chainlet
import ip
from chainlet import Chainlet

def isChainlet(obj):
    return isinstance(obj,Chainlet)


class LangletTransformer(BaseClass("Transformer", parent_langlet)):
    '''
    Defines langlet specific CST transformations.
    '''

    @transform
    def IPv4Address(self, node):
        nd = find_node(node, self.token.IPv4Address)
        if nd:
            sub = nd[1].split(".")
            T = self.fn.Tuple(*sub)
            return self.fn.atom('(', self.fn.testlist_comp(self.fn.CallFunc("ip.IPv4", [T])),')')

    @transform
    def thunk_stmt(self, node):
        "thunk_stmt: small_stmt ':' suite"
        small = find_node(node, self.symbol.small_stmt)

        # perform checks on expression form NAME '=' NAME for small_stmt
        # and extract names

        _expr_stmt = find_node(small, self.symbol.expr_stmt)
        if not _expr_stmt:
            raise SyntaxError("thunk_stmt is required to have the form:  NAME = NAME ':' SUITE")
        if len(_expr_stmt) == 4:
            nid, tl1, eq, tl2 = _expr_stmt
            if not ( is_node(tl1, self.symbol.testlist) and \
                     is_node(eq,  self.token.EQUAL) and \
                     is_node(tl2, self.symbol.testlist)):
                raise SyntaxError("thunk_stmt must have the form:  NAME = NAME ':' SUITE")
            a1, a2 = smallest_node(tl1), smallest_node(tl2)
            if not ( is_node(a1, self.token.NAME) and \
                     is_node(a2, self.token.NAME)):
                raise SyntaxError("thunk_stmt must have the form:  NAME = NAME ':' SUITE")
            Name = find_node(a1, self.token.NAME,depth = 1)
            Func = find_node(a2, self.token.NAME,depth = 1)
            if Name is None or Func is None:
                raise SyntaxError("thunk_stmt must have the form:  NAME = NAME ':' SUITE")
        else:
            raise SyntaxError("thunk_stmt must have the form:  NAME = NAME ':' SUITE")

        name, func = Name[1], Func[1]
        returns    = self.fn.stmt(self.fn.Return(self.fn.CallFunc("locals",[])))
        BLOCK      = self.fn.add_to_suite(find_node(node, self.symbol.suite), returns)
        thunk      = self.fn.stmt(self.fn.Function("thunk", BLOCK, ()))
        thunk_call = self.fn.stmt(self.fn.Assign(name,
                                    self.fn.CallFunc(func,
                                                     dstar_args = self.fn.CallFunc("thunk",[]))))
        del_thunk  = self.fn.stmt(self.fn.Del("thunk"))
        return [thunk, thunk_call, del_thunk]

    @transform
    def if_stmt(self, node):
        "if_stmt: 'if' test [ as_name ] ':' suite ('elif' test [ as_name ] ':' suite)* ['else' ':' suite]"
        #
        # if test as x:
        #    BLOCK
        #
        #  --------->
        #
        # __d = {}
        # if __d.__setitem__("x", test) or __d["x"]:
        #    x = __d["x"]
        #    BLOCK
        # del __d
        #
        #

        if not find_node(node, self.symbol.as_name,depth = 1):
            return

        __d = "__d_"+str(random.randrange(100000))
        __d_assign = self.fn.stmt(self.fn.Assign(__d, self.fn.Dict()))
        __d_del    = self.fn.stmt(self.fn.Del(__d))
        nodes = node[1:]
        new_if = [self.symbol.if_stmt]
        i = 0
        while i<len(nodes):
            item = nodes[i]
            if is_node(item, self.symbol.test):
                _test = item
                if is_node(nodes[i+1], self.symbol.as_name):
                    _suite = nodes[i+3]
                    name = find_all(nodes[i+1], self.token.NAME)[-1][1]
                    new_if.append(
                        self.fn.Or(
                            self.fn.CallFunc("%s.%s"%(__d, "__setitem__"), [self.fn.String(name),_test]),
                            self.fn.GetItem(__d, self.fn.String(name))))
                    new_if.append(nodes[i+2])
                    name_assign = self.fn.stmt(self.fn.Assign(name, self.fn.GetItem(__d, self.fn.String(name))))
                    new_if.append(self.fn.add_to_suite(_suite, name_assign, 0))
                    i+=4
                    continue
                else:
                    new_if.append(item)
            else:
                new_if.append(item)
            i+=1
        return [__d_assign, self.fn.stmt(new_if), __d_del]

    @transform
    def repeat_stmt(self, node):
        "repeat_stmt: 'repeat' ':' suite 'until' ':' (NEWLINE INDENT test NEWLINE DEDENT | test NEWLINE )"
        _suite = find_node(node, self.symbol.suite)
        _test  = find_node(node, self.symbol.test, depth=1)
        _until = self.fn.if_stmt(_test, self.fn.suite(self.fn.stmt(self.fn.break_stmt())))
        _suite.insert(-1, self.fn.stmt(_until))
        return self.fn.stmt(self.fn.While(True, _suite))

    @transform
    def switch_stmt(self, node):
        "switch_stmt: 'switch' expr ':' NEWLINE INDENT case_stmt DEDENT ['else' ':' suite]"
        # this implementation uses only basic CST functions
        # derived from grammar rules as well as CST interpolation
        SELECT  = "SELECT_"+str(random.randrange(100000))
        _test   = node[2]
        _case   = find_node(node, self.symbol.case_stmt, depth = 1)
        _else   = find_node(node, self.symbol.suite, depth = 1)

        _cond   = self.fn.power("isChainlet", self.fn.trailer("(", _test, ")"))
        _select = self.fn.testlist(SELECT)
        assign_else = self.fn.stmt(self.fn.expr_stmt(_select,"=", _test))
        _testlist   = map(self.fn.test, find_all(_case, self.symbol.expr, depth = 1))
        select_args = self.fn.arglist(*map(self.fn.argument, _testlist))
        trailer_select      = self.fn.trailer(".", "select")
        trailer_select_args = self.fn.trailer("(", select_args, ")")
        call_select = self.fn.power( self.fn.atom("(",_test, ")"),
                                     trailer_select,
                                     trailer_select_args)
        assign_if   = self.fn.stmt(self.fn.expr_stmt(SELECT,"=",call_select))
        if_chainlet = self.fn.stmt(self.fn.if_stmt(
                                        _cond,
                                        self.fn.suite(assign_if),
                                        'else',
                                        self.fn.suite(assign_else)))
        if_case     = self.fn.stmt(self._handle_case_stmt(_case,_select,_else))
        del_select  = self.fn.stmt(self.fn.del_stmt(SELECT))
        return if_chainlet, if_case, del_select

    def _handle_case_stmt(self, node, _select, _else_suite = None):
        "case_stmt: 'case' expr ':' suite ('case' expr ':' suite)*"
        _tests   = map(self.fn.test, find_all(node, self.symbol.expr,depth = 1))
        _suites  = find_all(node, self.symbol.suite,depth = 1)
        _select  = find_node(_select, self.symbol.expr)
        _conds   = [self.fn.comparison(find_node(test, self.symbol.expr),"==",_select) for test in _tests]
        if_input = sum(map(list, zip(_conds,_suites)),[])
        for i in range(len(if_input)-2,1,-2):
            if_input.insert(i, "elif")
        if _else_suite:
            if_input.append("else")
            if_input.append(_else_suite)
        return self.fn.if_stmt(*if_input)

__superglobal__ = ["isChainlet", "Chainlet", "ip"]
