from foldet.rande import password
class Shape:
    def draw(self):
        print("Start with shape")
class Circle(Shape):
    def draw_circle(self):
        for i in range(6):
            password.p()
class red(Circle):
    def color(self):
        print("paisa de do")
d=red()
d.color()
d.draw_circle()
d.draw()