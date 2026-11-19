"""
Deterministic financial feasibility simulator.

All numbers here are plain Python arithmetic on the user's own inputs.
No LLM is involved, so the results are reproducible and unit-tested.
Outputs are planning projections based on the assumptions supplied,
NOT forecasts of real business performance.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

# Demand multipliers applied to the user's starting orders per month.
# These are adjustable planning assumptions, not market data.
DEFAULT_SCENARIOS = {
    "pessimistic": 0.6,
    "base": 1.0,
    "optimistic": 1.4,
}


class FinanceInput(BaseModel):
    budget: float = Field(ge=0, description="Starting cash (INR)")
    price_per_order: float = Field(gt=0, description="Average revenue per order")
    variable_cost_per_order: float = Field(ge=0, description="Cost to serve one order")
    monthly_fixed_costs: float = Field(ge=0, description="Rent, salaries, tools, etc.")
    starting_orders_per_month: float = Field(ge=0, description="Orders in month 1")
    monthly_growth_pct: float = Field(default=0, ge=-50, le=200)
    months: int = Field(default=12, ge=1, le=36)


def simulate_scenario(data: FinanceInput, demand_multiplier: float) -> dict:
    cash = data.budget
    rows = []
    break_even_month: Optional[int] = None  # first month with profit >= 0
    runway_month: Optional[int] = None      # first month cash drops below 0
    lowest_cash = cash

    for m in range(1, data.months + 1):
        orders = (
            data.starting_orders_per_month
            * demand_multiplier
            * (1 + data.monthly_growth_pct / 100) ** (m - 1)
        )
        revenue = orders * data.price_per_order
        variable = orders * data.variable_cost_per_order
        profit = revenue - variable - data.monthly_fixed_costs
        cash += profit
        lowest_cash = min(lowest_cash, cash)

        if break_even_month is None and profit >= 0:
            break_even_month = m
        if runway_month is None and cash < 0:
            runway_month = m

        rows.append({
            "month": m,
            "orders": round(orders, 2),
            "revenue": round(revenue, 2),
            "variable_cost": round(variable, 2),
            "fixed_cost": round(data.monthly_fixed_costs, 2),
            "profit": round(profit, 2),
            "cash_balance": round(cash, 2),
        })

    return {
        "demand_multiplier": demand_multiplier,
        "break_even_month": break_even_month,
        "cash_runs_out_month": runway_month,
        "lowest_cash": round(lowest_cash, 2),
        "ending_cash": round(cash, 2),
        "monthly": rows,
    }


def simulate(data: FinanceInput, scenarios: Optional[dict] = None) -> dict:
    scenarios = scenarios or DEFAULT_SCENARIOS
    contribution = data.price_per_order - data.variable_cost_per_order

    warnings: List[str] = []
    if contribution <= 0:
        warnings.append(
            "Variable cost per order is at or above the price, so each order "
            "loses money. Break-even is impossible at this price."
        )
    if data.budget == 0:
        warnings.append("Budget is 0, so any loss means cash runs out immediately.")

    break_even_orders = (
        round(data.monthly_fixed_costs / contribution, 2)
        if contribution > 0 else None
    )

    return {
        "contribution_per_order": round(contribution, 2),
        "contribution_margin_pct": round(contribution / data.price_per_order * 100, 2),
        "break_even_orders_per_month": break_even_orders,
        "scenarios": {
            name: simulate_scenario(data, mult)
            for name, mult in scenarios.items()
        },
        "warnings": warnings,
        "disclaimer": (
            "Planning projection from the assumptions you entered. "
            "It is not a forecast of actual results."
        ),
    }
