import sys
import os
import tweepy
from time import sleep

import re

from secrets import consumer_key, consumer_secret, access_token, access_token_secret, bearer

#authenticate to twitter
auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_token_secret)
api = tweepy.API(auth)

def print_dm(dm):
    print(dm._json["id"], ': "', dm._json["message_create"]["message_data"]["text"], '"', sep="")

#def check_for_new_dm():
if True:

    old_dms=[]
    if os.path.exists("dm_logs.txt"):
        dm_file=open("dm_log.txt") #a txt file containing the last 20 dms ids recieved (is cleared and rewritten consistently)
        old_dms = dm_file.readlines()
        dm_file.close()

    curr_dms_objects = api.get_direct_messages()

    #curr_dms_ids = []

    new_dms = []

    dm_file=open("dm_log.txt","w")
    
    for dm in curr_dms_objects:
        dm_file.write(dm._json["id"]+"\n")

    dm_file.close()

    for curr_dm in curr_dms_objects:
        if curr_dm._json["id"]+"\n" not in old_dms:
            new_dms.append(curr_dm)


    for dm in new_dms:
        dm_text=dm._json["message_create"]["message_data"]["text"].lower()
        
        print("New DM:",dm._json["id"],dm_text)

        pattern="find season (?P<s>\d) episode (?P<e>\d*) frame (?P<f>\d*)"

        results = re.search(pattern, dm_text)

        if results is not None:
            season=int(results.group("s"))
            episode=int(results.group("e"))
            frame=int(results.group("f"))

            print(f"user wants to find s{season}e{episode} frame {frame}")
            #TODO: Call the function for responding.
        
        sender_id=int(dm._json["message_create"]["sender_id"])
        
