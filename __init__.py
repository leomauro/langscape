#! /usr/bin/env python
#
# URL:      http://www.fiber-space.de
# Author:   Kay Schluehr <kay at fiber-space.de>
# Creation: 15 Oct 2009

import atexit
import sys

def fill_superglobals():
    import __builtin__
    import langscape.ls_exceptions

    # load exception classes into __builtin__

    for name, value in langscape.ls_exceptions.__dict__.items():
        if isinstance(value, type) and issubclass(value, Exception):
            __builtin__.__dict__[name] = value

fill_superglobals()

def load_langlet(langlet_name):
    '''
    Loads existing langlet object.
    '''
    import base.loader
    return base.loader.load_langlet(langlet_name)



def create_langlet(langlet_name,
                   parent = "python",
                   prompt  = "> ",
                   location = "",
                   source_ext = "",
                   compiled_ext = "",
                   target = "",
                   target_compiler=""):
    '''
    Creates new langlet.
    '''
    options = vars()
    import base.langlet_gen
    lgen = base.langlet_gen.LangletGenerator(options)
    lgen.run()


