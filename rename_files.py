import sys
import os

path="C:\\Users\\yayar\\Desktop\\twitterbot\\frames\\2\\5"


filelist=os.listdir(path)

for i in range(len(filelist)):
    filelist[i]=int(filelist[i][:-4])
filelist.sort()

#print(filelist)

#for num in range(len(filelist)-1,-1,-1):
for num in range(len(filelist)):
    os.rename(path+"\\"+str(filelist[num])+".png", path+"\\"+str(num+1)+".png")
