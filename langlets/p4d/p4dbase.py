# -*- coding: UTF-8 -*-
import sys
import p4dutils
import xmlutils
from parsedef.parse_nfa import keywords

__all__ = ["P4D", "P4DNode", "P4D", "P4DList", "P4DName", "P4DNamespace", "P4DAccessError", "P4DContentList"]

ALL = 0

IGNOREWHITESPACE = True

class FileLike(object):
    def __init__(self):
        self.items = []

    def write(self, s):
        self.items.append(s)

    def __repr__(self):
        return ''.join(self.items)

class P4DAccessError(AttributeError):pass

class P4DContentList(list):
    def __str__(self):
        return ''.join(str(item) for item in self)

class P4DList(list):
    '''
    Class used to represent lists of P4D objects. A special property of P4DList
    objects is the provisioning of P4D object methods for P4DLists containing a
    single P4D element.

    So P4DList([a]).m() == a.m() for P4D methods like child(), comment(), text() etc.
    '''

    def search(self, filter_function):
        '''
        Uses a filter_function to search elements in this list. The search function is
        applied when
        '''
        T, filter = filter_function()
        _found = P4DList([])
        for item in self:
            if isinstance(item, list):
                item = P4D(item)
            try:
                if T == 1:  # attribute filter
                    if filter(item):
                        _found.append(item)
                elif T == 2:  # node filter
                    for c in item.children():
                        if filter(c):
                            _found.append(item)
                            break
                elif T == 3:
                    if filter(item):
                        _found.append(item)
            except P4DAccessError:
                raise
            except Exception, e:   # This has to be take with a grain of salt because
                pass
        return _found


    def _get_tag(self):
        if len(self) == 1:
            return self[0].tag
        else:
            raise P4DAccessError("Cannot access tag of P4DList with length!=1.")

    tag = property(_get_tag)

    def xmlstr(self, **kwd):
        if len(self) == 1:
            return self[0].xmlstr(**kwd)
        else:
            raise P4DAccessError("Cannot convert P4DList object into XML str for lists with length!=1.")

    def p4dstr(self, **kwd):
        if len(self) == 1:
            return self[0].p4dstr(**kwd)
        else:
            raise P4DAccessError("Cannot convert P4DList object into P4D str for lists with length!=1.")

    def add(self, elem):
        if len(self) == 1:
            self[0].add(elem)
        else:
            raise P4DAccessError("Cannot add P4D object object to P4DList with list length!=1.")

    def comment(self):
        if len(self) == 1:
            return self[0].comment()
        else:
            raise P4DAccessError("Cannot access P4D comment on P4DList with length!=1.")

    def CDATA(self):
        if len(self) == 1:
            return self[0].CDATA()
        else:
            raise P4DAccessError("Cannot access P4D CDATA on P4DList with length!=1.")

    def text(self):
        if len(self) == 1:
            return self[0].text()
        else:
            raise P4DAccessError("Cannot access P4D text on P4DList with length!=1.")

    def content(self):
        if len(self) == 1:
            return self[0].content()
        else:
            raise P4DAccessError("Cannot access P4D content on P4DList with length!=1.")

    def get(self, tag):
        if len(self) == 1:
            return self[0].get(tag)
        else:
            raise P4DAccessError("Cannot access P4D child element on P4DList with length!=1.")

    def attribute(self, name):
        if len(self) == 1:
            return self[0].attribute(name)
        else:
            raise P4DAccessError("Cannot access P4D attribute on P4DList with length!=1.")

    def attributes(self):
        if len(self) == 1:
            return self[0].attributes()
        else:
            raise P4DAccessError("Cannot access P4D attributes on P4DList with length!=1.")

    def child(self, tag):
        if len(self) == 1:
            return self[0].child(tag)
        else:
            raise P4DAccessError("Cannot access P4D child element on P4DList with length!=1.")

    def children(self, tag = None):
        if len(self) == 1:
            return self[0].children(tag)
        else:
            raise P4DAccessError("Cannot access P4D child element on P4DList with length!=1.")

    def first_child(self):
        if len(self) == 1:
            return self[0].first_child()
        else:
            raise P4DAccessError("Cannot access P4D child element on P4DList with length!=1.")

    def update(self):
        for child in self:
            child.update()

    def __delitem__(self, key):
        if isinstance(key, str):
            if len(self) == 1:
                self[0].__delitem__(key)
            else:
                raise P4DAccessError("Cannot delete item `%s` from P4DList with length!=1."%key)
        else:
            object.__delitem__(self, key)


    def __getattr__(self, name):
        return self.children(name)

    def __setattr__(self, name, value):
        if len(self) == 1:
            self[0].__setattr__(name, value)
        else:
            raise P4DAccessError("Cannot set attribute on P4DList with length!=1.")

class P4DName(str):
    def __init__(self, tag, tagwrapper = None):
        self.fragments = tag.split(":")
        str.__init__(self, tag)
        self._uri = None
        self._local_name = None

    def _get_uri(self):
        if self._uri is not None:
            return self._uri
        elif len(self.fragments)>1:
            prefix = self.fragments
            self._uri = P4DNamespace._namespaces.get(prefix, "")
        else:
            self._uri = ""
        return self._uri

    uri = property(_get_uri)

    def _get_local_name(self):
        if self._local_name is not None:
            return self._local_name
        elif len(self.fragments)>1:
            self._local_name = self.fragments[-1]
        else:
            self._local_name = self
        return self._local_name

    local_name = property(_get_local_name)

class P4DAttributes(dict): pass


class P4DNamespace(object):
    _namespaces = {"p4d": "http://fiber-space.de/p4dns",
                   "http://fiber-space.de/p4dns":"p4d",
                   "xmlns":"http://www.w3.org/2000/xmlns",
                   "http://www.w3.org/2000/xmlns":"xmlns",
                   "bl":"http://fiber-space.de/blns",
                   "http://fiber-space.de/blns":"bl",
                   "bl-schema":"http://fiber-space.de/bl-schemans",
                   "http://fiber-space.de/bl-schemans":"bl-schemans",
                   }
    def __init__(self, prefix = None, uri = None):
        self.prefix = prefix
        self.uri = uri

    @classmethod
    def add_namespace(cls, prefix, uri):
        cls._namespaces[prefix] = uri
        cls._namespaces[uri] = prefix

    @classmethod
    def get(self, key):
        return self._namespaces[key]

    def __str__(self):
        return self.uri



class P4D(object):
    '''
    P4D objects are lazy wrappers around nested lists that store
    XML or P4D data.
    '''
    __slots__ = ['_tree', '_parent', '_content', '_children', '_idx', '_parent', 'tag', '_attrs', '_name']
    parser   = None
    p4d_kwd  = False
    ListType = P4DList
    def __init__(self, tree, parent = None):
        '''
        @param tree: A tree is a nested list of elements of the kind
                     C{[TAG, ATTR, CHILDREN, TEXT]}.
                     C{TAG} and C{TEXT} are strings, C{ATTR} is a dict and C{CHILDREN} is a list of elements
                     having the same tree structure.

        @param parent: the parent P4D object.
        '''
        tag, attrs, children, content = tree
        self.tag    = (tag if tag not in keywords else "p4d:"+tag)
        self._tree  = tree
        self._attrs = (self._create_attributes(attrs) if attrs else {})
        self._name  = None
        if IGNOREWHITESPACE:
            self._content  = content # p4dutils.ignore_whitespace(text)
        else:
            self._content  = content
        self._children  = self.ListType(children)
        self._idx = -1
        self._parent = parent

    def _remap(self):
        self._tree = [self.tag, self._attrs, self._children, self._content]
        if self._parent:
            self._parent._remap()

    def __nonzero__( self):
        return True

    def clone(self):
        _children = []
        for child in self.children():
            _children.append(child.clone())
        return P4D([self.tag, dict(self._attrs), _children, self._content])


    @classmethod
    def from_p4dnode(cls, p4dnode):
        '''
        Converts P4DNode object into P4D object.
        '''
        return P4D(p4dnode.to_list())

    @classmethod
    def eval(self, p4d_str):
        '''
        Evaluates p4d_str in globals and locals.
        '''
        p4d_langlet = langscape.load_langlet("p4d")
        exec_str = "p_4_d_s_t_r = "+p4d_str+"\n"
        code = p4d_langlet.compile(exec_str)
        exec code in globals(), locals()
        return p_4_d_s_t_r

    @classmethod
    def from_xml(cls, xml_src):
        '''
        Create P4D object from xml source string.

        @param xml_src: str or unicode object containing xml source.
        @return: P4D object.
        '''
        if not P4D.parser:
            P4D.parser = xmlutils.ExpatParser()
        tree = P4D.parser.parse(xml_src)
        return P4D(tree)

    @classmethod
    def from_html(cls, html_src):
        '''
        Create P4D object from html source string.

        @param html_src: str or unicode object containing html source.
        @return: P4D object.
        '''
        parser = xmlutils.BeautifulSoupParser()
        return P4D(parser.parse(html_src))

    def add(self, p4dobj):
        self._children.append(p4dobj)
        self._remap()

    def insert(self, i, p4dobj):
        self._children.insert(i, p4dobj)
        self.update()

    def update(self):
        import p4deval
        p4deval.mapeval(self._tree, globals(), locals())

    def comment(self):
        '''
        Seeks for single P4D comment object ( characterized by tag = '*' ) and returns its comment text.
        @return: comment text.
        '''
        try:
            return self.child("*").text()
        except ValueError:
            return ""

    def CDATA(self):
        '''
        Seeks for single P4D CDATA object ( characterized by tag = '**' ) and returns its CDATA text.
        @return: CDATA text.
        '''
        try:
            return self.child("**").text()
        except ValueError:
            return ""

    def xmlstr(self, xml_declaration = False, strip_p4d = True, xmlprinter = xmlutils.xmlprinter):
        '''
        Creates XML string from current P4D object.

        @param xml_declaration: xmlstr prints XML declaration header.
        @param strip_p4d: xmlstr performs C{p4d:xxx -> xxx} transformations for elements prefixed by p4d.
        @param xmlprinter: optional xmlprinter object. Default is xmlutils.xmlprinter.
        '''
        f = FileLike()
        xmlprinter(self._tree, f).pprint(xml_declaration = xml_declaration, strip_p4d = strip_p4d)
        return str(f)


    def p4dstr(self, name = "", p4d_kwd = True):
        '''
        Creates P4D string from current P4D object.

        @param name: adds assignment of P4D object to name so you don't have to write 'name = ...' yourself.
        @param p4d_kwd: Adds `p4d:` prefix in cases where tag or attribute names are P4D keywords.
        '''
        f = FileLike()
        p4dutils.p4dprinter(self._tree, f).pprint(prefix_keyword = p4d_kwd or P4D.p4d_kwd)
        if name:
            assert "-" not in name and ':' not in name, "name `%s` contains non Python characters"%name
            return name + " = "+str(f)
        else:
            return str(f)

    def search(self, filter_function):
        '''
        Searches for elements in the children of this P4D node for which filter_function(Item) == True.

        @param filter_function: A function of a single parameter that returns an object of type bool.
        '''
        return self.children().search(filter_function)

    def namespace(self, prefix = None):
        if prefix:
            uri = P4DNamespace.get(prefix)
            if uri is None:
                raise P4DAccessError("namespace with prefix `%s` is not available."%prefix)
            return P4DNamespace(prefix, uri)
        if self._name is None:
            self._name = P4DName(self.tag)
        if len(self._name.fragments)>1:
            prefix = self._name.fragments[0]
            uri = P4DNamespace.get(prefix)
            if uri is None:
                raise P4DAccessError("namespace with prefix `%s` is not available."%prefix)
            return P4DNamespace(prefix, uri)
        else:
            return P4DNamespace()

    def attributes(self):
        '''
        Returns all attributes of this P4D element.
        '''
        return self._attrs

    def attribute(self, name, value = None):
        '''
        Attribute accessor of a given name for this P4D element.

        @return: attribute value.
        @rtype: str
        @raises KeyError: if no attribute with the given name is available

        Corresponding P4D syntax::

            A.attribute('b') <==> A.@b
        '''
        qname = self._extract_from_qname(name)
        if value is not None:
            self._attrs[qname] = value
            self._remap()
        else:
            return self._attrs[qname]

    def content(self):
        return self._content

    def text(self):
        '''
        Returns textual content of this P4D node.
        '''
        if isinstance(self._content, basestring):
            return self._content
        else:
            return str(self._content)

    def first_child(self):
        '''
        Returns the first child object of this P4D node.
        @raises IndexError: if no child element is available
        '''
        if self._children:
            return self._lazy_child_access(0)
        raise IndexError("No child element available")

    def children(self, tag = None):
        '''
        Returns all child P4D nodes of this node.

        @param tag: filters nodes according to tag value.
        @returns: P4DList object
        @raises ValueError: if no child element is available with given tag.

        Corresponding P4D syntax::

            A.children('b') <==> A.b

        '''
        _children = self.ListType()
        if not tag:
            self._children = self.ListType([self._lazy_child_access(i) for i in xrange(len(self._children))])
            return self._children
        for i in xrange(len(self._children)):
            child = self._lazy_child_access(i)
            if child and child.tag == tag:
                _children.append(child)
        if _children:
            return _children
        else:
            raise ValueError("No child element with tag `%s` found"%tag)

    def get(self, tag):
        '''
        Like child(tag) but doesn't raise an exception when child was not found.

        @param tag: filters nodes according to tag value.
        '''
        for i in xrange(len(self._children)):
            child = self._lazy_child_access(i)
            if child and child.tag == tag:
                return child

    def child(self, tag):
        '''
        Returns first child P4D node with a given tag.

        @param tag: filters nodes according to tag value.
        @raises ValueError: if no child element is available with given tag.
        '''
        child = self.get(tag)
        if child:
            return child
        raise ValueError("No child element with tag `%s` found"%tag)

    def __getattr__(self, tag):
        return self.children(tag)

    def __delitem__(self, name):
        children = self.children(name)
        if children == []:
            raise KeyError(name)
        else:
            for c in children:
                self._children.remove(c)

    def __setattr__(self, name, value):
        dct = object.__getattribute__(self, "__slots__")
        if name not in dct:
            nodes = self.children(name)
            if len(nodes)>1:
                raise P4DAccessError("Unable to manipulate node list of length>1 using __setattr__.")
            nd = nodes[0]
            if isinstance(value, P4D):
                if value.tag !=name:
                    raise AttributeError("Cannot replace content of node with tag `%s` by node with tag `%s`."%(name,value.tag))
                self._children[self._children.index(nd)] = value
            else:
                nd._content = value
                nd._tree[-1] = value
        else:
            object.__setattr__(self, name, value)

    def _create_attributes(self, attrs):
        D = P4DAttributes()
        for key, value in attrs.items():
            key = (key if key not in keywords else "p4d:"+key)
            attr_name = P4DName(key)
            if len(attr_name.fragments)>1:
                prefix = attr_name.fragments[0]
                if prefix == u"xmlns":
                    P4DNamespace.add_namespace(attr_name.fragments[1], value)
            D[attr_name] = value
        return D

    def _extract_from_qname(self, name):
        if name.startswith("{"):
            i = name.find("}")
            uri, local_name = name[1:i], name[i+2:]
            return P4DNamespace.get(uri)+":"+local_name
        if '::' in name:
            return name.replace('::', ':')
        return name

    def _lazy_child_access(self, i):
        c = self._children[i]
        if isinstance(c, list):
            child = P4D(c, self)
            self._children[i] = child
            return child
        elif isinstance(c, P4D):
            return c
        elif c is None:
            raise IndexError

    def _attr_access(self, key):
        if isinstance(self._attrs, P4DAttributes):
            return self._attrs[key]

    def __iter__(self):
        return self

    def next(self):
        try:
            self._idx+=1
            return self._lazy_child_access(self._idx)
        except IndexError:
            raise StopIteration

    def object_data(self):
        '''
        Framework method. Returns nested list passed to P4D constructor.
        '''
        return self._tree


    def __repr__(self):
        return 'P4D<%s>' % self.tag

class _child_iter(object):
    def __init__(self, name, tag, children):
        self.tag = tag
        self.children = children
        self.name = name

    def __iter__(self):
        for c in self.children:
            if c.tag == self.name:
                yield c

    def next(self):
        return self

    def _get_first(self):
        for c in self.children:
            if c.tag == name:
                return c

    first = property(_get_first)

    def __getattr__(self, sub):
        c = self.first
        if not c:
            raise AttributeError("P4DNode<%s> has not childelement '%s'"%(self.tag, self.name))
        return getattr(c, sub)


class P4DNode(object):
    '''
    Used to build list-trees from the bottom up. P4DNode objects might eventually be converted
    into P4D objects providing a richer interface.
    '''
    def __init__(self, tag="", attrs={}, text=""):
        self.children = []
        self.text  = text
        self.attrs = attrs
        self.tag   = tag

    def copy(self):
        return P4DNode(self.tag, dict(self.attrs), self.text)

    def __getattr__(self, name):
        return _child_iter(name, self.tag, self.children)

    def __getitem__(self, idx):
        return self._lst[idx]

    def _to_list(self):
        return [self.tag, dict(self.attrs), [(m._to_list() if isinstance(m, P4DNode) else m) for m in self.children], self.text]

    def __repr__(self):
        return str(self._to_list())



