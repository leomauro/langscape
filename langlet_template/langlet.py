#################  imports  #########################################################

import langlet_config as config                   # langlet config parameters
from langscape.base.langlet import BaseLanglet    # base class of Langlet

#################  Langlet Class ####################################################

class Langlet(BaseLanglet):
    _instance = None
    def __init__(self, options = {}):
        if self._instance is not None:
            self.__dict__ = self._instance.__dict__
        else:
            super(Langlet, self).__init__(options)
            self.config         = config
            Langlet._instance   = self



