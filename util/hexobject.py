# ======================================================================
#
# Copyright (C) 2003-2004 Kay Schluehr (kay.schluehr@gmx.de)
# Hex.py is free software; you can redistribute it
# and/or modify it under the same terms as Python itself.
#
# Hex.py, v B.0 2003/06/18
#
# ======================================================================

'''
This module defines a generic hexadecimal object.
'''
import binascii
import re

class NotConvertibleException(Exception):pass

class HexOrBin(object):pass

def ssplit(s,len_part):
    n = len(s)-len(s)%len_part
    res = [ s[i:i+len_part] for i in range(n)[::len_part]]
    if len(s)%len_part:
        return res+[s[-(len(s)%len_part):]]
    else:
        return res

class Bits(list):
    def __init__(self,l):
        self.format = Hex.F_CP
        list.__init__(self)
        for byte in l[::-1]:
            self.insert(0,byte&1)
            for i in range(7):
                byte>>=1
                self.insert(0,byte&1)

    def __repr__(self):
        if self.format == Hex.F_CP:
            s = "%d"*len(self)
            return s%tuple(self)
        else:
            s = "%d"*8 + " "
            s = s*(len(self)/8)
            return s%tuple(self)

class patch0:
    def __init__(self, func):
        self.func = func

    def __call__(self, arg, arg2=None):
        print self
        print arg, arg2
        if self.bytes and self.bytes[0] == 0:
            self.bytes.insert(0,1)
            res = this.func(self, arg)
            res.bytes = res.bytes[1:]
        else:
            res = func(self, arg)
        return res


def _patch0(func):
    binop = clspatch0(func).binop
    def _binop(self, arg):
        if self.bytes and self.bytes[0] == 0:
            self.bytes.insert(0,1)
            res = func(self, arg)
            res.bytes = res.bytes[1:]
        else:
            res = func(self, arg)
        return res
    binop.im_func.__name__ = func.__name__
    binop.im_func.__doc__ = func.__doc__
    return binop


class Hex(HexOrBin):
    '''
    Generic hexadecimal object.

    Hex()             -> None
    HEX(0x7889)       -> "78 89..."
    HEX("78FF...")    -> "78 FF...
    HEX("78 FF...")   -> "78 FF...

    '''
    F_STD   = 0
    F_0x    = 1
    F_OBJ   = 2
    F_CP    = 3
    F_CP_0x = 4
    F_ASCII = 5
    format = F_STD
    def __init__(self,data=None,format=None):
        if format:
            self.format = format
        else:
            self.format = Hex.format
        self.bytes = []
        if data not in ( None, ""):
            if isinstance(data,Hex):
                self.bytes = data.bytes[:]
            elif isinstance(data, int) or isinstance(data, long):
                self._trans_int(data)
            elif isinstance(data,str):
                self._trans_str(data)
            elif isinstance(data,list):
                self.bytes = data
            else:
                raise NotConvertibleException(data)

    def from_bytes(cls,*bytes):
        h = Hex()
        h.bytes = list(bytes)
        return h

    from_bytes = classmethod(from_bytes)

    def from_string(cls, s):
        h = Hex()
        h.bytes = [ord(c) for c in s]
        return h

    from_string = classmethod(from_string)

    def as_decimal(cls, s):
        s = str(s)
        return Hex("{"+s+"}")

    as_decimal = classmethod(as_decimal)

    def from_decimal(cls,s):
        """
        Function converts from decimal into a hex.

            >>> Hex.from_decimal("255")
            FF

        from_decimal acts the same like Hex(int(s))

        @param s: input string or int ( may contain only decimal digits )
        @type s: string/int.
        """
        try:
            return Hex(int(s))
        except (ValueError,TypeError):
            if isinstance(s,str):
                msg = "String contains non decimal digits: '%s'"%s
            else:
                msg = "Argument type must be a 'str' containg decimal digits. Found '%s'"%type(s)
            raise NotConvertibleException,msg

    from_decimal = classmethod(from_decimal)

    def _trans_str(self,s):
        def tokenize(s):
            l = []
            k = s.find("{")
            if k==-1:
                l.append(s)
                return l
            elif k>0:
                l.append(s[:k])
            s = s[k+1:]

            # substitutions
            s = s.replace("\\{",'\x01')
            s = s.replace("\\}",'\x02')
            i = j = 0
            while 1:
                j = s[i:].find("}")
                n = s[i:].find("{")
                if -1< n < j:
                    raise NotConvertibleException,"Instance not convertible into Hex object."
                else:
                    head = s[:j]
                    head = head.replace('\x01',"{")
                    head = head.replace('\x02',"}")
                    l.append("$"+head)
                    if s[j+1:]:
                        res = tokenize(s[j+1:])
                        l+=res
                    return l
        try:
            if s.startswith("0x"):
                s = s[2:]
            l = tokenize(s)
            P = re.compile(" ?(0x)?")
            for item in l:
                if item[0]=="$":
                    self.bytes += [ord(x) for x in item[1:]]
                else:
                    self.bytes += [int(x,16) for x in ssplit(P.sub("",item),2)]
        except Exception:
            raise NotConvertibleException,"Instance not convertible into Hex object: %s"%s


    def _trans_int(self,n):
        if n<0x100:
            self.bytes = [n]
            return
        s = hex(n)[2:]
        if s[-1] == "L":
            s = s[:-1]
        if len(s)%2==1:
            s = "0"+s
        self._trans_str(s)

    def __call__(self):
        return self.buffer()

    def clone(self):
        h = Hex()
        h.format = self.format
        h.bytes = self.bytes[:]
        return h

    def ascii(self):
        '''
        Returns hex object as ASCII - string.
        @remark: the ascii function is manipulated.
            The beep ascii character as well as the EOF character
            will be converted into '\xFF'
        '''
        s = "".join([chr(byte) for byte in self.bytes])
        # replace beep
        s = s.replace('\x07','\x03')
        s = s.replace('\x1A','\x03')
        return s


    def num(self):
        if len(self)>8:
            return -1
        else:
            n = 0
            self.bytes.reverse()
            for k in range(len(self)):
                n+=256**k*self.bytes[k]
            self.bytes.reverse()
            return n

    def __len__(self):
        return len(self.bytes)

    def buffer(self):
        s = "%02X"*len(self)
        return s%tuple(self.bytes)

    def sc(self):
        s = "%02X"*len(self)
        return s%tuple(self.bytes)

    def sw(self,n):
        form = "%%0%dX"%n
        s = form*len(self)
        return s%tuple(self.bytes)

    def spath(self):
        '''
        @return:
        '''
        if not len(self)%2 == 0:
            raise TypeError,"Hex object is not a path"
        form = "%02X%02X "*(len(self)/2)
        return (form%tuple(self.bytes)).rstrip()

    def bits(self):
        return Bits(self.bytes)

    def binary(self):
        format = self.format
        self.format = Hex.F_CP
        s = self.__repr__()
        self.format = format
        return binascii.a2b_hex(s)

    def reverse(self):
        res = Hex()
        res.bytes = self.bytes[:]
        res.bytes.reverse()
        return res

    def digits(self):
        '''
        The digits method returns a generator that iterates over the digits
        of this Hex object.
        '''
        def digit_generator():
            "digit iterator for Hex object."
            for item in self.bytes:
                yield item>>4
                yield item&0x0F
        return digit_generator()

    def swapped(self):
        bytes = []
        digigen = self.digits()
        for i in range(len(self)):
            d1 = digigen.next()
            d0 = digigen.next()
            bytes.append((d0<<4)+d1)
        res = Hex()
        res.bytes = bytes
        return res

    def __nonzero__(self):
        if len(self.bytes):
            for b in self.bytes:
                if b!=0:
                    return True
        return False

    def __neg__(self):
        return Hex(-self.num())


    def __radd__(self,hNbr):
        if isinstance(hNbr,(int,long)):
            return Hex.__add__(self,hNbr)
        raise TypeError,hNbr


    def __add__(self,hNbr):
        if isinstance(hNbr,(int,long)):
            return Hex(hNbr+self.num())
        else:
            return Hex(hNbr.num()+self.num())


    def __rmul__(self,hNbr):
        if isinstance(hNbr,(int,long)):
            return Hex.__mul__(self,hNbr)
        raise TypeError,hNbr


    def __mul__(self,hNbr):
        if isinstance(hNbr,(int,long)):
            return Hex(hNbr*self.num())
        else:
            return Hex(hNbr.num()*self.num())


    def __rxor__(self,hNbr):
        if isinstance(hNbr,(int,long)):
            return Hex.__xor__(self,hNbr)
        raise TypeError,hNbr


    def __xor__(self,hNbr):
        if isinstance(hNbr,(int,long)):
            return Hex(hNbr^self.num())
        else:
            return Hex(hNbr.num()^self.num())


    def __rsub__(self,hNbr):
        if isinstance(hNbr,(int,long)):
            return Hex.__sub__(self,hNbr)
        raise TypeError,hNbr


    def __mod__(self, hNbr):
        if isinstance(hNbr,(int,long)):
            return Hex(self.num()%hNbr)
        else:
            return Hex(self.num()%hNbr.num())

    #@patch0
    def __rshift__(self, hNbr):
        if isinstance(hNbr,(int,long)):
            return Hex(self.num()>>hNbr)
        else:
            return Hex(self.num()>>hNbr.num())

    #@patch0
    def __lshift__(self, hNbr):
        if isinstance(hNbr,(int,long)):
            return Hex(self.num()<<hNbr)
        else:
            return Hex(self.num()<<hNbr.num())


    def __sub__(self,hNbr):
        if isinstance(hNbr,(int,long)):
            return Hex(self.num()-hNbr)
        else:
            return Hex(self.num()-hNbr.num())


    def __rdiv__(self,hNbr):
        if isinstance(hNbr,(int,long)):
            return Hex.__div__(self,hNbr)
        raise TypeError,hNbr


    def __div__(self,hNbr):
        if isinstance(hNbr,(int,long)):
            return Hex(self.num()/hNbr)
        else:
            return Hex(self.num()/hNbr.num())


    def __floordiv__(self,hNbr):
        if isinstance(hNbr,int) and hNbr<0x100:
            h = Hex(self)
            h.bytes.append(hNbr)
            return h
        else:
            h  = Hex(self)
            h.bytes+=Hex(hNbr).bytes
            return h


    def __rfloordiv__(self,hNbr):
        return Hex(hNbr).__floordiv__(self)


    def __or__(self,hNbr):
        if isinstance(hNbr,int) and hNbr<0x100:
            h = Hex(self)
            h.bytes[0]= self.bytes[0]|hNbr
            return h
        else:
            h  = Hex(hNbr)
            return Hex(h.num()|self.num())


    def __and__(self,hNbr):
        if isinstance(hNbr,int) and hNbr<0x100:
            h = Hex(self)
            h.bytes[0]= self.bytes[0]&hNbr
            return h
        else:
            h  = Hex(hNbr)
            return Hex(h.num()&self.num())


    def __eq__ (self, hNbr):
        if isinstance(hNbr,int) and hNbr<0x100:
            if len(self)==1 and self.bytes[0] == hNbr:
                return True
            return False
        try:
            h = Hex(hNbr)
            return h.bytes == self.bytes
        except:
            return False

    def __ne__ (self, hNbr):
        return not self.__eq__(hNbr)


    def __lt__(self,other):
        if isinstance(other,int):
            return self.num()<other
        try:
            return self.num()<other.num()
        except:
            return False

    def __gt__(self,other):
        if isinstance(other,int):
            return self.num()>other
        try:
            return self.num()>other.num()
        except:
            return False

    def __le__(self,other):
        return self<other or self == other

    def __ge__(self,other):
        return self>other or self == other


    def __getitem__(self,i):
        return Hex(self.bytes[i])

    def __getslice__(self,i,j):
        return Hex(self.bytes[i:j])

    def __setitem__(self,i,val):
        if isinstance(val,int) and val<0x100:
            self.bytes[i] = val
        else:
            h = Hex(val)
            if len(h)==1:
                self.bytes[i] = h.bytes[0]
            else:
                raise "Cannot set Hex object at position %d on value %s"%(i,val)

    def __setslice__(self,i,j,val):
        h = Hex(val)
        self.bytes[i:j] = h.bytes

    def split(self, part_len):
        n = 0
        while n<len(self):
            yield self[n:n+part_len]
            n+=part_len

    def pad(self, n, value):
        k = len(self)
        m = n-k
        res = Hex(self)
        while m:
            res.bytes.append(value)
            m-=1
        return res

    def concat(self, hNbr, binoffset = 0, bits = 0):
        if binoffset == bits == 0:
            return 0, self//hNbr
        k1 = 8 - binoffset
        k2 = bits%8
        if k1 == 8:
            return k2, self//(hNbr<<(8-k2))
        h_bits = len(hNbr)*8
        has_leading_1 = False
        if bits<=h_bits:
            h = hNbr & (2**bits-1)
        elif bits>h_bits:
            d = 1+(bits - h_bits)/8
            h = Hex()
            h.bytes = [0]*d + hNbr.bytes[:]
            h.bytes.insert(0,1) # this is for use of preserving leading nulls
                                # in shifts
            has_leading_1 = True
        if k1>k2:
            shift = (k1-k2)
            h = h<<shift
        elif k2>k1:
            shift = (k2-k1)
            h.bytes.append(0)
            h = h>>shift
        if has_leading_1:
            del h.bytes[0]
        hx = self.clone()
        hx.bytes[-1] = h.bytes[0] | hx.bytes[-1]
        return (binoffset+bits)%8, hx // h[1:]


    def rest(self, byteoffset, binoffset):
        n = len(self)
        return self.section(byteoffset, binoffset, n-byteoffset)[-1]

    def byte(self, byteoffset, binoffset):
        return self.section(byteoffset, binoffset, 1)[-1]

    def section(self, byteoffset, binoffset, n, bit = False):
        bytes = self.bytes[byteoffset:]
        if bit:
            k,r = divmod(n,8)
            if r+binoffset<8:
                _section = bytes[:k+1]
            else:
                _section = bytes[:k+2]
            if binoffset:
                S = Hex(_section)<<binoffset
            else:
                S = Hex(_section)
            l,binoffset = divmod(r+binoffset,8)
            if len(S)>len(_section):
                return (byteoffset+l+k,binoffset),S[1:2+k]>>(8-r)
            else:
                return (byteoffset+l+k,binoffset),S[:1+k]>>(8-r)
        if binoffset:
            _section = bytes[:n+1]
            S = Hex(_section)<<binoffset
            if len(S)>len(_section):
                return (byteoffset+n,binoffset),S[1:1+n]
            else:
                return (byteoffset+n,binoffset),S[:n]
        else:
            return (byteoffset+n,0),Hex(bytes[:n])

    def shuffle(self):
        h = Hex()
        for b in self.bytes:
            h.bytes+=[b,0]
        return h

    def unshuffle(self):
        h = Hex()
        h.bytes = self.bytes[::2]
        return h

    def xor_check(self):
        return Hex(reduce(lambda x,y:x^y,self.bytes))

    def __repr__(self):
        if self.format == Hex.F_STD:
            s = "%02X "*len(self)
            s = s[:-1]
            return s%tuple(self.bytes)
        elif self.format == Hex.F_0x:
            s = "0x%02X "*len(self)
            s = s[:-1]
            return s%tuple(self.bytes)
        elif self.format == Hex.F_OBJ:
            s = "%02X "*len(self)
            s = s[:-1]
            return "Hex<"+s%tuple(self.bytes)+">"
        elif self.format == Hex.F_CP:
            s = "%02X"*len(self)
            return s%tuple(self.bytes)
        elif self.format == Hex.F_CP_0x:
            s = "%02X"*len(self)
            return "0x"+s%tuple(self.bytes)
        elif self.format == Hex.F_ASCII:
            return '"%s"'%self.ascii()
        else:
            raise TypeError, self.format

    def __pos__(self):
        self.__pos = True
        return self

class Bin(int):
    def __init__(self,data):
        int.__init__(self, data)

    def num(self):
        return self

    def __repr__(self):
        n = self.num()
        return "0b%d"%n

def test_concat():
    h = Hex(0x14)
    offset, h = h.concat(Hex(7),0,3)
    assert offset == 3
    assert h == Hex("14 E0")
    offset, h = h.concat(Hex(1),3,1)
    assert offset == 4
    assert h == Hex("14 F0")
    offset, h = h.concat(Hex(10),4,4)
    assert offset == 0
    assert h == Hex("14 FA")
    offset, h = h.concat(Hex(10),0,4)
    assert offset == 4
    assert h == Hex("14 FA A0")

    h = Hex(0x7E)
    offset, h = h.concat(Hex(0x00),7,1)
    assert offset == 0, offset
    assert h == Hex(0x7E)

    h = Hex(0xF0)
    offset, h = h.concat(Hex(0xAAA), 4, 12)
    assert offset == 0, offset
    assert h == Hex("FA AA")

    h = Hex(0xFC)
    offset, h = h.concat(Hex(0xF), 6, 4)
    assert offset == 2, offset
    assert h == Hex("FF C0"), h

    h = Hex(0xC0)
    offset, h = h.concat(Hex(0xF), 2, 4)
    assert offset == 6, offset
    assert h == Hex("FC"), h

    h = Hex(0xC0)
    offset, h = h.concat(Hex(0xFF), 2, 4)
    assert offset == 6, offset
    assert h == Hex("FC"), h

    h = Hex(0xC0)
    offset, h = h.concat(Hex(0xFF), 2, 6)
    assert offset == 0, offset
    assert h == Hex("FF"), h

    h = Hex(0xC0)
    offset, h = h.concat(Hex(0xFF), 2, 8)
    assert offset == 2, offset
    assert h == Hex("FF C0"), h

    h = Hex()
    offset, h = h.concat(Hex(0), 0, 1)
    assert offset == 1
    assert h == Hex(0)

    offset, h = h.concat(Hex(1), offset, 1)
    assert offset == 2
    assert h == Hex(0x40)

    h = Hex(0xF0)
    offset, h = h.concat(Hex(0xFF), 4, 12)
    assert offset == 0
    assert h == Hex("F0 FF"), h

    h = Hex()
    offset, h = h.concat(Hex(0x0A), 0, 4)
    assert offset == 4
    assert h == Hex(0xA0)
    offset, h = h.concat(Hex(0x0A), 4, 16)
    assert offset == 4
    assert h == Hex("A0 00 A0"), h
    offset, h = h.concat(Hex(0x04), 4, 4)
    assert offset == 0
    assert h == Hex("A0 00 A4"), h





if __name__=='__main__':
    h = Hex("FFFFFF")
    h[0:2] = "89 56"
    h = Hex(787)
    h++h
    h = Hex(0x403)
    #print h.binary()
    Hex("0x00")
    Hex("{\}}")
    h = Hex("00 {der kaiser franz-josef}")
    #for item in Hex("01020304050607").split(3):
    #    print item

    h = Hex(0x02)
    while h:
        h-=1
        if h==-10:
            raise TypeError
    #print Hex("3F007F20").spath()
    #print Hex("A0A40000023F00").shuffle()
    #print Hex("00 00 00 00 07 00 A0 00 A4 00 00 00 00 00 02 00 3F 00 00 00 3E 00").unshuffle()
    h = Hex("45 76 89")
    #print "section", h.section(1,4,12, bit = True)

    #assert h == Hex(0x7E), h
    test_concat()

