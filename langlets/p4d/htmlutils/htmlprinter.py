from markdown2 import Markdown
import langscape.langlets.p4d.xmlutils as xmlutils
import langscape.langlets.p4d.p4dutils as p4dutils

markdown = Markdown()

class htmlprinter(xmlutils.xmlprinter):
    def filter(self, *args, **kwd):
        level = kwd.get("level",0)
        tag = args[0]
        text = markdown.convert('\n'.join(p4dutils.shave(args[-1])))
        text = text.rstrip()
        if text.startswith("<"):
            text = "\n"+" "*(level+1)*self._indentw+text+"\n"+" "*level*self._indentw
        print "TEXT", [text]
        tag  = args[0]
        return tag, args[1], text


