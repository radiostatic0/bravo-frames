import sys
import os
import tweepy
from time import sleep

from secrets import consumer_key, consumer_secret, access_token, access_token_secret, bearer, my_id
# ^ my twitter bot's access tokens (Get your own!!)

from titles import titles

frames_dir="frames"
spentpath ="spent_frames"

#authenticate to twitter - api1.1
auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_token_secret)
api = tweepy.API(auth)

#authenticate to twitter - api2.0 (needed for fetching "users who liked this tweet" list)
client=tweepy.Client(consumer_key=consumer_key,
                     consumer_secret=consumer_secret,
                     access_token=access_token,
                     access_token_secret=access_token_secret)


def log_tweet(tweet, season, episode, frame):
    logfile=open(f"id_logs/s{season}e{episode}_log.txt", "a")
    logfile.write(f"{frame}:{tweet.id}\n")
    logfile.close()

def dm_me(message):
    api.send_direct_message(my_id,message)

def send_new_episode_dm(season,episode,tweet_id):
    pinned_id=1595639562205904896
    liked_users=client.get_liking_users(pinned_id,user_auth=True).data

    message="Whoa mama, just posted the first frame of s"+str(season)+"e"+str(episode)+\
             "\n(unlike my pinned tweet to stop receiving these dms)"
    link="https://twitter.com/jbravo_frames/status/"+str(tweet_id)

    for user in liked_users:
        api.send_direct_message(user.id,message)
        api.send_direct_message(user.id,link)

    dm_me("Sent a first frame dm to "+str(len(liked_users))+" users")
    print("Sent a first frame dm to",len(liked_users),"users")

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
        upload_media = api.media_upload(pathto(this_season,this_episode,this_frame))
        tweet=api.update_status("Season "+str(this_season)+" Episode "+str(this_episode)+": "+
                          titles[this_season][this_episode] + "\nFrame "+str(this_frame)+" out of "+str(frames[-1]),
                          media_ids=[upload_media.media_id])
        print("Posted season", this_season, "episode", this_episode, "frame", this_frame)

        #write tweet id to logfile
        log_tweet(tweet,this_season,this_episode,this_frame)

        if this_frame==1:
            send_new_episode_dm(this_season,this_episode,tweet.id)

        #move this frame to the corresponding spent frame directory
        if not(os.path.exists(spentpath)):
            os.mkdir(spentpath)
            
        if not(os.path.exists(pathto(this_season, spent=True))):
            os.mkdir(pathto(this_season, spent=True))

        if not(os.path.exists(pathto(this_season, this_episode, spent=True))):
            os.mkdir(pathto(this_season, this_episode, spent=True))

        os.rename(pathto(this_season, this_episode, this_frame), pathto(this_season, this_episode, this_frame, spent=True))
        #print("renamed",pathto(this_season, this_episode, this_frame),"to",pathto(this_season, this_episode, this_frame, spent=True))

        return True


    else:
        print("Frames directory is empty.")
        dm_me("Frames directory is empty!!!")
        
        return False


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



keep_running=True
while keep_running:
    print("Running...")
    
    try:
        keep_running=run()
        
    except tweepy.errors.TooManyRequests as e:
        print("Too Many Requests, waiting 15 min")
        dm_me("Too many requests: " + str(e) + ", waiting 15 min")
        sleep(15*60)
        
    except Exception as ex:
        #dm_me(e.message)
        dm_me("Bot crashed: " + str(ex))
        raise(ex)
        keep_running=False

    print("Sleeping for 60 sec...")
    sleep(60)


