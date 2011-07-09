#################  imports  #############################################

import langlet_config as config
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
            self.options["refactor_mode"] = True
            Langlet._instance   = self

    def compile(self, ruledef):
        cst = self.parse(ruledef+"\n")
        self.transformer.rules = {}
        self.transformer.run(cst)
        return self.transformer.rules

    def compile_file(self, filename):
        ruledef = self.parse(open(filename).read())
        return self.compile(ruledef)



