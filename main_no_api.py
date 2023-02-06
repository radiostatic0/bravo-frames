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

# go to compose tweet
driver.get("https://twitter.com/compose/tweet")

# cursor automatically is placed in tweet, we don't have to click it
sleep(1)
ActionChains(driver).send_keys("this is a test :)").perform()

# click "upload image" button
for i in range(2):
    ActionChains(driver).send_keys(Keys.TAB).perform()
ActionChains(driver).send_keys(Keys.ENTER).perform()
sleep(2)

# upload the image
pyautogui.write("C:\\Users\\yayar\\Desktop\\bravo-frames\\helloworld.png")
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

text = tweet.find_elements(By.CSS_SELECTOR,'span')[4].get_attribute("innerHTML") #the 5th <span> is the one with the tweet text.
tweetid = tweet.find_elements(By.CSS_SELECTOR,'a')[4].get_attribute("href")[41:60]


print("Text:",text,"Id:",tweetid)

