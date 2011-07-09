#################  imports  #############################################

import sys
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
            self.config         = config
            Langlet._instance   = self

    def run_module(self, cmdline_module_path):
        super(Langlet, self).run_module(cmdline_module_path)
        # end of embedding
        output = self.options.get("output")
        if output:
            try:
                f = file(output,"w")
            except IOError:
                sys.stdout.write("ERROR: failed to open file %s. Coverage langlet uses stdout instead!", output)
                f = sys.stdout
        else:
            f = sys.stdout
        self.transformer.mon.show_report(out = f)
        if self.options.get("erase"):
            for f in module_descriptor.fpth_mod_full.dirname().walk():
                if f.ext == ".pcv":
                    f.remove()

