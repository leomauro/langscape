# ______________________________________________________________________
# This was automatically generated by nfagen.py.
# Hack at your own risk.

# LANGLET ID

LANGLET_ID = 760000

from langscape.util.univset import ANY


# trail NFAs:

nfas = {761000: ['eval_input: rule ENDMARKER',
          (761000, 0, 761000),
          {(760000, 2, 761000): [(None, '-', 761000)],
           (761000, 0, 761000): [(761002, 1, 761000)],
           (761002, 1, 761000): [(760000, 2, 761000)]}],
 761001: ['file_input: ( rule | NEWLINE)* ENDMARKER',
          (761001, 0, 761001),
          {(760000, 3, 761001): [(None, '-', 761001)],
           (760004, 2, 761001): [(761002, 1, 761001),
                                 (760004, 2, 761001),
                                 (760000, 3, 761001)],
           (761001, 0, 761001): [(761002, 1, 761001),
                                 (760004, 2, 761001),
                                 (760000, 3, 761001)],
           (761002, 1, 761001): [(761002, 1, 761001),
                                 (760004, 2, 761001),
                                 (760000, 3, 761001)]}],
 761002: ["rule: NAME ':' rhs NEWLINE",
          (761002, 0, 761002),
          {(760001, 1, 761002): [(760011, 2, 761002)],
           (760004, 4, 761002): [(None, '-', 761002)],
           (760011, 2, 761002): [(761003, 3, 761002)],
           (761002, 0, 761002): [(760001, 1, 761002)],
           (761003, 3, 761002): [(760004, 4, 761002)]}],
 761003: ["rhs: alt ('|' alt)*",
          (761003, 0, 761003),
          {(760014, 2, 761003): [(761004, 3, 761003)],
           (761003, 0, 761003): [(761004, 1, 761003)],
           (761004, 1, 761003): [(760014, 2, 761003), (None, '-', 761003)],
           (761004, 3, 761003): [(760014, 2, 761003), (None, '-', 761003)]}],
 761004: ['alt: item+',
          (761004, 0, 761004),
          {(761004, 0, 761004): [(761005, 1, 761004)],
           (761005, 1, 761004): [(761005, 1, 761004), (None, '-', 761004)]}],
 761005: ["item: '[' rhs ']' | atom ['*' | '+']",
          (761005, 0, 761005),
          {(760009, 1, 761005): [(761003, 2, 761005)],
           (760010, 3, 761005): [(None, '-', 761005)],
           (760012, 6, 761005): [(None, '-', 761005)],
           (760013, 5, 761005): [(None, '-', 761005)],
           (761003, 2, 761005): [(760010, 3, 761005)],
           (761005, 0, 761005): [(761006, 4, 761005), (760009, 1, 761005)],
           (761006, 4, 761005): [(760013, 5, 761005),
                                 (None, '-', 761005),
                                 (760012, 6, 761005)]}],
 761006: ["atom: '(' rhs ')' | NAME | STRING",
          (761006, 0, 761006),
          {(760001, 4, 761006): [(None, '-', 761006)],
           (760003, 5, 761006): [(None, '-', 761006)],
           (760007, 1, 761006): [(761003, 2, 761006)],
           (760008, 3, 761006): [(None, '-', 761006)],
           (761003, 2, 761006): [(760008, 3, 761006)],
           (761006, 0, 761006): [(760001, 4, 761006),
                                 (760007, 1, 761006),
                                 (760003, 5, 761006)]}]}

# expansion targets:

expanded  = {}

# reachables:

reachables = {761000: set([760001, 761002]),
 761001: set([760000, 760001, 761002, 760004]),
 761002: set([760001]),
 761003: set([760001, 760003, 760007, 760009, 761004, 761005, 761006]),
 761004: set([760001, 760003, 760007, 760009, 761005, 761006]),
 761005: set([760001, 760009, 760003, 761006, 760007]),
 761006: set([760001, 760003, 760007])}

# terminals:

terminals  = set([760000, 760001, 760003, 760004, 760007, 760008, 760009, 760010, 760011, 760012, 760013, 760014])

# terminal ancestors:

ancestors  = {760000: set([761001]),
 760001: set([761000, 761001, 761002, 761003, 761004, 761005, 761006]),
 760003: set([761003, 761004, 761005, 761006]),
 760004: set([761001]),
 760007: set([761003, 761004, 761005, 761006]),
 760009: set([761003, 761004, 761005])}

# last set:

last_set  = {761000: set([760000]),
 761001: set([760000]),
 761002: set([760004]),
 761003: set([760001, 760003, 760008, 760012, 760010, 761004, 761005, 761006, 760013]),
 761004: set([760001, 760003, 760008, 760010, 760012, 761005, 761006, 760013]),
 761005: set([760001, 760003, 760008, 760010, 760012, 760013, 761006]),
 761006: set([760008, 760001, 760003])}

# symbols of:

symbols_of  = {761000: set([760000, 761002]),
 761001: set([760000, 761002, 760004]),
 761002: set([760001, 760011, 760004, 761003]),
 761003: set([761004, 760014]),
 761004: set([761005]),
 761005: set([760009, 760010, 761003, 760012, 760013, 761006]),
 761006: set([760008, 760001, 760003, 761003, 760007])}

# keywords:

keywords  = {}

# start symbols:

start_symbols  = (761001, set([761000, 761001]))
