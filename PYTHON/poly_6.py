# def Add(a,b):
#     a=a+b
# def Add(A,B,C):
#     p= A*B*C
#     print(p)
# Add(10,20,15)


def add(datatype,*args):
    if datatype=='int':
        res=0
    elif datatype=='str':
        res=''
    for item in args:
        res+=item
    print(res)
add('int',5,6)
add('str','hi','Geeks')