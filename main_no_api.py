from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options  #for headless modes
from selenium.webdriver.common.by import By             #for finding elements
from selenium.webdriver.common.keys import Keys         #for sending keystrokes (logging in)

from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.common.action_chains import ActionChains

import pyautogui # file upload dialog

from time import sleep, time

import re

from datetime import date, timedelta

from secrets import pw

import os

from titles import titles

IS_PINNED_TWEET = True
# The detection method of whether there is a pinned tweet, which determines
# which tweet to check when making sure a frame posted successfully,
# all of a sudden hasn't been working reliably.
# So for now I am hard-coding whether or not there is a pinned tweet!
# (yes, this means that if I unpin a tweet without replacing it, it will break!)


frames_dir="frames"
spentpath ="spent_frames"

service = Service(executable_path="C:\\Users\\yayar\\Documents\\geckodriver-v0.31.0-win64\\geckodriver.exe")

options = Options()

#options.add_argument("--headless")

driver = webdriver.Firefox(service=service, options=options)

def login():
    driver.get("https://twitter.com")
    exceptions=0

    while True:
        #Log in
        #driver.get("https://twitter.com/i/flow/login")
        sleep(3)
        while True:
            try:
                driver.find_element(By.CSS_SELECTOR,"a[data-testid='login']").click()
                break
            except NoSuchElementException:
                print("caught NoSuchElementException, waiting...")
                sleep(3)
                exceptions=exceptions+1
                if exceptions>3:
                    return #we must be logged in

        #input() #user has to log in then press ENTER on terminal to resume program

        attempts=0
        while True:
            try:
                username_input=driver.find_elements(By.CSS_SELECTOR,"input")[0]
                break
            except IndexError:
                sleep(3)
                attempts=attempts+1
                if attempts>=5:
                    raise Exception
        
        username_input.click()
        username_input.send_keys("jbravo_frames")
        sleep(3)
        username_input.send_keys(Keys.ENTER)
        sleep(3)

        find_password_attempts=0
        while True:
            try:
                pw_box=driver.find_element(By.CSS_SELECTOR,"input[type='password']")
                break
            except NoSuchElementException:
                find_password_attempts = find_password_attempts + 1
                if find_password_attempts >= 5:
                    raise Exception
                sleep(3)
                
        pw_box.send_keys(pw)
        pw_box.send_keys(Keys.ENTER)
        sleep(2)

        # check if error dialogue was thrown

        error_dialogs = driver.find_elements(By.CSS_SELECTOR,"div[data-testid='confirmationSheetDialog']")
        if len(error_dialogs)>0:
            print("Login failed, trying again..")
            confirm_button = error_dialogs[0].find_element(By.CSS_SELECTOR,"div[data-testid='confirmationSheetConfirm']")
            confirm_button.click()
        else:
            print("Login succeeded!")
            break
    # end while true

    
    #input()
    '''
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
    sleep(3)
    username_input.send_keys(Keys.ENTER)
    sleep(3)
    pw_box=driver.find_element(By.CSS_SELECTOR,"input[type='password']")
    pw_box.send_keys(pw)
    pw_box.send_keys(Keys.ENTER)
    sleep(2)
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
            print("Trying to find tweet button...")
            # sometimes we just need to go to the login page to refresh (we dont need to actually log in)
            driver.get("https://twitter.com/i/flow/login")
            sleep(3)
            driver.get("https://twitter.com/jbravo_frames")
            attempt_counter=attempt_counter+1

            tweet_button_list=driver.find_elements(By.CSS_SELECTOR,"a[href='/compose/tweet']")
            # if we've tried 5 times now and failed, just give up, something must be wrong
            if attempt_counter>=5:
                print("Relogging in...")
                login()
                sleep(4)
                tweet_button_list=driver.find_elements(By.CSS_SELECTOR,"a[href='/compose/tweet']")

        

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

        '''
        for i in range(2):
            ActionChains(driver).send_keys(Keys.TAB).perform()
            sleep(0.2)
        ActionChains(driver).send_keys(Keys.ENTER).perform()
        '''
        try_upload_image=True
        while try_upload_image:
            # the media upload button is a div with the aria-label attribute set to "Add photos or video"
            driver.find_element(By.CSS_SELECTOR,"div[aria-label='Add photos or video']").click()
            
            sleep(3)
            
            # The file upload dialog should now be open, which we use pyautogui to interact with.
            # upload the image (type the full filename into the file upload dialog and then press ENTER)
            pyautogui.typewrite(path, interval=0.05)
            sleep(2)
            pyautogui.typewrite("\n")
            sleep(4)

            # check if file got uploaded

            # If there is an image uploaded, there will be a div element with the aria-label attribute set to
            # "Remove media" (representing the X button to remove image/video), if there is no such element,
            # that means the image didn't get uploaded, so we'll try again.
            remove_media=len(driver.find_elements(By.CSS_SELECTOR, "div[aria-label='Remove media']"))
            
            if remove_media==0:
                print("upload image failed, trying again")
            elif remove_media==1:
                try_upload_image=False
            else:
                # anything else is erroneous. stop execution
                raise Exception
                
                

        # post tweet.
        post_button=driver.find_element(By.CSS_SELECTOR,'div[data-testid="tweetButton"]')
        post_button.click()
        
        lastpost=time()
        
        sleep(6)

        driver.get("https://twitter.com/jbravo_frames")

        sleep(5)


        ######################### VERIFY POST #######################
        print("Verifying post...")
        tweet_index=0
        '''
        if len(driver.find_elements(By.CSS_SELECTOR, "div[data-testid='socialContext']"))==1:
            #there is a pinned tweet. that means the tweet we want to check is now going to be index 1 instead of 0
            tweet_index=1
            print("There is a pinned tweet")
        else:
            print("There is NOT a pinned tweet")
        '''
        if IS_PINNED_TWEET:
            tweet_index = 1

        # We're still on @jbravo_frames' timeline. Get the last tweet posted to make sure it's the frame that we just tried to post.

        while True:
            try:
                tweet_text_div = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='tweetText']")[tweet_index]
                found_text = tweet_text_div.find_elements(By.CSS_SELECTOR,"span")[0].get_attribute("innerHTML")
                tweet_container = tweet_text_div.find_elements(By.XPATH, "../../..")[0] #container we want is great-grandparent of the tweet text div
                break
            except IndexError:
                sleep(2)
                driver.get("https://twitter.com/jbravo_frames")
                sleep(2)

        '''
        while True:
            try:
                tweet_container=driver.find_elements(By.CSS_SELECTOR,"div[data-testid='cellInnerDiv']")[tweet_index]
                break
            except:
                sleep(2)
                driver.get("https://twitter.com/jbravo_frames")
                sleep(2)


        found_text = tweet_container.find_elements(By.CSS_SELECTOR,'span')[4].get_attribute("innerHTML")
        #the 5th <span> inside a tweet container is the element that contains the tweet text.
        '''
        #print("Found text:",found_text)
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

login()
lastpost=-1
keep_running=True
while keep_running:
    print("Running...")
    timer=time()
    keep_running=run()
    time_remaining=120-(lastpost-timer)
    if time_remaining<=0:
        time_remaining=30
    print("Sleeping for",time_remaining,"sec...")
    sleep(time_remaining)

