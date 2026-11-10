import json
import os
import sys
import secrets

# Add parent directory to path to import advisor module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv
from openai import AzureOpenAI
from advisor import FinancialAdvisor

load_dotenv()

_advisors = {}

def _get_azure_client():
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = os.getenv("OPENAI_API_VERSION")
    
    if not api_key or not endpoint:
        raise ValueError("Missing Azure OpenAI credentials in environment variables")
    
    return AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint,
    )

def _advisor(sid):
    if sid is None or sid not in _advisors:
        sid = secrets.token_hex(16)
        _advisors[sid] = FinancialAdvisor(client=_get_azure_client())
    return _advisors[sid], sid

def handler(event, context):
    try:
        body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else event.get("body", {})
        message = body.get("message", "").strip()
        sid = body.get("sid")
        
        if not message:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Empty message"}),
                "headers": {"Content-Type": "application/json"}
            }
        
        advisor, new_sid = _advisor(sid)
        reply = advisor.ask(message)
        
        return {
            "statusCode": 200,
            "body": json.dumps({"reply": reply, "sid": new_sid}),
            "headers": {"Content-Type": "application/json"}
        }
    except Exception as exc:
        import traceback
        error_msg = f"{type(exc).__name__}: {exc}"
        print(f"Error in chat handler: {error_msg}")
        print(traceback.format_exc())
        return {
            "statusCode": 502,
            "body": json.dumps({"error": f"Error talking to the model: {error_msg}"}),
            "headers": {"Content-Type": "application/json"}
        }

