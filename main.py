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


        check_dm((this_season, this_episode, this_frame))

        return True


    else:
        print("Frames directory is empty.")
        dm_me("Frames directory is empty!!!")
        
        return False


def check_dm(current_frame):
    #current frame is a tuple of (season, episode, frame)

    old_dms=[]
    if os.path.exists("dm_log.txt"):
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
            sender_id=int(dm._json["message_create"]["sender_id"])
            
            season=int(results.group("s"))
            episode=int(results.group("e"))
            frame=int(results.group("f"))
            
            frame_to_find=(season, episode, frame)

            print(f"user wants to find s{season}e{episode} frame {frame}")

            message = generate_message(frame_to_find, current_frame)
            
            api.send_direct_message(sender_id,message)


def generate_message(frame_to_find, current_frame):
    
    try:
        title = titles[frame_to_find[0]][frame_to_find[1]]
    except KeyError:
        return "Hey, that episode doens't exist!"
        # No such episode


    if frame_to_find[0]>current_frame[0]: #season is greater than current season
        return f"Sorry, I'm still on season {current_frame[0]}!"
        #season hasnt been posted yet
    elif frame_to_find[0]==current_frame[0] and frame_to_find[1]>current_frame[1]:
        return f"Sorry, I'm only on season {current_frame[0]} episode {current_frame[1]}!"
        #we're on this season, but haven't posted this episode yet
    elif frame_to_find[0:2]==current_frame[0:2] and frame_to_find[2]>current_frame[2]:
        return f"Sorry, I'm only up to frame {current_frame[2]} of that episode!"
        #we're on this season AND episode but haven't posted this frame yet

    filename = f"id_logs/s{frame_to_find[0]}e{frame_to_find[1]}_log.txt"
    if not os.path.exists(filename):
        return f"Sorry, I couldn't find that frame (I'm only on s{current_frame[0]}e{current_frame[1]} frame {current_frame[2]})"

    logfile=open(filename, "r")
    lines=logfile.readlines()
    logfile.close()

    if frame_to_find[2]-1>len(lines):
        return f"Sorry, but I couldn't find that frame (I'm only on s{current_frame[0]}e{current_frame[1]} frame {current_frame[2]})"


    line=lines[frames_to_find[2]-1]

    tweet_id=line.split(":")[1]

    return f"https://twitter.com/jbravo_frames/status/{tweet_id}"


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


