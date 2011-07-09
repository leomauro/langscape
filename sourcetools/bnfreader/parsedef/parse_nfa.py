# ______________________________________________________________________
# This was automatically generated by nfagen.py.
# Hack at your own risk.

# LANGLET ID

LANGLET_ID = 980000

from langscape.util.univset import*


# trail NFAs:

nfas = {981000: ['file_input: rule* ENDMARKER',
          (981000, 0, 981000),
          {(980000, 2, 981000): [(None, '-', 981000)],
           (981000, 0, 981000): [(980000, 2, 981000), (981001, 1, 981000)],
           (981001, 1, 981000): [(980000, 2, 981000), (981001, 1, 981000)]}],
 981001: ["rule: NAME ':' rhs ';'",
          (981001, 0, 981001),
          {(980001, 1, 981001): [(980009, 2, 981001)],
           (980009, 2, 981001): [(981002, 3, 981001)],
           (980010, 4, 981001): [(None, '-', 981001)],
           (981001, 0, 981001): [(980001, 1, 981001)],
           (981002, 3, 981001): [(980010, 4, 981001)]}],
 981002: ["rhs: alt ('|' alt)*",
          (981002, 0, 981002),
          {(980013, 2, 981002): [(981003, 3, 981002)],
           (981002, 0, 981002): [(981003, 1, 981002)],
           (981003, 1, 981002): [(980013, 2, 981002), (None, '-', 981002)],
           (981003, 3, 981002): [(980013, 2, 981002), (None, '-', 981002)]}],
 981003: ['alt: item+',
          (981003, 0, 981003),
          {(981003, 0, 981003): [(981004, 1, 981003)],
           (981004, 1, 981003): [(981004, 1, 981003), (None, '-', 981003)]}],
 981004: ["item: '[' rhs ']' | atom ['*' | '+']",
          (981004, 0, 981004),
          {(980007, 1, 981004): [(981002, 2, 981004)],
           (980008, 3, 981004): [(None, '-', 981004)],
           (980011, 6, 981004): [(None, '-', 981004)],
           (980012, 5, 981004): [(None, '-', 981004)],
           (981002, 2, 981004): [(980008, 3, 981004)],
           (981004, 0, 981004): [(980007, 1, 981004), (981005, 4, 981004)],
           (981005, 4, 981004): [(980011, 6, 981004),
                                 (980012, 5, 981004),
                                 (None, '-', 981004)]}],
 981005: ["atom: '(' rhs ')' | NAME | STRING",
          (981005, 0, 981005),
          {(980001, 4, 981005): [(None, '-', 981005)],
           (980003, 5, 981005): [(None, '-', 981005)],
           (980005, 1, 981005): [(981002, 2, 981005)],
           (980006, 3, 981005): [(None, '-', 981005)],
           (981002, 2, 981005): [(980006, 3, 981005)],
           (981005, 0, 981005): [(980005, 1, 981005),
                                 (980003, 5, 981005),
                                 (980001, 4, 981005)]}]}

# expansion targets:

expanded  = {}

# reachables:

reachables = {981000: set([980000, 980001, 981001]), 981001: set([980001]), 981002: set([980001, 980003, 980005, 980007, 981003, 981004, 981005]), 981003: set([980001, 980003, 980005, 980007, 981004, 981005]), 981004: set([980001, 980003, 980005, 980007, 981005]), 981005: set([980001, 980003, 980005])}

# terminals:

terminals  = set([980000, 980001, 980003, 980005, 980006, 980007, 980008, 980009, 980010, 980011, 980012, 980013])

# terminal ancestors:

ancestors  = {980000: set([981000]), 980001: set([981000, 981001, 981002, 981003, 981004, 981005]), 980003: set([981002, 981003, 981004, 981005]), 980005: set([981002, 981003, 981004, 981005]), 980007: set([981002, 981003, 981004])}

# last set:

last_set  = {981000: set([980000]), 981001: set([980010]), 981002: set([980001, 980003, 980006, 980008, 980011, 980012, 981003, 981004, 981005]), 981003: set([980001, 980003, 980006, 980008, 980011, 980012, 981004, 981005]), 981004: set([980001, 980003, 980006, 980008, 980011, 980012, 981005]), 981005: set([980001, 980003, 980006])}

# symbols of:

symbols_of  = {981000: set([980000, 981001]),
 981001: set([980001, 980009, 980010, 981002]),
 981002: set([980013, 981003]),
 981003: set([981004]),
 981004: set([980007, 980008, 980011, 980012, 981002, 981005]),
 981005: set([980001, 980003, 980005, 980006, 981002])}

# keywords:

keywords  = {}

# start symbols:

start_symbols  = (981000, set([981000]))
