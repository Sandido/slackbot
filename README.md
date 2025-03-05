# Slackbot Translator App
For making a slack bot that translates languages, with a focus on martial arts. <br>
This app connects my Azure Open AI Resource to my Slack Bot that I can add to different Slack Workspaces. <br>
This code lives on an Azure Web App that listens for the API calls from Slack then executes the business logic.<br>
Dev Time = 3 hours to initial release. First time using Slack API and Azure Web Apps.<br>
Iterative Dev Time = 0 so far.<br>
<br>
## Local Testing:
If you want to run this code locally, you will need some extra setup.<br> 
# Run venv
testenv\Scripts\activate<br>

# Setup
pip install -r requirements.txt<br>

ngrok needs to be running via <br>
'ngrok http ####' <br>
'####' being whatever port you have the app running on in the app code. The value in the app's main function needs to be updated to match this.<br>
Grab the url redirect value.<br>

# Run
Run the app.py file.<br>
It must be running to add the url redirect from ngrok to the Slack API portal.<br>
Go through the setup in Event Subscriptions in the Slack API for a normal Slack Bot, add a Slash command called 'translate'.<br>
Add this slackbot to a channel in your workspace. <br>
Then go to the slack workspace and use the /translate cmd. <br>
