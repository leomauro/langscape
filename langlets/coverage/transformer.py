############### langlet transformer definition ##################

from langlet_config import parent_langlet
from langscape.base.loader import BaseClass
from langscape.csttools.cstutil   import*
from langscape.csttools.cstsearch import find_node, find_all, find_all_gen, find_token_gen, find_all_token
from langscape.base.transformer   import transform, transform_dbg, t_dbg

import langscape.langlets.coverage.monitor as monitor

measure_stmt = monitor.measure_stmt
measure_expr = monitor.measure_expr

def shuffle(ls1, ls2):
    res = []
    for i in range(len(ls1)):
        res.append(ls1[i])
        res.append(ls2[i])
    return res

class LangletTransformer(BaseClass("Transformer", parent_langlet)):
    '''
    Defines langlet specific CST transformations.
    '''
    def set_module(self, module_descriptor):
        self._module_descriptor = module_descriptor
        self.mon = monitor.Monitor()
        self.mon.assign_sensors(module_descriptor.fpth_mod_full)

    def get_line_info_begin(self, node):
        try:
            node_begin = node[1][2]
        except IndexError:
            token = find_token_gen(node)
            nl = 0
            for T in token:
                if len(T)>2:
                    node_begin = T[2]-nl
                    break
                else:
                    nl+=T[1].count("\n")
        return node_begin

    def get_line_info_end(self, node):
        try:
            node_end = node[-1][2]-1
        except IndexError:
            token = find_all_token(node)
            nl = 0
            for T in token[::-1]:
                if len(T)>2:
                    node_end = T[2]+nl-1
                    break
                else:
                    nl+=T[1].count("\n")
        return node_end

    def get_line_info(self, node):
        node_begin = self.get_line_info_begin(node)
        node_end   = self.get_line_info_end(node)
        return node_begin, node_end

    @transform
    def file_input(self, node):
        for sub in node[1:]:
            self.run(sub)
        super(LangletTransformer, self).file_input(node)

    @transform
    def if_stmt(self, node):
        # Set sensors in "if __name__ == '__main__':" statements
        # which correspond to __main__ only. In all other cases the statement is unreachable
        if self.is_main(node):
            if self._module_descriptor.is_main:
                for sub in node[1:]:
                    self.run(sub)
            else:
                self.unmark_node(node)

    @transform
    @t_dbg("cv", cond = lambda node, **locals: locals.get("line",-1)>=0)
    def and_test(self, node, line = -1, idx = 0):
        if find_node(node, self.keyword["and"],depth = 1):
            _not_tests = find_all(node, self.symbol.not_test, depth=1)
            for sub in _not_tests:
                if find_node(sub, self.symbol.test):
                    self.run(sub, line = line, idx = idx)
                else:
                    # find not_test nodes
                    for item in find_all_gen(node, self.symbol.atom):
                        if len(item)>2:
                            first_line = item[1][2]
                        else:
                            continue
                        if isinstance(first_line, int):
                            break
                    else:
                        continue
                    if first_line == line:
                        idx+=1
                    else:
                        line = first_line
                        idx  = 1
                    _num = self.fn.Number(len(monitor.Monitor().expr_sensors))
                    monitor.ExprSensor(first_line, idx)
                    self.run(sub, line = line, idx = idx)
                    cloned = clone_node(sub)
                    call_measure_expr = self.fn.CallFunc("measure_expr",[cloned, _num])
                    replace_node(sub, self.fn.not_test(call_measure_expr))


    @transform
    def or_test(self, node, line = -1, idx = 0):
        if find_node(node, self.keyword["or"],depth = 1):
            and_tests = find_all(node, self.symbol.and_test,depth = 1)
            for i, t in enumerate(and_tests):
                self.run(t, line = 0, idx = idx)
            for sub in and_tests:
                for item in find_all_gen(node, self.symbol.atom):
                    if len(item)>2:
                        first_line = item[1][2]
                    else:
                        continue
                    if isinstance(first_line, int):
                        break
                else:
                    continue
                if first_line == line:
                    idx+=1
                else:
                    line = first_line
                    idx  = 1
                _num = self.fn.Number(len(monitor.Monitor().expr_sensors))
                monitor.ExprSensor(first_line, idx)
                self.run(sub, line = line, idx = idx)
                cloned = clone_node(sub)
                call_measure_expr = self.fn.CallFunc("measure_expr",[cloned, _num])
                replace_node(sub, self.fn.and_test(call_measure_expr))


    @transform
    # @t_dbg("si")
    def suite(self, node):
        # special case: no use of sensors in 'if __main__...' stmts of modules that are not __main__.
        _stmts = find_all(node, self.symbol.stmt,depth = 1)
        _num = self.fn.Number(len(monitor.Monitor().stmt_sensors))

        # compile a call 'measure_stmt(_num)' into each suite
        call_measure_stmt = self.fn.CallFunc("measure_stmt",[_num])
        _sensor_stmt = self.fn.stmt(call_measure_stmt)
        IDX = 0
        for i,item in enumerate(node[1:]):
            if item[0] == self.symbol.stmt:
                if find_node(item, self.symbol.flow_stmt, depth=3):    # measure_stmt shall be execed before
                    IDX = i                                       # return, break, continue
                    break
                IDX = i
        if IDX:
            suite_begin, suite_end = self.get_line_info(node)
            monitor.StmtSensor(suite_begin, suite_end)
            _small = find_node(node[i], self.symbol.small_stmt,depth = 3)
            if _small and self.fn.is_atomic(_small) and find_node(_small, self.token.STRING):
                node.insert(IDX+2, _sensor_stmt)
            else:
                node.insert(IDX+1, _sensor_stmt)

__superglobal__ = ["measure_stmt","measure_expr","monitor"]
