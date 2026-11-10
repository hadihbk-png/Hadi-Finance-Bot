"""Deterministic financial calculators exposed to the model as tools.

The model never does arithmetic itself; it calls these functions so the
numbers it reports are exact.
"""

from __future__ import annotations

import math


def budget_breakdown(monthly_income: float, expenses: dict[str, float] | None = None) -> dict:
    """Compare spending against the 50/30/20 rule and report the surplus."""
    expenses = expenses or {}
    total = sum(expenses.values())
    return {
        "monthly_income": round(monthly_income, 2),
        "total_expenses": round(total, 2),
        "surplus": round(monthly_income - total, 2),
        "savings_rate_pct": round((monthly_income - total) / monthly_income * 100, 1) if monthly_income else 0,
        "guideline_50_30_20": {
            "needs": round(monthly_income * 0.50, 2),
            "wants": round(monthly_income * 0.30, 2),
            "savings_and_debt": round(monthly_income * 0.20, 2),
        },
        "expense_share_pct": {
            k: round(v / monthly_income * 100, 1) for k, v in expenses.items()
        } if monthly_income else {},
    }


def compound_growth(
    principal: float,
    annual_rate_pct: float,
    years: int,
    monthly_contribution: float = 0.0,
    inflation_pct: float = 0.0,
) -> dict:
    """Future value with monthly compounding and monthly contributions."""
    r = annual_rate_pct / 100 / 12
    n = years * 12
    balance = principal
    yearly = []
    for month in range(1, n + 1):
        balance = balance * (1 + r) + monthly_contribution
        if month % 12 == 0:
            yearly.append({"year": month // 12, "balance": round(balance, 2)})
    contributed = principal + monthly_contribution * n
    real = balance / ((1 + inflation_pct / 100) ** years)
    return {
        "future_value": round(balance, 2),
        "future_value_in_todays_dollars": round(real, 2),
        "total_contributed": round(contributed, 2),
        "total_growth": round(balance - contributed, 2),
        "by_year": yearly if years <= 10 else yearly[::max(1, years // 10)] + [yearly[-1]],
    }


def loan_payment(principal: float, annual_rate_pct: float, years: float) -> dict:
    """Fixed monthly payment for an amortizing loan (mortgage, auto, etc.)."""
    n = round(years * 12)
    r = annual_rate_pct / 100 / 12
    payment = principal / n if r == 0 else principal * r / (1 - (1 + r) ** -n)
    total = payment * n
    return {
        "monthly_payment": round(payment, 2),
        "total_paid": round(total, 2),
        "total_interest": round(total - principal, 2),
        "months": n,
    }


def debt_payoff(debts: list[dict], monthly_budget: float, strategy: str = "avalanche") -> dict:
    """Simulate paying off several debts with avalanche (highest APR first)
    or snowball (smallest balance first). Each debt: name, balance, apr_pct, min_payment."""
    ds = [dict(d) for d in debts]
    min_total = sum(d["min_payment"] for d in ds)
    if monthly_budget < min_total:
        return {"error": f"Budget {monthly_budget} is below total minimum payments {round(min_total, 2)}."}

    key = (lambda d: -d["apr_pct"]) if strategy == "avalanche" else (lambda d: d["balance"])
    months, interest_paid, payoff_order = 0, 0.0, []
    while any(d["balance"] > 0.005 for d in ds):
        months += 1
        if months > 1200:
            return {"error": "Debts never pay off at this budget (interest exceeds payments)."}
        for d in ds:
            if d["balance"] > 0:
                i = d["balance"] * d["apr_pct"] / 100 / 12
                d["balance"] += i
                interest_paid += i
        remaining = monthly_budget
        for d in ds:
            pay = min(d["min_payment"], d["balance"])
            d["balance"] -= pay
            remaining -= pay
        for d in sorted((d for d in ds if d["balance"] > 0), key=key):
            pay = min(remaining, d["balance"])
            d["balance"] -= pay
            remaining -= pay
        for d in ds:
            if d["balance"] <= 0.005 and d["name"] not in [p["name"] for p in payoff_order]:
                payoff_order.append({"name": d["name"], "paid_off_month": months})
    return {
        "strategy": strategy,
        "months_to_debt_free": months,
        "years_to_debt_free": round(months / 12, 1),
        "total_interest_paid": round(interest_paid, 2),
        "payoff_order": payoff_order,
    }


def retirement_projection(
    current_age: int,
    retirement_age: int,
    current_savings: float,
    monthly_contribution: float,
    annual_return_pct: float = 7.0,
    desired_annual_income: float | None = None,
    withdrawal_rate_pct: float = 4.0,
) -> dict:
    """Project savings at retirement and compare to a target using a safe-withdrawal rate."""
    years = retirement_age - current_age
    if years <= 0:
        return {"error": "Retirement age must be greater than current age."}
    growth = compound_growth(current_savings, annual_return_pct, years, monthly_contribution)
    nest_egg = growth["future_value"]
    result = {
        "years_until_retirement": years,
        "projected_nest_egg": nest_egg,
        "sustainable_annual_income": round(nest_egg * withdrawal_rate_pct / 100, 2),
    }
    if desired_annual_income:
        target = desired_annual_income / (withdrawal_rate_pct / 100)
        result["target_nest_egg"] = round(target, 2)
        result["shortfall"] = round(max(0.0, target - nest_egg), 2)
        if nest_egg < target:
            r = annual_return_pct / 100 / 12
            n = years * 12
            fv_principal = current_savings * (1 + r) ** n
            factor = n if r == 0 else ((1 + r) ** n - 1) / r
            result["monthly_contribution_needed"] = round((target - fv_principal) / factor, 2)
    return result


def emergency_fund(monthly_essential_expenses: float, current_fund: float = 0.0, months_target: int = 6) -> dict:
    """How big an emergency fund should be and how far along the user is."""
    target = monthly_essential_expenses * months_target
    return {
        "target": round(target, 2),
        "current": round(current_fund, 2),
        "gap": round(max(0.0, target - current_fund), 2),
        "months_covered": round(current_fund / monthly_essential_expenses, 1) if monthly_essential_expenses else math.inf,
    }


TOOLS = {
    "budget_breakdown": budget_breakdown,
    "compound_growth": compound_growth,
    "loan_payment": loan_payment,
    "debt_payoff": debt_payoff,
    "retirement_projection": retirement_projection,
    "emergency_fund": emergency_fund,
}


def _fn(name: str, description: str, properties: dict, required: list[str]) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required},
        },
    }


_num = {"type": "number"}
_int = {"type": "integer"}

TOOL_SCHEMAS = [
    _fn(
        "budget_breakdown",
        "Analyze a monthly budget: surplus, savings rate, and comparison to the 50/30/20 rule.",
        {
            "monthly_income": {**_num, "description": "Take-home monthly income"},
            "expenses": {
                "type": "object",
                "description": "Map of expense category to monthly amount",
                "additionalProperties": _num,
            },
        },
        ["monthly_income"],
    ),
    _fn(
        "compound_growth",
        "Project investment growth with monthly compounding and optional monthly contributions.",
        {
            "principal": _num,
            "annual_rate_pct": {**_num, "description": "Expected annual return, e.g. 7 for 7%"},
            "years": _int,
            "monthly_contribution": _num,
            "inflation_pct": {**_num, "description": "Used to express the result in today's dollars"},
        },
        ["principal", "annual_rate_pct", "years"],
    ),
    _fn(
        "loan_payment",
        "Monthly payment, total interest and total cost of a fixed-rate amortizing loan.",
        {"principal": _num, "annual_rate_pct": _num, "years": _num},
        ["principal", "annual_rate_pct", "years"],
    ),
    _fn(
        "debt_payoff",
        "Simulate paying off multiple debts with the avalanche or snowball method.",
        {
            "debts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "balance": _num,
                        "apr_pct": _num,
                        "min_payment": _num,
                    },
                    "required": ["name", "balance", "apr_pct", "min_payment"],
                },
            },
            "monthly_budget": {**_num, "description": "Total amount available for debt each month"},
            "strategy": {"type": "string", "enum": ["avalanche", "snowball"]},
        },
        ["debts", "monthly_budget"],
    ),
    _fn(
        "retirement_projection",
        "Project retirement savings and whether they cover a desired income (safe-withdrawal-rate method).",
        {
            "current_age": _int,
            "retirement_age": _int,
            "current_savings": _num,
            "monthly_contribution": _num,
            "annual_return_pct": _num,
            "desired_annual_income": _num,
            "withdrawal_rate_pct": _num,
        },
        ["current_age", "retirement_age", "current_savings", "monthly_contribution"],
    ),
    _fn(
        "emergency_fund",
        "Size an emergency fund and measure progress toward it.",
        {"monthly_essential_expenses": _num, "current_fund": _num, "months_target": _int},
        ["monthly_essential_expenses"],
    ),
]
