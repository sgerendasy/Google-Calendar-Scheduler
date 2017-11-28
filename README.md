## Project 10 Google Calendar Scheduler
Displays the busy times of the user's Google calendar for a selected date/time range.
Author: Sam Gerendasy


## To run the application:
git clone  
mv client_secret.json proj10-scheduler/  
cd proj10-scheduler  
make  
make configure  
source env/bin/activate  
make run  
connect via localhost:5000  
or visit https://meeting-checker.herokuapp.com  

## Other information:
Meeting IDs are generated randomly. A meeting ID is needed to login to a meeting. Anyone with a Meeting ID can add their Google calendar events, so keeping a meeting ID between the desired users is a must.  
A mailto link is provided for convenience, but one could simply email someone a link to the webpage including the meetingID.  
File structure was modified to satisfy Heroku's needs.