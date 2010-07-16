def more_recent(file_A, file_B):
    import os
    return list(os.stat(file_A))[-2]>=list(os.stat(file_B))[-2]


def psyco_optimized(f):
    '''
    Decorator for Psyco optimized functions.
    '''
    try:
        import psyco
        return psyco.proxy(f)
    except ImportError:
        return f


def abstractmethod(f):
    '''
    Used for Python 2.5 only.
    '''
    def call(*args, **kwd):
        raise NotImplementedError
    call.__name__ = f.__name__
    call.__doc__ = f.__doc__
    return call

import __builtin__

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
    '''
    rdct = {}
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


