from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options  #for headless modes
from selenium.webdriver.common.by import By             #for finding elements
from selenium.webdriver.common.keys import Keys         #for sending keystrokes (logging in)

from selenium.webdriver.common.action_chains import ActionChains

import pyautogui # file upload dialog

from time import sleep, time

import re

from datetime import date, timedelta

from secrets import pw

import os

from titles import titles


frames_dir="frames"
spentpath ="spent_frames"

service = Service(executable_path="C:\\Users\\yayar\\Documents\\geckodriver-v0.31.0-win64\\geckodriver.exe")

options = Options()

options.add_argument("--headless")

driver = webdriver.Firefox(service=service, options=options)

def init():

    #Log in
    driver.get("https://twitter.com/i/flow/login")
    sleep(5)

    attempts=0
    do_try=True
    username_input_list=driver.find_elements(By.CSS_SELECTOR,"input")

    while len(username_input_list)==0:
        attempts=attempts+1
        sleep(3)
        
        username_input_list=driver.find_elements(By.CSS_SELECTOR,"input")

        if attempts>=5:
            raise Exception


    username_input=username_input_list[0]

    username_input.click()
    username_input.send_keys("jbravo_frames")
    username_input.send_keys(Keys.ENTER)
    sleep(2)
    pw_box=driver.find_element(By.CSS_SELECTOR,"input[type='password']")
    pw_box.send_keys(pw)
    pw_box.send_keys(Keys.ENTER)
    sleep(2)


def pathto(season, episode=None, frame=None, spent=False):
    if episode==None:
        retval = "frames\\"+str(season)
    elif frame==None:
        retval = "frames\\"+str(season)+"\\"+str(episode)
    else:
        retval = "frames\\"+str(season)+"\\"+str(episode)+"\\"+str(frame)+".png"
    if spent:
        retval = retval.replace("frames","spent_frames")
    return retval


def post(season, episode, frame, maxframe):
    global lastpost

    path="C:\\Users\\yayar\\Desktop\\twitterbot\\"+pathto(season,episode,frame)


    text=("Season "+ str(season) + " Episode " + str(episode) + ": " +\
              titles[season][episode], "\nFrame " + str(frame) + " out of " + str(maxframe))

    attempts_to_post=0
    
    do_try=True
    while do_try:
        # go to compose tweet
        driver.get("https://twitter.com/jbravo_frames")
        sleep(3)

        # attempt to locate the tweet button
        tweet_button_list=driver.find_elements(By.CSS_SELECTOR,"a[href='/compose/tweet']")
        
        attempt_counter=0
        
        while len(tweet_button_list)==0: # If we couldn't find it:
            # sometimes we just need to go to the login page to refresh (we dont need to actually log in)
            driver.get("https://twitter.com/i/flow/login")
            sleep(3)
            driver.get("https://twitter.com/jbravo_frames")
            attempt_counter=attempt_counter+1

            tweet_button_list=driver.find_elements(By.CSS_SELECTOR,"a[href='/compose/tweet']")

            # if we've tried 5 times now and failed, just give up, something must be wrong
            if attempt_counter>=5:
                raise Exception

        tweet_button=tweet_button_list[0]
        
            
        tweet_button.click()    
        #driver.get("https://twitter.com/compose/tweet")

        # cursor automatically is placed in tweet, we don't have to click it
        sleep(5)
        ActionChains(driver).send_keys(text[0]).perform()
        ActionChains(driver).send_keys(Keys.ENTER).perform()
        ActionChains(driver).send_keys(text[1]).perform()
        sleep(4)

        # click "upload image" button
        for i in range(2):
            ActionChains(driver).send_keys(Keys.TAB).perform()
            sleep(0.2)
        ActionChains(driver).send_keys(Keys.ENTER).perform()
        
        sleep(3)
        
        # The file upload dialog should now be open, which we use pyautogui to interact with.
        # upload the image (type the full filename into the file upload dialog and then press ENTER)
        pyautogui.typewrite(path, interval=0.05)
        sleep(2)
        pyautogui.typewrite("\n")

        # post tweet.
        sleep(2)
        post_button=driver.find_element(By.CSS_SELECTOR,'div[data-testid="tweetButton"]')
        post_button.click()
        
        lastpost=time()
        
        sleep(6)


        ######################### VERIFY POST #######################
        tweet_index=0
        if len(driver.find_elements(By.CSS_SELECTOR, "div[data-testid='socialContext']"))==1:
            #there is a pinned tweet. that means the tweet we want to check is now going to be index 1 instead of 0
            tweet_index=1

        # We're still on @jbravo_frames' timeline. Get the last tweet posted to make sure it's the frame that we just tried to post.
        tweet_container=driver.find_elements(By.CSS_SELECTOR,"div[data-testid='cellInnerDiv']")[tweet_index]

        
        found_text = tweet_container.find_elements(By.CSS_SELECTOR,'span')[4].get_attribute("innerHTML")
        #the 5th <span> inside a tweet container is the element that contains the tweet text.

        results = re.search("^Season (?P<s>\d+) Episode (?P<e>\d+)", found_text)

        if results is None:
            print("Tweet doesn't look like a frame tweet:", found_text)
            continue #try again from the top
        
        found_season=int(results.group("s"))
        found_episode=int(results.group("e"))

        # extract frame num, max frame from tweet text
        results = re.search("Frame (?P<f>\d*) out of (?P<max>\d*)", found_text)
        found_frame = int(results.group("f"))
        #maxframe = int(results.group("max"))

        if found_season==season and found_episode==episode and found_frame==frame:
            
            imgs = tweet_container.find_elements(By.CSS_SELECTOR,'img')

            if len(imgs)>=2:
            # A valid frame post should have 2 images: the account's profile pic, and the actual frame
                print(f"Validated that we just posted s{season}e{episode} frame {frame}!")
                do_try=False
                #break loop

            else:
                print(f"Found our tweet for s{season}e{episode} frame {frame} but it has no image! "\
                      "trying again")
    
        else:
            print(f"Tried to post s{season}e{episode} frame {frame}, "\
                  f"instead found s{found_season}e{found_episode} frame {found_frame}, "\
                  "trying again")

        attempts_to_post = attempts_to_post+1

        if attempts_to_post>=15:
            # max attempts to post the same tweet is 15
            raise Exception
    

    tweetid = tweet_container.find_elements(By.CSS_SELECTOR,'a')[4].get_attribute("href")[41:60]
    # ^ this extracts the tweet ID from the tweet (taken from the image link) for the logfile.
    
    return tweetid


def log_tweet(tweetid, season, episode, frame):
    logfile=open(f"id_logs/s{season}e{episode}_log.txt", "a")
    logfile.write(f"{frame}:{tweetid}\n")
    logfile.close()


def run():
    
    #remove empty directories
    for dir, subdirs, files in os.walk("frames", topdown=False):
        if len(os.listdir(dir)) == 0 and dir!="frames":
            os.rmdir(dir)

    if len(os.listdir(frames_dir))!=0:

        #get season list
        seasons=os.listdir(frames_dir)
        for i in range(len(seasons)):
            seasons[i]=int(seasons[i])
        seasons.sort()
        #print("Seasons:",seasons)

        this_season=seasons[0]

        #get episode list
        episodes=os.listdir(pathto(this_season))
        for i in range(len(episodes)):
            episodes[i]=int(episodes[i])
        episodes.sort()

        this_episode=episodes[0]

        #get frames list
        frames=os.listdir(pathto(this_season,this_episode))
        for i in range(len(frames)):
            frames[i]=int(frames[i][:-4])
        frames.sort()

        this_frame=frames[0]

        tweetid=post(this_season, this_episode, this_frame, frames[-1])
        
        #write tweet id to logfile
        log_tweet(tweetid,this_season,this_episode,this_frame)

        #move this frame to the corresponding spent frame directory
        if not(os.path.exists(spentpath)):
            os.mkdir(spentpath)
            
        if not(os.path.exists(pathto(this_season, spent=True))):
            os.mkdir(pathto(this_season, spent=True))

        if not(os.path.exists(pathto(this_season, this_episode, spent=True))):
            os.mkdir(pathto(this_season, this_episode, spent=True))

        os.rename(pathto(this_season, this_episode, this_frame), pathto(this_season, this_episode, this_frame, spent=True))

        return True
    
    else:
        print("Frames directory is empty.")
        
        return False


########## main program

init()
lastpost=-1
keep_running=True
while keep_running:
    print("Running...")
    timer=time()
    keep_running=run()
    time_remaining=90-(lastpost-timer)
    print("Sleeping for",time_remaining,"sec...")
    sleep(time_remaining)

