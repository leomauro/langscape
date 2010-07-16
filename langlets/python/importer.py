###############  langlet importer definition ##################

# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    10 May 2006

# This module isn't generic for anything but Python derivatives and it shouldn't be used
# by Python but only by Langlets derived from Python.

from __future__ import with_statement
import sys
from langscape.util.path import path
import langscape.util.ihooks as ihooks
import zipimport
import imp
import os

__all__ = ["dbg_import", "LSImporter", "LSModuleFilter", "import_from_langlet"]

def dbg_import(text):
    # lightweight logging function
    frame  = sys._getframe()
    f_name = frame.f_back.f_code.co_name
    f_line = frame.f_back.f_lineno
    sys.stdout.write("dbg-import: %s: %s: %s\n"%(f_name, f_line, text))


class LangletHooks(ihooks.Hooks):
    def __init__(self, langlet):
        ihooks.Hooks.__init__(self)
        self.langlet = langlet
        self._search_suffixes()

    def _search_suffixes(self):
        # find suffixes and add compiled-ext and source-ext suffixes
        # if not yet available
        compiled_ext  = self.langlet.config.compiled_ext
        source_ext    = self.langlet.config.source_ext
        self.suffixes = list(ihooks.Hooks.get_suffixes(self))
        for i,(ext, code, prio) in enumerate(self.suffixes[:]):
            if compiled_ext == ext:
                break
        else:
            if not self.langlet.options.get("ignore_compiled"):
                self.suffixes.insert(0,(compiled_ext, 'rb', 2))
        for (ext, code, prio) in self.suffixes:
            if source_ext == ext:
                break
        else:
            self.suffixes.insert(1,(source_ext, 'U', 1))

    def get_suffixes(self):
        # sys.stdout.write("get_suffixes: langlet: %s\n"%self.langlet)
        # sys.stdout.write("get_suffixes: suffixes: %s\n"%self.suffixes)
        return self.suffixes


class LSModuleLoader(ihooks.ModuleLoader):

    def is_source(self, file):
        for info in self.hooks.get_suffixes():
            if file.endswith(info[0]):
                if info[-1] == 1:
                    return True
                else:
                    return False
        return False

    def find_module_in_dir(self, name, dir, allow_packages=1):
        # sys.stdout.write("find_module_in_dir: %s : %s\n"%(name, dir))
        if dir is None:
            return self.find_builtin_module(name)
        if allow_packages:
            if dir.endswith(".egg"):
                try:
                    zipimporter = zipimport.zipimporter(dir)
                    return zipimporter.find_module(name)
                except zipimport.ZipImportError:
                    return

            fullname = self.hooks.path_join(dir, name)
            if self.hooks.path_isdir(fullname):
                # path suffix might be .py for arbitrary langlets
                suffixes = self.hooks.get_suffixes()
                suffixes.append(('.py', 'U', 2))
                stuff = self.find_module_in_dir("__init__", fullname, 0)
                # drop .py suffix again. If langlet source suffix is .py
                # it was redundant anyway
                suffixes.pop()
                if stuff:
                    f = stuff[0]
                    if f:
                        f.close()
                    return None, fullname, ('', '', ihooks.PKG_DIRECTORY)
        f = ()
        for info in self.hooks.get_suffixes():
            suff, mode, typ = info
            fullname = self.hooks.path_join(dir, name+suff)
            if self.hooks.path_isfile(fullname):
                if self.hooks.langlet.options.get("re_compile"):
                    if self.is_source(fullname):
                        f = (0, fullname, mode, info )
                        break
                datetime = os.stat(fullname)[-2]
                if f:
                    if f[0] < datetime:
                        f = (datetime, fullname, mode, info )
                else:
                    f = (datetime, fullname, mode, info )
        if f:
            try:
                fp = self.hooks.openfile(f[1], f[2])
                return fp, f[1], f[-1]
            except self.hooks.openfile_error:
                pass

    def find_module(self, name, path = None):
        # if name == "demo":
        #     sys.stdout.write("find_module: suffixes: %s\n"%self.hooks.get_suffixes())
        if path is None:
            path = [None] + self.default_path()
        for dir in path:
            stuff = self.find_module_in_dir(name, dir)
            # sys.stdout.write("find_module: %s in dir: %s -> %s\n"%(name, dir, stuff))
            if stuff:
                return stuff
        return None

class ModuleFilter(object):
    def __init__(self, langlet):
        self.langlet  = langlet
        self.dbg          = langlet.options.get("debug_importer")
        self.module_blacklist = set(["langlet.py",
                                     "langlet_config.py"])
        self.dir_blacklist = set(["langscape.trail",
                                  "langscape.csttools",
                                  "langscape.base"])

    def is_langletmodule(self, fpth_m):
        return fpth_m.ext in (self.langlet.config.source_ext,
                              self.langlet.config.compiled_ext)

    def pre_filter(self, fpth_mod):
        if not path(fpth_mod).ext == u".py":
            return True
        fpth_dir = path(fpth_mod.lower()).dirname()
        if fpth_dir.basename() in ("lexdef", "parsedef", "langscape", "cstdef", "trail"):
            return False
        if fpth_mod.basename() in self.module_blacklist:
            return False
        return True

    def is_mainmodule(self, fpth_m):
        _main_mod = self.langlet.options.get("main_module")
        if _main_mod:
            module_name, _mod = _main_mod
            if module_name == fpth_m.basename():
                return True

    def accept_module(self, fpth_mod):
        '''
        Method used to determine if a langlet accepts module for langlet-specific import.
        @param fpth_mod: a path object specifying the complete module path.
        '''
        # sys.stdout.write("eeimporter.py: check-module-for acceptance %s\n"%fpth_mod)
        if self.pre_filter(fpth_mod):
            if self.dbg:
                dbg_import("pre-filtered o.k:`%s`"%fpth_mod)
            if self.is_langletmodule(fpth_mod):
                return True
            if self.is_mainmodule(fpth_mod):
                return True
        return False

class LangletImporter(object):

    def __init__(self, langlet, modfilter = ModuleFilter):
        '''
        :param langlet: langlet module object
        '''
        self.langlet      = langlet
        self.fpth_langlet = self.langlet_path()
        self.fpth_mod     = None
        self.loader       = self.module_loader()
        self.dbg          = langlet.options.get("debug_importer")
        self.modulefilter = modfilter(langlet)

    def langlet_path(self):
        return self.langlet.path

    def module_loader(self):
        return LSModuleLoader(hooks = LangletHooks(self.langlet))

    def register_importer(self):
        if self.dbg:
            dbg_import(str(self))
        pth = str(self.fpth_langlet)
        if pth not in sys.path:
            sys.path.append(pth)
        if not self in sys.meta_path:
            sys.meta_path.append(self)

    def find_module(self, mpth_mod, mpth_pack = None):
        '''
        Framework function find_module(). See

            http://www.python.org/dev/peps/pep-0302/
        '''
        if mpth_pack and ".egg" in mpth_pack[0]:  # TODO - enable zipimport of langlet modules
            return
        if mpth_mod.startswith("langscape.base."):
            mpth_mod = mpth_mod[15:]
            if mpth_pack:
                if mpth_pack[0].endswith("base"):
                    del mpth_pack[0]
        package = ""
        idx = mpth_mod.rfind(".")  # maybe dotted module name ?
        if self.dbg:
            dbg_import("input: module: `%s`"%mpth_mod)
            dbg_import("input: package:`%s`"%mpth_pack)
        if idx>0:
            package, mpth_mod = mpth_mod[:idx], mpth_mod[idx+1:]
            mpth_pack = sys.modules[package].__path__

        moduledata  = self.loader.find_module(mpth_mod, mpth_pack)

        if isinstance(moduledata, zipimport.zipimporter):
            if self.dbg:
                dbg_import("zipimport: `%s`"%mpth_mod)
            moduledata.load_module(mpth_mod)
            return

        if not moduledata:
            if self.dbg:
                dbg_import("no-data: `%s`, `%s`, `%s`"%(mpth_mod, package, mpth_pack))
            if mpth_pack:
                raise ImportError("No module named %s found at %s."%(mpth_mod, mpth_pack))
            else:
                raise ImportError("No module named %s found."%mpth_mod)
        if self.dbg:
            sys.stdout.write("dbg-importer: find_module: moduledata: `%s`\n"%(moduledata[1:],))
        if not moduledata[1]:
            return
        self.fpth_mod = path(moduledata[1])
        self.mpth_mod = mpth_mod
        # sys.stdout.write("DEBUG import_path: %s, module: %s\n"%(self.mpth_mod, self.fpth_mod))
        if self.modulefilter.accept_module(self.fpth_mod):
            if self.dbg:
                dbg_import("accept_module:`%s`"%self.fpth_mod)
            return self

    def load_module(self, fullname):
        '''
        Framework function load_module(). See

            http://www.python.org/dev/peps/pep-0302/

        :param fullname: fully qualified name e.g. 'spam.ham'
        '''
        mod = self.fpth_mod
        if self.loader.is_source(mod):
            if self.dbg:
                dbg_import("-"*(len(mod)+30))
                dbg_import("compile source: `%s`"%mod)
                dbg_import("-"*(len(mod)+30))
            self.langlet.compile_file(mod)
            compiled_module_path = mod.stripext()+self.langlet.config.compiled_ext
        else:
            compiled_module_path = mod
        if self.dbg:
            dbg_import("load compiled: `%s`\n"%compiled_module_path)
        return self.langlet.compiler.load_compiled(fullname, compiled_module_path)

    def import_module(self, fullname):
        if self.find_module(fullname):
            return self.load_module(fullname)


def import_from_langlet(langlet, fullname):
    '''
    Function used to import a module of an arbitrary langlet.

    Rationale::
        suppose you want to import a module ipconverter.gal from a Python program.
        This is easy when ipconverter.gal has been compiled already and you have the *.pyc
        file accordingly. However this may not be the case and you have to compile the
        *.gal file separately. This compilation is done on import but you can't import files
        with *.gal extensions from Python!

        The solution to this problem is to import ipconverter.gal from the gallery langlet:

            import langscape.langlets.gallery as langlet
            import_from_langlet(langlet, "<module-path-to-ipconverter>.ipconverter")

    @param langlet: langlet you want to import module from
    @param fullname: a module path
    @return: the compiled and imported module
    '''
    importer = Importer(langlet)
    importer.find_module(fullname)
    return importer.load_module(fullname)


