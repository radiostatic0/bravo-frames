import sys
import os

path="C:\\Users\\yayar\\Desktop\\twitterbot\\frames\\2\\13"


filelist=os.listdir(path)

for i in range(len(filelist)):
    filelist[i]=float(filelist[i][:-4].replace("-","."))
filelist.sort()

for i in range(len(filelist)):
    if "." in str(filelist[i]):
        filelist[i] = str(filelist[i]).replace(".","-")
    if "-0" in str(filelist[i]):
        filelist[i] = str(filelist[i]).replace("-0","")

#print(filelist)

#for num in range(len(filelist)-1,-1,-1):
for num in range(len(filelist)):
    os.rename(path+"\\"+str(filelist[num])+".png", path+"\\"+str(num+1)+".png")
