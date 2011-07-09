# Module ls_config.py
# ===================

# This module is used to define names, visible in each langlet. Hence it serves as a global
# configuration file for Langscape.
#
# The names can be overwritten in langlets, their sub-langlets and so on.
#
# If A, B are langlets and B.parent_langlet == 'A'. If N is a name defined in ls_config.py
# then:
#
#       B.langlet_config.N    overwrites
#       A.langlet_config.N    overwrites
#       ls_config.N
#
# If a name is available in ls_config.py its presence in langlet_config.py is optional.

# ---------------------------------------------------------------------------------------

encoding = ""

# ---------------------------------------------------------------------------------------
# If the following option is set the compiled module will be removed after execution.
# This is useful when module execution depends on temporary data created during
# transformation which won't be cached in the compiled module

remove_compiled_after_exec = False

# ---------------------------------------------------------------------------------------
# specifies default compiler type -- change this for hosting langscape on an alternative
# Python implementations

target_compiler = "cpython"




