# Implementation is out of data and awaits a major redesign
# Please don't use CodeTemplate!

__all__ = ["CodeTemplate", "CodeMarker", "CodeSelection"]

import random
import pprint

import langscape.csttools.cstrepr as cstrepr
import langscape.csttools.cstcheck as cstcheck
from langscape.csttools.cstsearch import*
from langscape.csttools.cstutil import*

class CSTNode(list):
    def __init__(self, node, langlet = None):
        list.__init__(self, node)
        self.langlet = langlet

    def __repr__(self):
        return self.langlet.unparse(self)

class CodeTemplate(object):
    def __init__(self, langlet, source):
        self._langlet = langlet
        self._target  = source
        source = cstrepr.prepare_source(source)
        self._cst = langlet.parse(source)
        self._code_marker = set()
        self._ST = None

    def substitute(self, **kwds):
        if not self._ST:
            self._ST = self.match()
        else:
            self._ST = self._ST.clone()
        for key in kwds.keys():
            if key not in self._ST:
                raise KeyError('%s'%key)
            marker = self._ST[key]
            for s in marker:
                s.code.substitute(kwds[key])
        return CSTNode(self._ST.top(), self._langlet)

    def match(self):
        ST = SelectionTree()
        ST.template = self
        for name in self._code_marker:
            _code_marker = getattr(self, name)
            ST[name]  = _code_marker.match(self._cst)
            ST.marker[name] = _code_marker
        return ST

    def __setattr__(self, name, value):
        if isinstance(value, CodeMarker):
            self._code_marker.add(name)
            value._langlet = self._langlet
        object.__setattr__(self, name, value)


class SelectionTree(dict):
    def __init__(self, dct = {}):
        self.update(dct)
        self.code   = None
        self.marker = {}

    def __setitem__(self, name, value):
        if name in self.__dict__:
            raise ValueError("'%s' is readonly"%name)
        dict.__setitem__(self, name, value)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError("'SelectionTree' object has no attribute '%s'"%name)


    def top(self):
        if self.code:
            return self.code.top()
        else:
            values = self.values()
            if values:
                return values[0][0].code.top()

    def clone(self, memo = None):
        if not memo:
            memo = {}
            # fill memo
            N = self.top()
            if N is None:
                return SelectionTree()
            clone_node(N, memo = memo)
        T = SelectionTree()
        T.marker = self.marker
        if self.code:
            T.code = self.code.clone(memo)
            T.code.tree = T
        for name, value in self.items():
            T[name] = [S.clone(memo) for S in value]
        return T


class CodeMarker(object):
    '''
    A CodeMarker object lets you mark a section in code that spans one or more token
    of a langlet. A CodeMarker doesn't operate on raw textual source but on token
    streams created by a lexer. This implies that the smallest chunk a CodeMarker
    can be bound to effecticely is a token string.

    There are basically two kinds of selective filters for CodeMarkers.

    1) One can bind to individual items  ::

           CodeMarker(item = "x")      # binds to all names `x`
           CodeMarker(item = ":")      # binds to all colons
           CodeMarker(item = "raise")  # binds to all names `raise`
           ...

    2) One binds to ranges of token ::

           Suppose you have the following nested if-statement

               if cond1:
                   block1
               elif cond2:
                   if cond3:
                       block3
               else:
                   block4

           CodeMarker(start = "if", end = "block4")  # the outer if-statement as well
                                                     # as the wrongly indented statement that starts
                                                     # with the inner if and ends with block4

           CodeMarker(start = "if", end = "block4",  # the outer if-statement only
                      includes = ["cond1"])

           CodeMarker(start = "if", end = "block3")  # the inner if-statement and the outer one
                                                     # excluding the else-branch

           CodeMarker(start = "if", end = "block3",  # the inner if-statement only
                      excludes = ["cond1"])


           Consider "if .. block3 \ {cond1}"
    '''
    def __init__(self, item = "", start = "", end="", followed_by="", includes=[], excludes=[]):
        self._create_conditions(item, start, end, followed_by, includes, excludes)
        self._check_conditions()
        self._parent_marker = None
        self._sub_marker    = set()
        self._langlet = None

    def parse_item(self, item):
        self._langlet.tokenize(item)

    def __setattr__(self, name, value):
        if isinstance(value, CodeMarker):
            self._sub_marker.add(name)
            value._langlet = self._langlet
            object.__setattr__(value, "_parent_marker", self)
        object.__setattr__(self, name, value)

    def match(self, node):
        # selections of a single marker
        subtrees   = []
        selections = self._create_selections(node)
        for S in selections:
            T = SelectionTree()
            T.code = S
            S.tree = T
            subtrees.append(T)
        for name in self._sub_marker:
            marker = getattr(self, name)
            for T in subtrees:
                T[name] = marker.match(T.code.node)
                T.marker[name] = marker
        return subtrees


    def _create_conditions(self, item, start, end, followed_by, includes, excludes):
        self.conditions = {}
        self.conditions["item"] = item
        self.conditions["start"] = start
        self.conditions["end"] = end
        self.conditions["followed_by"] = followed_by
        if isinstance(includes, str):
            self.conditions["includes"] = [includes]
        else:
            self.conditions["includes"] = includes
        if isinstance(excludes, str):
            self.conditions["excludes"] = [excludes]
        else:
            self.conditions["excludes"] = excludes

    def _check_conditions(self):
        item  = self.conditions["item"]
        start = self.conditions["start"]
        end   = self.conditions["end"]
        includes    = self.conditions["includes"]
        excludes    = self.conditions["excludes"]
        followed_by = self.conditions["followed_by"]
        OK = True
        assert (not (end and followed_by))
        assert (end not in excludes)
        assert (not (start or end) if item else OK)
        assert set(includes) & set(excludes) == set()
        #assert (start or end or item)

    def _create_selections(self, node):
        '''
        The match method applies the CodeMarker selection filters on a CST node. It returns
        a (possibly empty) list of CodeSelection objects.
        '''
        # Strategy: let sec be a section with (t0,c0), (t1,c1) as endpoints.
        #   1) We compute N which is the lower limit of nodes that are in c0.unfold() /\ c1.unfold().
        #   2) For each subnode SubN of N we compute the token-chains of SubN.
        #   3)
        #

        # construction: consider the chain c0 of nodes above the leftmost token t0 and the
        #               and the chain of nodes c1 of the rightmost token t1.
        #
        #               Keep the smallest common node N of both chains. There must be at least
        #               one N which is search node.
        #
        #               Compute the index i0 of the subnode N0 in N that contains t0 and the
        #               index i1 of the subnode N1 in N that contains t1.
        #
        # If S is the section of token than we will call N(S) the smallest subnode of the search
        # node that contains S.
        sections = self._match_node(node)
        selection = []
        for section in sections:
            if len(section) == 1:
                t, c  = section[0]
                selection.append(TokenSelection(t, (0,0), c, section, self._langlet))
                continue
            t0,c0 = section[0]
            t1,c1 = section[-1]
            T0 = [(id(nd),nd) for nd in c0.unfold()]
            T1 = [(id(nd),nd) for nd in c1.unfold()]
            S  = set([T[0] for T in T0])
            for idx, (_id, N) in enumerate(T1):
                if _id in S:
                    subnode_tokenlist = []
                    for sub in N[1:]:
                        if is_token(sub[0]):
                            subnode_tokenlist.append([sub])
                        else:
                            subnode_tokenlist.append([chain.step()[0] for chain in find_token_chains_gen(sub)])
                    t, c = section[0]
                    n = len(section)
                    j,m,i1,i2 = -1,-1,-1,-1
                    for k, sublist in enumerate(subnode_tokenlist):
                        if t in sublist:
                            i1 = k+1
                            m = len(sublist) - sublist.index(t)
                            continue
                        if m>=0:
                            if m>=n:
                                i2 = k #+1
                                break
                            else:
                                m+=len(sublist)
                    else:
                        i2 = len(subnode_tokenlist)
                    selection.append(CodeSelection(N, (i1, i2), c1, section, self._langlet))
                    break
        return selection

    def _find_all(self, S, R, K = 0):
        k = len(R)
        start_index = []
        if R:
            while K>=0:
                K = S.find(R, K)
                if K>=0:
                    try:
                        if S[K+k] == '\1':
                            start_index.append(K)
                    except IndexError:
                        break
                    K+=k
        return start_index


    def _match_node(self, node):
        chains = list(find_token_chains_gen(node))
        domain = [chain.step() for chain in chains]
        S = '\1'.join(t[1] for (t,c) in domain)
        if self.conditions["item"]:
            items = []
            item  = self.conditions["item"]
            for i in self._find_all(S, item):
                head = S[:i]
                t,c = domain[len(head.split('\1'))-1]
                if t[1] == item:
                    items.append([(t,c)])
            return items
        else:
            A = self.conditions["start"]
            if A:
                start_index = self._find_all(S,A)
            else:
                start_index = [0]
            if start_index == []:
                return []
            B = self.conditions["end"]
            if B:
                end_index = self._find_all(S,B,(start_index[0] if start_index else 0))
            else:
                C = self.conditions["followed_by"]
                if C:
                    end_index = [I-1 for I in self._find_all(S,C,(start_index[0] if start_index else 0))]
                else:
                    end_index = [S.rfind('\1')+1]
            if end_index == []:
                return []

            pre_section = []
            K = 0
            for s in start_index:
                for k,r in enumerate(end_index[K:]):
                    if r>s:
                        pre_section.append((s,k+K))
                        K = k
                        break
            if self.conditions["includes"]:
                for (i0, k) in pre_section[:]:
                    K = k
                    for s in self.conditions["includes"]:
                        for kx in range(K,len(end_index)):
                            if s in S[i0+1:end_index[kx]]:
                                break
                        else:
                            K = -1
                            pre_section.remove((i0,k))
                            break
                        K = kx
                    else:
                        if k != K:
                            pre_section.remove((i0,k))
                            pre_section.append((i0,K))
            sections = []
            for (i0,k) in pre_section:
                for kx in range(k, len(end_index)):
                    i1 = end_index[kx]
                    head = S[:i0]
                    body = S[i0:i1]
                    for s in self.conditions["excludes"]:
                        if s in body[1:]:
                            break
                    else:
                        k0 = len(head.split('\1'))-1
                        k1 = k0+len(body.split('\1'))
                        sections.append(domain[k0: k1])
            return sections



class CodeSelection:

    def __init__(self, node, seq, chain, section, langlet = None):
        '''
        @param node: If the selected string is matched by a single node than this is the node. Otherwise
                     it is the parent node of a section which is a list of nodes.
        @param seq: a pair of indices I_l, I_r used to characterize the range of nodes relative to the
                    parent node.
        @param chain: a chain object used to step up from `node` to its parent nodes.
        @param section: a list of items of the kind ( token, chain ). These items characterize
        '''
        self.node    = node
        self.i_l     = seq[0]
        self.i_r     = seq[1]
        self.chain   = chain
        self.section = section
        self.langlet = langlet
        self._substituted = False
        self.tree = None

    def top(self):
        return self.chain._chain[0]

    def token(self):
        return [s[0] for s in self.section]

    def clone(self, memo):
        cloned = memo[id(self.node)]
        cloned_chain = Chain([memo[id(C)] for C in self.chain._chain])
        cloned_section = []
        for T,C in self.section:
            _T = memo[id(T)]
            _C = Chain([memo[id(c)] for c in C._chain])
            cloned_section.append((_T,_C))
        return self.__class__(cloned, (self.i_l, self.i_r), cloned_chain, cloned_section, self.langlet)

    def safe_insert(self, mult, unfolded):
        Node = self.node
        _id  = id(Node)
        k = 0
        while unfolded:
            N = unfolded.pop()
            for j, SubN in enumerate(N):
                if id(SubN) == id(Node):
                    nodes   = N[1:j+1]+[Node]+N[j+1:]
                    builder = self.langlet.get_node_builder(N[0]) # getattr(cstbuilder, cstrepr.get_node_name(self.langlet, N[0]))
                    try:
                        builder(*nodes)
                        nodes = [clone_node(Node) for i in range(mult)]
                        N[:] = builder(*N[1:j+1]+nodes+N[j+1:])
                        return unfolded+[N], nodes
                    except ValueError:
                        break
            Node = N
        raise ValueError("Cannot replicate node.")


    def replicate(self, k=1):
        #
        # Currently only envelopes of the token sequences will be replicated. In the end one might
        # consider the smallest envelope that is still syntactically correct.
        head   = self.node[:self.i_r+1]
        tail   = self.node[self.i_r+1:]
        i = 0
        n, d = self.i_r, self.i_r+1 - self.i_l
        new_selections = []
        unfolded = self.chain.upper_chain(self.node).unfold()
        if len(self.node)-1 == d:
            upper, nodes = self.safe_insert(k, unfolded[::-1])
            section = []
            for node in nodes:
                for T,chain in [C.step() for C in find_token_chains_gen(node)]:
                    chain._chain = upper+chain._chain
                    section.append((T, chain))
                new_selections.append( CodeSelection(node, (self.i_l, self.i_r), chain, section, self.langlet) )
            return new_selections
        else:
            N = []
            while i<k:
                i+=1
                if i>1:
                    nodes = [clone_node(nd) for nd in self.node[self.i_l: self.i_r+1]]
                else:
                    nodes = self.node[self.i_l: self.i_r+1]
                section = []
                for nd in nodes:
                    for T, chain in [C.step() for C in find_token_chains_gen(nd)]:
                        if chain is None:
                            chain = Chain(unfolded)
                        else:
                            chain._chain = unfolded[::-1]+chain._chain
                        section.append((T,chain))
                new_selections.append( CodeSelection(N, (n, n+d), chain, section, self.langlet) )
                n+=d
                head += nodes
            N[:] = self.node[:] = head + tail
            cstcheck.check_node(N, self.langlet, no_ok_msg = True)
            for S in new_selections:
                T = SelectionTree()
                T.code = S
                S.tree = T
                for name, marker in self.tree.marker.items():
                    T[name] = marker.match([N[0]]+S.subnodes())
                    T.marker[name] = marker
            return new_selections


    def subnodes(self):
        return self.node[self.i_l: self.i_r+1]

    def delete(self):
        # The delete functions cuts off the subnodes of N(section).
        #
        if self._substituted:
            raise RuntimeError("Cannot delete node twice.")
        self._substituted = True
        del self.node[self.i_l: self.i_r+1]

    def mangle(self, *names):
        assert len(names)>0, "No names passed into mangle"
        for name in names:
            self.subst_identifier(name, name+"_%d"%random.randint(10000, 99999))


    def substitute(self, obj=None, *cst_nodes):
        '''
        This method is a T -> CST subsitution where T is a token object.
        The token object can be node id of a token or a token string.
        All token objects that match obj will be substituted.
        '''
        raise NotImplementedError("Refactor This Function")
        assert cst_nodes
        assert obj
        if self._substituted:
            raise RuntimeError("Cannot substitute node twice.")
        self._substituted = True

        transformer = FSTransformer()
        for T, C in self.section:
            if T[0] == obj or T[1] == obj:
                transformer.substitute(T, cst_nodes, cst_nodes[0][0], C._chain)

class TokenSelection(CodeSelection):
    def token(self):
        return [self.node]

    def substitute(self, *cst_node):
        raise NotImplementedError("Refactor This Function")
        if self._substituted:
            raise RuntimeError("Cannot substitute node twice.")
        self._substituted = True
        if not isinstance(cst_node[0], list):
            cst_node = [list(cst_node)]
        transformer = FSTransformer()
        for T, C in self.section:
            if T[0] == self.node[0] or T[1] == self.node[1]:
                transformer.substitute(T, cst_node, cst_node[0][0], C._chain)

    def delete(self):
        if self._substituted:
            raise RuntimeError("Cannot delete node twice.")
        self._substituted = True
        _id = id(self.node)
        N, C = self.section[0][1].step()
        N.remove(self.node)

    def subnodes(self):
        return []

    def replicate(self, k=1):
        # print "TOKEN-SELECTION -- replicate"
        N, chain = self.section[0][1].step()
        new_selections = []
        unfolded = self.chain.unfold()
        upper, nodes = self.safe_insert(k, unfolded[::-1])
        section = []
        for node in nodes:
            for T,chain in [C.step() for C in find_token_chains_gen(node)]:
                chain._chain = upper+chain._chain
                section.append((T, chain))
            new_selections.append( CodeSelection(node, (self.i_l, self.i_r), chain, section, self.langlet) )
        return new_selections



if __name__ == '__main__':
    target="""
        mgr   = (EXPR)
        exit  = mgr.__exit__  # Not calling it yet
        value = mgr.__enter__()
        exc = True
        try:
            try:
                VAR = value  # Only if "as VAR" is present
                BLOCK
            except:
                # The exceptional case is handled here
                exc = False
                if not exit(*sys.exc_info()):
                    raise
                elif not exit():
                    pass
                # The exception is swallowed if exit() returns true
        finally:
            # The normal and non-local-goto cases are handled here
            if exc:
                exit(None, None, None)
        """

    python = langscape.load_langlet("python")
    ct = CodeTemplate(python, target)
    ct.cm_enter = CodeMarker(start = "value", end = ")", includes = "__enter__", excludes = "exc")
    ST = ct.match()
    #print [s[0] for s in ST.cm_enter[0].code.section]

    for marker in ST.cm_enter:
        marker.code.replicate(5)
        #print python.unparse(ST.top())
    ct = CodeTemplate(python, target)
    ct.cm_bool = CodeMarker(item = "False")
    sum = smallest_node(find_node(python.parse("0\n"), python.parse_symbol.test))
    print ct.substitute(cm_bool = sum)

    #ct.substitute(cm_bool = "foo")

