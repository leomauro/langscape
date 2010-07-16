import pprint

import langscape.util.unittest as unittest

from langscape.phrasetools.codetemplate import*
from langscape.csttools.cstsearch import*

python = langscape.load_langlet("python")

class TestCodeTemplate(unittest.TestCase):
    def setUp(self):
        self.target="""
        mgr   = (EXPR)
        exit  = mgr.__exit__  # Not calling it yet
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

    def test_create_template_1(self):
        ct = CodeTemplate(python, self.target)
        self.assertEqual(find_node(ct._cst, python.parse_symbol.raise_stmt)!=None, True)

    def test_create_template_2(self):
        ct = CodeTemplate(python, self.target)
        self.assertEqual(find_node(ct._cst, python.parse_symbol.raise_stmt)!=None, True)

    def test_add_code_marker(self):
        ct = CodeTemplate(python, self.target)
        ct.mc_bla = CodeMarker()
        self.assertEqual(ct._code_marker, set(["mc_bla"]))
        self.assertEqual(ct._langlet, python)

    def test_match_empty(self):
        ct = CodeTemplate(python, self.target)
        ST = ct.match()
        self.assertEqual(ST.values(), [])


class TestCodeMarker(unittest.TestCase):
    def setUp(self):
        self.target="""
        mgr   = (EXPR)
        exit  = mgr.__exit__  # Not calling it yet
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

    def test_marker_conditions(self):
        ct = CodeTemplate(python, self.target)
        ct.cm_expr = CodeMarker(item = "EXPR")
        self.assertEqual(ct.cm_expr.conditions["item"], "EXPR")
        ct.cm_from_to = CodeMarker(start = "EXPR", end = "try")
        self.assertEqual(ct.cm_from_to.conditions["start"], "EXPR")
        self.assertEqual(ct.cm_from_to.conditions["end"], "try")
        ct.cm_all = CodeMarker(start = "EXPR", end = "try",
                               excludes = ["blub"],
                               includes = "sub")
        self.assertEqual(ct.cm_all.conditions["includes"], ["sub"])

    def test_match_item(self):
        ct = CodeTemplate(python, self.target)
        ct.cm_expr = CodeMarker(item = "EXPR")
        ST = ct.match()
        self.assertEqual(ST.cm_expr[0]!=None, True)
        sel = ST.cm_expr[0].code
        self.assertEqual(sel.langlet, python)
        self.assertEqual(len(sel.section), 1)
        self.assertEqual(sel.section[0][0][:2], [1, 'EXPR'])
        self.assertEqual(isinstance(sel.section[0][1], Chain), True)
        self.assertEqual(sel.i_l, 0)
        self.assertEqual(sel.i_r, 0)
        self.assertEqual(sel.chain._chain[0][0], python.parse_symbol.file_input)

    def test_match_multiple_items(self):
        ct = CodeTemplate(python, self.target)
        ct.cm_exc = CodeMarker(item = "exc")
        ct.cm_None = CodeMarker(item = "None")
        ST = ct.match()
        self.assertEqual(len(ST.cm_exc), 3)
        self.assertEqual(len(ST.cm_None), 3)

    def test_match_seq_incl_None(self):
        ct = CodeTemplate(python, self.target)
        ct.cm_None = CodeMarker(start = "(", end = ")", includes = ["None"])
        ST = ct.match()
        self.assertEqual(len(find_all(ST.cm_None[0].code.node, python.parse_token.NAME)), 3)

    def test_match_start_only(self):
        ct = CodeTemplate(python, self.target)
        ct.cm_try = CodeMarker(start = "try")
        ST = ct.match()
        self.assertEqual(len(ST.cm_try), 2)

    def test_match_end_only(self):
        ct = CodeTemplate(python, self.target)
        ct.cm_try = CodeMarker(end = "try")
        ST = ct.match()
        self.assertEqual(len(ST.cm_try), 2)

    def test_match_one_try(self):
        ct = CodeTemplate(python, self.target)
        ct.cm_try = CodeMarker(start = "try", end = ")", includes = ["None", "try"])
        ST = ct.match()
        self.assertEqual(len(ST.cm_try), 1)
        (t0,c0) = ST.cm_try[0].code.section[0]
        (t1,c1) = ST.cm_try[0].code.section[-1]
        self.assertEqual(t0[1], "try")
        self.assertEqual(t1[1], ")")

    def test_match_None_to_None(self):
        ct = CodeTemplate(python, self.target)
        ct.cm_try = CodeMarker(start = "None", end = "None")
        ST = ct.match()
        self.assertEqual(len(ST.cm_try), 3)

    def test_match_VAR_to_linebreak(self):
        ct = CodeTemplate(python, self.target)
        ct.cm_VAR = CodeMarker(start = "VAR", end = "\n", excludes = "BLOCK")
        ST = ct.match()
        self.assertEqual(len(ST.cm_VAR), 1)

    def _test_match_None_followedBy_rbrace(self):
        ct = CodeTemplate(python, self.target)
        ct.cm_None = CodeMarker(start = "None", followed_by = ")")
        ST = ct.match()
        self.assertEqual(len(ST.cm_None.selections[0].token()), 5)
        self.assertEqual(len(ST.cm_None.selections[1].token()), 3)
        self.assertEqual(len(ST.cm_None.selections[2].token()), 1)
        self.assertEqual(len(ST.cm_None.selections), 3)

    def test_match_None_followedBy_rbrace2(self):
        ct = CodeTemplate(python, self.target)
        ct.cm_None_s = CodeMarker(start = "None", excludes=["None"], followed_by = ")")
        ST = ct.match()
        self.assertEqual(len(ST.cm_None_s), 1)
        self.assertEqual(len(ST.cm_None_s[0].code.token()), 1)

    def test_match_comma_followedBy_rbrace3(self):
        ct = CodeTemplate(python, self.target)
        ct.cm_None_s = CodeMarker(start = ",", includes=["None"], excludes=[","], followed_by = ")")
        ST = ct.match()
        self.assertEqual(len(ST.cm_None_s), 1)
        self.assertEqual(len(ST.cm_None_s[0].code.token()), 2)

    def test_match_token_only(self):
        ct = CodeTemplate(python, self.target)
        ct.cm_try = CodeMarker(start = "value", end="__enter__", excludes="m")
        ST = ct.match()
        self.assertEqual(len(ST.cm_try), 0)


class TestCSTTransformations(unittest.TestCase):
    def setUp(self):
        self.target="""
        mgr   = (EXPR)
        exit  = mgr.__exit__  # Not calling it yet
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

        self.if_stmt = """
        if TEST:
            BLOCK1
        elif TEST:
            BLOCK2
        else:
            BLOCK3
        """

    def test_delete_1(self):
        ct = CodeTemplate(python, self.target)
        ct.cm_VAR = CodeMarker(start = "VAR", end = "\n", excludes = ["BLOCK"])
        ST = ct.match()
        self.assertEqual(len(ST.cm_VAR), 1)
        sel = ST.cm_VAR[0].code
        nd = sel.delete()
        ct.cm_BLOCK = CodeMarker(start = "try", end = "except", excludes = ["try"])
        ST = ct.match()
        self.assertEqual(len(ST.cm_VAR), 0)
        self.assertEqual(len(ST.cm_BLOCK), 1)
        self.assertEqual(len(ST.cm_BLOCK[0].code.section), 8)

    def test_replicate_1(self):
        ct = CodeTemplate(python, self.target)
        ct.cm_enter = CodeMarker(start = "except", end = "False")
        ST = ct.match()
        self.assertEqual(len(ST.cm_enter), 1)
        sel = ST.cm_enter[0].code
        nd = sel.replicate()

    def test_replicate_2(self):
        ct = CodeTemplate(python, self.target)
        ct.cm_enter = CodeMarker(start = "exc", includes = "False", excludes=["if", "exc"], followed_by = "\n")
        ST = ct.match()
        self.assertEqual(len(ST.cm_enter), 1)
        sel = ST.cm_enter[0].code
        nd = sel.replicate()
        sel.subst("exc", [1,"__yyy__"])
        nd[0].subst("exc", [1,"__xxx__"])
        self.assertEqual(len([N for N in find_all(nd[0].top(), python.parse_token.NAME) if N[1] == "__xxx__"]),1)
        self.assertEqual(len([N for N in find_all(nd[0].top(), python.parse_token.NAME) if N[1] == "__yyy__"]),1)

    def test_replicate_3(self):
        """
        Replicate:
            value = mgr.__enter__()
        """
        ct = CodeTemplate(python, self.target)
        ct.cm_enter = CodeMarker(start = "value", end = "\n", includes = "__enter__", excludes = "exc")
        ST = ct.match()
        self.assertEqual(len(ST.cm_enter), 1)
        sel = ST.cm_enter[0].code
        nd = sel.replicate(2)
        self.assertEqual(len(nd),2)

    def test_replicate_4(self):
        """
        Replicate:
            (None, None --> , None <--)
        """
        ct = CodeTemplate(python, self.target)
        ct.cm_None = CodeMarker(start = ",", includes=["None"], excludes=[","], followed_by = ")")
        ST = ct.match()
        sel = ST.cm_None[0].code
        nd = sel.replicate(3)
        self.assertEqual(len(nd),3)
        self.assertEqual(len([n for n in find_all(nd[0].node, python.parse_token.NAME) if n[1] == 'None']), 6)

    def test_replicate_elif(self):
        ct = CodeTemplate(python, self.if_stmt)
        ct.cm_elif = CodeMarker(start = "elif", end = "BLOCK2")
        ST = ct.match()
        ST.cm_elif[0].code.replicate(2)
        self.assertEqual(len([n for n in find_all(ST.top(), python.get_kwd_id("elif")) if n[1] == 'elif']), 3)


    def test_replicate_block(self):
        ct = CodeTemplate(python, self.if_stmt)
        ct.cm_block2 = CodeMarker(start = "BLOCK2", end="\n")
        ST = ct.match()
        ST.cm_block2[0].code.replicate()
        print python.unparse(ST.top())
        self.assertEqual(len([n for n in find_all(ST.top(), python.get_kwd_id("elif")) if n[1] == 'elif']), 3)

unittest.run_unittest(TestCodeTemplate)
unittest.run_unittest(TestCodeMarker)
unittest.run_unittest(TestCSTTransformations)


