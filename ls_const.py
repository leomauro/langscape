# Custom langlets can be added to the LANGLETPATH. Only absolute module paths
# of the kind A.B.C ... are allowed.

LANGLETPATH = ["langscape.langlets"]

# default indent value

TABWIDTH = 4
INDENT = " "*TABWIDTH

# specifies default compiler type -- change this for alternative Python implementations

target_compiler = "cpython"

TOKEN_OFFSET      = 100
KEYWORD_OFFSET    = 500
SYMBOL_OFFSET     = 1000
LANGLET_ID_OFFSET = 10000

