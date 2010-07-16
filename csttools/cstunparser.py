__all__ = ["Unparser"]

from langscape.trail.nfadef import tokenstring, INTRON_NID
from langscape.csttools.cstsearch import find_node, find_all_token
from langscape.ls_const import INDENT

# used by formatter

ischar  = lambda c: c.isalnum() or c == "_"
isop    = lambda c: c in "+~*/&%|"
isquote = lambda c: c == "'" or c == '"'
iscmp   = lambda c: c in "!=<>"

# formatting types
F_CUSTOM = 1
F_EXACT  = 2

class UnparserMeta(type):
    def __init__(cls, name, bases, dct):
        super(UnparserMeta, cls).__init__(name, bases, dict)
        setattr(cls, "formatters", {})
        classes = list(bases)+[cls]
        for C in bases:
            cls.formatters.update(C.formatters)
        for f in cls.__dict__:
            if f.startswith("format_"):
                cls.formatters[f] = cls.__dict__[f]

class Unparser:
    __metaclass__ = UnparserMeta
    def __init__(self, langlet, **kwd):
        self.symbol    = langlet.parse_symbol
        self.token     = langlet.parse_token
        self.keywords  = langlet.parse_nfa.keywords
        self.last_printed = ''
        self.f_type = F_EXACT
        self.indent_level = 0
        self.offset = langlet.langlet_id
        self.output = [""]
        self.__dict__.update(kwd)

    def reset(self):
        self.last_printed = ''
        self.output = [""]

    # token specific handler

    def get_name(self, tok):
        return self.token.tok_name.get(tok[0]+self.offset) or self.token.tok_name.get(tok[0])

    def handle_ENDMARKER(self, node, intron = ""):
        pass

    def _indent(self, modify=0):
        self.output.append(INDENT * (self.indent_level+modify))

    def handle_NEWLINE(self, node, intron = ""):
        if intron:
            entry = intron[:1+intron.rfind("\n")]
        else:
            entry = "\n"
        self.output.append(entry)
        self._indent()

    def handle_INDENT(self, node, intron = ""):
        self.indent_level+=1
        self.output.append(INDENT)

    def handle_DEDENT(self, node, intron = ""):
        self.indent_level-=1
        last = self.output.pop()
        self.output.append(last[:-len(INDENT)])

    # public method

    def unparse(self, node):
        """Writes a node's equivalent source code to the output object.

        @raise TypeError: If the node's type is unknown.
        """
        self.reset()
        stream = find_all_token(node)
        for tok in stream:
            text = tok[1]
            if isinstance(text, tokenstring):
                intron = text.ext
            else:
                intron = ""
            name = self.get_name(tok)
            # print "TOKEN", len(tok), tok, [intron], type(tok[1]), name
            if name and hasattr(self, "handle_"+name):
                method = getattr(self, "handle_"+name)
                method(tok, intron = intron)
            else:
                self._format(tok, intron)
            self.last_node = tok
            #print "\n-------------\n"+self.format()+"\n----------------"
        S = "".join(self.output).lstrip('\n')
        return S

    # formatting functions

    def _format(self, tok, intron = ""):
        if intron:
            # print "F-INTRON", [self.output[-1], tok[1], intron]
            self._format_with_intron(intron, tok)
            self.f_type = F_EXACT
        else:
            # print "F-CHAR", [self.output[-1], tok]
            last = self.output[-1]
            text = tok[1]
            if not last:
                self.output.append(text)
                return
            c0 = last[-1]
            c1 = (text[0] if text else "")

            for formatter in self.formatters.values():
                res = formatter(self, c0, c1, text)
                if res:
                    self.output.append(res)
                    break
            else:
                self.output.append(text)
            self.f_type = F_CUSTOM

    def _format_with_intron(self, intron, tok):
        text = tok[1]
        if self.f_type == F_CUSTOM:
            last = self.output[-1]
            if last and last[-1] in "([{":
                self.output.append(text)
            else:
                self.output.append(intron+text)
        else:
            self.output.append(intron+text)


    def ischar(self, c):
        return c.isalnum() or c == "_"

    def isop(self, c):
        try:
            return c in "+~*/&%|"
        except TypeError:
            print c
            raise

    def isquote(self, c):
        return c == "'" or c == '"'

    def iscmp(self, c):
        return c in "!=<>"

    # special formatters

    def format_op(self, c0, c1, text):
        if self.isop(c1):
            if self.ischar(c1) and self.output[-1] in self.keywords:
                return " "+text
            elif c0 in ",;":
                return " "+text
            else:
                return text

    def format_char(self, c0, c1, text):
        if self.ischar(c1):
            if self.ischar(c0):
                return " "+text
            elif self.isquote(c0):
                return " "+text
            elif c0 in "!=<>,:;)]}":
                return " "+text
            else:
                return text

    def format_left(self, c0, c1, text):
        if c1 in "([{":
            if c0 in "=!:,;'\"":
                return " "+text
            else:
                return text

    def format_quote(self, c0, c1, text):
        if self.isquote(c1):
            if c0 in " .[({":
                return text
            else:
                return " "+text

    def format_cmp(self, c0, c1, text):
        if self.iscmp(c1):
            if c0 in ".[({":
                return text
            else:
                return " "+text


if __name__ == '__main__':
    source = open(r"C:\lang\Python25\Lib\site-packages\langscape\csttools\cstunparser.py").read()
    import pprint
    import langscape
    import cProfile as profile
    coverage = langscape.load_langlet("coverage")
    coverage.options["refactor_mode"] = True
    cst = coverage.parse(source)
    S = coverage.unparse(cst)
    print S
