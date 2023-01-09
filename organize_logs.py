
# Nov 19, 20, 21, 22, 23, 24, 25, 26

#dates=["11-26","11-27","11-28","11-29","11-30","12-01"]
#dates=["12-01","12-02","12-03","12-04","12-05","12-06"]
dates=["12-06", "12-07"]

filenames=[]


for i in dates:
    filenames.append(f"scrape/2022-{i}.txt")

#infile=open("tweetlogs/Nov_19_Tweets.txt","r")

outfile=open("s1e4_log.txt","w")


for filename in filenames:
    infile=open(filename, "r")
    filelines=infile.readlines()
    print(filelines[:3])
    infile.close()

    filelines.reverse()
    
    for line in filelines:
        if line[:2]=="e4":
            outfile.write(line[3:])



outfile.close()


