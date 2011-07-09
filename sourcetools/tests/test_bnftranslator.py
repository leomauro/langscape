import pprint

from langscape.util.path import path
import langscape.util.unittest as unittest
import langscape.sourcetools.bnftranslator as bnftranslator
from langscape.csttools.cstsearch import*
from langscape.ls_const import*

class TestLeftRecElimination(unittest.TestCase):
    '''
    This test doesn't really fit into the general scheme but it is instructive after all.
    So I let it be here.
    '''

    def test_transform_recursion(self):
        A = 1
        B = 2
        X = 3
        nfa = ["A: A X | B",
        (A,0,0,A),
        {(A,0,0,A): [(A,1,0,A),(B,2,0,A)],
        (B,2,0,A): [(FIN,FEX,0,A)],
        (A,1,0,A): [(X,3,0,A)],
        (X,3,0,A): [(FIN,FEX,0,A)]}]
        bnftranslator.transform_recursion(nfa,(A,1,0,A))
        pprint.pprint(nfa[2])

    def test_eliminate_left_recursion(self):
        A = 1
        B = 2
        X = 3
        C = 4
        Y = 5
        nfa = ["A: A X Y | B | C",
        (A,0,0,A),
        {(A,0,0,A): [(A,1,0,A),(B,2,0,A),(C,4,0,A)],
        (B,2,0,A): [(FIN,FEX,0,A)],
        (C,4,0,A): [(FIN,FEX,0,A)],
        (A,1,0,A): [(X,3,0,A)],
        (X,3,0,A): [(Y,5,0,A)],
        (Y,5,0,A): [(FIN,FEX,0,A)]}]
        bnftranslator.eliminate_left_recursion(nfa)
        pprint.pprint(nfa[2])

    def test_eliminate_left_recursion_2(self):
        A = 1
        B = 2
        X = 3
        C = 4
        Y = 5
        nfa = ["A: A X Y | A B | C",
        (A,0,0,A),
        {(A,0,0,A): [(A,1,0,A),(A,6,0,A),(C,4,0,A)],
        (A,6,0,A): [(B,2,0,A)],
        (B,2,0,A): [(FIN,FEX,0,A)],
        (C,4,0,A): [(FIN,FEX,0,A)],
        (A,1,0,A): [(X,3,A)],
        (X,3,0,A): [(Y,5,0,A)],
        (Y,5,0,A): [(FIN,FEX,0,A)]}]
        # A: C (X Y | B )*
        bnftranslator.eliminate_left_recursion(nfa)
        pprint.pprint(nfa[2])

    def test_eliminate_left_recursion_3(self):
        A = 1
        B = 2
        nfa = ["A: A A A | A A | B",
        (A,0,0,A),
        {(A,0,0,A): [(A,1,0,A),(A,2,0,A),(B,3,0,A)],
        (A,1,0,A): [(A,5,0,A)],
        (A,5,0,A): [(A,6,0,A)],
        (B,3,0,A): [(FIN,FEX,0,A)],
        (A,6,0,A): [(FIN,FEX,0,A)],
        (A,2,0,A): [(A,4,0,A)],
        (A,4,0,A): [(FIN,FEX,0,A)]}]
        # A: B (A | A A)*
        bnftranslator.eliminate_left_recursion(nfa)
        pprint.pprint(nfa[2])

class TestBNFTranslator(unittest.TestCase):
    def test_c_bnf_to_ebnf(self):
        c_grammar_pth = path(__file__).dirname().joinpath("c.g")
        c_token_pth = path(__file__).dirname().joinpath("token.g")

        grammar = bnftranslator.convertbnf(c_grammar_pth, c_token_pth)
        # The 'and_expression' rule is an example of a BNF -> EBNF rule conversion
        self.assertTrue(grammar.find("and_expression: equality_expression ('&' equality_expression)*")>0)


unittest.run_unittest(TestLeftRecElimination)
unittest.run_unittest(TestBNFTranslator)



