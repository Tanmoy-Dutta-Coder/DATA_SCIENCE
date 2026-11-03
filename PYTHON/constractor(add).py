class Person:
  def __init__(self, name, age):
    self.name = name
    self.age = age

  def __add__(self, other ):
    return self.age + other.age 

p1 = Person("Tanmoy", 20)
p2 = Person("rahul", 24)
p3=Person("Kumar", 23)

print(p1  + p3)