import json
import os
from dotenv import load_dotenv
from advisor import FinancialAdvisor
from openai import AzureOpenAI

load_dotenv()

_advisors = {}

def _get_azure_client():
    return AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )

def _advisor(sid):
    if sid and sid in _advisors:
        return _advisors[sid]
    return None

def handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        sid = body.get("sid")
        
        advisor = _advisor(sid)
        if advisor:
            advisor.reset()
        
        return {
            "statusCode": 200,
            "body": json.dumps({"ok": True}),
            "headers": {"Content-Type": "application/json"}
        }
    except Exception as exc:
        return {
            "statusCode": 502,
            "body": json.dumps({"error": f"Error resetting conversation: {exc}"}),
            "headers": {"Content-Type": "application/json"}
        }
