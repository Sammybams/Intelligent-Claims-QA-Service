import os
import yaml
from pathlib import Path

# Import Azure OpenAI client
from openai import AzureOpenAI
# from src.functions import claims_qa_response

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("AZURE_OPENAI_API_KEY")
base_url = os.getenv("AZURE_OPENAI_BASE_URL")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=api_key,
    azure_endpoint=base_url,
    api_version=api_version
)


# Function to load the prompt template
def load_prompt():
    path = "src/prompts/qna_prompt.yml"
    subs = {
        # "LANG": "English",
    }
    t = yaml.safe_load(Path(path).read_text(encoding="utf-8"))["prompt"]
    for k,v in subs.items():
        t = t.replace("{{"+k+"}}", str(v))
    return t


def structure_claims_qa(document_content: str, question: str):
    """
    Answers a question based on the structured claims document content using Azure OpenAI.
    Args:
        document_content (str): The structured claims document content as a string.
        question (str): The question to be answered.

    Returns:
        str: The answer to the question.
    """

    user_prompt = load_prompt()
    response = client.chat.completions.create(
        model = deployment_name,
        messages = [
            {
                "role": "system",
                "content": "You are an expert at structured data question answering. You will be given a structured extract from a Claims document and should answer the question based on that extract.",
            },
            {
                "role": "user",
                "content": user_prompt + "\n\nDocument Content:\n" + document_content + "\n\nQuestion:\n" + question,
            },
        ],
        # File
        temperature=0.7,
        max_tokens=1024,
    )

    return response.choices[0].message.content