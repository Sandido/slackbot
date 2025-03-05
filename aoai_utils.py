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

# currently unused
# Define your model's maximum token limit
MODEL_NAME = os.getenv('AOAI_DEPLOYMENT') 
TOKEN_LIMIT = os.getenv('TOKEN_LIMIT') 
# Initialize tokenizer
tokenizer = tiktoken.encoding_for_model(MODEL_NAME)

def count_tokens(text):
    """Counts the number of tokens in a given text."""
    return len(tokenizer.encode(text))



def call_aoai_translate(query_request):
    print("!!!!! entered aoai call method")
    system_msg = AOAIMessage(role="system", content=f"You only translate between english and japanese and Japanese to english. \
                Whenever you receive english text, translate it exactly to japanese. When you receive japanese text, translate it to english. \
                Do not add anything else to the text. \
                You practice Shinto Muso Ryu and Daito Ryu under Kei Goto. This space is place for members of the dojo to use for translating messages between Japanese and English about practice and event coordination.")
    user_msg = AOAIMessage(role="user", content=f"The text to translate is: {query_request.user_query}")
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


def call_aoai_multilingual_translate(source_lang: str, target_lang: str, text: str) -> str:
    """
    Use Azure OpenAI to translate `text` FROM source_lang TO target_lang.
    Modify system instructions to suit your style.
    """
    system_msg = AOAIMessage(
        role="system",
        content=(
            "You are a translation assistant capable of translating from one language to another. "
            f"Translate FROM {source_lang} TO {target_lang}. "
            "Output only the translated text; do not add extra commentary or formatting."
        )
    )
    user_msg = AOAIMessage(
        role="user",
        content=f"{text}"
    )

    gpt_request = AOAIRequest(
        model=config.deployment,
        messages=[system_msg, user_msg]
    )

    vm_response_raw = client.chat.completions.create(**gpt_request.model_dump())
    vm_response_data = vm_response_raw.model_dump()
    vm_response = AOAIResponse(**vm_response_data)

    # Extract the translation text:
    answer = vm_response.choices[0].message.content.strip()
    return answer