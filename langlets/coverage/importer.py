###############  langlet importer definition ##################

import re
import sys, os
from langlet_config import parent_langlet
from langscape.base.loader import BaseClass

class LangletModuleFilter(BaseClass("importer.ModuleFilter", parent_langlet)):
    def __init__(self, langlet):
        super(LangletModuleFilter, self).__init__(langlet)

    def define_pattern(self):
        sm = self.langlet.options.get("start_module")
        self._start_module       = sm.split(".")[0] if sm else ""
        self._pattern_default    = re.compile(r'(?P<test>test\_(?P<mod_name>\w+))')
        self._default_groups     = []
        self._deactivate_default = self.langlet.options.get("deactivate_default")

    def accept_module(self, module_path):
        if self.dbg:
            sys.stdout.write("run accept_module: %s\n"%module_path)
        #TODO: what happens when a module m gets imported before an associated test_m
        #      module is imported? Notify this.
        module_name = (module_path.split(os.sep)[-1]).split(".")[0].lower()
        if unicode(module_name +".py") in self.module_blacklist:
            return
        if self.dbg:
            sys.stdout.write("accept_module: module_name: %s\n"%module_name)
        if not self._deactivate_default:
            m = self._pattern_default.match(module_name)
            if m:
                self._default_groups.append(m.group(2).lower())
                self.langlet.transformer.set_module(module_path)
                return self
            elif module_name in self._default_groups:
                self._default_groups.remove(module_name)
                self.langlet.transformer.set_module(module_path)
                return self
        if module_name == self._start_module.lower():
            self.langlet.transformer.set_module(module_path)
            return self
        if self.langlet.options.get("main_module") == module_path:
            return self

class LangletImporter(BaseClass("Importer", parent_langlet)):
    '''
    Defines langlet specific import hooks.
    '''
    '''
    Specialized Importer for coverage purposes. This is delicate because not every module shall be
    covered. The basic coverage relation associates a module
    test_bla.py with a module bla.py. If for example "coverage test_all.py" is executed each test_xxx.py
    module imported by test_all is covered as well as xxx modules.
    '''
    def __init__(self, langlet):
        # sys.stdout.write("initialize coverage.importer\n")
        super(LangletImporter, self).__init__(langlet)
        self.modulefilter = LangletModuleFilter(langlet)
        self.modulefilter.dbg = self.dbg
        self.modulefilter.module_blacklist.add("test_support.py")

    def define_pattern(self):
        self.modulefilter.define_pattern()

