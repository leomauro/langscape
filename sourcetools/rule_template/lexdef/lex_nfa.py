# ______________________________________________________________________
# This was automatically generated by nfagen.py.
# Hack at your own risk.

# LANGLET ID

LANGLET_ID = 110000

from langscape.util.univset import*


# trail NFAs:

nfas = {111000: ['ENDMARKER: T_ENDMARKER',
          (111000, 0, 0, 111000),
          {(110001, 1, 0, 111000): [(-1, -1, 0, 111000)],
           (111000, 0, 0, 111000): [(110001, 1, 0, 111000)]}],
 111001: ['NAME: A_CHAR ( A_CHAR | A_DIGIT)*',
          (111001, 0, 0, 111001),
          {(110011, 1, 0, 111001): [(110015, 3, 0, 111001),
                                    (110011, 2, 0, 111001),
                                    (-1, -1, 0, 111001)],
           (110011, 2, 0, 111001): [(110015, 3, 0, 111001),
                                    (110011, 2, 0, 111001),
                                    (-1, -1, 0, 111001)],
           (110015, 3, 0, 111001): [(110015, 3, 0, 111001),
                                    (110011, 2, 0, 111001),
                                    (-1, -1, 0, 111001)],
           (111001, 0, 0, 111001): [(110011, 1, 0, 111001)]}],
 111002: ['NUMBER: A_DIGIT+',
          (111002, 0, 0, 111002),
          {(110015, 1, 0, 111002): [(110015, 1, 0, 111002),
                                    (-1, -1, 0, 111002)],
           (111002, 0, 0, 111002): [(110015, 1, 0, 111002)]}],
 111003: ['STRING: Single | Double',
          (111003, 0, 0, 111003),
          {(111003, 0, 0, 111003): [(111024, 2, 0, 111003),
                                    (111023, 1, 0, 111003)],
           (111023, 1, 0, 111003): [(-1, -1, 0, 111003)],
           (111024, 2, 0, 111003): [(-1, -1, 0, 111003)]}],
 111004: ['NEWLINE: A_LINE_END',
          (111004, 0, 0, 111004),
          {(110010, 1, 0, 111004): [(-1, -1, 0, 111004)],
           (111004, 0, 0, 111004): [(110010, 1, 0, 111004)]}],
 111005: ['INDENT: T_INDENT',
          (111005, 0, 0, 111005),
          {(110002, 1, 0, 111005): [(-1, -1, 0, 111005)],
           (111005, 0, 0, 111005): [(110002, 1, 0, 111005)]}],
 111006: ['DEDENT: T_DEDENT',
          (111006, 0, 0, 111006),
          {(110003, 1, 0, 111006): [(-1, -1, 0, 111006)],
           (111006, 0, 0, 111006): [(110003, 1, 0, 111006)]}],
 111007: ["LPAR: '('",
          (111007, 0, 0, 111007),
          {(110500, 1, 0, 111007): [(-1, -1, 0, 111007)],
           (111007, 0, 0, 111007): [(110500, 1, 0, 111007)]}],
 111008: ["RPAR: ')'",
          (111008, 0, 0, 111008),
          {(110502, 1, 0, 111008): [(-1, -1, 0, 111008)],
           (111008, 0, 0, 111008): [(110502, 1, 0, 111008)]}],
 111009: ["LSQB: '['",
          (111009, 0, 0, 111009),
          {(110512, 1, 0, 111009): [(-1, -1, 0, 111009)],
           (111009, 0, 0, 111009): [(110512, 1, 0, 111009)]}],
 111010: ["RSQB: ']'",
          (111010, 0, 0, 111010),
          {(110509, 1, 0, 111010): [(-1, -1, 0, 111010)],
           (111010, 0, 0, 111010): [(110509, 1, 0, 111010)]}],
 111011: ["COLON: ':'",
          (111011, 0, 0, 111011),
          {(110508, 1, 0, 111011): [(-1, -1, 0, 111011)],
           (111011, 0, 0, 111011): [(110508, 1, 0, 111011)]}],
 111012: ["PLUS: '+'",
          (111012, 0, 0, 111012),
          {(110506, 1, 0, 111012): [(-1, -1, 0, 111012)],
           (111012, 0, 0, 111012): [(110506, 1, 0, 111012)]}],
 111013: ["STAR: '*'",
          (111013, 0, 0, 111013),
          {(110501, 1, 0, 111013): [(-1, -1, 0, 111013)],
           (111013, 0, 0, 111013): [(110501, 1, 0, 111013)]}],
 111014: ["VBAR: '|'",
          (111014, 0, 0, 111014),
          {(110503, 1, 0, 111014): [(-1, -1, 0, 111014)],
           (111014, 0, 0, 111014): [(110503, 1, 0, 111014)]}],
 111015: ['COMMENT: LINE_COMMENT ANY* A_LINE_END',
          (111015, 0, 0, 111015),
          {(110010, 3, 0, 111015): [(-1, -1, 0, 111015)],
           (110017, 2, 0, 111015): [(110017, 2, 0, 111015),
                                    (110010, 3, 0, 111015)],
           (111015, 0, 0, 111015): [(111021, 1, 0, 111015)],
           (111021, 1, 0, 111015): [(110017, 2, 0, 111015),
                                    (110010, 3, 0, 111015)]}],
 111016: ['token_input: unit* ENDMARKER',
          (111016, 0, 0, 111016),
          {(111000, 2, 0, 111016): [(-1, -1, 0, 111016)],
           (111016, 0, 0, 111016): [(111000, 2, 0, 111016),
                                    (111017, 1, 0, 111016)],
           (111017, 1, 0, 111016): [(111000, 2, 0, 111016),
                                    (111017, 1, 0, 111016)]}],
 111017: ['unit: NAME | NEWLINE | LPAR | RPAR | LSQB | RSQB | COLON | PLUS | STAR | WHITE | VBAR | STRING | COMMENT | LBRA | RBRA | COMMA',
          (111017, 0, 0, 111017),
          {(110010, 2001, 0, 111004): [(111004, 4000, 1, 111017)],
           (110010, 4001, 0, 111022): [(111022, 6000, 1, 111017),
                                       (110010, 4001, 0, 111022),
                                       (110514, 4001, 0, 111022)],
           (110514, 4001, 0, 111022): [(111022, 6000, 1, 111017),
                                       (110010, 4001, 0, 111022),
                                       (110514, 4001, 0, 111022)],
           (111001, 1, 0, 111017): [(-1, -1, 0, 111017)],
           (111003, 12, 0, 111017): [(-1, -1, 0, 111017)],
           (111004, 4000, 1, 111017): [(-1, -1, 0, 111017)],
           (111007, 3, 0, 111017): [(-1, -1, 0, 111017)],
           (111008, 4, 0, 111017): [(-1, -1, 0, 111017)],
           (111009, 5, 0, 111017): [(-1, -1, 0, 111017)],
           (111010, 6, 0, 111017): [(-1, -1, 0, 111017)],
           (111011, 7, 0, 111017): [(-1, -1, 0, 111017)],
           (111012, 8, 0, 111017): [(-1, -1, 0, 111017)],
           (111013, 9, 0, 111017): [(-1, -1, 0, 111017)],
           (111014, 11, 0, 111017): [(-1, -1, 0, 111017)],
           (111015, 13, 0, 111017): [(-1, -1, 0, 111017)],
           (111017, 0, 0, 111017): [(111018, 14, 0, 111017),
                                    (111003, 12, 0, 111017),
                                    (111019, 15, 0, 111017),
                                    (111011, 7, 0, 111017),
                                    (111007, 3, 0, 111017),
                                    (111010, 6, 0, 111017),
                                    (111012, 8, 0, 111017),
                                    (111001, 1, 0, 111017),
                                    (111013, 9, 0, 111017),
                                    (111020, 16, 0, 111017),
                                    (111014, 11, 0, 111017),
                                    (111009, 5, 0, 111017),
                                    (111015, 13, 0, 111017),
                                    (111008, 4, 0, 111017),
                                    (110010, 2001, 0, 111004),
                                    (110010, 4001, 0, 111022),
                                    (110514, 4001, 0, 111022)],
           (111018, 14, 0, 111017): [(-1, -1, 0, 111017)],
           (111019, 15, 0, 111017): [(-1, -1, 0, 111017)],
           (111020, 16, 0, 111017): [(-1, -1, 0, 111017)],
           (111022, 6000, 1, 111017): [(-1, -1, 0, 111017)]}],
 111018: ["LBRA: '{'",
          (111018, 0, 0, 111018),
          {(110505, 1, 0, 111018): [(-1, -1, 0, 111018)],
           (111018, 0, 0, 111018): [(110505, 1, 0, 111018)]}],
 111019: ["RBRA: '}'",
          (111019, 0, 0, 111019),
          {(110504, 1, 0, 111019): [(-1, -1, 0, 111019)],
           (111019, 0, 0, 111019): [(110504, 1, 0, 111019)]}],
 111020: ["COMMA: ','",
          (111020, 0, 0, 111020),
          {(110507, 1, 0, 111020): [(-1, -1, 0, 111020)],
           (111020, 0, 0, 111020): [(110507, 1, 0, 111020)]}],
 111021: ["LINE_COMMENT: '#'",
          (111021, 0, 0, 111021),
          {(110510, 1, 0, 111021): [(-1, -1, 0, 111021)],
           (111021, 0, 0, 111021): [(110510, 1, 0, 111021)]}],
 111022: ['WHITE: A_WHITE+',
          (111022, 0, 0, 111022),
          {(110012, 1, 0, 111022): [(-1, -1, 0, 111022),
                                    (110012, 1, 0, 111022)],
           (111022, 0, 0, 111022): [(110012, 1, 0, 111022)]}],
 111023: ['Single: "\'" ( A_BACKSLASH ANY | ANY)* "\'"',
          (111023, 0, 0, 111023),
          {(110016, 2, 0, 111023): [(110017, 3, 0, 111023)],
           (110017, 3, 0, 111023): [(110513, 5, 0, 111023),
                                    (110016, 2, 0, 111023),
                                    (110017, 4, 0, 111023)],
           (110017, 4, 0, 111023): [(110513, 5, 0, 111023),
                                    (110016, 2, 0, 111023),
                                    (110017, 4, 0, 111023)],
           (110513, 1, 0, 111023): [(110513, 5, 0, 111023),
                                    (110016, 2, 0, 111023),
                                    (110017, 4, 0, 111023)],
           (110513, 5, 0, 111023): [(-1, -1, 0, 111023)],
           (111023, 0, 0, 111023): [(110513, 1, 0, 111023)]}],
 111024: ['Double: \'"\' ( A_BACKSLASH ANY | ANY)* \'"\'',
          (111024, 0, 0, 111024),
          {(110016, 2, 0, 111024): [(110017, 3, 0, 111024)],
           (110017, 3, 0, 111024): [(110017, 4, 0, 111024),
                                    (110016, 2, 0, 111024),
                                    (110511, 5, 0, 111024)],
           (110017, 4, 0, 111024): [(110017, 4, 0, 111024),
                                    (110016, 2, 0, 111024),
                                    (110511, 5, 0, 111024)],
           (110511, 1, 0, 111024): [(110017, 4, 0, 111024),
                                    (110016, 2, 0, 111024),
                                    (110511, 5, 0, 111024)],
           (110511, 5, 0, 111024): [(-1, -1, 0, 111024)],
           (111024, 0, 0, 111024): [(110511, 1, 0, 111024)]}]}

# expansion targets:

expanded  = {111017: ['unit: NAME | NEWLINE | LPAR | RPAR | LSQB | RSQB | COLON | PLUS | STAR | WHITE | VBAR | STRING | COMMENT | LBRA | RBRA | COMMA',
          (111017, 0, 0, 111017),
          {(111001, 1, 0, 111017): [(-1, -1, 0, 111017)],
           (111003, 12, 0, 111017): [(-1, -1, 0, 111017)],
           (111004, 2, 0, 111017): [(-1, -1, 0, 111017)],
           (111007, 3, 0, 111017): [(-1, -1, 0, 111017)],
           (111008, 4, 0, 111017): [(-1, -1, 0, 111017)],
           (111009, 5, 0, 111017): [(-1, -1, 0, 111017)],
           (111010, 6, 0, 111017): [(-1, -1, 0, 111017)],
           (111011, 7, 0, 111017): [(-1, -1, 0, 111017)],
           (111012, 8, 0, 111017): [(-1, -1, 0, 111017)],
           (111013, 9, 0, 111017): [(-1, -1, 0, 111017)],
           (111014, 11, 0, 111017): [(-1, -1, 0, 111017)],
           (111015, 13, 0, 111017): [(-1, -1, 0, 111017)],
           (111017, 0, 0, 111017): [(111018, 14, 0, 111017),
                                    (111003, 12, 0, 111017),
                                    (111004, 2, 0, 111017),
                                    (111019, 15, 0, 111017),
                                    (111011, 7, 0, 111017),
                                    (111007, 3, 0, 111017),
                                    (111010, 6, 0, 111017),
                                    (111012, 8, 0, 111017),
                                    (111001, 1, 0, 111017),
                                    (111022, 10, 0, 111017),
                                    (111013, 9, 0, 111017),
                                    (111020, 16, 0, 111017),
                                    (111014, 11, 0, 111017),
                                    (111009, 5, 0, 111017),
                                    (111015, 13, 0, 111017),
                                    (111008, 4, 0, 111017)],
           (111018, 14, 0, 111017): [(-1, -1, 0, 111017)],
           (111019, 15, 0, 111017): [(-1, -1, 0, 111017)],
           (111020, 16, 0, 111017): [(-1, -1, 0, 111017)],
           (111022, 10, 0, 111017): [(-1, -1, 0, 111017)]}]}

# reachables:

reachables = {111000: set([110001]),
 111001: set([110011]),
 111002: set([110015]),
 111003: set([110511, 110513, 111023, 111024]),
 111004: set([110010]),
 111005: set([110002]),
 111006: set([110003]),
 111007: set([110500]),
 111008: set([110502]),
 111009: set([110512]),
 111010: set([110509]),
 111011: set([110508]),
 111012: set([110506]),
 111013: set([110501]),
 111014: set([110503]),
 111015: set([110510, 111021]),
 111016: set([110001, 110010, 110011, 110012, 110500, 110501, 110502, 110503, 110504, 110505, 110506, 110507, 110508, 110509, 110510, 110511, 110512, 110513, 111000, 111001, 111003, 111004, 111007, 111008, 111009, 111010, 111011, 111012, 111013, 111014, 111015, 111017, 111018, 111019, 111020, 111021, 111022, 111023, 111024]),
 111017: set([110010, 110011, 110012, 110500, 110501, 110502, 110503, 110504, 110505, 110506, 110507, 110508, 110509, 110510, 110511, 110512, 110513, 111001, 111003, 111004, 111007, 111008, 111009, 111010, 111011, 111012, 111013, 111014, 111015, 111018, 111019, 111020, 111021, 111022, 111023, 111024]),
 111018: set([110505]),
 111019: set([110504]),
 111020: set([110507]),
 111021: set([110510]),
 111022: set([110012]),
 111023: set([110513]),
 111024: set([110511])}

# terminals:

terminals  = set([110001, 110002, 110003, 110010, 110011, 110012, 110015, 110016, 110017, 110500, 110501, 110502, 110503, 110504, 110505, 110506, 110507, 110508, 110509, 110510, 110511, 110512, 110513])

# terminal ancestors:

ancestors  = {110001: set([111000, 111016]),
 110002: set([111005]),
 110003: set([111006]),
 110010: set([111004, 111016, 111017]),
 110011: set([111001, 111016, 111017]),
 110012: set([111016, 111017, 111022]),
 110015: set([111002]),
 110500: set([111007, 111016, 111017]),
 110501: set([111013, 111016, 111017]),
 110502: set([111008, 111016, 111017]),
 110503: set([111014, 111016, 111017]),
 110504: set([111016, 111017, 111019]),
 110505: set([111016, 111017, 111018]),
 110506: set([111012, 111016, 111017]),
 110507: set([111016, 111017, 111020]),
 110508: set([111011, 111016, 111017]),
 110509: set([111010, 111016, 111017]),
 110510: set([111015, 111016, 111017, 111021]),
 110511: set([111003, 111016, 111017, 111024]),
 110512: set([111009, 111016, 111017]),
 110513: set([111003, 111016, 111017, 111023])}

# last set:

last_set  = {111000: set([110001]),
 111001: set([110011, 110015]),
 111002: set([110015]),
 111003: set([110511, 110513, 111023, 111024]),
 111004: set([110010]),
 111005: set([110002]),
 111006: set([110003]),
 111007: set([110500]),
 111008: set([110502]),
 111009: set([110512]),
 111010: set([110509]),
 111011: set([110508]),
 111012: set([110506]),
 111013: set([110501]),
 111014: set([110503]),
 111015: set([110010]),
 111016: set([110001, 111000]),
 111017: set([110010, 110011, 110015, 110500, 110501, 110502, 110503, 110504, 110505, 110506, 110507, 110508, 110509, 110511, 110512, 110513, 110514, 111001, 111003, 111007, 111008, 111009, 111010, 111011, 111012, 111013, 111014, 111015, 111018, 111019, 111020, 111023, 111024]),
 111018: set([110505]),
 111019: set([110504]),
 111020: set([110507]),
 111021: set([110510]),
 111022: set([110012]),
 111023: set([110513]),
 111024: set([110511])}

# symbols of:

symbols_of  = {111000: set([110001]),
 111001: set([110011, 110015]),
 111002: set([110015]),
 111003: set([111023, 111024]),
 111004: set([110010]),
 111005: set([110002]),
 111006: set([110003]),
 111007: set([110500]),
 111008: set([110502]),
 111009: set([110512]),
 111010: set([110509]),
 111011: set([110508]),
 111012: set([110506]),
 111013: set([110501]),
 111014: set([110503]),
 111015: set([110010, 110017, 111021]),
 111016: set([111000, 111017]),
 111017: set([111001, 111003, 111004, 111007, 111008, 111009, 111010, 111011, 111012, 111013, 111014, 111015, 111018, 111019, 111020, 111022]),
 111018: set([110505]),
 111019: set([110504]),
 111020: set([110507]),
 111021: set([110510]),
 111022: set([110012]),
 111023: set([110016, 110017, 110513]),
 111024: set([110016, 110017, 110511])}

# keywords:

keywords  = {'"': 110511,
 '#': 110510,
 "'": 110513,
 '(': 110500,
 ')': 110502,
 '*': 110501,
 '+': 110506,
 ',': 110507,
 ':': 110508,
 '[': 110512,
 ']': 110509,
 '{': 110505,
 '|': 110503,
 '}': 110504}

# start symbols:

start_symbols  = (111016, set([111002, 111005, 111006, 111016]))

# lexer_terminal:

lexer_terminal  = {110010: set(['\n', '\r']),
 110011: set(['A',
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
 110012: set(['\t', '\n', '\x0b', '\x0c', '\r', ' ']),
 110013: set(['0',
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
 110014: set(['0', '1', '2', '3', '4', '5', '6', '7']),
 110015: set(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']),
 110016: set(['\\']),
 110017: set(),
 110018: set(['1', '2', '3', '4', '5', '6', '7', '8', '9']),
 110019: set(),
 110500: set(['(']),
 110501: set(['*']),
 110502: set([')']),
 110503: set(['|']),
 110504: set(['}']),
 110505: set(['{']),
 110506: set(['+']),
 110507: set([',']),
 110508: set([':']),
 110509: set([']']),
 110510: set(['#']),
 110511: set(['"']),
 110512: set(['[']),
 110513: set(["'"]),
 110514: set(['\t', '\x0b', '\x0c', ' '])}

# constants:

constants  = {111000: '',
 111005: '',
 111006: '',
 111007: '(',
 111008: ')',
 111009: '[',
 111010: ']',
 111011: ':',
 111012: '+',
 111013: '*',
 111014: '|',
 111018: '{',
 111019: '}',
 111020: ',',
 111021: '#'}

