def foo(*args):
    funcs=args[0]
    fargs=args[1]
    for i in range(len(funcs)):
        funcs[i](*fargs[i])

def foo1(a,b,c):
    print(a,b,c)

def foo2(c,b,a):
    print(a,b,c)

foo([foo1,foo2],[[1,2,3],[1,2,3]])