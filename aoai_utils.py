import tiktoken
import os
from dotenv import load_dotenv
from models import AOAIMessage, AOAIRequest, AOAIResponse, AOAIConfig
from pydantic import ValidationError
from openai import AzureOpenAI
from pathlib import Path

# Load environment variables from .env
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

try:
    config = AOAIConfig(
        endpoint=os.getenv('AOAI_ENDPOINT'),
        key=os.getenv('AOAI_KEY'),
        deployment=os.getenv('AOAI_DEPLOYMENT')
        ,api_version =os.getenv('AOAI_API_VERSION')
    )
except ValidationError as e:
    raise RuntimeError(f"Configuration validation error: {e}")

# Configure OpenAI client
client = AzureOpenAI(
    api_key=config.key,
    api_version=config.api_version,
    azure_endpoint=config.endpoint
)

# Define your model's maximum token limit
MODEL_NAME = os.getenv('AOAI_DEPLOYMENT') # "gpt-4o-mini"
TOKEN_LIMIT = os.getenv('TOKEN_LIMIT') 
# Initialize tokenizer
tokenizer = tiktoken.encoding_for_model(MODEL_NAME)

def count_tokens(text):
    """Counts the number of tokens in a given text."""
    return len(tokenizer.encode(text))



def call_aoai_general_response(query_request):
    print("!!!!! entered aoai call method")
    system_msg = AOAIMessage(role="system", content=f"You are a helpful assistant specialized in translating from Japanese to English and vice a versa. \
                 Whenever you receive english text, translate it to japanese but only use the hiragana and katakana alphabets. When you receive japanese text, translate it to english.")
    user_msg = AOAIMessage(role="user", content=query_request.user_query)
    gpt_request = AOAIRequest(
        model=config.deployment,
        messages=[
            system_msg,
            user_msg
        ]
    )

    vm_response_raw = client.chat.completions.create(**gpt_request.model_dump())
    vm_response_data = vm_response_raw.model_dump()
    vm_response = AOAIResponse(**vm_response_data)
    answer = vm_response.choices[0].message.content
    return answer