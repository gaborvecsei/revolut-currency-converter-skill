#!/usr/bin/env python3
"""
Revolut Currency Converter CLI
"""

import argparse
import json
import sys
from typing import Any

import requests

API = "https://www.revolut.com/api/exchange/quote"
DEFAULT_BRIDGES = ["EUR", "USD"]


def validate_amount(amount: int) -> None:
    if amount < 1:
        raise ValueError("Amount must be at least 1")


def convert(from_c: str, to_c: str, amount: int) -> dict[str, Any]:
    validate_amount(amount)
    data = _query(from_c, to_c, amount)
    rate = data["rate"]["rate"]
    result = amount * rate
    return {
        "success": True,
        "from": from_c.upper(),
        "to": to_c.upper(),
        "amount": amount,
        "result": round(result, 2),
        "rate": rate,
    }


def find_route(
    from_c: str,
    to_c: str,
    amount: int,
    bridges: list[str] | None = None,
    max_hops: int = 1,
) -> dict[str, Any]:
    validate_amount(amount)
    if bridges is None:
        bridges = DEFAULT_BRIDGES

    from_c, to_c = from_c.upper(), to_c.upper()
    bridges = [b.upper() for b in bridges if b.upper() not in (from_c, to_c)]

    routes = {}

    # Direct
    try:
        data = _query(from_c, to_c, amount)
        r = data["rate"]["rate"]
        routes["direct"] = {
            "path": [from_c, to_c],
            "amount": round(amount * r, 2),
            "rate": r,
        }
    except Exception:
        pass

    # Via bridge
    if max_hops >= 1:
        for b in bridges:
            try:
                d1 = _query(from_c, b, amount)
                r1 = d1["rate"]["rate"]
                mid = amount * r1
                d2 = _query(b, to_c, int(mid))
                r2 = d2["rate"]["rate"]
                final = mid * r2
                routes[f"{from_c}->{b}->{to_c}"] = {
                    "path": [from_c, b, to_c],
                    "amount": round(final, 2),
                    "rate": r2,
                }
            except Exception:
                pass

    best = max(routes.values(), key=lambda x: x["amount"]) if routes else None

    return {
        "success": bool(routes),
        "from": from_c,
        "to": to_c,
        "amount": amount,
        "routes": routes,
        "best": best["path"] if best else None,
        "best_amount": best["amount"] if best else None,
    }


def rate(from_c: str, to_c: str) -> dict[str, Any]:
    data = _query(from_c, to_c, 1)
    return {
        "success": True,
        "from": from_c.upper(),
        "to": to_c.upper(),
        "rate": data["rate"]["rate"],
    }


def _query(from_c: str, to_c: str, amount: int) -> dict:
    params = {
        "amount": amount,
        "fromCurrency": from_c,
        "toCurrency": to_c,
        "country": "GB",
        "isRecipientAmount": "false",
        "localeCode": "en-GB",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "accept-language": "en-US,en;q=0.9",
    }
    r = requests.get(API, params=params, headers=headers)
    r.raise_for_status()
    return r.json()


def main():
    p = argparse.ArgumentParser(description="Revolut Currency Converter")
    sub = p.add_subparsers(dest="cmd")

    c = sub.add_parser("convert", help="Convert amount")
    c.add_argument("amount", type=int, help="Amount (integer >= 1)")
    c.add_argument("from_c")
    c.add_argument("to_c")
    c.add_argument("--pretty", action="store_true")

    r = sub.add_parser("find-route", help="Find best route")
    r.add_argument("amount", type=int)
    r.add_argument("from_c")
    r.add_argument("to_c")
    r.add_argument("-n", "--hops", type=int, default=1)
    r.add_argument("-b", "--bridges", nargs="+", default=DEFAULT_BRIDGES)
    r.add_argument("--pretty", action="store_true")

    s = sub.add_parser("rate", help="Get rate")
    s.add_argument("from_c")
    s.add_argument("to_c")
    s.add_argument("--pretty", action="store_true")

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        sys.exit(1)

    try:
        if args.cmd == "convert":
            out = convert(args.from_c, args.to_c, args.amount)
        elif args.cmd == "find-route":
            out = find_route(
                args.from_c, args.to_c, args.amount, args.bridges, args.hops
            )
        else:
            out = rate(args.from_c, args.to_c)

        print(json.dumps(out, indent=2 if getattr(args, "pretty", False) else None))

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
