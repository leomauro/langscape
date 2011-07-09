# Module defining global constants
# ================================

# ---------------------------------------------------------------------------------------
# default indent value

TABWIDTH = 4
INDENT = " "*TABWIDTH

# ---------------------------------------------------------------------------------------
# offsets defining symbol categories. For each langlet a symbol range is defined by
#
#   langlet.langlet_id + offset + [0 .. next_offset-1]
#

TOKEN_OFFSET      = 100
KEYWORD_OFFSET    = 500
SYMBOL_OFFSET     = 1000
LANGLET_ID_OFFSET = 10000

# ---------------------------------------------------------------------------------------
# fixed node id's
INTRON_NID        = 999

# ---------------------------------------------------------------------------------------
# trail specific constants
TRAIL_SKIP    = 1
TRAIL_OPEN    = 2
TRAIL_CLOSE   = 3
TRAIL_ADD     = 4
TRAIL_CONTROL = (TRAIL_SKIP, TRAIL_OPEN, TRAIL_CLOSE, TRAIL_ADD)

# ---------------------------------------------------------------------------------------
# maximum allowed states in NFA
TRAIL_MAX_ALLOWED_STATES = 2000

# ---------------------------------------------------------------------------------------
# Special definitions used by characterizing states
FIN = -1
FEX = -1



