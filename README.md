# Johnny Bravo frame bot

Twitter bot posting Johnny Bravo frames in order.

~~Uses the Tweepy library for using the twitter API.~~ **Now running 100% API-free using browser automation with Selenium, because thanks Elon! :P**

The way I wrote the program depends on the organization of frames in the file system.
In the project directory, there are 2 directories holding frames, `frames` and `spent_frames`.
(I obviously don't commit the frame directories to github since they contain 10000's of images)

All frames that haven't yet been posted are held in `frames`, organized in subdirectories by season and episode.
One directory for each season; then in each season directory, one directory for each episode; then in each episode directory, one .png file for each frame.

Like this:
```
frames/
|- 1/ <-- season number
   |- 1/ <-- episode number
      |- 1.png
      |- 2.png
      |- 3.png
      |- etc... up to the last frame in s1e1
   |- 2/
      |- 1.png
      |- 2.png
      |- 3.png
      |- etc... up to the last frame in s1e2
   |- etc... up until the last episode in season 1
|- 2/
   |- one folder for each episode in season 2
|- 3/
   |- one folder for each episode in season 3
|- 4/
   |- one folder for each episode in season 4
```
   
Program always posts the lowest frame number, of the lowest episode number, of the lowest season number from inside the `frames` directory.
After posting it, it moves the frame to another directory with an identical structure but named `spent_frames`.
