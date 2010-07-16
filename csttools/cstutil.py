from langscape.util import psyco_optimized
from langscape.ls_const import*

#####

# list object used to represent CST nodes. Special list attributes are required
# for cst transformations.
class cstnode(list):

    def __init__(self, lst=[]):
        list.__init__(self, lst)
        self.msg = ""
        self.transformable = False
        self.handler  = None
        self.prepared = False

    def __message__(self):
        return self.msg


# Used to add introns to tokens
class csttoken(cstnode):
    def __init__(self, lst=[]):
        super(csttoken, self).__init__(lst)
        self.intron = []

def is_token(nid):
    try:
        return nid%LANGLET_ID_OFFSET<SYMBOL_OFFSET
    except TypeError:
        return False

def is_lexer_token(nid):
    try:
        return nid%LANGLET_ID_OFFSET<TOKEN_OFFSET
    except TypeError:
        return False

def is_keyword(nid):
    try:
        n = nid%LANGLET_ID_OFFSET
        return KEYWORD_OFFSET<=n<SYMBOL_OFFSET
    except TypeError:
        return False

def is_symbol(nid):
    try:
        return nid%LANGLET_ID_OFFSET>=SYMBOL_OFFSET
    except TypeError:
        return False

def is_supersimple(node):
    if is_token(node[0]):
       return True
    if len(node) == 2:
        return is_supersimple(node[1])
    return False

def is_node(node, nid):
    return node[0] == nid

def smallest_node(node):
    if is_token(node[0]):
       return node
    elif len(node) == 2:
        return smallest_node(node[1])
    else:
        return node

def clone_node(node, with_marker = True, memo = None):
    '''
    Creates an identical copy of node.
    '''
    if memo is None:
        memo = {}
    if not isinstance(node, list):
        return node
    elif isinstance(node, cstnode):
        res = cstnode()
        res.msg = node.msg
        res.transformable = with_marker and node.transformable
        res.handler  = node.handler
        res.prepared = node.prepared
    else:
        res = cstnode([])
    for item in node:
        cloned = clone_node(item, with_marker, memo)
        res.append(cloned)
    memo[id(node)] = res
    return res

def is_node(node, nid):
    return node[0] == nid


def remove_from(A, Z):
    '''
    Removes node A from node Z. Only the main axis of Z is considered.
    '''
    id_A = id(A)
    for i, item in enumerate(Z):
        if id(item) == id_A:
            del Z[i]
            return Z
    return Z

def proj_nid(node):
    '''
    Projects node on its nid.
    '''
    return node[0]%LANGLET_ID_OFFSET


def left_shift(node):
    '''
    inplace replacement of [k,[l,...]] by [l,...]
    '''
    rest = node[1]
    return replace_node(node, rest)

def replace_node(old_node, new_node):
    '''
    inplace replacement of old node by new new node.
    @param old: node to be replaced
    @param new: node replacement
    '''
    del old_node[:]
    old_node.extend(new_node)
    return old_node


def replace_all_nodes(old_node, new_node, contains = None):
    '''
    Replace all nodes N within i{context} where nid(N) = i{in_nid} by i{node}
    when a node M with nid(M) = i{nid} can be found in N.

    @param context: contextual cst node
    @param nid: node id that constraints the node to be replaced.
    @param in_nid: node id of the target node of replacement.
    @param node: substitution.
    '''
    nid = node[0]
    for node in find_all(old_node, nid):
        if contains:
            if find_node(node, contains):
                replace_node(node, new_node)
        else:
            replace_node(node, new_node)


def rotate_cst(node, rotaxis = 0):
    nid = node[0]
    if isinstance(node[1], list):
        # print rotaxis == nid, rotaxis, nid
        if rotaxis%LANGLET_ID_OFFSET == nid%LANGLET_ID_OFFSET:
            rotated = [nid] + [rotate_cst(item, rotaxis) for item in node[1:]][::-1]
        else:
            rotated = [nid] + [rotate_cst(item, rotaxis) for item in node[1:]]
    else:
        rotated = node[:]
    return rotated

def postorder(tree):
    '''
    postorder or breadth-first traversal generator.
    '''
    for sub in tree[1:]:
        if isinstance(sub, list):
            for item in postorder(sub):
                yield item
    yield tree

def preorder(tree):
    '''
    preorder or depth-first traversal generator.
    '''
    yield tree
    for sub in tree[1:]:
        if isinstance(sub, list):
            for item in preorder(sub):
                yield item

