"""Financial Advisor Bot - an interactive command-line chat.

Run:  python advisor.py
"""

from __future__ import annotations

import json
import os
import sys

from dotenv import load_dotenv
from openai import AzureOpenAI

from finance_tools import TOOL_SCHEMAS, TOOLS

load_dotenv()

MODEL = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")

SYSTEM_PROMPT = """You are a friendly, practical personal financial advisor.

How you work:
- Ask short clarifying questions only when essential personal numbers (income, expenses, debts, ages, balances) are missing.
- For market assumptions, don't ask - use sensible defaults (7% annual return, 3% inflation, 4% withdrawal rate), state them, and answer.
- NEVER do arithmetic in your head. Use the provided tools for every calculation and report their results.
- Give concrete, prioritized next steps. A common order is: small emergency buffer -> capture any employer retirement match -> pay off high-interest debt -> full emergency fund -> long-term investing.
- Explain trade-offs and assumptions (return rates, inflation) plainly. Prefer low-cost, diversified, long-term approaches.
- Do not recommend specific individual stocks, crypto tokens, or market timing. Do not promise returns.
- For taxes, legal matters, or large/complex decisions, suggest consulting a licensed professional (CFP, CPA, attorney).
- Keep answers concise and use short bullet lists and simple tables when helpful.

You provide general educational information, not personalized licensed financial advice."""

DISCLAIMER = (
    "Educational information only - not licensed financial, tax, or legal advice.\n"
    "Type your question, or 'quit' to exit. Type 'reset' to start a new conversation."
)


class FinancialAdvisor:
    def __init__(self, client: AzureOpenAI | None = None, model: str = MODEL):
        if client is None:
            client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("OPENAI_API_VERSION"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            )
        self.client = client
        self.model = model
        self.reset()

    def reset(self) -> None:
        self.messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    def _run_tool(self, name: str, arguments: str) -> str:
        func = TOOLS.get(name)
        if func is None:
            return json.dumps({"error": f"Unknown tool {name}"})
        try:
            return json.dumps(func(**json.loads(arguments or "{}")))
        except Exception as exc:  # report bad arguments back to the model so it can retry
            return json.dumps({"error": f"{type(exc).__name__}: {exc}"})

    def ask(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        while True:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=TOOL_SCHEMAS,
            )
            msg = response.choices[0].message
            self.messages.append(msg.model_dump(exclude_none=True))
            if not msg.tool_calls:
                return msg.content or ""
            for call in msg.tool_calls:
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": self._run_tool(call.function.name, call.function.arguments),
                    }
                )


def main() -> None:
    if not os.getenv("AZURE_OPENAI_API_KEY"):
        sys.exit("AZURE_OPENAI_API_KEY is not set. Add it to the .env file.")
    if not os.getenv("AZURE_OPENAI_ENDPOINT"):
        sys.exit("AZURE_OPENAI_ENDPOINT is not set. Add it to the .env file.")

    advisor = FinancialAdvisor()
    print("=== Financial Advisor Bot ===")
    print(DISCLAIMER)
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit", "q"}:
            print("Goodbye!")
            break
        if user_input.lower() == "reset":
            advisor.reset()
            print("Conversation reset.")
            continue
        try:
            print(f"\nAdvisor: {advisor.ask(user_input)}")
        except Exception as exc:
            print(f"\n[Error talking to the model: {exc}]")


if __name__ == "__main__":
    main()
