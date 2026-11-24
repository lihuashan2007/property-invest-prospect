#!/usr/bin/env python3
"""Estimate recurring pre-tax cash flow for interest-only property loans."""

import argparse
import json
from decimal import Decimal, InvalidOperation, ROUND_FLOOR, ROUND_HALF_UP
from itertools import product


FULL_YEAR_WEEKS = Decimal(52)
PERCENT = Decimal(100)
CENT = Decimal("0.01")


def decimal_input(value):
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError(f"Expected a number, got {value!r}") from exc
    if not number.is_finite():
        raise argparse.ArgumentTypeError("Expected a finite number")
    return number


def rounded(value):
    return float(value.quantize(CENT, rounding=ROUND_HALF_UP))


def parse_inputs():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--price", nargs="+", required=True, type=decimal_input,
        help="Purchase price or price range endpoints.",
    )
    parser.add_argument(
        "--weekly-rent", nargs="+", required=True, type=decimal_input,
        help="Weekly rent estimates. Run a separate scenario with different expenses when needed.",
    )
    parser.add_argument(
        "--rates", nargs="+", default=[Decimal(4), Decimal(5), Decimal(6)],
        type=decimal_input, help="Annual interest rates in percent. Default: 4 5 6.",
    )
    parser.add_argument(
        "--deposit-percent", type=decimal_input, default=Decimal(20),
        help="Deposit as a percentage of the purchase price. Default: 20.",
    )
    parser.add_argument(
        "--rented-weeks", type=decimal_input, default=Decimal(50),
        help="Expected paid weeks per year. Default: 50.",
    )
    parser.add_argument(
        "--management-percent", type=decimal_input, default=Decimal("7.7"),
        help="Management fee as a percentage of collected rent. Default: 7.7.",
    )
    parser.add_argument(
        "--annual-fixed-costs", type=decimal_input, default=Decimal(6500),
        help="Annual recurring holding costs excluding management fees and interest. Default: 6500.",
    )
    inputs = parser.parse_args()
    if any(price <= 0 for price in inputs.price):
        parser.error("Purchase prices must be positive.")
    if any(rent < 0 for rent in inputs.weekly_rent):
        parser.error("Weekly rents must be nonnegative.")
    if any(rate < 0 for rate in inputs.rates):
        parser.error("Interest rates must be nonnegative.")
    if not 0 <= inputs.deposit_percent <= PERCENT:
        parser.error("Deposit percentage must be between 0 and 100.")
    if not 0 < inputs.rented_weeks <= FULL_YEAR_WEEKS:
        parser.error("Paid weeks must be above 0 and no more than 52.")
    if not 0 <= inputs.management_percent < PERCENT:
        parser.error("Management percentage must be at least 0 and below 100.")
    if inputs.annual_fixed_costs < 0:
        parser.error("Annual fixed costs must be nonnegative.")
    return inputs


def scenario(price, weekly_rent, rate, inputs):
    loan_amount = price * (1 - inputs.deposit_percent / PERCENT)
    annual_interest = loan_amount * rate / PERCENT
    management_rate = inputs.management_percent / PERCENT
    collected_rent = weekly_rent * inputs.rented_weeks
    management_fee = collected_rent * management_rate
    fixed_costs = inputs.annual_fixed_costs
    total_outgoings = annual_interest + management_fee + fixed_costs
    cash_flow = collected_rent - total_outgoings
    break_even_rent = (annual_interest + fixed_costs) / (
        inputs.rented_weeks * (1 - management_rate)
    )
    first_positive_rent = int(break_even_rent.to_integral_value(rounding=ROUND_FLOOR)) + 1

    return {
        "purchase_price": rounded(price),
        "weekly_rent": rounded(weekly_rent),
        "loan_amount": rounded(loan_amount),
        "interest_rate_percent": float(rate),
        "gross_yield_percent": rounded(weekly_rent * FULL_YEAR_WEEKS / price * PERCENT),
        "annual_collected_rent": rounded(collected_rent),
        "annual_management_fee": rounded(management_fee),
        "annual_fixed_holding_costs": rounded(fixed_costs),
        "annual_interest": rounded(annual_interest),
        "annual_total_outgoings": rounded(total_outgoings),
        "annual_cash_flow": rounded(cash_flow),
        "monthly_cash_flow": rounded(cash_flow / 12),
        "annual_out_of_pocket": rounded(max(-cash_flow, Decimal(0))),
        "weekly_break_even_rent": rounded(break_even_rent),
        "weekly_rent_for_positive_cash_flow_whole_dollars": first_positive_rent,
    }


def main():
    inputs = parse_inputs()
    result = {
        "assumptions": {
            "repayment": "interest_only",
            "deposit_percent": float(inputs.deposit_percent),
            "paid_weeks_per_year": float(inputs.rented_weeks),
            "management_percent": float(inputs.management_percent),
            "annual_fixed_holding_costs": rounded(inputs.annual_fixed_costs),
            "gross_yield_weeks_per_year": int(FULL_YEAR_WEEKS),
        },
        "scenarios": [
            scenario(price, rent, rate, inputs)
            for price, rent, rate in product(inputs.price, inputs.weekly_rent, inputs.rates)
        ],
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
