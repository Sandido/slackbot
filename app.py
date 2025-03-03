import slack
import os 
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
from aoai_utils import call_aoai_translate
from models import QueryRequest

# tutorial stuff
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_BOT_TOKEN'])
# client.chat_postMessage(channel='#new-channel', text="Hello World 2!")
BOT_ID = client.api_call("auth.test")['user_id']

# don't need it, used earlier for testing purposes
@slack_event_adapter.on('message')
def message(payload):
    print(payload)
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

# check if bot is running
@app.route("/")
def index():
    return "Slack bot is up and running!", 200

@app.route('/translate-message' , methods=['POST'])
def translate_message():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    # The raw text from the slash command (after /translate ...)
    slash_command_text = data.get('text', '').strip()

    # If the user did not provide any text after /translate
    if not slash_command_text:
        # Try to grab the most recent non-bot message from the channel
        try:
            # Fetch recent messages
            response = client.conversations_history(channel=channel_id, limit=5)
            messages = response.get("messages", [])

            # Look for the first user message that is neither a bot message nor a subtype
            for msg in messages:
                # Some messages (like bot messages) can have 'bot_id' or a 'subtype'. These are special messages not from normal users. 
                if not msg.get("bot_id") and not msg.get("subtype"):
                    slash_command_text = msg.get("text", "")
                    break

        except Exception as e:
            # Handle API error, e.g. missing permissions or invalid channel
            print(f"Error fetching conversation history: {e}")
            slash_command_text = ""

    # If still empty, let the user know or set a default
    if not slash_command_text:
        slash_command_text = "No text found to translate."
        client.chat_postMessage(
            channel=channel_id, 
            text=f"Nothing found: {slash_command_text}"
        )
        return Response(), 200

    # Log what we’re translating
    client.chat_postMessage(
        channel=channel_id, 
        text=f"Translating: {slash_command_text}"
    )

    try:
        # Call Azure OpenAI to get the translation
        result = call_aoai_translate(
            QueryRequest(user_query=slash_command_text)
        )
        # Return the translation to Slack
        client.chat_postMessage(
            channel=channel_id, 
            text=f"Translation result:\n{result}"
        )
        return Response(), 200

    except Exception as e:
        print("Error during AOAI call:", str(e))
        client.chat_postMessage(channel=channel_id, text="Sorry, I hit an error: " + str(e))
        return Response(status=500)
        

if __name__ == "__main__":
    app.run(debug=True, port=5000)
