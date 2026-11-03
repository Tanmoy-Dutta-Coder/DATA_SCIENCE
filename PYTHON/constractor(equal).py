class am:
    def __init__(self,name,branch):
        self.name=name
        self.branch=branch
    def __eq__(self,other):
        return self.name==other.name and self.branch==other.branch
s1=am("Ram","CSE")
s2=am("Ram","CSE")
print(s1==s2)
        