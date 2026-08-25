# class Learning_Hub:
#     def __init__(self,Name,Dept):
#         self.Name=Name
#         self.Dept=Dept
# class Trainer:
#     def __init__(self,Name,Dept,Job_role):
#         self.Hub=Learning_Hub(Name,Dept)
#         self.Job=Job_role
#     def info(self):
#         print(f"The employee is {self.Hub.Name} Depertment is {self.Hub.Dept} and Job Role is {self.Job}")
# tea=Trainer("Kartik Sir","IT","Devloper")
# tea.info()
# teacher=Trainer("Pragaya Mam","IT","Trainer")
# teacher.info()       

class Shape:
    def __init__(self,Draw,type):
        self.D=Draw
        self.T=type
    def draw(self):
        print(f"Start with {self.D}")
class Circle:
    def __init__(self,D,T):
        self.c=Shape(D,T)
    def draw_circle(self):
        print(self.c.D)
class red:
    def __init__(self,D,T):
        self.R=Circle(D,T)
    def color(self):
        print(f"paisa de do{self.R.draw_circle()}")
# d=Circle("Ball",'pencile')
# # d.color()
# d.draw_circle()
# d.c.draw()
k=red("car","blaok")
k.color()
# k.c.draw_circle()