import langscape.util
from collections import deque
from langscape.csttools.cstutil import is_token, is_symbol, LANGLET_ID_OFFSET

MAX_DEPTH = 1000

class optimizer(object):
    activated = False   # right now there is no support for layers

    @classmethod
    def node_cmp(cls, tree, node_id):
        '''
        Compares first node of cst tree with node_id.

        @param tree:  CST
        @param node_id: integer representing a py_symbol or a py_token

        @return:
                 - 0 if node_id is tree-root.
                 - -1 if tree is a py_token or node_id cannot be the node_id of any subtree.
                 - 1 otherwise
        '''
        tree_id = tree[0] % LANGLET_ID_OFFSET
        node_id = node_id % LANGLET_ID_OFFSET
        if tree_id == node_id:           # do we still want this? it makes nodes of two different langlets
            return 0                     # comparable.
        elif is_token(tree_id): # is token
            return -1
        if cls.activated:
            if is_symbol(node_id):
                try:
                    s0 = hierarchy[tree_id]    # global ???
                    s1 = hierarchy[node_id]
                    if s0>s1:
                        return -1
                except KeyError:
                    return 1
            else:
                return 1
        else:
            return 1

######################################################################################################
#
#
#   Search functions
#
#
######################################################################################################

def find_node_1(tree, nid, depth = MAX_DEPTH, exclude = ()):
    '''
    finds one node with a certain node_id.
    '''
    if depth<0:
        return
    res = optimizer.node_cmp(tree, nid)
    if res == 0:
        return tree
    elif res == -1:
        return
    for sub in tree[1:-1]:
        if sub[0] not in exclude:
            res = find_node_1(sub, nid, depth=depth-1, exclude = exclude)
            if res:
                return res

    if isinstance(tree[-1], list) and tree[-1][0] not in exclude:
        return find_node_1(tree[-1], nid, depth=depth-1, exclude = exclude)


def find_node(tree, nid, depth = MAX_DEPTH, exclude = ()):
    '''
    Finds one node of a given node id.

    ( Non-recursive depth first search implementation. )
    '''
    if is_token(tree[0]):
        if nid == tree[0]:
            return tree
        else:
            return
    dq = deque()
    for sub in tree[1:]:
        dq.append((sub, depth-1))
    while dq:
        node, depth = dq.popleft()
        s = node[0]
        if s == nid:
            return node
        elif is_symbol(s) and s not in exclude and depth>0:
            subnodes = zip(node[:0:-1], [depth-1]*(len(node)-1))
            dq.extendleft(subnodes)


def find_one_of(tree, node_ids, depth = MAX_DEPTH, exclude = ()):
    '''
    Generalization of find_node. Instead of one node_id a list of several node ids
    can be passed. The first match will be returned.
    '''
    for nid in node_ids:
        res = find_node(tree, nid, depth = depth, exclude = exclude)
        if res:
            return res

def find_all(tree, node_id, depth=MAX_DEPTH, exclude = (), optimize = True):
    '''
    generator that finds all nodes with a certain node_id.
    '''
    return list(find_all_gen(tree, node_id, depth = depth, exclude = exclude))


def find_all_gen(tree, node_id, depth=MAX_DEPTH, exclude = ()):
    '''
    generator that finds all nodes with a certain node_id.
    '''

    if depth<0:
        raise StopIteration
    res = optimizer.node_cmp(tree, node_id)
    if res == 0:
        yield tree
    elif res == -1:
        raise StopIteration
    for sub in tree[1:]:
        if isinstance(sub, list) and sub[0] not in exclude:
            for item in find_all(sub, node_id, depth=depth-1, exclude = exclude):
                if item:
                    yield item

def find_all_of(tree, node_ids = [], depth=MAX_DEPTH, exclude = ()):
    '''
    Finds all nodes with a node id in node_ids and returns a list of the results.
    '''
    return list(find_all_of_gen(tree, node_ids, depth, exclude))

def find_all_of_gen(tree, node_ids = [], depth=MAX_DEPTH, exclude = ()):
    '''
    generator that finds all nodes with a certain node_id.
    '''

    for node_id in node_ids:
        res = optimizer.node_cmp(tree, node_id)
        if res == 0:
            yield tree
        elif res == -1 or depth<0:
            raise StopIteration
        for sub in tree[1:]:
            if isinstance(sub, list) and sub[0] not in exclude:
                for item in find_all(sub, node_id, depth=depth-1, exclude = exclude):
                    if item:
                        yield item

def find_token_gen(tree, depth = MAX_DEPTH):
    if is_token(tree[0]):
        yield tree
    elif depth<0:
        raise StopIteration
    for sub in tree[1:]:
        if isinstance(sub, list):
            for item in find_token_gen(sub, depth=depth-1):
                if item:
                    yield item

def find_all_token(node, depth = MAX_DEPTH):
    return list(find_token_gen(node, depth))

def count_node(tree, node_id, depth=MAX_DEPTH, exclude = ()):
    '''
    generator that finds all nodes with a certain node_id.
    '''
    res = optimizer.node_cmp(tree, node_id)
    if res == 0:
        return 1
    elif res == -1 or depth<0:
        return 0
    count = 0
    for sub in tree[1:]:
        if isinstance(sub, list) and sub[0] not in exclude:
            count+=count_node(sub, node_id, depth=depth-1, exclude = exclude)
    return count

def remove_node(tree, node, depth = MAX_DEPTH, exclude = ()):
    node_id = node[0]
    res = optimizer.node_cmp(tree, node_id)
    if res == -1:
        return
    if depth<0:
        return
    for i, sub in enumerate(tree):
        if isinstance(sub, list) and sub[0] not in exclude:
            if sub == node:
                tree.remove(sub)
                return True
            else:
                res = remove_node(sub, node, depth=depth-1)
                if res:
                    return res
    return False


##################################################################################################
#
#
#    Chains and chained searches
#
#
##################################################################################################


class Chain(object):
    def __init__(self, chain):
        self._chain = chain

    def bottom(self):
        return self._chain[-1]

    def step(self):
        n = len(self._chain)
        if n == 1:
            return self._chain[-1], None
        elif n>1:
            return self._chain[-1], Chain(self._chain[:-1])
        else:
            return None, None

    def steps(self, k):
        nd, chain = self.step()
        if k == 0:
            return nd, chain
        elif chain is None:
            return None, None
        else:
            return chain.steps(k-1)

    def find(self, nid):
        nd, chain = self.step()
        if nd is None:
            return None, None
        if nd[0]%LANGLET_ID_OFFSET == nid%LANGLET_ID_OFFSET:
            return nd, chain
        else:
            return chain.find(nid)

    def unfold(self):
        '''
        Returns an unfolded list [C0, C1, ... Cn] of nodes in the Chain.
        '''
        nd, chain = self.step()
        lst = [nd]
        if chain:
            return lst+chain.unfold()
        else:
            return lst

    def upper_chain(self, node):
        nd, chain = self.step()
        if nd is None:
            return
        elif id(nd) == id(node):
            return chain
        else:
            return chain.upper_chain(node)


def find_node_chain(tree, nid, depth = MAX_DEPTH, exclude = (), chain = []):
    '''
    Find node and returns as node chain.
    '''
    res = optimizer.node_cmp(tree, nid)
    if res == 0:
        return Chain(chain+[tree])
    elif res == -1:
        return
    if depth<0:
        return
    for sub in tree[1:-1]:
        if sub[0] not in exclude:
            res = find_node_chain(sub, nid, depth=depth-1, exclude = exclude, chain = chain+[tree])
            if res:
                return res

    if isinstance(tree[-1], list) and tree[-1][0] not in exclude:
        return find_node_chain(tree[-1], nid, depth=depth-1, exclude = exclude, chain = chain+[tree])

def find_token_chain(tree, depth = MAX_DEPTH, chain = []):
    if is_token(tree[0]):
        return Chain(chain+[tree])
    if depth<0:
        return
    for sub in tree[1:-1]:
        res = find_token_chain(sub, depth=depth-1, chain = chain+[tree])
        if res:
            return res
    if isinstance(tree[-1], list):
        return find_token_chain(tree[-1], depth=depth-1, chain = chain+[tree])

def find_token_chains_gen(tree, depth = MAX_DEPTH, chain=[]):

    if is_token(tree[0]):
        yield Chain(chain+[tree])
    elif depth<0:
        raise StopIteration
    for sub in tree[1:]:
        if isinstance(sub, list):
            for item in find_token_chains_gen(sub, depth=depth-1, chain = chain+[tree]):
                if item:
                    yield item


def find_all_chains_gen(tree, node_id, depth=MAX_DEPTH, exclude = (), chain = []):
    '''
    generator that finds all nodes with a certain node_id.
    '''
    res = optimizer.node_cmp(tree, node_id)
    if res == 0:
        yield Chain(chain+[tree])
    elif res == -1 or depth<0:
        raise StopIteration
    for sub in tree[1:]:
        if isinstance(sub, list) and sub[0] not in exclude:
            for item in find_all_chains(sub, node_id, depth=depth-1, exclude = exclude, chain = chain+[tree]):
                if item:
                    yield item


def find_all_chains(tree, node_id, depth=MAX_DEPTH, exclude = (), chain = []):
    '''
    generator that finds all nodes with a certain node_id.
    '''
    return list(find_all_chains_gen(tree, node_id, depth = depth, exclude = exclude, chain = chain))

def find_subnodes_at_line(node, line):
    tokens = []
    for C in find_token_chains_gen(node):
        T = C.bottom()
        if len(T)>2:
            if T[2] == line:
                tokens.append(T)
            elif T[2]>line:
                break
    if tokens:
        T0 = tokens[0]
        T1 = tokens[-1]




if __name__ == '__main__':
    import time
    import langscape
    langlet = langscape.load_langlet("python")
    source = open(r"c:\lang\Python27\Lib\site-packages\langscape\langlets\python\tests\pythonexpr.py").read()
    cst = langlet.parse(source)
    a = time.time()
    for name, value in langlet.parse_symbol.__dict__.items():
        if isinstance(value, int):
            find_node_1(cst, value)
    print time.time() - a
    a = time.time()
    for name, value in langlet.parse_symbol.__dict__.items():
        if isinstance(value, int):
            find_node(cst, value)
    print time.time() - a
    for name, value in langlet.parse_symbol.__dict__.items():
        if isinstance(value, int):
            assert find_node(cst, value) == find_node_1(cst, value)



