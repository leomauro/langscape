#################  imports  #############################################

import langlet_config as config
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

