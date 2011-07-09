##################  automatically generated #############################

LANGLET_ID = 330000

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
opt.add_option("-d", "--deactivate-default", dest="deactivate_default", action = "store_const", const=True, help="deactivate default pattern that recognizes modules of the kind test_xxx and xxx accordingly")
opt.add_option("-o", "--output", dest="output",  help="Report output file")
opt.add_option("-e", "--erase", dest="erase",  help="Delete all pycv files found in the directory of the main module and below", action = "store_true")

#
# compiled module suffix -- default is .pyc

compiled_ext = ".pcv"

#
# source module suffix -- default is .py

source_ext = ".py"

#
# command shell prompt -- default is '>>>'

prompt = ">>> "

#
# langlet name

langlet_name = "coverage"

#
# name of parent langlet -- default is 'python'
# if langlet has no parent the empty string '' is used

parent_langlet = "python"

#
# transformation target -- default is 'python'
# target must be non-empty

target_langlet = "python"

#
# used compiler -- ( see langscape.compiler for other compiler options )
# default is 'cpython'

target_compiler = 'cpython'


#########################################################################


