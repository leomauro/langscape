'''
Using grammar rules to search on text.
'''
from langscape.trail.nfatracer import TokenTracer
from langscape.trail.nfaparser import TokenStream
from langscape.base.langlet import BaseLanglet
from langscape.csttools.cstsearch import*

def get_index(string, line):
    idx = -1
    i = 1
    while i<line:
        n = string.find("\n", idx+1)
        if n>=0:
            idx = n
        else:
            break
        i+=1
    return idx

class CMatchObject(object):
    def __init__(self, string):
        self.string = string
        self.begin = 0
        self.end = 0
        self.matched = ""
        self.tokstream = None


class CSearchObject(object):
    def __init__(self, langlet, symbol):
        self.langlet = langlet
        self.symbol  = symbol
        self._condition = lambda x: True

    def get_condition(self):
        return self._condition

    def set_condition(self, value):
        assert hasattr(value, "__call__")
        self._condition = value

    condition = property(get_condition, set_condition)

    def finditer(self, string, pos = 0, endpos = -1):
        while True:
            m = self._search(string, pos, endpos)
            if m:
                yield m
                pos = m.end
            else:
                break

    def findall(self, string, pos, endpos = -1):
        return list(self.finditer(string, pos, endpos))

    def subst(self, string, repl = "", count = 0):
        S = []
        end = 0
        cm = CMatchObject("")
        for i, cm in enumerate(self.finditer(string, 0, -1)):
            if (count and i<count) or count == 0:
                if cm.begin>end:
                    S.append(string[end:cm.begin])
                if isinstance(repl, basestring):
                    S.append(repl)
                    continue
                elif hasattr(repl, "__call__"):
                    cst = self.langlet.parse(cm.tokstream, start_symbol = self.symbol)
                    cst = repl(self.langlet, cst)
                else:
                    cst = self.langlet.parse(cm.tokstream, start_symbol = self.symbol)
                    cst = self.langlet.transform(cst)
                if S and str.isspace(S[-1][-1]):
                    S.append(self.langlet.unparse(cst)+" ")
                else:
                    S.append(" "+self.langlet.unparse(cst)+" ")
                end = cm.end
        S.append(string[cm.end:])
        return "".join(S)

    def search(self, string, pos = 0, endpos = -1):
        if endpos == -1:
            endpos = len(string)
        return self._search(string, pos, endpos)

    def _search(self, string, pos, endpos):
        self.begin = 0
        self.end = 0
        S = string[pos:endpos]
        tokstream = self.langlet.tokenize(S)
        n = len(tokstream)
        tracer = TokenTracer(self.langlet, self.symbol)
        initial = tracer.selectables()
        i = 0
        while i<n:
            tok   = tokstream[i]
            if tok[0] in initial:
                selection = []
                res = None
                for j,T in enumerate(tokstream[i:]):
                    try:
                        selection = tracer.select(T[0])
                    except NonSelectableError:
                        if res is not None:
                            stream = tokstream[i:i+res+1]
                            if self.condition(stream):
                                m = CMatchObject(string)
                                m.begin = pos+get_index(S, stream[0][2])+stream[0][-1][0]+1
                                m.end   = m.begin+get_index(S[m.begin:], stream[-1][2]-stream[0][2])+stream[-1][-1][1]-stream[0][-1][0]+1
                                m.matched = string[m.begin: m.end]
                                m.tokstream = TokenStream(stream)
                                return m
                            break
                    if None in selection:
                        res = j
                tracer = TokenTracer(self.langlet, self.symbol)
            i+=1

if __name__ == '__main__':
    import langscape
    python = langscape.load_langlet("python")
    so = CSearchObject(python, python.parse_symbol.return_stmt)
    so.condition = lambda x: True
    text = open(r"C:\lang\Python25\Lib\site-packages\langscape\sourcetools\search.py").read()
    '''
    textit = so.finditer(text)
    for item in textit:
        print item.matched
    # print so.begin, so.end
    # print text[so.begin: so.end]
    '''
    def subst_return(langlet, node):
        test = find_node(node, langlet.symbol.test)
        if test:
            test[:] = langlet.fn.test(langlet.fn.CallFunc("measure", [test[:]]))
        return node

    cso = CSearchObject(python, python.parse_symbol.return_stmt)
    res = cso.subst(text, subst_return)
    print res


