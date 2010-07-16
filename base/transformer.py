# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    10 May 2006
#
# Genereral CST transformation module. Defines two classes FSTransformer and Transformer.
#
# Transformer is derived from FSTransformer whereas FSTransformer holds one or more
# instances of Transformer objects. Transformer objects are langlet specific and FSTransformer
# collects node handler methods defined for Transformers.
#


# TODO: transformer is not langlet independent

import sys
from langscape.util.path import path
from langscape.util import psyco_optimized
from langscape.csttools.cstsearch import*
from langscape.csttools.cstrepr import*
from langscape.csttools.cstcheck import*
from langscape.csttools.cstutil import is_token
from langscape.base.langlet import LangletTable
from langscape.base.transform_dbg import transform_dbg, t_dbg
import langscape.base.loader as loader


__all__ = ["Transformer", "transform", "transform_dbg", "t_dbg"]


# new transformer?

# Required: a simple visitor for a single langlet transformer.
# Challenge: If N is an Input node and [A, B, C, ... ] are output nodes, find a safe method
#            to replace N.
#            This might be fully encapsulated and tested using Chain objects:
#
#            1. Fetch all node chains for nodes which are decorated. No marker is needed.
#            2. Apply handlers on those nodes.
#            3. Retrofit returned nodes ( if there are any ) into the Chain.
#
# Problems:  What if N -> N' eliminates nodes, which have been found?
#

class TransformDecorator(object):
    def __init__(self, kwds = None):
        self.kwds = kwds

    def __call__(self, fn):
        fn.cst_transformer = True
        if self.kwds:
            fn.kwd_transformer = self.kwds
        return fn

    def keyword(self, kwd, *kwds):
        if kwds:
            return TransformDecorator((kwd,)+kwds)
        else:
            return TransformDecorator((kwd,))

transform = TransformDecorator()

class Transformer(object):
    def __init__(self, langlet):
        self.langlet = langlet
        self.token   = self.langlet.parse_token
        self.symbol  = self.langlet.parse_symbol
        self.keyword = self.langlet.parse_nfa.keywords
        self.fn      = self.langlet.fn
        self.options     = {}
        self._handler    = {}
        self._node_stack = {}
        self._find_handler()

    def run(self, tree, **kwd):
        self.options = kwd
        self._node_stack = {}
        cst = self.mark_node(tree)
        self.transform_tree(cst, [])
        return cst

    def count_node_handlers(self):
        return len(self._handler)

    def node_stack(self, node):
        chain = self._node_stack.get(id(node))
        if chain:
            return Chain(chain)
        else:
            raise ValueError("No node_stack available for node")

    def _find_handler(self):
        '''
        Method used to find all methods that handle one node.
        '''
        items = [(name, getattr(self, name)) for name in dir(self)]
        for name, val in items:
            if hasattr(val, "cst_transformer"):
                if hasattr(val, "kwd_transformer"):
                    for kwd in val.kwd_transformer:
                        self._handler[self.keyword[kwd]] = val
                elif hasattr(self.symbol, name):
                    self._handler[getattr(self.symbol, name)] = val
                elif hasattr(self.token, name):
                    self._handler[getattr(self.token, name)] = val
                else:
                    raise ValueError("Cannot find token, symbol or keyword that matches '%s'"%val)


    def mark_node(self, tree, parent = None, par_idx = -1, untrans = set()):
        '''
        Method used to apply settings on nodes having node id's that correspond with
        node handlers.

        If relevant node N was found wrap N into a cstnode object and set ::

             N.transformable = True
        '''
        nid = tree[0]
        if not nid in untrans:
            h = self._handler.get(nid)
            if h:
                if not isinstance(tree, cstnode):
                    cst = cstnode(tree)
                else:
                    cst = tree
                cst.transformable = True
                cst.prepared = True
                if parent:
                    parent[par_idx] = cst
            else:
                untrans.add(nid)
                cst = tree
        else:
            cst = tree
        for i,sub in enumerate(cst[1:]):
            if isinstance(sub, list):
                if isinstance(sub, cstnode):
                    if sub.prepared:
                        break
                self.mark_node(sub, cst, i+1, untrans)
        return cst

    def unmark_node(self, tree, nid = -1):
        '''
        Unmark all nodes i.e. set N.transformable = False on all cstnode
        objects.
        '''
        if isinstance(tree, cstnode):
            if nid>=0:
                if is_node(tree, nid):
                    tree.transformable = False
            else:
                tree.transformable = False
        for item in tree[1:]:
            if isinstance(item, list):
                self.unmark_node(item, nid)
        return tree

    def is_transformable(self, tree):
        return isinstance(tree, cstnode) and tree.transformable

    def to_node_list(self, handler_name, nodes):
        if isinstance(nodes, list):
            if isinstance(nodes[0], int):
                return (nodes,)
            elif not isinstance(nodes[0], list):
                raise TypeError("unsupported type '%s' as element type of return value of node transformer '%s'"%(type(nodes[0]), handler_name))
        elif not isinstance(nodes, tuple):
            raise TypeError("unsupported type '%s' of return value of node transformer '%s'"%(type(nodes[0]), handler_name))
        nid = nodes[0][0]
        for node in nodes[1:]:
            if node[0]!=nid:
                raise ValueError("Nodes must all of the same node-id. Nodes of type '%s' and '%s' found for handler '%s'"%(
                        self.langlet.get_node_name(nid), self.langlet.get_node_name(node[0]), handler_name))
        return nodes

    def create_translation_error(self, tree, nodes, node_stack):
        repl_id = nodes[0][0]
        if is_token(repl_id):
            raise TranslationError("Cannot substitute non-terminal %s by terminal %s"%(
                 (tree[0], self.langlet.get_node_name(tree[0])),
                 (repl_id, self.langlet.get_node_name(repl_id))
                ))
        else:
            trace = [(tree[0], self.langlet.get_node_name(tree[0]))]
            while node_stack:
                P = node_stack.pop()
                trace.append((P[0], self.langlet.get_node_name(P[0])))
            trace = str(trace)

            S = "Failed to substitute node %s by %s.\n  Node %s must be one of the nodes or a projection in:  \n\n%s"%(
                 (tree[0], to_text(tree[0])),
                 (repl_id, to_text(repl_id)),
                 (repl_id, to_text(repl_id)),
                 trace)
        raise TranslationError( S )

    def substitute(self, tree, nodes, node_stack):
        '''
        Let (parent(tree), parent(parent(tree)), ..., parent(...(parent(tree))...))
        the parental hierarchy of tree. It can be denoted as (P1, ..., P(n)) where P(i) is
        the node id of the i-th grandparent of tree.

        The substitution algorithm seeks for P(i) with repl_id == P(i). If found it
        replaces P(i) in P(i+1) with nodes = (N1, ..., N(k)). It is guaranteed that the node
        id of N(j) is repl_id.
        '''
        repl_id = nodes[0][0]

        if is_token(repl_id):          # replace token
            if is_token(tree[0]):
                tree[:] = nodes[0]
                return (tree, node_stack)
        else:
            i = len(node_stack)-1
            while i>=0:
                P = node_stack[i]
                i-=1
                if repl_id == P[0]:
                    try:
                        nd_list = node_stack[i]
                        i-=1
                        for j, N in enumerate(nd_list):
                            if id(N) == id(P):
                                nd_list[:] = nd_list[:j]+list(nodes)+nd_list[j+1:]
                                return (nd_list, node_stack[i-1:])
                    except IndexError:    # nothing to pop from node_stack
                        P[:] = nodes[0]
                        return (P, node_stack[i-1:])
                C_0 = P
        self.create_translation_error(tree, nodes, node_stack)


    def transform_tree(self, tree, chain):
        if self.is_transformable(tree):
            nid = tree[0]
            handler = self._handler.get(nid)
            if handler:
                self._node_stack[id(tree)] = chain
                tree.transformable = False
                nodes = handler(tree)
                if nodes:
                    nodes = self.to_node_list(handler.__name__, nodes)
                    (N, parent_chain) = self.substitute(tree, nodes, chain)
                    self.transform_tree(N, parent_chain+[N])
                    return
        for sub in tree[1:]:
            if isinstance(sub, list):
                self.transform_tree(sub, chain+[tree])


