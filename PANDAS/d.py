import pandas as pd
data={
    "Name":['Tanmoy','Ram','Kumar','Suras',
            'sam'],
    "Joining_Date":['2005-12-16','2005-12-31','2005-12-27','2005-12-12','2005-12-23'],
    "Joining_Time":['14:23:51','02:12:55','23:45:12','12:22:05','01:45:20'],
    "Marks":[45,78,0,25,87]
    }
df=pd.DataFrame(data)
#print(df)
df["Joining_Date"]=pd.to_datetime(df['Joining_Date'])
df["Joining_Time"]=pd.to_datetime(df['Joining_Time'])
df=df.set_index('Joining_Date')
#df=df.set_index()
print(df)
#print(df.loc['2005-07-16'])

#Resample
# week=df.resample("W").sum()
# #print(week)
# Month=df.resample("ME").sum()
# #print(Month)
# Year=df.resample("YE").sum()
# #print(Year)
Day=df.resample("D")
print(Day)
#Rolling_Window
df["p"]=df["Marks"].rolling(window=5).mean()
#print(df)
#print(df.head(3))
#Expanding Windows
df["Exp_avg"]=df['Marks'].expanding().mean()
#print(df)
