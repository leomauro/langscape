class IPv4(tuple):
    def __init__(self, *args):
        tuple.__init__(self, *args)

    def __repr__(self):
        return "<IPv4: %s>"% ".".join(map(str,self))


