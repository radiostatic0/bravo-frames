"""
Info:
This file is an auxillary standalone program that is not used by the Twitter bot,
but I wrote it to scrape @jbravo_frames' Tweets in order to retroactively create tweet ID log files
for frames that the bot had posted before I changed it to log tweet IDs as it posts them.
It uses the Selenium library so it is browser-based and very slow

I did it this way because the Twitter API "Get User Timeline" method only accesses
the most recent 3,200 of a user's tweets and jbravo_frames posts about 1,440 tweets every day
so I could no longer use the API to access tweets older than a few days.

So if you need to scrape Tweets from an account with less than 3,200 tweets,
you should just use the API and not this slow as fuck program !!!
"""

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options  #for headless modes
from selenium.webdriver.common.by import By             #for finding elements
from selenium.webdriver.common.keys import Keys         #for sending keystrokes (logging in)

from selenium.webdriver.common.action_chains import ActionChains

from time import sleep

import re

from datetime import date, timedelta

from secrets import pw


service = Service(executable_path="C:\\Users\\yayar\\Documents\\geckodriver-v0.31.0-win64\\geckodriver.exe")

options = Options()
options.add_argument("--headless")

driver = webdriver.Firefox(service=service, options=options)


first_date = date(2022, 12, 6) #first date to scrape tweets from (inclusive)
last_date = date(2022, 12, 6) #last date to scrape tweets from (inclusive)


#Log in
driver.get("https://twitter.com/i/flow/login")
sleep(3)

username_input=driver.find_elements(By.CSS_SELECTOR,"input")[0]
username_input.click()
username_input.send_keys("jbravo_frames")
username_input.send_keys(Keys.ENTER)
sleep(3)
pw_box=driver.find_element(By.CSS_SELECTOR,"input[type='password']")
pw_box.send_keys(pw)
pw_box.send_keys(Keys.ENTER)
sleep(3)


driver.get(f"https://twitter.com/search?q=from%3Ajbravo_frames%20since%3A{str(first_date)}%20until%3A{str(first_date+timedelta(days=1))}&src=typed_query&f=live")

sleep(2)

#handle annoying Turn On Notifications popup if it appears
popups=driver.find_elements(By.CSS_SELECTOR,"div[data-testid='sheetDialog'")
if len(popups)>0:
    buttons = popups[0].find_elements(By.CSS_SELECTOR,"div[role='button']")
    buttons[2].click() #hits the "Not Now" button


current_date = first_date


while current_date<=last_date:
    print("Getting tweets for",current_date,"...")


    driver.get(f"https://twitter.com/search?q=from%3Ajbravo_frames%20since%3A{str(current_date)}%20until%3A{str(current_date+timedelta(days=1))}&src=typed_query&f=live")

    sleep(2)

    #handle annoying Turn On Notifications popup if it appears.
    popups=driver.find_elements(By.CSS_SELECTOR,"div[data-testid='sheetDialog'")
    if len(popups)>0:
        buttons = popups[0].find_elements(By.CSS_SELECTOR,"div[role='button']")
        buttons[2].click() #hits the "Not Now" button
    
    file=open(f"scrape/{str(current_date)}.txt","w")

    prev_batch=[]
    this_batch=[]

    waitAttempts=0

    while True:

        #Collects all tweet containers
        tweetContainers=driver.find_elements(By.CSS_SELECTOR,"div[data-testid='cellInnerDiv']")

        print("New Batch")

        prev_batch=this_batch
        this_batch=[]
        
        for container in tweetContainers:

            # Skip this Div if it isn't a tweet container (all tweet containers should contain at least 5 <span> child elements)
            if len(container.find_elements(By.CSS_SELECTOR,'span'))<5:
                print("Skipping this container (fewer than 5 elements)")
                continue

            text = container.find_elements(By.CSS_SELECTOR,'span')[4].get_attribute("innerHTML") #the 5th <span> is the one with the tweet text.

            # extract season, episode num from tweet text
            results = re.search("^Season (?P<s>\d+) Episode (?P<e>\d+)", text)

            if results is None: #this tweet doesn't contain this string, so skip over it.
                print("Tweet doesn't look like a frame tweet:",text)
                continue
            
            season=int(results.group("s"))
            episode=int(results.group("e"))

            # extract frame num, max frame from tweet text
            results = re.search("Frame (?P<f>\d*) out of (?P<max>\d*)", text)
            frame = int(results.group("f"))
            maxframe = int(results.group("max"))

            # get the tweet ID (spliced from the picture's link)
            tweetid=container.find_elements(By.CSS_SELECTOR,'a')[4].get_attribute("href")[41:60] 

            #print(f"e{episode}f{frame}:{tweetid}")
            this_batch.append(f"e{episode}f{frame}:{tweetid}")


        new_tweets=0
        
        # write every tweet in the batch that wasn't in the previous batch, count how many new tweets we got
        for string in this_batch:
            if string not in prev_batch:
                file.write(string+"\n")
                print(string)
                new_tweets+=1

        #If no new tweets this batch, Increment the wait attempt counter
        if new_tweets==0:
            waitAttempts=waitAttempts+1
        else:
            waitAttempts=0

        # The program only breaks out of the loop after 4 consecutive attempts at retrieving tweets has only yielded the same set
        # (this lowers the chance of the program terminating prematurely when tweets are just slow to load)
        if waitAttempts==3:
            break

        #scroll down by 6 tweets. 6 seems to be the magic number to avoid skipping any tweets (but there is still some overlap between batches).
        for i in range(5):
            #driver.find_element(By.CSS_SELECTOR,"body").send_keys(Keys.PAGE_DOWN)
            # ^ used to work but now makes the tweet timeline jump back to the top before scrolling down
            ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()

        sleep(1.5)

    #end while True

    file.close()

    #Progress to the next day
    current_date=current_date+timedelta(days=1)

    sleep(2)
    
print("Program finished")
