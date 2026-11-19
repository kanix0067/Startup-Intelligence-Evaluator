import pytest
from pydantic import ValidationError
from app.tools.finance import FinanceInput, simulate, simulate_scenario


def make(**kw):
    base = dict(budget=100000, price_per_order=100, variable_cost_per_order=60,
                monthly_fixed_costs=20000, starting_orders_per_month=1000,
                monthly_growth_pct=0, months=6)
    base.update(kw)
    return FinanceInput(**base)


def test_break_even_orders_formula():
    r = simulate(make())
    # fixed 20000 / contribution 40 = 500 orders
    assert r["break_even_orders_per_month"] == 500
    assert r["contribution_per_order"] == 40
    assert r["contribution_margin_pct"] == 40


def test_base_month_one_numbers():
    m1 = simulate_scenario(make(), 1.0)["monthly"][0]
    assert m1["revenue"] == 100000
    assert m1["variable_cost"] == 60000
    assert m1["profit"] == 20000
    assert m1["cash_balance"] == 120000


def test_cash_runs_out_when_losing_money():
    r = simulate_scenario(make(starting_orders_per_month=100), 1.0)
    # profit/month = 100*40 - 20000 = -16000 ; 100000 lasts 6 months, runs out in month 7
    r = simulate_scenario(make(starting_orders_per_month=100, months=12), 1.0)
    assert r["cash_runs_out_month"] == 7
    assert r["break_even_month"] is None


def test_growth_compounds():
    rows = simulate_scenario(make(monthly_growth_pct=10), 1.0)["monthly"]
    assert rows[1]["orders"] == 1100
    assert rows[2]["orders"] == 1210


def test_negative_contribution_warns_and_no_break_even():
    r = simulate(make(variable_cost_per_order=120))
    assert r["break_even_orders_per_month"] is None
    assert r["warnings"]


def test_scenarios_scale_demand():
    s = simulate(make())["scenarios"]
    assert s["pessimistic"]["monthly"][0]["orders"] == 600
    assert s["optimistic"]["monthly"][0]["orders"] == 1400


@pytest.mark.parametrize("bad", [
    dict(price_per_order=0), dict(budget=-1), dict(months=0), dict(months=99),
    dict(monthly_growth_pct=500),
])
def test_invalid_inputs_rejected(bad):
    with pytest.raises(ValidationError):
        make(**bad)
