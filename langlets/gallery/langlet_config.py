##################  automatically generated #############################

LANGLET_ID = 830000

##################  user definable properties ###########################

from langscape.ls_config import*

#
# User defined command line options. Options defined here are added to the
# langscape command line options defined in langscape.ls_options
#
# Example:
#   opt.add_option("-o", "--output", dest="output",  help="Report output")
#

import langscape.ls_cmdline_options
opt = langscape.ls_cmdline_options.getoptions()

#
# compiled module suffix

compiled_ext = ".pyc"

#
# source module suffix

source_ext = ".gal"

#
# command shell prompt

prompt = "gal> "

#
# langlet name

langlet_name = "gallery"

#
# name of parent langlet

parent_langlet = "python"

#
# transformation target

target_langlet = "python"

#
# used compiler -- ( see langscape.compiler for other compiler options )

target_compiler = "cpython"



