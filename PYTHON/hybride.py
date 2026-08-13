class A:
    def method1(self):
        print("This is method 1")
class B(A):
    def method2(self):
        print("This is Method 2")
class C(A):
    def method3(self):
        print("This is Method 3")
class D(B,C):
    def method4(self):
        print("this is method 4")
d=D()
d.method1()
d.method2()
d.method3()
d.method4()