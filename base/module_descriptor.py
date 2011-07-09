import sys
import os
from langscape.util.path import path

def get_fs_path(path_fragment):
    F = path(os.getcwd())
    P = path(path_fragment)
    FP = F.joinpath(P)
    if FP.isfile():
        return FP
    if P.isfile():
        return P
    fragments = P.split(os.sep)
    for i, item in enumerate(fragments):
        if item in (".", ".."):
            F = F.dirname()
        elif i>0:
            P = path(os.sep.join(fragments[i:]))
            FP = F.joinpath(P)
            if FP.isfile():
                return FP
            break
    raise IOError("Can't open file '%s'"%path_fragment)


class LangletModuleDescriptor(object):
    def __init__(self):
        self.is_main        = False   # True if module is __main__, False else
        self.fpth_mod_input = None    # corresponds to user input
        self.fpth_mod_full  = None    # corresponds to proper file path
        self.module_path    = None    # full module path: a.b.c
        self.module_pack    = None    # package of this path a.b
        self.module_name    = None    # module c

    def compute_module_path(self):
        '''
        Computes module path from user input file-path fragment.
        '''
        self.fpth_mod_full = get_fs_path(self.fpth_mod_input)
        if os.sep in self.fpth_mod_input:
            module_path = []
            self.module_name = path(self.fpth_mod_full.basename()).splitext()[0]
            module_path.append(self.module_name)
            k = len(self.fpth_mod_input.split(os.sep))-1
            F = self.fpth_mod_full.dirname()
            while k:
                if F.joinpath("__init__.py").isfile():
                    module_path.insert(0, F.basename())
                else:
                    if F not in sys.path:
                        sys.path.append(F)
                    break
                F = F.dirname()
                k-=1
            else:
                if F not in sys.path:
                    sys.path.append(F)
            self.module_path = ".".join(module_path)
        else:
            F = self.fpth_mod_full.dirname()
            if F not in sys.path:
                sys.path.append(F)
            self.module_path = self.module_name = self.fpth_mod_input.splitext()[0]


if __name__ == '__main__':
    md = LangletModuleDescriptor()
    md.fpth_mod_input = r"tests\demo.py"
    md.compute_module_path()
    assert md.module_path == "tests.demo"



