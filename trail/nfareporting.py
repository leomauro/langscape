from langscape.csttools.cstutil import*

class NFAErrorReport(object):
    def __init__(self, langlet, typ):
        assert typ in ("lex", "parse"), typ
        self.langlet = langlet
        self.typ = typ

    def error_message(self, cst, error_token, expected_nids, max_length = 50):
        rule  ="Failed to apply grammar rule: \n\n    "

        rule_names = []
        for item in cst[1:]:
            if isinstance(item, (tuple, list)):
                nid = item[0]
                rule_names.append(self.langlet.get_node_name(nid, self.typ))

        expected_rules = []
        for nid in expected_nids:
            expected_rules.append(self.langlet.get_node_name(nid, self.typ))

        # format rule sequence
        n1 = len(rule)

        rule+=self.langlet.get_node_name(cst[0], self.typ)+": "
        if len(rule_names)>6:
            front = " ".join(rule_names[:3])
            end   = " ".join(rule_names[-3:])
            k2 = len(end)
            k1 = len(front)
            i  = 4
            while k1+k2<max_length-10 and i<len(rule_names)-3:
                name = rule_names[i]
                front+=" "+name
                k1 = len(front)
                i+=1
            rule+=front+" {...} "+end

        else:
            rule += " ".join(rule_names)
        n2 = len(rule)
        ERR_TOKEN = self.langlet.get_node_name(error_token[0], self.typ)
        rule += " "+ERR_TOKEN+"\n\n"
        rule += " "*(n2-n1+5)+"^"*len(ERR_TOKEN)
        return rule

    def format_terminals(self, terminals):
        kwds = []
        symbols = []
        for t in terminals:
            if is_keyword(t):
                kwds.append(self.langlet.get_node_name(t))
            else:
                token = self.langlet.parse_token
                symbols.append(token.symbol_map.get(t, token.sym_name.get(t, str(t))))
        s = ["\nOne of the following symbols must be used:\n"]
        if kwds:
            s.append("    Keywords")
            for k in kwds:
                s.append("             %s"%k)
        if symbols:
            s.append("    Symbols")
            for k in symbols:
                s.append("             %s"%k)
        return "\n".join(s)


if __name__ == '__main__':
    import langscape as ls
    langlet = ls.load_langlet("python")
    langlet.tokenize("foo(0x89) :?")
