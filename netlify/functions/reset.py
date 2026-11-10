import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv
from advisor import FinancialAdvisor

load_dotenv()

_advisors = {}

def _advisor(sid):
    if sid and sid in _advisors:
        return _advisors[sid]
    return None

def handler(event, context):
    try:
        body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else event.get("body", {})
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
        import traceback
        error_msg = f"{type(exc).__name__}: {exc}"
        print(f"Error in reset handler: {error_msg}")
        print(traceback.format_exc())
        return {
            "statusCode": 502,
            "body": json.dumps({"error": f"Error resetting conversation: {error_msg}"}),
            "headers": {"Content-Type": "application/json"}
        }

