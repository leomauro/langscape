# -*- coding: UTF-8 -*-

import sys
import p4dbase
from copy import copy
import math
from langscape.util.hexobject import Hex, Bin

__all__ = ["Bytelet", "ByteletSchema", "LEN", "Hex", "Bin", "VAL", "RAWLEN", "ByteletError"]

class ByteletError(Exception): pass

###################################################################
#
# Flow objects are used to implement wicked dataflow bindings.
#
# Flow objects are placed as *content* in P4D node::
#
#                        [TAG, {}, [], FLOW ]
#
# On execution FLOW holds a refence to the containing
# element and its parent accordingly. So it can traverse the container
# and perform computations on its elements. The result will be written
# into FLOW._value.
#
####################################################################

class Flow(object):
    def __init__(self):
        self._value = None
        self._structure = []
        self._node   = None
        self._parent = None
        self._field_ref  = None

    def flow_value(self):
        if self._value is None:
            self.update()
        return self._value

    def set_flow_value(self, val):
        self._value = val

    def set_node(self, node, parent = None):
        self._node   = node
        self._parent = (parent if parent else node._parent)

    def __getitem__(self, name):
        obj = copy(self)
        obj._field_ref = name
        return obj

    def __copy__(self):
        obj = self.__class__()
        obj._value = self._value
        obj._structure = self._structure[:]
        obj._field_ref = self._field_ref
        return obj

    def __add__(self, item):
        obj = copy(self)
        obj._structure = self._structure[:]
        obj._structure.append(('+',item))
        return obj

    def __radd__(self, item):
        obj = copy(self)
        obj._structure.append(('+',item))
        return obj

    def __sub__(self, item):
        obj = copy(self)
        obj._structure.append(('-',item))
        return obj

    def __rsub__(self, item):
        obj = copy(self)
        obj._structure.append(('-',item))
        return obj

    def __mul__(self, item):
        obj = copy(self)
        obj._structure.append(('*',item))
        return obj

    def __rmul__(self, item):
        obj = copy(self)
        obj._structure.append(('*',item))
        return obj

    def __div__(self, item):
        obj = copy(self)
        obj._structure.append(('/',item))
        return obj

    def __rdiv__(self, item):
        obj = copy(self)
        obj._structure.append(('/',item))
        return obj

    def compute(self, n):
        for (op, val) in self._structure:
            if isinstance(val, Flow):
                val.set_node(self._node, self._parent)
                val = val.flow_value().num()
            if op == '+':
                n+=val
            elif op == '-':
                n-=val
            elif op == '*':
                n*=val
            elif op == '/':
                n/=val
        return n

    def update(self):
        raise NotImplementedError

class FlowLen(Flow):
    def __len__(self):
        return len(self._value)

    def update(self):
        if self._field_ref:
            n = self._compute_field_len()
        else:
            n = self._compute_rest()
        self.compute_value(n)

    def compute_value(self, n):
        raise NotImplementedError

    def _compute_rest(self):
        children = self._parent.children()
        k = children.index(self._node)
        btl = Bytelet(["btl",{},children[k+1:],''])
        n = len(btl)
        return self.compute(n)

    def _compute_field_len(self):
        children = self._parent.children()
        n = 0
        for child in children:
            if child.tag == self._field_ref:
                if isinstance(child, Bytelet):
                    n+=len(child)
                else:
                    n+=len(child.hex())
                break
        return self.compute(n)

    def __str__(self):
        return "%s:%s:%s"%(self.__class__.__name__, self._structure, self._value)


class FlowLenBER(FlowLen):
    def _BER_encode(self, n):
        if n<=0x80:
            return Hex(n)
        else:
            h = Hex(n)
            return Hex(0x80+len(h)) // h

    def compute_value(self, n):
        self._value = self._BER_encode(n)

class FlowLenRaw(FlowLen):
    def compute_value(self, n):
        self._value = Hex(n)

class FlowFieldVal(Flow):
    def __init__(self):
        super(FlowFieldVal, self).__init__()
        self._lock = False

    def __copy__(self):
        obj = super(FlowFieldVal, self).__copy__()
        obj._lock = self._lock
        return obj

    def update(self):
        if self._lock == True:
            self._lock = False
            ref = (self._field_ref if self._field_ref else 'Len')
            raise RuntimeError("Cannot compute value of field `%s`. Check if corresponding `%s` field has a value."%(self._node.tag, ref))
        self._lock = True
        tag = self._field_ref
        n = 0
        children = self._parent.children()
        for i, child in enumerate(children):
            if tag:
                if child.tag == tag:
                    try:
                        n = child._content._value.num()
                    except AttributeError:
                        n = child.hex().num()
                    break
            else:
                if child.tag.upper() == "LEN" or (isinstance(child._content, FlowLen) and child._content._field_ref == None):
                    try:
                        n = child._content._value.num()
                    except AttributeError:
                        n = child.hex().num()
                    break
        else:
            self._lock = False
            raise KeyError("No reference available for field `%s`."%self._node.tag)
        self._lock = False
        n = self.compute(n)
        self._value = Hex(n)


    def __str__(self):
        return "FlowFieldVal<%s>"%str(self._value)

##################################

# Global objects

LEN    = FlowLenBER()
RAWLEN = FlowLenRaw()
VAL    = FlowFieldVal()

##################################

class ByteletList(p4dbase.P4DList):
    def hex(self):
        if len(self) == 1:
            return self[0].hex()
        else:
            raise p4dbase.P4DAccessError("Cannot access Bytelet hex object on ByteletList with length!=1.")

    def clone(self):
        if len(self) == 1:
            return self[0].clone()
        else:
            raise p4dbase.P4DAccessError("Cannot clone Bytelet on ByteletList with length!=1.")


class Bytelet(p4dbase.P4D):
    '''
    Bytelets are flexible data structures used for binary serialization.

    Bytelets are based on BER encoded TLV data-structures. Length calculations are
    maintained using dataflow-bindings.

    Bytelets will be supported on language level by means of the namespace ::

        namespace: "http://fiber-space.de/byteletns"
        prefix: bl

    Bytelet elements will be created like this ::

        bl = bl:x:
            f: 1
            g: 0x89

    The bl prefix acts like a constructor.
    '''
    __slots__ = p4dbase.P4D.__slots__ + ["_initialized"]
    ListType  = ByteletList
    def __init__(self, tree, parent = None):
        self._initialized = False
        p4dbase.P4D.__init__(self, tree, parent)
        self.flow_obj_init()
        self._initialized = True

    @classmethod
    def from_p4dnode(cls, p4dnode):
        '''
        Converts P4DNode object into Bytelet object.
        '''
        return Bytelet(p4dnode.to_list())

    def flow_obj_init(self):
        if isinstance(self._content, Flow):
            self._content.set_node(self)

    def update(self, back_propagate = True):
        if back_propagate:
            if self._parent:
                return self._parent.update(back_propagate)
        for child in self.children()[::-1]:
            child.update(back_propagate = False)
        if hasattr(self._content, "update"):
            if isinstance(self._content, Flow):
                self._content.set_node(self)
            self._content.update()

    def __repr__(self):
        return 'Bytelet<%s>' % self.tag

    def clone(self):
        if isinstance(self._content, Flow):
            content = copy(self._content)
        else:
            content = self._content
        cloned = Bytelet([self.tag, dict(self._attrs), [], content])
        children = ByteletList()
        for child in self.children():
            if isinstance(child, Bytelet):
                c = child.clone()
                c._parent = cloned
                c.flow_obj_init()
                children.append(c)
            else:
                c = Bytelet(child, cloned).clone()
                c.flow_obj_init()
                children.append(c)
        cloned._children = children
        cloned._remap()
        return cloned

    def _check_size(self, width, hx):
        if (hx>>width)==0:
            return True
        return False

    def hex(self):
        bitshift = [False]
        items = []
        def _hex(btl):
            if btl._children == []:
                if btl._content!='':
                    if isinstance(btl._content, Flow):
                        hx = btl._content.flow_value()
                    else:
                        btl._content
                        hx = Hex(btl._content)
                    width = int(btl._attrs.get("w",0))
                    if width:
                        if self._check_size(width, hx):
                            bitshift[0] = True
                        else:
                            raise TypeError("Hex object %s does not fit into a %d bit array."%(hx, width))
                    items.append((hx, width))
            else:
                for child in btl.children():
                    _hex(child)
        _hex(self)
        h = Hex()
        if not bitshift[0] or len(items)==1:
            for (item,w) in items:
                h.bytes.extend(item.bytes)
        else:
            #print "TO-HEX", len(items), [type(t[0]) for t in items]
            offset = 0
            for (item,w) in items:
                offset, h = h.concat(item, offset, w)
        return h

    def _lazy_child_access(self, i):
        c = self._children[i]
        if isinstance(c, list):
            child = Bytelet(c, self)
            self._children[i] = child
            return child
        elif isinstance(c, p4dbase.P4D):
            return c
        elif c is None:
            raise IndexError

    def __len__(self):
        def _len(self):
            children = self.children()
            if children == []:
                try:
                    width = int(self._attrs.get("w",0))
                    if width:
                        k,r = divmod(width,8)
                        return k+r/8.0
                    return len(self.hex())
                except TypeError:
                    return len(self.hex())
            else:
                return sum(_len(child) for child in children)

        return math.ceil(_len(self))

    def __delitem__(self, name):
        super(Bytelet, self).__delitem__(name)
        if self._initialized:
            self.update()

    def __setattr__(self, name, value):
        dct = object.__getattribute__(self, "__slots__")
        if name not in dct:
            super(Bytelet, self).__setattr__(name, value)
            if self._initialized:
                self.update()
        else:
            object.__setattr__(self, name, value)

    def content(self):
        if isinstance(self._content, Flow):
            return self._content.flow_value()
        else:
            return self._content

    def text(self):
        return str(self.content())


class ByteletSchema(Bytelet):
    ListType  = ByteletList
    def __repr__(self):
        return 'ByteletSchema<%s>' % self.tag

    def update(self, back_propagate = True):
        pass

    def parse(self, hexcode, strict = True):
        '''
        Parses hexcode into Bytelet according to a Schema.

        @param hexcode: any object that can be converted into a Hex object.
        '''
        use = self._attrs.get("use")
        if use == "tlvlist":
            return self._parse_tlvlist_schema(hexcode, strict)
        else:
            return self._parse_std_schema(hexcode, strict)

    def _parse_std_schema(self, hexcode, strict):
        hexoffset = 0
        binoffset = 0
        if type(hexcode) == Hex:
            bc = hexcode
        else:
            bc = Hex(hexcode)
        if self.tag.startswith("bl-schema"):
            tag = "bl:"+self.tag.split(":")[1]
        else:
            tag = self.tag
        matched = Bytelet([tag,{},[],''])
        for child in self.children():
            if hexoffset>=len(bc):
                if strict:
                    content = child._tree[-1]
                    if isinstance(content, FlowFieldVal):
                        content.set_node(child, matched)
                        n = content.flow_value().num()
                        if n == 0:
                            continue
                    else:
                        n = child.hex().num()
                        if n == 0:
                            continue
                    raise ByteletError("[01]: Schema too short. Field `%s` of ByteletSchema `%s` does not match any hexcode."%(child.tag, self.tag))
                break
            content = child._tree[-1]
            if isinstance(content, FlowFieldVal):
                # print "MATCH FlowFieldVal"
                content.set_node(child, matched)
                n = content.flow_value().num()
                if strict and hexoffset+n>len(bc):
                    raise ByteletError("[02]:Incorrect number of bytes for field `%s`. Expected `%s` bytes but `%s` bytes found."%(child.tag, n, hexoffset+n-len(bc)))
                (hexoffset, binoffset),v = bc.section(hexoffset, binoffset, n)
                matched._children.append(Bytelet([child.tag, {}, [], v], matched))
            elif isinstance(content, FlowLen):
                # print "MATCH FlowLen"
                lgt = bc.byte(hexoffset, binoffset)
                if lgt & 0x80:
                    lenlen = 1 + (lgt & 0x0F)
                    (hexoffset, binoffset),v = bc.section(hexoffset, binoffset, lenlen.num())
                else:
                    v = lgt
                    hexoffset+=1
                # print "NEW HEXOFFSET", hexoffset
                # set new flow len value
                flen = copy(content)
                flen.set_flow_value(v)
                matched._children.append(Bytelet([child.tag, {}, [], flen], matched))
            elif len(child._children)>0:
                # print "MATCH children"
                if not isinstance(child, ByteletSchema):
                    child_schema = ByteletSchema(child._tree, child._parent)
                else:
                    child_schema = child
                mi = child_schema.parse(bc.rest(hexoffset, binoffset), strict)
                # print "MATCHED", mi
                matched._children.append(mi)
                hexoffset+=len(mi)
            elif isinstance(content, Bin):
                # print "MATCH bits"
                n = content.num()
                #print "REST", bc[hexoffset:]
                (hexoffset, binoffset),v = bc.section(hexoffset, binoffset, n, bit = True)
                #print "V",v
                matched._children.append(Bytelet([child.tag, {"w":n}, [], v], matched))
            elif isinstance(content, Hex):
                # print "MATCH HX exact"
                n = len(content)
                (hexoffset, binoffset), section = bc.section(hexoffset,binoffset,n)
                if strict and section != content:
                    raise ByteletError("[03]:Expected content of field `%s` = `%s`. Received: `%s`."%(child.tag, content, section))
                matched._children.append(Bytelet([child.tag, {}, [], content], matched))

            else:
                # print "MATCH bytes"
                n = Hex(content).num()
                (hexoffset, binoffset),section = bc.section(hexoffset,binoffset,n)
                matched._children.append(Bytelet([child.tag, {}, [], section], matched))
        if strict:
            n = hexoffset - len(bc)
            if n<0 and self._parent is None:
                n = len(bc) - hexoffset
                if binoffset:
                    raise ByteletError("[041]: Schema too short. ByteletSchema `%s` did not scan %s bits of hexcode."%(self.tag, 8*n-binoffset))
                else:
                    raise ByteletError("[042]: Schema too short. ByteletSchema `%s` did not scan %s bytes of hexcode."%(self.tag,n))
            elif n>0 or binoffset:
                if n>0:
                    raise ByteletError("[051]: Schema too long. ByteletSchema `%s` specified %d bytes that did not match."%(self.tag, n))
                else:
                    raise ByteletError("[052]: Schema too long. ByteletSchema `%s` specified %d bits that did not match."%(self.tag, binoffset))
        matched._remap()
        return matched

    def _split(self, hexcode):
        T = hexcode[0]
        lgt = hexcode[1]
        if lgt & 0x80:
            lenlen = 1 + (lgt & 0x0F)
            L = hexcode[1:1+lenlen]
        else:
            L = lgt
            lenlen = 1
        k = L.num()
        V, rest = hexcode[1+lenlen:1+lenlen+k], hexcode[1+lenlen+k:]
        return (T,L,V), rest


    def _scan_with_tlvlist(self, hexcode, tagset):
        bytelets = []
        #print "TAGSET", tagset
        while len(hexcode)>0:
            (T,L,V), hexcode = self._split(hexcode)
            #print "T", T
            #print "L", L
            if len(V) != L.num():
                V = Hex("{ <-----------  ERROR: not enough bytes available!}")
                V.format = Hex.F_ASCII
            # print "rest", hexcode
            child = tagset.get(T.num())
            if child:
                btl = Bytelet([child.tag,{},[['Tag',{},[],T],['Len',{},[],L]],''])
                if child._children:
                    if child._attrs.get("use") == "std":
                        child_schema = ByteletSchema(child._tree)
                        btl = child_schema._parse_std_schema(T//L//V, True)
                    else:
                        tags = {}
                        for c in child.children():
                            t = c._attrs["tag"]
                            tags[Hex(t).num()] = c
                        for sub in self._scan_with_tlvlist(V, tags):
                            sub._parent = btl
                            btl._children.append(sub)
                else:
                    btl = Bytelet([child.tag,{},[['Tag',{},[],T],['Len',{},[],L],['Val',{},[],V]],''])
            else:
                btl = Bytelet(['UNDEF',{},[['Tag',{},[],T],['Len',{},[],L],['Val',{},[],V]],''])
            btl._remap()
            bytelets.append(btl)
        return bytelets


    def _parse_tlvlist_schema(self, hexcode, strict):
        if type(hexcode) == Hex:
            bc = hexcode
        else:
            bc = Hex(hexcode)
        tagset = {}
        for child in self.children():
            t = child._attrs["tag"]
            tagset[Hex(t).num()] = child
        bytelets = self._scan_with_tlvlist(bc, tagset)
        matched  = bytelets[0]
        return matched



