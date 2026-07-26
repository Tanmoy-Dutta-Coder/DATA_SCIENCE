def letter():
    x=input("Enter your String :")
    y=input(f"Enter what is you remove from {x}:")
    X=x.upper()
    Y=y.upper()
    if Y in X:
         L1=list(X)
         L1.remove(Y)
         print(L1)
    else:
         print("enter y from  x not other")
# letter()

def evlen():
    x=input("Enter Your String:").upper()
    word=x.split()
    for i in word:
        if len(i) %2 ==0:
            print(i)
        else:
            print("No")
# evlen()

def uphalf():
    x=input("Enter a String :")
    if len(x)%2==0:
        s=x.split()
        print(s)
        for i in s:
           print(i)
uphalf()
#uppercase of half string
def uphalf():
    x=input("Enter a string :")
    word=x.split()
    for i in word:
        u=i[:(len(i)//2)].upper()
        print(u)
# uphalf()

def capfl():
    x=input("Enter a string :")
    word=x.split()
    for i in word:
        print(i)
        u=i[0].upper()
        v=i[-1].upper()
        print(f"First letter {u} and last lette {v}")
# capfl()


def letnum():
    x=input("Enter a string :")
    word=x.split(" ")
    for i in word:
        # print(i,i.isnumeric())
        if i.isnumeric()==True:
            print(f"{i} is Number")
        elif i.isalpha()==True:
            print(f"{i} is alphabate")
        else:
            print(f"{i} is another type")
# letnum()

def countv():
    count=0
    x=input("Enter a string :")
    word=x.split()
    v=["a","e","i","o","u"]
    for i in word:
        for j in i:
            if j in v:
                count=count+1
    print(count)
# countv()

def revduo():
    x=input("Enter 1st string :")
    y=input("Enter 2nd String :")
    word1=x.split()
    word2=y.split()
    for i in word1:
        print(i)
        for j in i:
            print(j)
            k=j in i
            if k == True:
                print(k)

revduo()

