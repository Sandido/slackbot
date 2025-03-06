import slack
import os 
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
from aoai_utils import call_aoai_translate, call_aoai_multilingual_translate
from models import QueryRequest

import hmac
import hashlib
import time

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_BOT_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']


def verify_slack_signature(signing_secret):
    print("start verification slack siganture")
    slack_signature = request.headers.get('X-Slack-Signature', '')
    slack_timestamp = request.headers.get('X-Slack-Request-Timestamp', '')

    # 1) Guard against replay attacks by verifying timestamp is recent (e.g. within 5 minutes)
    if abs(time.time() - float(slack_timestamp)) > 60 * 5:
        return False

    # 2) Create the signature base string as prescribed by Slack
    sig_basestring = f"v0:{slack_timestamp}:{request.get_data(as_text=True)}"

    # 3) Compute the expected signature
    my_signature = 'v0=' + hmac.new(
        signing_secret.encode('utf-8'),
        sig_basestring.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    print("end verification slack siganture")

    # 4) Compare signatures safely
    return hmac.compare_digest(my_signature, slack_signature)


# check if bot is running
@app.route("/")
def index():
    return "Slack bot is up and running!", 200

def handle_two_language_request(channel_id: str, source_lang: str, target_lang: str, text_to_translate: str) -> Response:
    """
    Called when the user passes exactly 3 tokens after /translate:
      - token[0] = source_lang
      - token[1] = target_lang
      - token[2] = text_to_translate
    """
    # Let the user know we received the request
    client.chat_postMessage(
        channel=channel_id,
        text=f"Translating from {source_lang} to {target_lang}:\n{text_to_translate}"
    )

    try:
        # Call the multilingual AOAI translation
        result = call_aoai_multilingual_translate(
            source_lang=source_lang,
            target_lang=target_lang,
            text=text_to_translate
        )
        # Return the translation to Slack
        client.chat_postMessage(
            channel=channel_id,
            text=f"**Translation:**\n{result}"
        )
        return Response(), 200

    except Exception as e:
        print("Error during AOAI call:", str(e))
        client.chat_postMessage(
            channel=channel_id,
            text=f"Sorry, I hit an error: {str(e)}"
        )
        return Response(status=500)


def handle_default_request(channel_id: str, slash_command_text: str) -> Response:
    """
    Called when the user does not provide exactly 3 tokens. (0, 1, or 2 tokens)
    - If `slash_command_text` is empty, it attempts to pull the last user message from the channel.
    - Otherwise, it calls the original call_aoai_translate for English/Japanese only.
    """
    # If the user did not provide any text
    if not slash_command_text:
        # Try to grab the most recent non-bot message from the channel
        try:
            response = client.conversations_history(channel=channel_id, limit=5)
            messages = response.get("messages", [])

            for msg in messages:
                # We only want messages from a human user (no bot_id, no subtype)
                if not msg.get("bot_id") and not msg.get("subtype"):
                    slash_command_text = msg.get("text", "")
                    break
        except Exception as e:
            print(f"Error fetching conversation history: {e}")
            slash_command_text = ""

    # If still empty, let the user know
    if not slash_command_text:
        slash_command_text = "No text found to translate."
        client.chat_postMessage(
            channel=channel_id, 
            text=f"Nothing found: {slash_command_text}"
        )
        return Response(), 200

    # Otherwise, proceed with the original Japanese/English translation logic
    client.chat_postMessage(
        channel=channel_id, 
        text=f"Translating: {slash_command_text}"
    )

    try:
        result = call_aoai_translate(QueryRequest(user_query=slash_command_text))
        client.chat_postMessage(
            channel=channel_id, 
            text=f"Translation result:\n{result}"
        )
        return Response(), 200

    except Exception as e:
        print("Error during AOAI call:", str(e))
        client.chat_postMessage(channel=channel_id, text="Sorry, I hit an error: " + str(e))
        return Response(status=500)


@app.route('/translate-message', methods=['POST'])
def translate_message():
    # Verify Slack signature
    print("about to verify slack signature")
    if not verify_slack_signature(os.environ['SIGNING_SECRET']):
        return Response("Invalid Slack signature", status=403)
    
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    slash_command_text = data.get('text', '').strip()

    tokens = slash_command_text.split(maxsplit=2)

    match len(tokens):
        case 3:
            source_lang, target_lang, text_to_translate = tokens
            return handle_two_language_request(channel_id, source_lang, target_lang, text_to_translate)
        case _:
            return handle_default_request(channel_id, slash_command_text)

        

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

# don't need below, used earlier for testing purposes, keeping for reference in case I want to expand this 
# in a particular channel just for the translate bot where it replies more often.
# @slack_event_adapter.on('message')
# def message(payload):
#    print(payload)
#    event = payload.get('event', {})
#    channel_id = event.get('channel')
#    user_id = event.get('user')
#    text = event.get('text')
