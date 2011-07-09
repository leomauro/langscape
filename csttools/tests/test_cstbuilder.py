import langscape.util.unittest as unittest
import langscape.csttools.cstbuilder
from langscape.csttools.cstsearch import find_node, find_all
from langscape.csttools.cstbuilder import CSTBuilder

class TestCSTBuilderTestlist(unittest.TestCase):
    def setUp(self):
        import langscape
        self.python = langscape.load_langlet("python")
        self.cstbuilder = CSTBuilder(self.python)
        self.symbol = self.python.parse_symbol
        self.token = self.python.parse_token

    def test_testlist(self):
        node = find_node(self.python.parse("A, B\n"), self.symbol.testlist)
        self.cstbuilder.build_cst(self.symbol.testlist, node)

    def test_expr(self):
        node = find_node(self.python.parse("A\n"), self.symbol.expr)
        self.cstbuilder.build_cst(self.symbol.testlist, node)

    def test_number(self):
        self.cstbuilder.build_cst(self.symbol.testlist, "1")

    def test_string(self):
        self.cstbuilder.build_cst(self.symbol.testlist, '"1"')

    def test_number_sequence(self):
        self.cstbuilder.build_cst(self.symbol.testlist, "1", "3")

class TestCSTBuilderFileInput(unittest.TestCase):
    def setUp(self):
        import langscape
        self.python = langscape.load_langlet("python")
        self.cstbuilder = CSTBuilder(self.python)
        self.symbol = self.python.parse_symbol
        self.token = self.python.parse_token

    def test_testlist(self):
        stmt = find_node(self.python.parse("A\n"), self.symbol.stmt)
        self.cstbuilder.build_cst(self.symbol.file_input, stmt)
        stmt = find_node(self.python.parse("A\n"), self.symbol.atom)


class TestCSTInterpolation(unittest.TestCase):
    def setUp(self):
        import langscape
        self.p4d = langscape.load_langlet("p4d")
        self.cstbuilder = CSTBuilder(self.p4d)
        self.symbol = self.p4d.parse_symbol
        self.token = self.p4d.parse_token

    def test_or(self):
        nd = self.p4d.fn.or_test("x", "y", "0")
        self.p4d.check_node(nd)
        kwd_or = self.p4d.parse_nfa.keywords["or"]
        self.assertTrue(len(find_all(nd, kwd_or)) == 2)

    def test_import(self):
        nd = self.p4d.fn.import_name("x")
        self.p4d.check_node(nd)



class TestCSTInterpolationGallery(unittest.TestCase):
    def setUp(self):
        import langscape
        self.langlet = langscape.load_langlet("gallery")
        self.cstbuilder = CSTBuilder(self.langlet)
        self.symbol = self.langlet.parse_symbol
        self.token = self.langlet.parse_token

    def test_def_func(self):
        suite = self.langlet.fn.suite(self.langlet.fn.print_stmt("a"))
        cst = self.langlet.fn.funcdef("def", "foo", self.langlet.fn.parameters("(", ")"), suite)
        self.langlet.check_node(cst)

    def test_return(self):
        self.langlet.fn.return_stmt("a")


unittest.run_unittest(TestCSTBuilderTestlist)
unittest.run_unittest(TestCSTBuilderFileInput)
unittest.run_unittest(TestCSTInterpolation)
unittest.run_unittest(TestCSTInterpolationGallery)

