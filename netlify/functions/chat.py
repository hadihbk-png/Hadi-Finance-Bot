import json
import os
import secrets
from dotenv import load_dotenv
from openai import AzureOpenAI
from advisor import FinancialAdvisor

load_dotenv()

_advisors = {}

def _get_azure_client():
    return AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )

def _advisor(sid):
    if sid is None or sid not in _advisors:
        sid = secrets.token_hex(16)
        _advisors[sid] = FinancialAdvisor(client=_get_azure_client())
    return _advisors[sid], sid

def handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
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
        return {
            "statusCode": 502,
            "body": json.dumps({"error": f"Error talking to the model: {exc}"}),
            "headers": {"Content-Type": "application/json"}
        }
