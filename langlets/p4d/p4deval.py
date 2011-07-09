# TODO: advance this module by
#
#  1. improving p4dbase, s.t. edit operations like replicating a node can be expressed in a more
#     direct style
#
#  2. The evaluator is currently
#
#           mapeval(node, locals, globals)
#
#     It could possibly be improved using an additional dict:
#
#           mapeval(node, nodevars, locals, globals)
#
#     nodevars contains P4D expressions which will be evaluated.
#

import copy
import p4dbase
from langscape.util.flatstring import is_flatstring, flatstring_revert

def hide_bad_chars(s):
    return s.replace("'", '\x01').replace('"','\x02').replace('\n', '\x03')

def restringify(s):
    r = s.replace('\x01', "'").replace('\x02', '"').replace('\x03', '\n')
    if r:
        if r[0] == '"':
            return r.strip('"')
        elif r[0] == "'":
            return r.strip("'")
    return r

def objectify(obj):
    if hasattr(obj, "object_data"):
        return obj.object_data()
    else:
        return str(obj)

def eval_str(item, _globals, _locals):
    if isinstance(item, basestring):
        if item.startswith("evaltostr_"):
            return str(eval(item[10:], _globals, _locals))
        elif item.startswith("evaltonum_"):
            return eval(item[10:], _globals, _locals)
        elif is_flatstring(item):
            return flatstring_revert(item)
        return item
    else:
        return item

def eval_attr(container, _globals, _locals):
    for key, val in container.items():
        if isinstance(val, basestring):
            if val.startswith("evaltostr_"):
                container[key] = str(eval(val[10:], _globals, _locals))
            elif val.startswith("evaltoobj_"):
                obj = eval(val[10:], _globals, _locals)
                container[key] = objectify(obj)
            elif is_flatstring(val):
                container[key] = eval(flatstring_revert(val), _globals, _locals)
            elif val.startswith("deferredeval_"):
                deferredp4d = DeferredP4D(val[13:], (container, key), None)
                container[key] = deferredp4d
                _globals["deferredobj"].append(deferredp4d)

class DeferredP4D(object):
    def __init__(self, lambdaexpr, (container, index), parent):
        self.lambdaexpr = lambdaexpr
        self.container  = container
        self.index  = index
        self.parent = parent

def eval_deferred(p4dobj, deferredp4d, deferredobj):
    fn  = eval(deferredp4d.lambdaexpr, globals(), locals())
    obj = fn(p4dobj)
    if isinstance(obj, DeferredP4D):
        exp = deferredp4d.lambdaexpr[deferredp4d.lambdaexpr.index(':')+1:]
        raise ValueError("Cannot support P4D element '%s' with '%s: && %s'."%(deferredp4d.container[0], deferredp4d.container[0], exp))
    if type(deferredp4d.index) == int:
        if isinstance(obj, list):
            deferredp4d.container[2] = obj
            deferredp4d.container[-1] = ''
        elif isinstance(obj, p4dbase.P4D):
            deferredp4d.container[2] = [obj]
            deferredp4d.container[-1] = ''
        else:
            if isinstance(obj, str) and obj.startswith("<langscape.langlets.p4d.p4deval.DeferredP4D object"):
                deferredobj.append(deferredp4d)
                #exp = deferredp4d.lambdaexpr[deferredp4d.lambdaexpr.index(':')+1:]
                #raise ValueError("Invalid chained reference in P4D element '%s' with '%s: && %s'."%(deferredp4d.container[0], deferredp4d.container[0], exp))
            deferredp4d.container[deferredp4d.index] = obj
    else:
        deferredp4d.container[deferredp4d.index] = obj
    return obj


def mapeval(S, _globals, _locals):
    if isinstance(S, basestring):
        C = eval(S)
    else:
        C = S

    replace = {}
    deferredobj = []

    def eval_all(container, pa, grandpa):
        # TODO: needs a more reliable algorithm.
        #       The following mess works within the bounds of the
        #       the tests but I suspect it's still broken.
        #
        removable = False
        for i, item in enumerate(container):
            if isinstance(item, dict):
                eval_attr(item, _globals, _locals)
            elif isinstance(item, list):
                container[i] = eval_all(item, container, pa)
            elif isinstance(item, str):
                obj = eval_str(item, _globals, _locals)
                if obj is not item:
                    container[i] = obj
                elif item.startswith("deferredeval_"):
                    deferredp4d = DeferredP4D(item[13:], (container,i), pa)
                    container[i] = deferredp4d
                    deferredobj.append(deferredp4d)
                elif item.startswith("evaltoobj_"):
                    try:
                        obj = eval(item[10:], _globals, _locals)
                    except NameError:
                        print "\nGLOBALS", _globals.keys()
                        print "LOCALS", _locals.keys()
                        raise
                    if hasattr(obj, "object_data"):
                        container[i] = obj.object_data()
                    elif hasattr(obj, "flow_value"):
                        pa[-1] = copy.copy(obj)
                        removable = True
                    else:
                        # grandpa -> [
                        #             pa ->  [tagB, {...}, [...], lstB],
                        #                    [tagC, {...}, [...], contC],
                        #                    ...
                        #
                        if isinstance(obj, (tuple, list)):
                            for k, son in enumerate(grandpa):
                                if pa[0] == son[0]:
                                    node = son[:]
                                    break
                            has_sub  = False
                            elements = []
                            for elem in [eval_all([objectify(x)],[],[])[0] for x in obj]:
                                if isinstance(elem, (list, tuple)):
                                    elements.append(elem)
                                    has_sub = True
                                else:
                                    elements.append(eval_str(elem,_globals,_locals))

                            if isinstance(elements[0], (int, float, basestring)):
                                pa[-1] = elements[0]
                                removable = True
                                S = [node[0], dict(node[1]),[], '']
                                inserted = False
                            else:
                                S = pa
                                inserted = True
                                container[i] = elements[0]
                            for j, elem in enumerate(elements[:0:-1]):
                                if isinstance(elem, (int,float,basestring)):
                                    grandpa.insert(k+1, [node[0], dict(node[1]),[], elem])
                                else:
                                    if not inserted:
                                        grandpa.insert(k+1, S)
                                        k+=1
                                        inserted = True
                                    S[2].insert(i+j, elem)
                        else:
                            if obj is not None:
                                r = eval_str(obj, _globals, _locals)
                                if pa[-1]:
                                    if isinstance(pa[-1], list):
                                        pa[-1].append(r)
                                    else:
                                        pa[-1] = p4dbase.P4DContentList([pa[-1], r])
                                else:
                                    pa[-1] = r
                            removable = True
        if pa and removable:
            children = pa[2]
            for i in range(len(children))[::-1]:
                if not type(children[i]) == list:
                    del pa[2][i]
        return container
    _tree = eval_all(C,[],[])
    if deferredobj:
        while deferredobj:
            obj = deferredobj.pop(0)
            p4dobj = p4dbase.P4D(_tree)
            eval_deferred(p4dobj, obj, deferredobj)
            _tree = p4dobj._tree
        return p4dobj._tree
    return _tree


