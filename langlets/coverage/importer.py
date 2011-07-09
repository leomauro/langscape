###############  langlet importer definition ##################

import re
import sys, os
from langlet_config import parent_langlet
from langscape.base.importer import dbg_import
from langscape.base.loader import BaseClass
from langscape.base.module_descriptor import LangletModuleDescriptor

class LangletModuleFilter(BaseClass("importer.ModuleFilter", parent_langlet)):
    def __init__(self, langlet):
        super(LangletModuleFilter, self).__init__(langlet)

    def define_pattern(self):
        sm = self.langlet.options.get("start_module")
        self._start_module       = sm.split(".")[0] if sm else ""
        self._pattern_default    = re.compile(r'(?P<test>test\_(?P<mod_name>\w+))')
        self._default_groups     = []
        self._deactivate_default = self.langlet.options.get("deactivate_default")

    def accept_module(self, fpth_mod):
        if not super(LangletModuleFilter, self).accept_module(fpth_mod):
            if self.dbg:
                dbg_import("module not covered: "+fpth_mod)
            return
        if self.is_mainmodule(fpth_mod):
            m = self._pattern_default.match(fpth_mod.basename())
            if m:
                self._default_groups.append(m.group(2).lower())
            self.langlet.transformer.set_module(self.langlet.importer.module_descr)
            return self
        if fpth_mod.basename() in self.module_blacklist:
            return
        if self.dbg:
            dbg_import("module_path: %s\n"%fpth_mod)
        if not self._deactivate_default:
            m = self._pattern_default.match(fpth_mod.basename())
            if m:
                md = LangletModuleDescriptor()
                md.fpth_mod_full = fpth_mod
                self._default_groups.append(m.group(2).lower())
                self.langlet.transformer.set_module(md)
                return self
            else:
                module_name = fpth_mod.splitext()[0].basename()
                if module_name in self._default_groups:
                    self._default_groups.remove(module_name)
                    md = LangletModuleDescriptor()
                    md.fpth_mod_full = fpth_mod
                    self.langlet.transformer.set_module(md)
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

    def prepare(self):
        self.langlet.options["re_compile"] = True
        self.define_pattern()

