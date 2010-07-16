###############  langlet transformer definition ##################

from langscape.util.path import path
from langlet_config import parent_langlet
from langscape.base.loader import BaseClass
from langscape.csttools.cstutil import*
from langscape.csttools.cstsearch import*
from langscape.base.transformer import transform, transform_dbg, t_dbg

class LangletTransformer(BaseClass("Transformer", parent_langlet)):
    '''
    Defines langlet specific CST transformations.
    '''
    @transform
    def file_input(self, node):
        if self.options.get("interactive"):  # global transformations for files
            return

        for i, nd in enumerate(node[1:]):
            if self._like_main_transform(nd, node, i+1):
                break

        for i,nd in enumerate(node[1:]):
            trans = self._import_langlet_trans(nd)
            if trans:
                node.insert(i+1, trans)
                break

    def is_main(self, node):
        _if_stmt = find_node(node, self.symbol.if_stmt, depth = 3)
        if _if_stmt is None:
            return False
        elif len(_if_stmt)>4:
            return self.fn.match_token_seq(_if_stmt, ["if", "__name__", "=="])
        else:
            return False

    def _future(self, node):
        _import_stmt = find_node(node, self.symbol.import_stmt, depth=3)
        if _import_stmt:
            return self.fn.match_token_seq(_import_stmt, ["from", "__future__"])
        return False

    def _import_langlet_trans(self, node):
        if self._future(node):
            return False
        load_langlet = 'import langscape; __langlet__ = langscape.load_langlet("%s")\n'%self.langlet.config.langlet_name
        return find_node(self.langlet.parse(load_langlet), self.symbol.stmt)

    def _like_main_transform(self, node, tree, i):
        if self.is_main(node):
            _suite = find_node(node, self.symbol.suite)
            _func_def_suite   = _suite[:]
            def__like_main__  = self.fn.stmt(
                                        self.fn.compound_stmt(
                                            self.fn.funcdef("def", self.fn.Name("__like_main__"),
                                                            self.fn.parameters(),
                                                            _func_def_suite)))
            tree.insert(i, def__like_main__)
            call__like_main__ = self.fn.CallFunc("__like_main__", [])
            replace_node(_suite, self.fn.suite(self.fn.stmt(call__like_main__)))
            return True
        return False


__superglobal__ = []
