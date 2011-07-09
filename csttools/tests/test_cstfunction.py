from textwrap import dedent
import langscape.util.unittest as unittest
from langscape.csttools.cstsearch import find_node, find_all_token

class TestCSTFunctionBase(unittest.TestCase):
    def setUp(self):
        import langscape
        self.python = langscape.load_langlet("python")
        self.cover  = langscape.load_langlet("coverage")
        from langscape.base.cstfunction import CSTFunction
        self.fn_py = CSTFunction(self.python)
        self.fn_cov = CSTFunction(self.cover)

    def test_split_py(self):
        src = '''
        if foo:
            print bar
        print 89
        '''
        cst = self.python.parse(dedent(src))
        self.assertEqual(len(self.fn_py.split(cst))>=2, True)

    def test_split_cov(self):
        src = '''
        if foo:
            print bar
        print 89
        '''
        cst = self.cover.parse(dedent(src))
        self.assertTrue(len(self.fn_cov.split(cst))>=2)

    def test_map(self):
        cst = self.cover.parse("del a,b\n")
        exprlist = find_node(cst, self.cover.parse_symbol.exprlist)
        testlist = self.fn_cov.map(exprlist, self.cover.parse_symbol.testlist)
        self.assertTrue(len(testlist) == 4)

    def test_normalize(self):
        cst = self.cover.parse("def foo(): pass\n")
        suite = find_node(cst, self.cover.parse_symbol.suite)
        suite_z = self.fn_cov.normalize(suite, self.cover.parse_symbol.simple_stmt,
                                               self.cover.parse_symbol.stmt)

        self.assertTrue(find_node(suite_z, self.cover.parse_token.INDENT) is not None)

    def test_match_token_seq(self):
        cst = self.cover.parse("def foo(): pass\n")
        tokenseq = find_all_token(cst)
        self.assertTrue(self.fn_cov.match_token_seq(cst, ["def", "foo", "(", ")", ":", "pass", "\n"]))
        self.assertTrue(self.fn_cov.match_token_seq(cst, ["def", "foo"]))
        self.assertFalse(self.fn_cov.match_token_seq(cst, ["foo", "("]))


class TestCSTFunctionPython(unittest.TestCase):
    def setUp(self):
        import langscape
        from langscape.langlets.python.cstfunction import LangletCSTFunction
        self.langlet = langscape.load_langlet("python")
        self.fn = LangletCSTFunction(self.langlet)

    def test_is_atomic(self):
        cst = self.langlet.parse("1+2\n")
        self.assertFalse(self.fn.is_atomic(cst))
        self.assertTrue(find_node(cst, self.langlet.parse_symbol.atom))
        self.assertTrue(self.fn.is_atomic(self.langlet.fn.Number("4")))

    def test_pprint_simple2(self):
        cst = self.langlet.parse("1+3\n")

class TestCSTFunctionCoverage(unittest.TestCase):
    def setUp(self):
        import langscape
        from langscape.langlets.python.cstfunction import LangletCSTFunction
        self.langlet = langscape.load_langlet("coverage")
        self.fn = LangletCSTFunction(self.langlet)

    def test_pprint_simple(self):
        cst = self.langlet.parse("1+2\n")

    def test_pprint_simple2(self):
        cst = self.langlet.parse("1+3\n")



unittest.run_unittest(TestCSTFunctionBase)
unittest.run_unittest(TestCSTFunctionPython)
unittest.run_unittest(TestCSTFunctionCoverage)

