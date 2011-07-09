##################  automatically generated #############################

LANGLET_ID = 730000

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
opt.add_option("--xml2p4d", dest="xml2p4d", action = "store_true", help="translate xml file into p4d file")
opt.add_option("--p4d:kwd", dest="p4d_kwd", action = "store_true", help="prefixes a tag with p4d that is a P4D keyword. This is applied on writing a P4D object")


#
# compiled module suffix

compiled_ext = ".pyc"

#
# source module suffix

source_ext = ".p4d"

#
# command shell prompt

prompt = "p4d> "

#
# langlet name

langlet_name = "p4d"

#
# name of parent langlet

parent_langlet = "python"

#
# transformation target

target_langlet = "python"

#
# used compiler -- ( see langscape.compiler for other compiler options )

target_compiler = "cpython"



