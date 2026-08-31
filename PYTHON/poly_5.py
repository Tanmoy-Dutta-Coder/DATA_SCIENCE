class Vehical:
    def __init__(self,brand,model):
        self.brand=brand
        self.model=model  
    def move(self):
        print("Move")
class Car(Vehical):
    pass
class Boat(Vehical):
    def move(self):
        print("Sail")
class Plane(Vehical):
    def move(self):
        print("Fly!")
car1=Car("Ford","Mustang")
Boat1=Boat("Ibizta","Touring 20")
plane1=Plane("Boeing","747")
for x in (car1,Boat1,plane1):
    print(x.brand)
    print(x.model)
    x.move()