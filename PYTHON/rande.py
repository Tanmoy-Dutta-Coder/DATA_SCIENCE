import random
class password:
    def p():
        word="ABCDEFGHIJKLmnopqrstUVWXYZ0123456987"
        password="".join(random.sample(word,6))
        print(password,"this is your pass")