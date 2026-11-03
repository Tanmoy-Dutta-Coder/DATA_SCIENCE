# always reutrn string
class student:
    def __init__(self,name):
        self.name=name
    def __str__(self):
        return self.name
k=student("Ram Narayan")
print(k)

class person:
    def __init__(self,name,age):
        self.name=name
        self.age=age
    def __str__(self):
        return f"{self.name}({self.age})"
p1=person("Tanmoy",19)
print(p1)