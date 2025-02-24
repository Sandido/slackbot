import slack
import os 
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
from aoai_utils import call_aoai_general_response
from models import QueryRequest

# tutorial stuff
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_BOT_TOKEN'])
# client.chat_postMessage(channel='#new-channel', text="Hello World 2!")
BOT_ID = client.api_call("auth.test")['user_id']

@slack_event_adapter.on('message')
def message(payload):
    print(payload)
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    if BOT_ID != user_id :
        client.chat_postMessage(channel=channel_id, text="Hello <@{}>! You said {} :tada:".format(user_id, text))

@app.route('/translate-message' , methods=['POST'])
def translate_message():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    text = data.get('text')
    try:
        client.chat_postMessage(channel=channel_id, text=f"I got the command text: {text}")
        # Call Azure OpenAI here
        result = call_aoai_general_response(QueryRequest(user_query=text))
        client.chat_postMessage(channel=channel_id, text=f"Azure OpenAI finished with + {result}")
        return Response(), 200
    
    except Exception as e:
        # Print the error message for debugging
        print("Error during AOAI call:", str(e))
        
        # Optionally, post an error message back to Slack
        client.chat_postMessage(channel=channel_id, text="Sorry, I hit an error of: " + str(e))
        
        # Return an HTTP 500 to let Slack know something went wrong
        return Response(status=500)
    

if __name__ == "__main__":
    app.run(debug=True, port=5000)