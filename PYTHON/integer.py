
##a=np.array([10,20,30,40,50,60,70,80])
##print(a[::-1])
##b=np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12]])
##print(b[:2,2:])
##print(b[::-1])


import numpy as np

print(np.random.rand())

print("-------------")
print(np.random.rand(2,4))
print("--------------")
print(np.random.randint(1,10))
print("------------")
print(np.random.randint(0,10,size=(2,3)))
print("____________")
print(np.random.randn(1,10))
print("----------------------")
d =np.array([1,2,3,4,5,6,7,9,8])
print(np.random.choice(d,size=4))
print("------------")
print(d)
print(np.random.shuffle(d))
print(d)
print("-----------------")


np.random.seed(78)
print(np.random.randint(0,10,size=(2,3)))


