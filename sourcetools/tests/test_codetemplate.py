import pprint

import langscape.util.unittest as unittest
from langscape.sourcetools.codetemplate import*
from langscape.csttools.cstsearch import*

python  = langscape.load_langlet("python")
gallery = langscape.load_langlet("gallery")

simple = "a"

with_stmt = """
mgr   = (EXPR)
exit  = mgr.__exit__          # Not calling it yet
value = mgr.__enter__()
exc = True
try:
    try:
        VAR = value  # Only if "as VAR" is present
        #<VAR> = <value>
        BLOCK
    except:
        # The exceptional case is handled here
        exc = False
        if not exit(*sys.exc_info()):
            raise
        elif not exit():
            pass
        # The exception is swallowed if exit() returns true
finally:
    # The normal and non-local-goto cases are handled here
    if exc:
        exit(None, None, None)
"""

swap = '''
    temp = b
    b = a
    a = temp
'''

class TestBasicSplicing(unittest.TestCase):
    '''
    This test doesn't really fit into the general scheme but it is instructive after all.
    So I let it be here.
    '''

    def test_factorial(self):
        '''
        The following definitions are inspired by Converge's splice and quasi-quotation operators.

        Of course these functions are ordinary Python functions, not macros but when you replace eval(S)
        by langlet.parse(S, start_symbol = symbol.expr) in mk_power() you get perfectly valid splices.
        '''
        def expand_power(n, x):
            if n == 0:
                return "1"
            else:
                return x+"*"+expand_power(n-1, x)

        def mk_power(n):
            return eval("lambda x:"+expand_power(n, "x"))

        power5 = mk_power(5)

        self.assertTrue(power5(2) == 32)


class TestCodeTemplate(unittest.TestCase):
    def test_remove(self):
        ct = CodeTemplate(python, with_stmt)
        self.assertTrue(with_stmt.find("VAR = value")>0)
        ct.bind(s = Marker(start="VAR", end="value"))
        # remove code using empty substitution
        cst = ct.substitute(s = "")
        code = python.unparse(cst)
        self.assertTrue(code.find("VAR = value") == -1)

    def test_subst_block1(self):
        ct = CodeTemplate(python, with_stmt)
        code = python.untokenize(ct.tokstream)
        k = code.find("VAR = value")
        self.assertTrue(k>0)
        ct.bind(s = Marker(start="VAR", end="value"))
        # remove code using empty substitution
        cst = ct.substitute(s = "print 77")
        code = python.unparse(cst)
        self.assertTrue(code.find("VAR = value") == -1)
        self.assertTrue(code.find("print 77\n") == k)

    def test_subst_block2(self):
        ct = CodeTemplate(python, with_stmt)
        code = python.untokenize(ct.tokstream)
        k = code.find("VAR = value")
        self.assertTrue(k>0)
        ct.bind(s = Marker(start="VAR", end="value"))
        # remove code using empty substitution
        cst = ct.substitute(s = "if x == 0:\n    print 77")
        code = python.unparse(cst)
        self.assertTrue(code.find("VAR = value") == -1)
        self.assertTrue(code.find("if x == 0:\n") == k)

    def test_subst_multiples(self):
        ct = CodeTemplate(python, with_stmt)
        k = 0
        for t in ct.tokstream:
            if t[1] == "None":
                k+=1
        ct.bind(value = "None")
        ct2 = ct.from_subst(value = "42")
        for t in ct2.tokstream:
            if t[1] == "42":
                k-=1
        self.assertTrue(k == 0)

    def test_subst_simple(self):
        ct = CodeTemplate(python, simple)
        ct.bind(value = "a")
        cst = ct.substitute(value = "print 88\n")
        self.assertTrue(python.unparse(cst) == "print 88\n")

        ct = CodeTemplate(gallery, simple)
        ct.bind(value = "a")
        cst = ct.substitute(value = "print 88\n")
        self.assertTrue(gallery.unparse(cst) == "print 88\n")

    def test_syntax_error(self):
        ct = CodeTemplate(python, "a = b\n")
        ct.bind(a = "a")
        ct.bind(b = "b")
        self.assertRaises(SyntaxError, ct.substitute, {"a":"assert"})
        self.assertRaises(SyntaxError, ct.substitute, {"b":"assert"})

    def test_unbind(self):
        ct = CodeTemplate(python, "a = b\n")
        ct.bind(a = "a")
        ct.bind(b = "b")
        cst = ct.substitute(a = "x", b="y")
        self.assertTrue(python.unparse(cst) == "x = y\n")
        ct.unbind("a")
        cst = ct.substitute(a = "x", b="y")
        self.assertTrue(python.unparse(cst) == "a = y\n")
        ct.bind(a = "a")
        ct.unbind("b")
        cst = ct.substitute(a = "x", b="y")
        self.assertTrue(python.unparse(cst) == "x = b\n")
        ct.unbind_all()
        cst = ct.substitute(a = "x", b="y")
        self.assertTrue(python.unparse(cst) == "a = b\n")

    def test_subst_strict(self):
        ct = CodeTemplate(python, "a = b\n")
        ct.bind(a = "a")
        ct.bind(b = "b")
        ct.strict_substitute(a = "x", b="y")
        self.assertRaises(KeyError, ct.strict_substitute, {"a":"x"})
        self.assertRaises(KeyError, ct.strict_substitute, {"a":"x", "b":"y","c":"z"})

    def test_big_switch(self):
        switch = """
            switch EXPR:
                case COND:
                    BLOCK
            else:
                ELSE_BLOCK

        """
        ct = CodeTemplate(gallery, switch)
        ct.bind(else_block = "ELSE_BLOCK")
        cst = ct.substitute(else_block = "print 88")

        ct.bind(case = Marker(start = "case", end = "BLOCK"))
        ct2 = ct.from_subst(case = "\n".join("case COND%d:\n    BLOCK%d"%(i,i) for i in range(5)) )

        D = dict((a+str(i), b+str(i)) for i in range(5) for (a,b) in (("cond", "COND"), ("block", "BLOCK")))
        D["else"] = "ELSE_BLOCK"
        D["expr"] = "EXPR"
        ct2.bind(**D)
        D["expr"]  = "n"
        D["else"]  = "print 'Only single-digit numbers are allowed.'"
        D["cond0"] = "0"
        D["cond1"] = "(1, 4, 9)"
        D["cond2"] = "2"
        D["cond3"] = "(3, 5, 7)"
        D["cond4"] = "(6, 8)"
        D["block0"]= "print 'you typed zero'"
        D["block1"]= "print 'n is a perfect square'"
        D["block2"]= "print 'n is an even number'"
        D["block3"]= "print 'n is a prime number'"
        D["block4"]= "print 'n is an even number'"
        cst = ct2.substitute(**D)
        print
        print gallery.unparse(cst)

    def test_loop(self):
        def loop(n):
            ct = PyCodeTemplate(python, with_stmt)
            for i in range(n):
                ct.bind(block = "BLOCK")
                ct.local_names("value", "exit", "exc", "mgr")
                ct = ct.from_subst(block = with_stmt)
            return ct.source
        loop(5)

class TestCodeTemplateWithCapture(unittest.TestCase):
    def test_with_capture(self):
        ct = CodeTemplate(python, swap)
        ct.bind(x = "a", y = "b")
        cst = ct.substitute(x = "temp", y="y")
        code = python.unparse(cst)
        D = {"temp":7, "y":8}
        exec code in D
        self.assertTrue(D["temp"] == D["y"] == 8)

    def test_without_capture(self):
        ct = CodeTemplate(python, swap)
        ct.bind(x = "a", y = "b")
        ct.local_names("temp")
        cst = ct.substitute(x = "temp", y="y")
        code = python.unparse(cst)
        D = {"temp":7, "y":8}
        exec code in D
        self.assertTrue(D["temp"] == 8)
        self.assertTrue(D["y"] == 7)


unittest.run_unittest(TestBasicSplicing)
unittest.run_unittest(TestCodeTemplate)
unittest.run_unittest(TestCodeTemplateWithCapture)




