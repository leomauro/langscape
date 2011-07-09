#################  imports  #############################################

import sys
import langlet_config as config
from tbprocessing import TracebackMessageProcessor
from langscape.csttools.cstutil import*
from langscape.base.langlet import BaseLanglet

#################  Langlet Classes ######################################

class Langlet(BaseLanglet):
    _instance = None
    def __init__(self, options = {}):
        if self._instance is not None:
            self.__dict__ = self._instance.__dict__
        else:
            super(Langlet, self).__init__(options)
            self.config         = config        # langlet configuration parameters
            Langlet._instance   = self
            self._code = {}

    def map_to_python(self, node, source_langlet = None, cloned = False):
        # The range of node nid's in CPython is [0..255] for terminals and [256..512] for non-terminals
        # This differs from the ranges used by Langscape. The map_to_python() functions maps the nid's
        # of Langscape on those of Python. For Pythons own ranges see token.py and symbol.py.
        if not cloned:
            node = clone_node(node)
        try:
            node[0] = node[0]%LANGLET_ID_OFFSET
            nid = node[0]
            if nid>self.MAX_NID:
                if source_langlet:
                    raise UnknownSymbol("Cannot map node '%s' to python target"%(nid,
                                        source_langlet.get_node_name(node[0])))
                else:
                    raise UnknownSymbol("Cannot map node '%s' to python target"%nid)
            if is_keyword(nid):
                node[0] = 1
                if len(node) == 4:
                    del node[-1]
            elif is_symbol(nid):
                node[0] = nid - SYMBOL_OFFSET + 256
            elif nid < 256 and len(node) == 4:
                del node[-1]
            for i, item in enumerate(node[1:]):
                if isinstance(item, list):
                    self.map_to_python(item, source_langlet, True)
        except IndexError:
            raise           # set breakpoint here
        return node

    def register_excepthook(self, langlet):
        '''
        Register TracebackMessageProcessor instance as excepthook.
        '''
        sys.excepthook = TracebackMessageProcessor(self, langlet)

if __name__ == '__main__':
    import langscape as ls
    python = ls.load_langlet("python")
    cst = python.parse("1+2")
    print python.map_to_python(cst)
    print
    print cst
