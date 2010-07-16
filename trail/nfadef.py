##
## Contains some material that can be used by other nfamodules
## The main purpose is to minimize circularity
##

import string
from langscape.csttools.cstutil import*


SKIP    = '.'
CONTROL = (SKIP, '(', ')', '+')
ALL     = 2
INTRON_NID = 999
MAX_ALLOWED_STATES = 2000

class tokenstring(str):
    def __new__(cls, s, ext = ''):
        obj = str.__new__(cls, s)
        obj.ext = ext
        return obj

def rule_error(langlet, cst, expected_nids, keywords = set(), parts = 10, type = "parse"):
    def get_symbols():
        try:
            return token.sym_name.items()
        except AttributeError:
            return token.token_map.items()

    if type == "parse":
        token = langlet.parse_token
    else:
        token = langlet.lex_token
    rule  ="Failed to apply grammar rule:  "+ langlet.get_node_name(cst[0], type)+": "
    words = []
    for i, item in enumerate(cst[1:]):
        if isinstance(item, (tuple,list)):
            nid = item[0]
            node_name = langlet.get_node_name(nid, type)
            if is_token(nid):
                if nid%LANGLET_ID_OFFSET not in range(TOKEN_OFFSET, TOKEN_OFFSET+7) or item[1] in keywords:
                    try:
                        words.append("'"+item[1]+"'")
                    except TypeError:
                        words.append(node_name)
                else:
                    words.append(node_name)
            else:
                words.append(node_name)
    nid_names = []

    for expnid in expected_nids:
        if is_keyword(expnid):
            nid_names.append(langlet.keywords.get(expnid, expnid))

        elif is_token(expnid):
            value = dict((y,x) for (x,y) in get_symbols()).get(expnid)
            if value and value[0]:
                if expnid == nid:
                    if nid%LANGLET_ID_OFFSET not in range(TOKEN_OFFSET, TOKEN_OFFSET+7):
                        nid_names.append("'"+value+"'")
                    else:
                        nid_names.append(value)
                    break
            else:
                nid_names.append(langlet.get_node_name(expnid, type))
        else:
            nid_names.append(langlet.get_node_name(expnid, type))
    if len(nid_names) == 1:
        expected = nid_names[0]
    else:
        expected = "( "+" | ".join(nid_names)+" )"
    if len(words)>parts:
        rule+=" ".join(words[:3])+" { ... } "
        rule+=" ".join(words[-(parts+3):])
    else:
        rule+=" ".join(words)
    k = len(rule)
    rule+=" "+expected+"\n"+" "*(k+1)+len(expected)*"~"
    return rule


