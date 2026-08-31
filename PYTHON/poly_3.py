class Animal:
    def sound(self):
        return "Some generic Sound"
class Dog(Animal):
    def sound(self):
        return "Berk"
class Cat(Animal):
    def sound(self):
        return "Meow"
animals=[Dog(),Cat(),Animal()]
for animal in animals:
    print(animal.sound())