"""Financial Advisor Bot - browser chat.

Run:  python web.py   then open http://localhost:8000
"""

from __future__ import annotations

import os
import secrets
import sys

from flask import Flask, jsonify, request, send_from_directory, session
from openai import AzureOpenAI

from advisor import FinancialAdvisor

app = Flask(__name__, static_folder="static")
app.secret_key = os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32)

# One advisor (conversation history) per browser session, kept in memory.
_advisors: dict[str, FinancialAdvisor] = {}


def _get_azure_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )


def _advisor() -> FinancialAdvisor:
    sid = session.get("sid")
    if sid is None or sid not in _advisors:
        sid = secrets.token_hex(16)
        session["sid"] = sid
        _advisors[sid] = FinancialAdvisor(client=_get_azure_client())
    return _advisors[sid]


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.post("/api/chat")
def chat():
    message = (request.get_json(silent=True) or {}).get("message", "").strip()
    if not message:
        return jsonify(error="Empty message"), 400
    try:
        return jsonify(reply=_advisor().ask(message))
    except Exception as exc:
        return jsonify(error=f"Error talking to the model: {exc}"), 502


@app.post("/api/reset")
def reset():
    _advisor().reset()
    return jsonify(ok=True)


if __name__ == "__main__":
    if not os.getenv("AZURE_OPENAI_API_KEY"):
        sys.exit("AZURE_OPENAI_API_KEY is not set. Add it to the .env file.")
    if not os.getenv("AZURE_OPENAI_ENDPOINT"):
        sys.exit("AZURE_OPENAI_ENDPOINT is not set. Add it to the .env file.")
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"Financial Advisor Bot running at http://localhost:{port}")
    app.run(host=host, port=port, debug=False)
