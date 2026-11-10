from dotenv import load_dotenv
import os
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv('AZURE_OPENAI_API_KEY'),
    api_version=os.getenv('OPENAI_API_VERSION'),
    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
)

print('Testing Azure OpenAI connection...')
print(f"Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
print(f"Deployment: {os.getenv('AZURE_OPENAI_DEPLOYMENT')}")
print(f"API Version: {os.getenv('OPENAI_API_VERSION')}")

try:
    response = client.chat.completions.create(
        model=os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o-mini'),
        messages=[{'role': 'user', 'content': 'Hello'}],
    )
    print('Success!')
except Exception as e:
    print(f'Error: {type(e).__name__}')
    print(f'Details: {e}')
