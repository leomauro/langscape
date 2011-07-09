def foo():
    a = ("c",
        0,
        (lambda x: 0+(lambda y: y/1)(2))(1),
        #b.p,
        0,
        1/0,
        b.p)

def bar():
    foo()

bar()
