class Calculator:
    def multiply(self,a=1,b=1,*args):
        result=a*b
        for num in args:
            result*=num
        return result
calc=Calculator()
print(calc.multiply())
print(calc.multiply(4))
print(calc.multiply(2,3))
print(calc.multiply(2,3,4))
