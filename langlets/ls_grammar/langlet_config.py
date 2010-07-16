##################  automatically generated #############################

LANGLET_ID = 760000

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
#  optional modules

optional_modules = {
	'importer': False,
}


#
# compiled module suffix

compiled_ext = ""

#
# source module suffix

source_ext = ".g"

#
# command shell prompt

prompt = "> "

#
# langlet name

langlet_name = "ls_grammar"

#
# name of parent langlet

parent_langlet = ""

#
# transformation target

target_langlet = "ls_grammar"

#
# used compiler -- ( see langscape.compiler for other compiler options )

target_compiler = "default"



