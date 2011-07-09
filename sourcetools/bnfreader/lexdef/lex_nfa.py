# ______________________________________________________________________
# This was automatically generated by nfagen.py.
# Hack at your own risk.

# LANGLET ID

LANGLET_ID = 980000

from langscape.util.univset import*


# trail NFAs:

nfas = {981000: ['ENDMARKER: T_ENDMARKER',
          (981000, 0, 981000),
          {(980001, 1, 981000): [(None, '-', 981000)],
           (981000, 0, 981000): [(980001, 1, 981000)]}],
 981001: ['NAME: A_CHAR ( A_CHAR | A_DIGIT)*',
          (981001, 0, 981001),
          {(980011, 1, 981001): [(None, '-', 981001),
                                 (980015, 3, 981001),
                                 (980011, 2, 981001)],
           (980011, 2, 981001): [(None, '-', 981001),
                                 (980015, 3, 981001),
                                 (980011, 2, 981001)],
           (980015, 3, 981001): [(None, '-', 981001),
                                 (980015, 3, 981001),
                                 (980011, 2, 981001)],
           (981001, 0, 981001): [(980011, 1, 981001)]}],
 981002: ['NUMBER: A_DIGIT+',
          (981002, 0, 981002),
          {(980015, 1, 981002): [(980015, 1, 981002), (None, '-', 981002)],
           (981002, 0, 981002): [(980015, 1, 981002)]}],
 981003: ['STRING: Single | Double',
          (981003, 0, 981003),
          {(981003, 0, 981003): [(981024, 2, 981003), (981023, 1, 981003)],
           (981023, 1, 981003): [(None, '-', 981003)],
           (981024, 2, 981003): [(None, '-', 981003)]}],
 981004: ['NEWLINE: A_LINE_END',
          (981004, 0, 981004),
          {(980010, 1, 981004): [(None, '-', 981004)],
           (981004, 0, 981004): [(980010, 1, 981004)]}],
 981005: ["LPAR: '('",
          (981005, 0, 981005),
          {(980500, 1, 981005): [(None, '-', 981005)],
           (981005, 0, 981005): [(980500, 1, 981005)]}],
 981006: ["RPAR: ')'",
          (981006, 0, 981006),
          {(980501, 1, 981006): [(None, '-', 981006)],
           (981006, 0, 981006): [(980501, 1, 981006)]}],
 981007: ["LSQB: '['",
          (981007, 0, 981007),
          {(980513, 1, 981007): [(None, '-', 981007)],
           (981007, 0, 981007): [(980513, 1, 981007)]}],
 981008: ["RSQB: ']'",
          (981008, 0, 981008),
          {(980510, 1, 981008): [(None, '-', 981008)],
           (981008, 0, 981008): [(980510, 1, 981008)]}],
 981009: ["COLON: ':'",
          (981009, 0, 981009),
          {(980509, 1, 981009): [(None, '-', 981009)],
           (981009, 0, 981009): [(980509, 1, 981009)]}],
 981010: ["SEMI: ';'",
          (981010, 0, 981010),
          {(980506, 1, 981010): [(None, '-', 981010)],
           (981010, 0, 981010): [(980506, 1, 981010)]}],
 981011: ["PLUS: '+'",
          (981011, 0, 981011),
          {(980507, 1, 981011): [(None, '-', 981011)],
           (981011, 0, 981011): [(980507, 1, 981011)]}],
 981012: ["STAR: '*'",
          (981012, 0, 981012),
          {(980503, 1, 981012): [(None, '-', 981012)],
           (981012, 0, 981012): [(980503, 1, 981012)]}],
 981013: ["VBAR: '|'",
          (981013, 0, 981013),
          {(980502, 1, 981013): [(None, '-', 981013)],
           (981013, 0, 981013): [(980502, 1, 981013)]}],
 981014: ['COMMENT: LINE_COMMENT ANY* A_LINE_END',
          (981014, 0, 981014),
          {(980010, 3, 981014): [(None, '-', 981014)],
           (980017, 2, 981014): [(980010, 3, 981014), (980017, 2, 981014)],
           (981014, 0, 981014): [(981020, 1, 981014)],
           (981020, 1, 981014): [(980010, 3, 981014), (980017, 2, 981014)]}],
 981015: ['token_input: unit* ENDMARKER',
          (981015, 0, 981015),
          {(981000, 2, 981015): [(None, '-', 981015)],
           (981015, 0, 981015): [(981016, 1, 981015), (981000, 2, 981015)],
           (981016, 1, 981015): [(981016, 1, 981015), (981000, 2, 981015)]}],
 981016: ['unit: ( NAME | INTRON | LPAR | RPAR | LSQB | RSQB | COLON | PLUS | STAR | VBAR | STRING | LBRA | RBRA | COMMA | SEMI)',
          (981016, 0, 981016),
          {(981001, 1, 981016): [(None, '-', 981016)],
           (981003, 11, 981016): [(None, '-', 981016)],
           (981005, 3, 981016): [(None, '-', 981016)],
           (981006, 4, 981016): [(None, '-', 981016)],
           (981007, 5, 981016): [(None, '-', 981016)],
           (981008, 6, 981016): [(None, '-', 981016)],
           (981009, 7, 981016): [(None, '-', 981016)],
           (981010, 15, 981016): [(None, '-', 981016)],
           (981011, 8, 981016): [(None, '-', 981016)],
           (981012, 9, 981016): [(None, '-', 981016)],
           (981013, 10, 981016): [(None, '-', 981016)],
           (981016, 0, 981016): [(981018, 13, 981016),
                                 (981003, 11, 981016),
                                 (981008, 6, 981016),
                                 (981001, 1, 981016),
                                 (981005, 3, 981016),
                                 (981006, 4, 981016),
                                 (981012, 9, 981016),
                                 (981011, 8, 981016),
                                 (981007, 5, 981016),
                                 (981019, 14, 981016),
                                 (981013, 10, 981016),
                                 (981009, 7, 981016),
                                 (981021, 2, 981016),
                                 (981010, 15, 981016),
                                 (981017, 12, 981016)],
           (981017, 12, 981016): [(None, '-', 981016)],
           (981018, 13, 981016): [(None, '-', 981016)],
           (981019, 14, 981016): [(None, '-', 981016)],
           (981021, 2, 981016): [(None, '-', 981016)]}],
 981017: ["LBRA: '{'",
          (981017, 0, 981017),
          {(980505, 1, 981017): [(None, '-', 981017)],
           (981017, 0, 981017): [(980505, 1, 981017)]}],
 981018: ["RBRA: '}'",
          (981018, 0, 981018),
          {(980504, 1, 981018): [(None, '-', 981018)],
           (981018, 0, 981018): [(980504, 1, 981018)]}],
 981019: ["COMMA: ','",
          (981019, 0, 981019),
          {(980508, 1, 981019): [(None, '-', 981019)],
           (981019, 0, 981019): [(980508, 1, 981019)]}],
 981020: ["LINE_COMMENT: '#'",
          (981020, 0, 981020),
          {(980511, 1, 981020): [(None, '-', 981020)],
           (981020, 0, 981020): [(980511, 1, 981020)]}],
 981021: ['INTRON: NEWLINE | WHITE | COMMENT',
          (981021, 0, 981021),
          {(980010, 2001, 981022): [(981022, '.', 4000, 981021),
                                    (980010, 2001, 981022),
                                    (980515, 2001, 981022)],
           (980010, 4001, 981004): [(981004, '.', 6000, 981021)],
           (980515, 2001, 981022): [(981022, '.', 4000, 981021),
                                    (980010, 2001, 981022),
                                    (980515, 2001, 981022)],
           (981004, '.', 6000, 981021): [(None, '-', 981021)],
           (981014, 3, 981021): [(None, '-', 981021)],
           (981021, 0, 981021): [(981014, 3, 981021),
                                 (980010, 4001, 981004),
                                 (980010, 2001, 981022),
                                 (980515, 2001, 981022)],
           (981022, '.', 4000, 981021): [(None, '-', 981021)]}],
 981022: ['WHITE: A_WHITE+',
          (981022, 0, 981022),
          {(980012, 1, 981022): [(980012, 1, 981022), (None, '-', 981022)],
           (981022, 0, 981022): [(980012, 1, 981022)]}],
 981023: ['Single: "\'" ( A_BACKSLASH ANY | ANY)* "\'"',
          (981023, 0, 981023),
          {(980016, 2, 981023): [(980017, 3, 981023)],
           (980017, 3, 981023): [(980017, 4, 981023),
                                 (980016, 2, 981023),
                                 (980514, 5, 981023)],
           (980017, 4, 981023): [(980017, 4, 981023),
                                 (980016, 2, 981023),
                                 (980514, 5, 981023)],
           (980514, 1, 981023): [(980017, 4, 981023),
                                 (980016, 2, 981023),
                                 (980514, 5, 981023)],
           (980514, 5, 981023): [(None, '-', 981023)],
           (981023, 0, 981023): [(980514, 1, 981023)]}],
 981024: ['Double: \'"\' ( A_BACKSLASH ANY | ANY)* \'"\'',
          (981024, 0, 981024),
          {(980016, 2, 981024): [(980017, 3, 981024)],
           (980017, 3, 981024): [(980016, 2, 981024),
                                 (980017, 4, 981024),
                                 (980512, 5, 981024)],
           (980017, 4, 981024): [(980016, 2, 981024),
                                 (980017, 4, 981024),
                                 (980512, 5, 981024)],
           (980512, 1, 981024): [(980016, 2, 981024),
                                 (980017, 4, 981024),
                                 (980512, 5, 981024)],
           (980512, 5, 981024): [(None, '-', 981024)],
           (981024, 0, 981024): [(980512, 1, 981024)]}]}

# expansion targets:

expanded  = {981021: ['INTRON: NEWLINE | WHITE | COMMENT',
          (981021, 0, 981021),
          {(981004, 1, 981021): [(None, '-', 981021)], (981014, 3, 981021): [(None, '-', 981021)], (981021, 0, 981021): [(981022, 2, 981021), (981004, 1, 981021), (981014, 3, 981021)], (981022, 2, 981021): [(None, '-', 981021)]}]}

# reachables:

reachables = {981000: set([980001]),
 981001: set([980011]),
 981002: set([980015]),
 981003: set([980512, 980514, 981023, 981024]),
 981004: set([980010]),
 981005: set([980500]),
 981006: set([980501]),
 981007: set([980513]),
 981008: set([980510]),
 981009: set([980509]),
 981010: set([980506]),
 981011: set([980507]),
 981012: set([980503]),
 981013: set([980502]),
 981014: set([980511, 981020]),
 981015: set([980001,
              980010,
              980011,
              980012,
              980500,
              980501,
              980502,
              980503,
              980504,
              980505,
              980506,
              980507,
              980508,
              980509,
              980510,
              980511,
              980512,
              980513,
              980514,
              981000,
              981001,
              981003,
              981004,
              981005,
              981006,
              981007,
              981008,
              981009,
              981010,
              981011,
              981012,
              981013,
              981014,
              981016,
              981017,
              981018,
              981019,
              981020,
              981021,
              981022,
              981023,
              981024]),
 981016: set([980010, 980011, 980012, 980500, 980501, 980502, 980503, 980504, 980505, 980506, 980507, 980508, 980509, 980510, 980511, 980512, 980513, 980514, 981001, 981003, 981004, 981005, 981006, 981007, 981008, 981009, 981010, 981011, 981012, 981013, 981014, 981017, 981018, 981019, 981020, 981021, 981022, 981023, 981024]),
 981017: set([980505]),
 981018: set([980504]),
 981019: set([980508]),
 981020: set([980511]),
 981021: set([980010, 980012, 980511, 981004, 981014, 981020, 981022]),
 981022: set([980012]),
 981023: set([980514]),
 981024: set([980512])}

# terminals:

terminals  = set([980001, 980010, 980011, 980012, 980015, 980016, 980017, 980500, 980501, 980502, 980503, 980504, 980505, 980506, 980507, 980508, 980509, 980510, 980511, 980512, 980513, 980514])

# terminal ancestors:

ancestors  = {980001: set([981000, 981015]),
 980010: set([981004, 981015, 981016, 981021]),
 980011: set([981001, 981015, 981016]),
 980012: set([981015, 981016, 981021, 981022]),
 980015: set([981002]),
 980500: set([981005, 981015, 981016]),
 980501: set([981006, 981015, 981016]),
 980502: set([981013, 981015, 981016]),
 980503: set([981012, 981015, 981016]),
 980504: set([981015, 981016, 981018]),
 980505: set([981015, 981016, 981017]),
 980506: set([981010, 981015, 981016]),
 980507: set([981011, 981015, 981016]),
 980508: set([981015, 981016, 981019]),
 980509: set([981009, 981015, 981016]),
 980510: set([981008, 981015, 981016]),
 980511: set([981014, 981015, 981016, 981020, 981021]),
 980512: set([981003, 981015, 981016, 981024]),
 980513: set([981007, 981015, 981016]),
 980514: set([981003, 981015, 981016, 981023])}

# last set:

last_set  = {981000: set([980001]),
 981001: set([980011, 980015]),
 981002: set([980015]),
 981003: set([980512, 980514, 981023, 981024]),
 981004: set([980010]),
 981005: set([980500]),
 981006: set([980501]),
 981007: set([980513]),
 981008: set([980510]),
 981009: set([980509]),
 981010: set([980506]),
 981011: set([980507]),
 981012: set([980503]),
 981013: set([980502]),
 981014: set([980010]),
 981015: set([980001, 981000]),
 981016: set([980010, 980011, 980015, 980500, 980501, 980502, 980503, 980504, 980505, 980506, 980507, 980508, 980509, 980510, 980512, 980513, 980514, 980515, 981001, 981003, 981005, 981006, 981007, 981008, 981009, 981010, 981011, 981012, 981013, 981014, 981017, 981018, 981019, 981021, 981023, 981024]),
 981017: set([980505]),
 981018: set([980504]),
 981019: set([980508]),
 981020: set([980511]),
 981021: set([980010, 980515, 981014]),
 981022: set([980012]),
 981023: set([980514]),
 981024: set([980512])}

# symbols of:

symbols_of  = {981000: set([980001]),
 981001: set([980011, 980015]),
 981002: set([980015]),
 981003: set([981023, 981024]),
 981004: set([980010]),
 981005: set([980500]),
 981006: set([980501]),
 981007: set([980513]),
 981008: set([980510]),
 981009: set([980509]),
 981010: set([980506]),
 981011: set([980507]),
 981012: set([980503]),
 981013: set([980502]),
 981014: set([980010, 980017, 981020]),
 981015: set([981000, 981016]),
 981016: set([981001, 981003, 981005, 981006, 981007, 981008, 981009, 981010, 981011, 981012, 981013, 981017, 981018, 981019, 981021]),
 981017: set([980505]),
 981018: set([980504]),
 981019: set([980508]),
 981020: set([980511]),
 981021: set([981004, 981014, 981022]),
 981022: set([980012]),
 981023: set([980016, 980017, 980514]),
 981024: set([980016, 980017, 980512])}

# keywords:

keywords  = {'"': 980512,
 '#': 980511,
 "'": 980514,
 '(': 980500,
 ')': 980501,
 '*': 980503,
 '+': 980507,
 ',': 980508,
 ':': 980509,
 ';': 980506,
 '[': 980513,
 ']': 980510,
 '{': 980505,
 '|': 980502,
 '}': 980504}

# start symbols:

start_symbols  = (981015, set([981002, 981015]))

# lexer_terminal:

lexer_terminal  = {980010: set(['\n', '\r']),
 980011: set(['A',
              'B',
              'C',
              'D',
              'E',
              'F',
              'G',
              'H',
              'I',
              'J',
              'K',
              'L',
              'M',
              'N',
              'O',
              'P',
              'Q',
              'R',
              'S',
              'T',
              'U',
              'V',
              'W',
              'X',
              'Y',
              'Z',
              '_',
              'a',
              'b',
              'c',
              'd',
              'e',
              'f',
              'g',
              'h',
              'i',
              'j',
              'k',
              'l',
              'm',
              'n',
              'o',
              'p',
              'q',
              'r',
              's',
              't',
              'u',
              'v',
              'w',
              'x',
              'y',
              'z']),
 980012: set(['\t', '\n', '\x0b', '\x0c', '\r', ' ']),
 980013: set(['0',
              '1',
              '2',
              '3',
              '4',
              '5',
              '6',
              '7',
              '8',
              '9',
              'A',
              'B',
              'C',
              'D',
              'E',
              'F',
              'a',
              'b',
              'c',
              'd',
              'e',
              'f']),
 980014: set(['0', '1', '2', '3', '4', '5', '6', '7']),
 980015: set(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']),
 980016: set(['\\']),
 980017: set(),
 980018: set(['1', '2', '3', '4', '5', '6', '7', '8', '9']),
 980019: set(),
 980500: set(['(']),
 980501: set([')']),
 980502: set(['|']),
 980503: set(['*']),
 980504: set(['}']),
 980505: set(['{']),
 980506: set([';']),
 980507: set(['+']),
 980508: set([',']),
 980509: set([':']),
 980510: set([']']),
 980511: set(['#']),
 980512: set(['"']),
 980513: set(['[']),
 980514: set(["'"]),
 980515: set(['\t', '\x0b', '\x0c', ' '])}

# constants:

constants  = {981000: '',
 981005: '(',
 981006: ')',
 981007: '[',
 981008: ']',
 981009: ':',
 981010: ';',
 981011: '+',
 981012: '*',
 981013: '|',
 981017: '{',
 981018: '}',
 981019: ',',
 981020: '#'}
