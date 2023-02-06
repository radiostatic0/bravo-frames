from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options  #for headless modes
from selenium.webdriver.common.by import By             #for finding elements
from selenium.webdriver.common.keys import Keys         #for sending keystrokes (logging in)

from selenium.webdriver.common.action_chains import ActionChains

import pyautogui

from time import sleep

import re

from datetime import date, timedelta

from secrets import pw


service = Service(executable_path="C:\\Users\\yayar\\Documents\\geckodriver-v0.31.0-win64\\geckodriver.exe")

options = Options()
#options.add_argument("--headless")

driver = webdriver.Firefox(service=service, options=options)

def init():

    #Log in
    driver.get("https://twitter.com/i/flow/login")
    sleep(3)

    username_input=driver.find_elements(By.CSS_SELECTOR,"input")[0]
    username_input.click()
    username_input.send_keys("jbravo_frames")
    username_input.send_keys(Keys.ENTER)
    sleep(1)
    pw_box=driver.find_element(By.CSS_SELECTOR,"input[type='password']")
    pw_box.send_keys(pw)
    pw_box.send_keys(Keys.ENTER)
    sleep(1)

    '''
    # Load home timeline, to try to invoke the annoying "turn on notifications" pop up before trying to post a tweet
    driver.get("https://twitter.com/home")

    sleep(2)

    #handle annoying "turn on notifications" popup if it appears
    popups=driver.find_elements(By.CSS_SELECTOR,"div[data-testid='sheetDialog'")
    if len(popups)>0:
        buttons = popups[0].find_elements(By.CSS_SELECTOR,"div[role='button']")
        buttons[2].click() #hits the "Not Now" button
    '''


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


def post(path, text):

    # go to compose tweet
    driver.get("https://twitter.com/compose/tweet")

    # cursor automatically is placed in tweet, we don't have to click it
    sleep(1)
    ActionChains(driver).send_keys(text).perform()

    # click "upload image" button
    for i in range(2):
        ActionChains(driver).send_keys(Keys.TAB).perform()
    ActionChains(driver).send_keys(Keys.ENTER).perform()
    sleep(2)

    # upload the image
    pyautogui.write(path)
    sleep(1)
    pyautogui.press("enter")
    sleep(1)

    # post tweet.
    for i in range(4):
        ActionChains(driver).send_keys(Keys.TAB).perform()
    sleep(1)
    ActionChains(driver).send_keys(Keys.ENTER).perform()

    sleep(2)

    # this line returns the div that contains the tweet of the first tweet on the timeline (which should be the tweet we just posted)
    tweet=driver.find_elements(By.CSS_SELECTOR,"div[data-testid='cellInnerDiv']")[0]

    tweetid = tweet.find_elements(By.CSS_SELECTOR,'a')[4].get_attribute("href")[41:60]

    return tweetid

    #print("Text:",text,"Id:",tweetid)



def log_tweet(tweetid, season, episode, frame):
    logfile=open(f"id_logs/s{season}e{episode}_log.txt", "a")
    logfile.write(f"{frame}:{tweetid}\n")
    logfile.close()
    
# Taken from main.py.

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
        #print("Episode directories in season ",this_season,": ", episodes, sep="")

        this_episode=episodes[0]

        #get frames list
        frames=os.listdir(pathto(this_season,this_episode))
        for i in range(len(frames)):
            frames[i]=int(frames[i][:-4])
        frames.sort()

        #print("Frames for season ", this_season, " episode ", this_episode, ": ", frames, sep="")

        this_frame=frames[0]
        #print("Path to this frame:",pathto(this_season,this_episode,this_frame))

        #post to twitter

        path=pathto(this_season,this_episode,this_frame)
        
        '''
        upload_media = api.media_upload(pathto(this_season,this_episode,this_frame))
        tweet=api.update_status("Season "+str(this_season)+" Episode "+str(this_episode)+": "+
                          titles[this_season][this_episode] + "\nFrame "+str(this_frame)+" out of "+str(frames[-1]),
                          media_ids=[upload_media.media_id])
        '''
        
        text=f"Season {this_season} Episode {this_episode}: {titles[this_season][this_episode]}"\
              "\nFrame {this_frame} out of {frames[-1]}"

        tweetid=post(path, text)
        
        print("Posted season", this_season, "episode", this_episode, "frame", this_frame)
        

        #write tweet id to logfile
        log_tweet(tweetid,this_season,this_episode,this_frame)

        #if this_frame==1:
        #    send_new_episode_dm(this_season,this_episode,tweet.id)

        #move this frame to the corresponding spent frame directory
        if not(os.path.exists(spentpath)):
            os.mkdir(spentpath)
            
        if not(os.path.exists(pathto(this_season, spent=True))):
            os.mkdir(pathto(this_season, spent=True))

        if not(os.path.exists(pathto(this_season, this_episode, spent=True))):
            os.mkdir(pathto(this_season, this_episode, spent=True))

        os.rename(pathto(this_season, this_episode, this_frame), pathto(this_season, this_episode, this_frame, spent=True))
        #print("renamed",pathto(this_season, this_episode, this_frame),"to",pathto(this_season, this_episode, this_frame, spent=True))


        #check_dm((this_season, this_episode, this_frame))

        return True
    
    else:
        print("Frames directory is empty.")
        
        return False




########## main program

init()

keep_running=True
while keep_running:
    print("Running...")
    keep_running=run()
    print("Sleeping for 90 sec...")
    sleep(90)




