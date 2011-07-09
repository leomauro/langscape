def split_list(L, n):
    '''
    Splits list L into sublists of length n.
    '''
    return [L[i:i+n] for i in range(len(L))[::n]]


def flatten_list(lst):
    if not isinstance(lst, list) or len(lst)==1:
        return lst
    else:
        flst = []
        for item in lst:
            fl = flatten_list(item)
            if isinstance(fl, list) and isinstance(fl[0], list):
                flst+=fl
            else:
                flst.append(fl)
        res  = [[lst[0]]+item for item in flst[1:]]
        if len(res) == 1:
            return res[0]
        else:
            return res

def flip(dct):
    '''
    If dct = {a1:b1, ..., an:bn} is a dictionary than flip(dct) = {b1:a1, ..., bn:an}

    Note: flip fails when the values of the original dict are not hashable.
    '''
    return dict((b,a) for (a,b) in dct.items())

def get_encoding_str(encoding):
    return "# -*- coding: %s -*-\n"%encoding

def get_traceback():
    import sys, traceback
    try:
        type, value, tb = sys.exc_info()
        sys.last_type = type
        sys.last_value = value
        sys.last_traceback = tb
        tblist = traceback.extract_tb(tb)
        del tblist[:1]
        lst = traceback.format_list(tblist)
        if lst:
            lst.insert(0, "Traceback (most recent call last):\n")
        lst[len(lst):] = traceback.format_exception_only(type, value)
    finally:
        tblist = tb = None
    return "".join(lst)


def levenshtein(s1, s2):
    '''
    Computes Levenshtein distance between two strings or more generally between two
    iterables supporting __len__() and __getitem__() like lists or tuples.
    '''
    l1 = len(s1)
    l2 = len(s2)
    matrix = [range(l1 + 1)] * (l2 + 1)
    for zz in range(l2 + 1):
        matrix[zz] = range(zz,zz + l1 + 1)
    for zz in range(0,l2):
        for sz in range(0,l1):
            if s1[sz] == s2[zz]:
                matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1, matrix[zz][sz+1] + 1, matrix[zz][sz])
            else:
                matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1, matrix[zz][sz+1] + 1, matrix[zz][sz] + 1)
    return matrix[l2][l1]



