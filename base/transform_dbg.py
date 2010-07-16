import sys

__all__ = ["transform_dbg", "t_dbg"]

def t_dbg(spec, cond = None, **kwd):
    '''
    Decorator used to display and check properties of input and output nodes
    that are passed into a node handler.

    Arguments::
        spec    --  specifier string. A specifier string is a list of command specifiers
                    e.g. 'ni no co gc'. Each command spec is only two letters long.

                    Commands can be chained arbitrarily with or without demlimiters.
                    If you use delimiters use whitespace, colons, commas or semicolons.

        cond    --  predicate. If cond predicate is available commands will only be executed when the
                    input data passed the cond filter. cond has the signature cond(node, **locals).


        kwd     --  dictionary containing actions for commands.


    Commands::
        ni   --  display plain node (input)
        no   --  display plain node(s) (output)
        ci   --  display input CST
        co   --  display output CSTs
        cv   --  CST validation test
        so   --  unparsed source output
        si   --  unparsed source input
        sn   --  unparsed source of input node after
                 transformation. Used when input node is modified.
        r1   --  check that result is a single node
        r>   --  check that result is a list of nodes
        r=   --  check that result node ids equals input node id
        r!   --  check that result node ids not equals input node id
        fi   --  arbitrary test function of one argument
                 executed on node input
        fo   --  arbitrary test function of one argument
                 executed on node list output

    Use::

        @transform_dbg("ni cv r1")
        def foo(self, node):
            ...

        @transform_dbg("r>soco")
        def bar(self, node):
            ...

        def raises(ln):
            if ln>1:
                raise ValueError("Only one output argument expected")

        @transform_dbg("r1,co", 'r1' = raises)
        def bar(self, node):
            ...
    '''
    def action(specifier, node, **kwd):
        f = kwd.get(specifier)
        if f:
            f(node, **kwd)

    def transform(f):
        name = f.__name__

        def call_dbg(self, node, **kwd):
            assert isinstance(node, list), type(node)
            assert node, "node == []"
            assert isinstance(node[0], int), type(node[0])
            if cond:
                if not cond(node, **kwd):
                    return f(self, node, **kwd)
            n_id = id(node)%100
            if 'fi' in spec:
                action('fi', node, **kwd)
            if 'ni' in spec:
                print "[ni -- plain node (input) -- %s:%02d>\n"%(name, n_id)
                print node
                action('ni', node, **kwd)
                print "<ni -- plain node (input)-- %s:%02d]\n"%(name, n_id)
            if 'si' in spec:
                print "[si -- source (input) -- %s:%02d>\n"%(name, n_id)
                print self.langlet.unparse(node)
                action('si', node, **kwd)
                print "<si -- source (input) -- %s:%02d]\n"%(name, n_id)
            if 'ci' in spec:
                print "[ci -- cst (input) -- %s:%02d>\n"%(name, n_id)
                self.langlet.pprint(node)
                action('ci', node, **kwd)
                print "<ci -- cst (input) -- %s:%02d]\n"%(name, n_id)

            res = f(self, node, **kwd)

            if 'sn' in spec:
                print "[sn -- source (input node -- after trans) -- %s:%02d>\n"%(name, n_id)
                print self.langlet.unparse(node)
                action('sn', node, **kwd)
                print "<sn -- source (input node -- after trans) -- %s:%02d]\n"%(name, n_id)
            if res:
                assert isinstance(res, (list, tuple)), type(res)
                if isinstance(res[0], int):
                    rlist = [res]
                else:
                    rlist = res
                if 'fo' in spec:
                    action('fo', rlist, **kwd)
                if 'no' in spec:
                    print "[no -- plain node (output) -- %s:%02d>\n"%(name, n_id)
                    print(res)
                    action('no', res)
                    print "<no -- plain node (output) -- %s:%02d]\n"%(name, n_id)

                if 'rs' in spec:
                    print "[rs -- single node return? -- %s:%02d>\n"%(name, n_id)
                    print len(rlist) == 1
                    action('rs', len(rlist))
                    print "<rs -- single node return? -- %s:%02d]\n"%(name, n_id)
                elif 'r>' in spec:
                    print "[r> -- multiple node return? -- %s:%02d>\n"%(name, n_id)
                    print len(rlist) > 1
                    action('r>', len(rlist), **kwd)
                    print "<r> -- multiple node return? -- %s:%02d]\n"%(name, n_id)
                if 'r=' in spec:
                    print "[r= -- nid(return_node) == nid(input_node)? -- %s:%02d>\n"%(name, n_id)
                    print all(x[0] == node[0] for x in rlist)
                    action('r=', rlist, **kwd)
                    print "<r= -- nid(return_node) == nid(input_node)? -- %s:%02d]\n"%(name, n_id)
                if 'r!' in spec:
                    print "[r! -- nid(return_node) != nid(input_node)? -- %s:%02d>\n"%(name, n_id)
                    print all(x[0] != node[0] for x in rlist)
                    action('r!', rlist, **kwd)
                    print "<r! -- nid(return_node) == nid(input_node)? -- %s:%02d]\n"%(name, n_id)
                if 'so' in spec:
                    print "[so -- source (output) -- %s:%02d>\n"%(name, n_id)
                    for i, nd in enumerate(rlist):
                        if i:
                            print "\n---------------- %s ----------------\n"%(i+2)
                        print self.langlet.unparse(nd)
                        action('so', nd, **kwd)
                    print "<so -- source (output) -- %s:%02d]\n"%(name, n_id)
                if 'co' in spec:
                    print "[co -- cst (output) -- %s:%02d>\n"%(name, n_id)
                    for i, nd in enumerate(rlist):
                        if i:
                            print "\n---------------- %s ----------------\n"%(i+2)
                        self.langlet.pprint(nd)
                        action('co', nd, **kwd)
                    print "<co -- cst (output) -- %s:%02d]\n"%(name, n_id)
                if 'cv' in spec:
                    target = self.langlet
                    print "[cv -- cst validation test -- %s:%02d>\n"%(name, n_id)
                    for i, nd in enumerate(rlist):
                        if i:
                            print "\n---------------- %s ----------------\n"%(i+2)
                        target.check_node(nd)
                        action('gc', nd, **kwd)
                    print "<cv -- cst validation test -- %s:%02d]\n"%(name, n_id)
            return res

        call_dbg.__name__ = name
        call_dbg.__doc__  = f.__doc__
        call_dbg.cst_transformer = False
        return call_dbg
    return transform

def transform_dbg(spec, cond = None, **kwd):
    def transform(f):
        call_dbg = t_dbg(spec, cond = cond, **kwd)(f)
        call_dbg.cst_transformer = True
        return call_dbg
    return transform



