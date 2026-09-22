class Student:
    def grade(self):
        mark=int(input("Enter your marks (0-100):"))
        if mark>100 or mark<0:
            print("Sorry , it is invalid")
        else:
            if mark>=90 and mark<=100:
                print("Congratulation you got ... A+")
            elif mark>=80 and mark<=89:
                print("WellDone you got ... A")
            elif mark>=70 and mark<=79:
                print("Good Job For your grade B and Focus")
            elif mark>=60 and mark<=69:
                print("ok you got C, fOCUS ON YOU STUDY")
            elif mark>=50 and mark<=59:
                print("Study Hard you got only D")
            elif mark<50:
                print("congraculation You are Fail")
std=Student()
# std.grade()

class Tax:
    def payer(self):
        salry=int(input("Enter Your Salary :"))
        if salry>0 and salry<=300000:
            print(f"In your current salary {salry} there is 0% tax")
        elif salry>=300001 and salry<=600000:
            new_salry=salry-(salry*(0.06))
            print(f"Your salary is {salry} after tax your current salry is {new_salry}")
        elif salry>=600001 and salry<=1000000:
            new_salry=salry-(salry*(0.1))
            print(f"Your salary is {salry} after tax your current salry is {new_salry}")
        elif salry>=1000001:
            new_salry=salry-(salry*(0.15))
            print(f"Your salary is {salry} after tax your current salry is {new_salry}")
        else:
            print("Sorry, 1st go for income!!!")
income_tax=Tax()
# income_tax.payer()




class Ticket:
    def pricing(self):
        age=int(input("Enter Your age:"))
        if age>0 and age<=5:
            print(f"Your age is {age} you have free ride")
        elif age>5 and age<=12:
            print(f"Your age is {age} you have to pay Rs.{10}")
        elif age>=13 and age<=59:
            print(f"Your age is {age} you have to pay Rs.{50}")                    
        elif age>=60 and age<=79:
            print(f"Your age is {age} you have to pay Rs.{60}")
        elif age>=80:
            print(f"Your age is {age} you have to pay Rs.{"Free"},ready to meet Yamraj ji")
        else:
            print("Sorry apke jindagi abhi suru nahi hua hai..")
tic=Ticket()
# tic.pricing()


class BMI:
    def bmi_cal(self):
        weight=float(input("ENter your Weight:"))
        height=float(input("ENter your height:"))
        print(f"Your BMI is {weight/(height**2)}")
bmi_sys=BMI()
# bmi_sys.bmi_cal()



class ATM:
    def user(self):
        print("Hello !!")
        print("Wellcome")
        print("Create a account:")
        ac_holder=input("Enter your name for account holder name:")
        ac_balence=int(input("Enter your account balence:"))
        atm_pin=input("Enter your pin :")
        if len(atm_pin)==4 or len(atm_pin)==6:
            print("your Pin is approve !!!")
        else:
            print("Enter a vslid pin")
            atm_pin=int(input("Enter your pin :"))
        while True:
            choice=int(input("""Choose what you want to do :
            1)withdrawl
            2)Balence Check
            3)Deposite
            4)PIN Change
            5)Exit
                    """))
            if ac_balence>1000:
                if choice==1:
                    amount=int(input("Enter how much you withdrawl :"))
                    if amount<(ac_balence-1000):
                        ac_balence=ac_balence-amount
                        print(f"you Withdral {amount} and your current balence is {ac_balence}")
                    else:
                        print("please take your maintanence balence !!")
                elif choice==2:
                    print(f"The account holder is {ac_holder} and current balence is {ac_balence}")
                elif choice==3:
                    amount=int(input("Enter the deposite amount:"))
                    ac_balence=ac_balence+amount
                    print(f"You deposite {amount} rupees and current balence is {ac_balence}")
                elif choice==4:
                    new_pin=int(input("enter new pin:"))
                    if len(atm_pin)==4 or len(atm_pin)==6:
                        print("your Pin is approve !!!")
                    else:
                        print("Enter a vslid pin")
                        new_atm_pin=int(input("Enter your pin :"))
                elif choice!=1 or choice!=2 or choice!=3 or choice!=4 : 
                    break
atm_machine=ATM()
# atm_machine.user()










