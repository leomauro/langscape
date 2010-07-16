from markdown2 import Markdown
import langscape.langlets.p4d.xmlutils as xmlutils

markdown = Markdown()

class htmlprinter(xmlutils.xmlprinter):
    def filter(self, *args, **kwd):
        level = kwd.get("level",0)
        tag = args[0]
        if tag == "mx:Script":
            if level:
                IND_1 = " "*level*self._indentw
                IND_2 = " "*(level+1)*self._indentw
                S = markdown.convert(args[-1].rstrip())
                #S = S.replace("\n", "\\n")
                return tag, args[1], S
            else:
                return tag, args[1], S
        return args


