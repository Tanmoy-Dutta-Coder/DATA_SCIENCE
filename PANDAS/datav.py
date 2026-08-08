import pandas as pd 
import matplotlib.pyplot as plt

dat = {
    'month':['jan','feb','mar','april'],
    'sales':[120,239,21,552],
    'profit':[20,30,40,45]
}
df = pd.DataFrame(dat)
print(df)
df.plot(
    x = 'sales',
    y = 'profit',
    kind = 'hexbin'
)
plt.show()
df.plot(
    x = 'sales',
    y = 'profit',
    kind = 'pie'
)
plt.show()
'''
df.plot(
    x = 'sales',
    y = 'profit',
    kind = 'hexbin'
)
plt.show()
df.plot(
    x = 'sales',
    y = 'profit',
    kind = 'hexbin'
)
plt.show()
df.plot(
    x = 'sales',
    y = 'profit',
    kind = 'hexbin'
)
plt.show()
df.plot(
    x = 'sales',
    y = 'profit',
    kind = 'hexbin'
)
plt.show()
df.plot(
    x = 'sales',
    y = 'profit',
    kind = 'hexbin'
)
plt.show()
'''
data={
    "Name":['ram','sam','bheem','ram','kam'],
    "Age":[12,15,17,12,19],
    "Gender":["male","Female","Female","male","male"],
    "City":['Rishra','kolkata','naihati','noorpur','Diamond Hurbour'],
    "Sub1":[85,75,96,12,45],
    "Sub2":[75,48,92,74,88],
    "Sub3":[45,79,98,45,85]
}
df=pd.DataFrame(data)
print(df)
