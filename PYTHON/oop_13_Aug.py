class Car:
    def __init__(self,model):
        self.model=model
    def Model(self):
        print("This car Modal is :",self.model)
class BMW(Car):
    def __init__(self, model,Type_of_Car):
        self.Type_of_Car=Type_of_Car
        super().__init__(model)
    def Type(self):
        print("The type of car is :",self.Type_of_Car)
b=BMW("M4","EV")
b.Model()
b.Type()
