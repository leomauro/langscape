import langscape.util.unittest as unittest

class Test_cstrep(unittest.TestCase):
    def setUp(self):
        import langscape
        self.python = langscape.load_langlet("python")

    def test_pprint_simple(self):
        cst = self.python.parse("1+2\n")
        self.python.pprint(cst)

    def test_pprint_simple2(self):
        cst = self.python.parse("1+3\n")


unittest.run_unittest(Test_cstrep)

