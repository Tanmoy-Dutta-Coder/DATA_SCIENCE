class A:
    def __init__(self,value):
        self.value=value
    def __add__(self, other):
        return self.value+ other.value
ob1=A(1)
ob2=A(2)
print(ob1+ob2)
print(A.__add__(ob1,ob2))
print(ob1.__add__(ob2))
