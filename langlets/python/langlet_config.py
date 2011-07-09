##################  automatically generated #############################

LANGLET_ID = 0

##################  user definable properties ###########################

from langscape.ls_config import*

from langscape.ls_cmdline_options import getoptions
opt = getoptions()

# add langlet specific options here. Example:
#
#     opt.add_option("-o", "--output", dest="output",  help="Report output")



# compiled module suffix -- default is .pyc

compiled_ext = ".pyc"

# source module suffix -- default is .py

source_ext = ".py"

# command shell prompt -- default is '>>>'

prompt = ">>> "

#
# langlet name ( mandartory )

langlet_name = "python"

#
# name of parent langlet -- default is 'python'
# if langlet has no parent the empty string '' is used

parent_langlet = ''

#
# transformation target -- default is 'python'
# target must be non-empty

target_langlet = "python"

# used compiler -- default is 'cpython'
# see langscape.compiler for other compiler options
#

target_compiler = "cpython"

#########################################################################


