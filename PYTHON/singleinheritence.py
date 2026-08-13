class Animal:
    def __init__(self,name):
        self.name=name
    def info(self):
        print("It's Name is ",self.name)
class Dog(Animal):
    def __init__(self, name,her_name):
        self.her_name=her_name
        super().__init__(name)
    def sound(self):
        print("This Animal Sound Like" ,self.her_name)
d = Dog("Rokey","ghau-ghau")
d.info()
d.sound()