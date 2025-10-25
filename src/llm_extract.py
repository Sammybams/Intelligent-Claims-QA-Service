import os
import base64
import yaml, json, uuid, datetime, re
from pathlib import Path

from src.functions import extract_function

# Import Azure OpenAI client
from openai import AzureOpenAI

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

# Function to encode the document
def encode_doc(file_path):
    with open(file_path, "rb") as document_file:
        return base64.b64encode(document_file.read()).decode("utf-8")


def load_prompt():
    path = "src/prompts/claims_summary.yml"
    subs = {
        # "LANG": "English",
    }

    t = yaml.safe_load(Path(path).read_text(encoding="utf-8"))["prompt"]
    for k,v in subs.items():
        t = t.replace("{{"+k+"}}", str(v))
    return t


def structure_ocr_extraction(file_path: str):
    user_prompt = load_prompt()
    base64_doc = encode_doc(file_path)
    # file_type = Path(file_path).suffix.lower()

    response = client.responses.parse(
        model = deployment_name,
        input = [
            {
                "role": "system",
                "content": "You are an expert at structured data extraction. You will be given unstructured text from a Claims document and should convert it into the given structure.",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file",
                        "filename": f"{file_path}",
                        "file_data": f"data:application/pdf;base64,{base64_doc}",
                    },
                    {
                        "type": "input_text",
                        "text": user_prompt,
                    },
                ],
            },
        ],
        # File
        text = extract_function,
    )

    return response.output_text


if __name__ == "__main__":
    test_file = "sample_docs/claim1.pdf"
    result = structure_ocr_extraction(test_file)
