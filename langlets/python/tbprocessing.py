import sys, string, traceback
import pprint
from langscape.util import get_traceback, levenshtein
import byteplay

class PatternEntry:
    def __init__(self, idx, token, pattern):
        self.idx     = idx
        self.token   = token
        self.pattern = pattern

    def __eq__(self, token):
        if isinstance(token, PatternEntry):
            return self.token == token.token
        try:
            return self.token == token
        except TypeError:
            return False

    def __repr__(self):
        return str((self.idx, self.token, self.pattern))


class TracebackMessageProcessor(object):
    '''
    Converter for traceback messages. This is used to restore the correct line
    in the langlet of the source file.
    '''
    def __init__(self, python, langlet):
        self.python  = python
        self.langlet = langlet
        self.NAME    = python.parse_token.NAME
        self.STRING  = python.parse_token.STRING
        self.NUMBER  = python.parse_token.NUMBER
        self._lndct  = {}

    def __call__(self, typ, value, tb):
        '''
        This function is an overloadable version of sys.excepthook
        '''
        filename = self.get_filename(tb)
        if filename not in self.python._code:
            with open(filename) as f:
                source = f.read()
                cst = self.langlet.transform(source, filename = filename)
                self.python._code[filename] = ('src', self.langlet.unparse(cst))
        _typ, code = self.python._code[filename]
        if _typ == 'src':
            pytoken = list(self.python.tokenize(code))
        else:
            pytoken = list(self.python.tokenize(self.langlet.unparse(code)))
        lltoken, lines = self.get_source_info(filename)
        frames = self.get_frames(tb, filename)
        source_data = []
        for f in frames:
            # print "-"*70
            pytok = self.get_failure_token(f)
            # print "PYTOK", pytok
            ln = self.find_match(pytok, pytoken, lltoken)
            line = lines[ln-1]
            source_data.append((ln, line))
            # print "LINE", ln, line
            # print "*"*70
        s_tb = self.get_patched_traceback(typ, value, tb, source_data[::-1], filename)
        print s_tb

    def get_patched_traceback(self, typ, value, tb, source_data, filename):
        try:
            sys.last_type = typ
            sys.last_value = value
            sys.last_traceback = tb
            tblist = traceback.extract_tb(tb)
            del tblist[:1]
            lst = traceback.format_list(tblist)
            for i, ln in enumerate(lst):
                if filename in ln:
                    n, line = source_data.pop()
                    fragments = ln.split(",")
                    fragments[1] = " line %d"%n
                    _lines = fragments[2].split("\n")
                    fragments[2] = _lines[0]+"\n"+"    "+line.strip()+"\n"
                    s = fragments[-1].strip()
                    if not s:
                        del fragments[-1]
                    lst[i] = ','.join(fragments)
            if lst:
                lst.insert(0, "Traceback (most recent call last):\n")
            lst[len(lst):] = traceback.format_exception_only(typ, value)
        finally:
            tblist = tb = self._lndct = None
        return "".join(lst)

    def get_predecessor(self, pytok, pytokenstream):
        P = None
        for T in pytokenstream:
            if T[:3] == pytok[:3]:
                return P
            elif T[0] in (self.NAME,
                          self.NUMBER,
                          self.STRING):
                P = T

    def find_match(self, pytok, pytokenstream, lltokenstream):
        P = pytok
        # print "PYT", P
        while True:
            D = {}
            source_pattern = self.compute_string_pattern(D, P[1], pytokenstream)
            target_pattern = self.compute_string_pattern(D, P[1], lltokenstream)
            if target_pattern:
                break
            else:
                P = self.get_predecessor(P, pytokenstream)
                if P is None:
                    return
#        print "SP",
#        pprint.pprint(source_pattern)
#        print "TP",
#        pprint.pprint(target_pattern)
#        print "P", P

        # find a match of pytok on an lltok token of the target langlet, respecting all other
        # matches of source_pattern token onto target_pattern token
        #
        # compute n*m matrix M[n,m] of Levenshtein distances between SP[i], TP[j]. Seek for the smallest
        # entry E(i,j) and eliminate Row i and Col j from M[n,m]. If SP[i] = pytok then select TP[j].line
        # as the found line. If n>m or m>n, we approve the best fit of the remaining entries.
        n = len(source_pattern)
        m = len(target_pattern)
        Rows = range(n)
        Cols = range(m)
        M = []
        for i in range(n):
            M.append([-1]*m)
        for i, SP in enumerate(source_pattern):
            for j, TP in enumerate(target_pattern):
                M[i][j] = levenshtein(SP.pattern, TP.pattern)
                # print "PATTERN", SP.pattern, TP.pattern, (i,j), M[i][j]
        while True:
            # print "Matrix", M
            k, I = 1000, -1
            if n>m and len(Cols) == 1:
                return target_pattern[Cols[0]].token[2]
            else:
                for i in Rows:
                    d = min(M[i])
                    if d<k:
                        k = d
                        I = i
                J = M[I].index(k)
                for row in M:
                    row[J] = 100
            SP = source_pattern[I]
            # print "SP-", SP.token, P, (I, J), k
            if SP == P:
                tok = target_pattern[J].token
                return tok[2]  # line
            else:
                # print "Cols", Cols, J
                Rows.remove(I)
                Cols.remove(J)

    def compute_string_pattern(self, D, V, tokenstream):
        a = 0x30  # for readibility: use digits in string pattern

        def make_pattern(i):
            S = []
            for p in tokenstream[max(0, i-5): i+5]:
                if p[1] in D:
                    S.append(D[p[1]])
                else:
                    c = unichr(len(D)+a)
                    D[p[1]] = c
                    S.append(c)
            return u''.join(S)

        string_pattern = []
        ln = -1
        for i, T in enumerate(tokenstream):
            if T[1] == V:
                if T[2]!=ln:
                    k  = 1
                    ln = T[2]
                else:
                    k +=1
                T[3] = k
                string_pattern.append(PatternEntry(i, T, make_pattern(i)))
        return string_pattern


    def correct_failure_token(self, pytok):
        pyline = pytok[2]
        V  = pytok[1]
        frames = self._lndct.get(pyline,[])

        def do_search(code, lastcode):
            if code == lastcode:
                return (0, True)
            k = 0
            for c in code:
                inst, value, offset = c
                if isinstance(value, byteplay.Code):
                    k1, status = do_search(value.code, lastcode)
                    k+=k1
                    if status == True:
                        return k, True
                elif str(value) == V:
                    k+=1
            return k, False

        if len(frames)>1:
            f, lastf = frames[-2], frames[-1]
            lastcode = byteplay.Code.from_code(lastf.f_code).code
            k = 0
            do_collect = False
            for c in byteplay.Code.from_code(f.f_code).code:
                inst, value, offset = c
                if inst == byteplay.SetLineno:
                    if value == pyline:
                        do_collect = True
                elif do_collect:
                    if isinstance(value, byteplay.Code):
                        k1, status = do_search(value.code, lastcode)
                        k+=k1
                        if status == True:
                            break
                    if str(value) == V:
                        k+=1
            pytok[-1] += k
        return pytok

    def get_failure_token(self, frame):
        isfirstline, pytok = self.find_failure_token(frame)
        if isfirstline:
            return self.correct_failure_token(pytok)
        return pytok

    def find_failure_token(self, frame):
        lineno  = firstline = 0
        tok     = None
        token   = []

        def scan_opcodes(code):
            # print "v"*40
            # T = token[:]
            ln = 0
            for c in code:
                # print c
                inst, value, offset = c
                if inst == byteplay.SetLineno:
                    ln = value
                else:
                    handle_opcode(inst, value, ln)
            # print "DELTA", [t for t in token if t not in T]
            # print "A"*40

        def handle_opcode(inst, value, ln):
            if inst == byteplay.LOAD_CONST:
                if isinstance(value, (int, float, complex, long)):
                    tok = [self.NUMBER, str(value), ln]
                    token.append(tok)
                elif isinstance(value, basestring):
                    tok = [self.STRING, value, ln]
                    token.append(tok)
                elif isinstance(value, byteplay.Code):
                    scan_opcodes(value.code)
            elif inst in (byteplay.LOAD_NAME,
                          byteplay.LOAD_FAST,
                          byteplay.LOAD_ATTR,
                          byteplay.LOAD_GLOBAL,
                          byteplay.IMPORT_NAME):
                tok = [self.NAME, value, ln]
                token.append(tok)
            elif isinstance(value, byteplay.Code):
                scan_opcodes(value.code)

        for c in byteplay.Code.from_code(frame.f_code).code:
            # print c
            inst, value, offset = c
            if inst == byteplay.SetLineno:
                L = self._lndct.get(value, [])
                if frame not in L:
                    L.append(frame)
                    self._lndct[value] = L
                if value!=lineno:
                    lineno = value
                    token  = []
                if firstline == 0:
                    firstline = lineno
            else:
                handle_opcode(inst, value, lineno)
            if offset>frame.f_lasti:
                break
        tok = token[-1]
        n = token.count(tok)
        return lineno == firstline, tok+[n]


    def get_filename(self, tb):
        _tb = tb
        while _tb is not None:
            f = _tb.tb_frame
            _tb = _tb.tb_next
        return f.f_code.co_filename

    def get_frames(self, tb, filename):
        _tb = tb
        frames = []
        while _tb is not None:
            f = _tb.tb_frame
            _tb = _tb.tb_next
            if f.f_code.co_filename == filename:
                frames.append(f)
        return frames

    def get_source_info(self, filename):
        with open(filename) as f:
            source = f.read()
            tokstream = self.langlet.tokenize(source)
            lines = source.split("\n")
            return list(tokstream), lines


