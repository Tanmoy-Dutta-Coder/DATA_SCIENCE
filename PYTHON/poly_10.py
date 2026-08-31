class Com:
    def  __init__(self,real,imag):
        self.real=real
        self.imag=imag
    def __add__(self, other):
        return self.real+other.real,self.imag+other.imag
c1=Com(1,2)
c2=Com(2,3)
print(c1+c2)