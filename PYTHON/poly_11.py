class A:
    def __init__(self,a):
        self.a=a
    def __gt__(self, other):
        return self.a>other.a
ob1=A(2)
ob2=A(3)
if ob1.__gt__(ob2):
    print("ob1 is greater than ob2")
else:
    print("ob2 is greater than ob1")