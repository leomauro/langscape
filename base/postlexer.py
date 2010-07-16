import sys
import pprint

from langscape.ls_const import SYMBOL_OFFSET
from langscape.trail.nfadef import INTRON_NID
from langscape.csttools.cstutil import csttoken

__all__ = ["postlex", "Postlexer"]

def postlex(f):
    '''
    Decorator used to mark post handlers.
    '''
    f.post_lex_handler = True
    return f

class Postlexer(object):
    def __init__(self, langlet):
        self.langlet   = langlet
        self.parenlev  = 0
        self.scan = None
        self.indents = []
        self._post_handler = {}
        self._refactor_mode = False
        self.stream = []
        self.lex_symbol = self.langlet.lex_symbol
        self.set_handler()

    def reset(self):
        self.stream = []
        self.indents = []
        self.scan = None
        self.parenlev = 0

    def run(self, scan):
        self.reset()
        self.set_refactor_mode()
        self.scan = scan
        for pos, tok in enumerate(scan):
            handler = self._post_handler.get(tok[0])
            if handler:
                handler(pos, tok)
            else:
                self.add_token(tok)
        self.terminate_stream()
        return self.stream

    def set_refactor_mode(self):
        self._refactor_mode = self.langlet.options.get("refactor_mode")

    def set_handler(self):
        for name in dir(self):
            obj = getattr(self, name)
            if hasattr(obj, "post_lex_handler"):
                try:
                    nid = getattr(self.lex_symbol, name)
                    self._post_handler[nid] = obj
                except AttributeError:
                    obj.im_func.post_lex_handler = False

    def get_endmarker(self):
        try:
            return self.lex_symbol.ENDMARKER
        except AttributeError:
            pass

    def get_dedent(self):
        try:
            return self.lex_symbol.DEDENT
        except AttributeError:
            return -1

    def add_token(self, tok):
        tok[0] = tok[0]-SYMBOL_OFFSET
        col = tok[-1]
        tok[-1] = (col, col+len(tok[1]))
        self.stream.append(csttoken(tok))

    def terminate_stream(self):
        ENDMARKER = self.get_endmarker()
        if ENDMARKER is None:
            return
        if self.stream:
            T = self.stream[-1]
            if T[0] == self.get_dedent():
                self.add_token([ENDMARKER, '', T[2], 0])
            else:
                self.add_token([ENDMARKER, '', T[2]+1, 0])
        else:
            self.add_token([ENDMARKER, '', 1, 0])

    @postlex
    def INTRON(self, pos, tok):
        intron = tok[:]
        intron[0] = INTRON_NID + SYMBOL_OFFSET
        self.add_token(intron)



