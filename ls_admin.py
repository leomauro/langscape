# This module helps developing Langscape
# Right now it supports:
#
#   * building all langlets
#   * running tests
#

import langscape
import pprint
import sys
import traceback
from langscape.util.path import path
from langscape.base.loader import LANGLETPATH

def find_langlets():
    for pth in LANGLETPATH:
        pkg = __import__(pth, fromlist=[""])
        for p in path(pkg.__file__).dirname().dirs():
            if p.joinpath("langlet.py").isfile():
                yield p, p.basename()


def rebuild_all():
    from langscape.base.loader import load_langlet
    good = []
    bad  = []
    for _, name in find_langlets():
        print "-"*90
        print "Build %s"%name
        print "-"*90
        try:
            load_langlet(name, build_langlet = True)
        except Exception:
            e = traceback.format_exc()
            print e
            s = "Failure: %s\n"%name
            print s
            bad.append(str(name))
        else:
            good.append(str(name))
    print "-"*90
    if good:
        print "\nSucceeded to build langlets: "
        print " "+pprint.pformat(good, indent = 4, width=1).replace("'", "").replace('"', "").replace(",", "")[1:-1]
    if bad:
        print "\nFailed to build langlets:"
        print " "+pprint.pformat(bad, indent = 4, width=1).replace("'", "").replace('"', "").replace(",", "")[1:-1]
    print
    print "-"*90+"\n"


def run_tests(name = "", exclude = ()):
    '''
    This module provides limited test discovery. Unittest is not sufficient because it would reject
    non-Python modules. The strategy compprises walking through the langscape subdirectories, searching
    for directories named 'tests'. In those directories test_<name>.<suffix> files will be identified
    and executed as scripts.
    '''
    remove_pyc()
    testpaths = []
    for P in path(langscape.__file__).dirname().walkdirs():
        S = P.splitall()
        if ".hg" in S:
            continue
        elif S[-1] == "tests":
            if "langlets" in S:
                testpaths.append((P, S[-2]))
            else:
                testpaths.append((P,""))
    langlet = langscape.load_langlet("python")
    log = open("log.txt", "w")
    for pth, nm in testpaths:
        if (name and name != nm) or nm in exclude:
            continue
        for f in pth.files():
            if nm and langlet.config.langlet_name!=nm:
                print "-"*70
                print "Load Langlet: ", nm
                langlet = langscape.load_langlet(nm)
            if f.basename().startswith("test_") and f.basename().endswith(langlet.config.source_ext):
                try:
                    print >> log, f
                    langlet.run_module(f)
                except Exception, e:
                    print "Failed to run", langlet
                    print " "*15, f
                    e = traceback.format_exc()
                    print e
                    return

def remove_pyc():
    for f in path(langscape.__file__).dirname().walkfiles():
        if f.ext in (".pcv", ".pyc"):
            f.remove()


if __name__ == '__main__':
    rebuild_all()
    run_tests(name="", exclude=[])




