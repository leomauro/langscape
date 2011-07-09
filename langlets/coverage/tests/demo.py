class Demo:
    def __init__(self,a,b):
        print "Demo.__init__"
        if a or not (b and True) or 1/0:
            if not b:
                while a>-1:
                    if a==0:
                        break
                        a-5        # ...does not detect all unreachables!
                    a-=2
                    if a:
                        continue
                    b-2            # may not be reached
        else:
            print "Demo Result =>  b:",b

    def f(self):
        return 0

if __name__ == '__main__':
    Demo(0,0)
    d = Demo(1.1,0)
    if 0:
        d.f()
