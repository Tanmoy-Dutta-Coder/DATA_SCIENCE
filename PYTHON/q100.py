'''
Variables & Data Types
Write a Python program to swap two variables without using a third variable and without using tuple unpacking.
Write a program to find the second largest number in a list without using sort(), max(), or min().
Write a program to remove duplicate elements from a list without using set(), while preserving the original order.
Write a program to find all elements that occur exactly twice in a list.
Write a program to find the first non-repeating element in a list.
Write a program to find all duplicate values from a dictionary.
Write a program to convert a nested list into a single flat list without using external libraries.
Write a program to rotate a list by K positions without using built-in rotation functions.
Functions
Write a function that accepts any number of integers and returns the largest, second-largest, smallest, and average without using max(), min(), or sort().
Write a recursive function to calculate the sum of digits of a number.
Write a recursive function to reverse a string without using slicing.
Write a recursive function to generate the first N Fibonacci numbers.
Write a function that accepts another function as an argument and applies it to every element of a list.
Write a decorator that counts how many times a function has been called.
Write a decorator that measures and prints the execution time of a function.
Write a decorator that allows a function to execute only if the user has permission "admin".
Write a function that accepts any number of positional and keyword arguments and returns a structured dictionary containing both.
Write a function that finds whether two strings are anagrams without using sorted().
String & Data Processing
Write a program to find the longest substring without repeating characters.
Write a program to find the longest word in a sentence without using max().
Write a program to compress a string using character counts.

Example:

Input:  aaabbcccc
Output: a3b2c4
Write a program to find the first character that appears only once in a string.
Write a program to check whether a string is a palindrome while ignoring spaces, punctuation, and letter case.
Write a program to find all pairs of numbers in a list whose sum equals a given target.
Write a program to find the intersection of two lists without using set().
Write a program to group a list of words into groups of anagrams.
Write a program to find the most frequently occurring word in a paragraph while ignoring punctuation and case.
Write a program to parse a string containing employee records and calculate the employee with the highest salary.
Class & Object Programming
Create a Student class that stores marks for multiple subjects and calculates total, percentage, grade, and rank.
Create a Product class where price cannot be set to a negative value. Implement proper encapsulation.
Create a ShoppingCart class supporting add product, remove product, update quantity, calculate subtotal, discount, tax, and final price.
Create a Library system using Book, Member, and Library classes. Implement issue, return, search, and overdue-book functionality.
Create a Hotel booking system using Hotel, Room, Customer, and Booking classes. Prevent booking an already occupied room.
Create an Employee hierarchy:
Employee
 ├── Developer
 ├── Manager
 └── HR

Each class must calculate salary differently using polymorphism.

Create a Vehicle hierarchy:
Vehicle
 ├── Car
 ├── Bike
 └── Truck

Implement polymorphic calculate_rent() methods.

Create a Payment hierarchy:
Payment
 ├── UPI
 ├── CreditCard
 ├── DebitCard
 └── Cash

Implement a common process_payment() interface.

Advanced OOP Programming
Create a Money class supporting:
m1 + m2
m1 - m2
m1 == m2
m1 > m2

Prevent operations between different currencies.

Create a custom EmployeeCollection class that supports:
len(employees)
employees[0]
for employee in employees:
    ...

Implement the required magic methods.

Create a custom context manager:
with DatabaseTransaction() as transaction:
    transaction.execute()

Commit when successful and rollback when an exception occurs.

Create an abstract PaymentGateway class and implement:
Razorpay
Stripe
Cashfree

Each class must implement pay() and refund().

Create a booking system using inheritance and polymorphism where:
Booking
 ├── FlightBooking
 ├── HotelBooking
 └── BusBooking

Each booking type calculates its own price.

Implement a SingletonDatabase class where multiple calls return the same object.
Implement a Factory that dynamically creates:
PaymentFactory.create("upi")
PaymentFactory.create("card")
PaymentFactory.create("cash")
Implement a thread-safe bank transfer system where two accounts can be accessed by multiple threads without causing incorrect balances.
Implement an LRU Cache from scratch with:
cache.get(key)
cache.put(key, value)

Both operations should have approximately O(1) average time complexity.

Final Project: Build a complete Travel Booking Management System using Python OOP.

It must support:

Customer
Agent
Hotel
Room
Flight
Airline
HotelBooking
FlightBooking
Payment
Invoice
Cancellation
Discount
Notification

Required operations:

Customer registration
Hotel booking
Flight booking
Room availability
Payment
Cancellation
Refund
Invoice generation
Discount calculation
Booking history
Revenue calculation
'''
'''
#Variable & Data type
def swap(var1,var2):
    print(f"Your current numbers are {var1} & {var2}")
    var1,var2=var2,var1
    print("After swaping ....")
    print(f"Now Your current numbers are {var1} & {var2}")
swap(45,24)
'''
'''
n=int(input("Enter the range :"))
ls=[]
for i in range(n):
    ele=int(input("Enter a element :"))
    ls.append(ele)
print(ls)
if ls[0]>ls[1]:
    larg=ls[0]
    s_larg=ls[1]
else:
    larg=ls[1]
    s_larg=ls[0]
for num in ls:
    if num > larg:
        s_larg=larg
        larg=num
    elif num > s_larg and num!=larg:
        s_larg=num
print("The second larg number is ",s_larg)
'''
'''
n=int(input("Enter the range :"))
ls=[]
new_ls=[]
for i in range(n):
    ele=int(input("Enter a element :"))
    ls.append(ele)
print(ls)
for j in ls:
    if j not in new_ls:
        new_ls.append(j)
print(new_ls)
'''
'''
n=int(input("Enter the range :"))
ls=[]
new_ls=[]
count=0
for i in range(n):
    ele=int(input("Enter a element :"))
    ls.append(ele)
print(ls)
for j in ls:
    if ls.count(j)==2:
        new_ls.append(j)
        ls.remove(j)
print(new_ls) 
'''
#Write a program to find the first non-repeating element in a list.
'''
n=int(input("Enter the range :"))
ls=[]
new_ls=[]
for i in range(n):
    ele=int(input("Enter a element :"))
    ls.append(ele)
print(ls)
for j in ls:
    if ls.count(j)==1:
        new_ls.append(j)
print(new_ls)
'''
# Write a program to find the frequency of every character in a string without using collections.Counter.
'''
string=input("Enter a string:")
ls=list(string)
for i in ls:
    frequency=0
    for j in range(len(ls)):
        if i == ls[j]:
            frequency += 1
    print(f"Frequency of {i} is :{frequency}")
'''
# Write a program to merge two dictionaries. If a key exists in both dictionaries, add their values.
'''
dict1={
    "name":"ram",
    "age":19
}
dict2={
    "name":"sam",
    "age":10
}
result=dict1.copy()
for key,value in dict2.items():
    if key in result:
        result[key]=result[key]+value
    else:
        result[key]=value
print(result)

'''
# Create an Employee class that automatically generates a unique employee ID for every object.
class Employee:
    _next_id = 1000

    def __init__(self, name):
        self.name = name
        self.employee_id = Employee._next_id
        Employee._next_id += 1

    def display(self):
        print(f"Employee ID: {self.employee_id}, Name: {self.name}")
'''
e1=Employee("Shivesh Tiwari")
e2=Employee("Soumodip Jana")
e3=Employee("Sudip Jana")
e4=Employee("Soumallyo Ghose")
e5=Employee("SHubham Jana")
e1.display()
e2.display()
e3.display()
e4.display()
e5.display()
'''
# Create a BankAccount class supporting deposit, withdrawal, balance checking, and transaction history. Prevent invalid withdrawals.

from datetime import datetime

class BankAccount:
    def __init__(self, account_holder, balance=0):
        self.balance = balance
        self.account_holder = account_holder
        self.history = []

    def deposit(self, amount):
        if amount < 0:
            print("The amount cannot be less than zero")
            return False
        else:
            self.balance = self.balance + amount         
            self.record_transaction("deposit", amount)
            print(f"The deposited amount is {amount}.\nThe new balance is {self.balance}")
            return True

    def withdraw(self, amount):  
        if amount > self.balance:
            print("The account has insufficient balance. Enter amount less or equal to the remaining balance.")
            return False
        elif amount < 0:
            print("The amount cannot be less than 0")
            return False
        else:
            self.balance = self.balance - amount
            self.record_transaction("withdraw", amount)
            print(f"The withdrawn amount is {amount}.\nNew balance is: {self.balance:.2f}")
            return True

    def check_balance(self):
        print("The current balance this account holds is:", self.balance)
        return self.balance
        
    def show_transaction_history(self):
        if not self.history:
            print("No transaction done yet")
            return
        else:
            print(f"Transaction history of account holder: {self.account_holder}")
            for item in self.history:
                print(item)

    def record_transaction(self, transaction_type, amount):
        time = datetime.now()
        record_entry = f"[{time}] {transaction_type}: {amount}, balance: {self.balance}"
        self.history.append(record_entry)


name = input("Enter account holder name: ")
while True:
    initial_balance = int(input("Enter your initial balance: "))
    if initial_balance < 0:
        print("Enter valid balance")
        continue
    break

account = BankAccount(name, initial_balance)

while True:
    menu = """
1. Deposit
2. Withdrawal
3. Check balance
4. Transaction history
5. Exit
"""
    print(menu)
    choice = int(input("Choose any one of the options: "))
    if choice == 1:
        amount = int(input("Enter deposit amount: "))
        account.deposit(amount)
    elif choice == 2:
        amount = int(input("Enter withdrawal amount: "))
        account.withdraw(amount)
    elif choice == 3:
        account.check_balance()
    elif choice == 4:
        account.show_transaction_history()
    elif choice == 5:
        print(f"Thank you for using our service, {name}!")
        break 
    else:
        print("Choose an option that is between 1-5")  
    print("\n" + "-"*40 + "\n")