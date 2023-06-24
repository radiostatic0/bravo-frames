# Note to reader - this is another utility program I wrote to rename frame image files to
# a more sensible sequence of numbers (because I deleted all the title theme frames causing
# the frame numbers to start at like 300 by default)

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
