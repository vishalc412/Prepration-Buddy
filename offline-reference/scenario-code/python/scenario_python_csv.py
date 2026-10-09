"""Python 3.11+; stdlib. Streaming row validation with explicit quarantine."""
import csv
import io
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from tempfile import TemporaryDirectory


def ingest(source, accepted, rejected):
    reader = csv.DictReader(source)
    if reader.fieldnames != ["id", "currency", "amount"]:
        raise ValueError("header must be id,currency,amount")
    counts = {"accepted": 0, "rejected": 0}
    for number, row in enumerate(reader, 2):
        error = None
        try:
            if None in row or any(v is None for v in row.values()):
                raise ValueError("wrong column count")
            identity = row["id"].strip()
            currency = row["currency"].strip().upper()
            raw = row["amount"].strip()
            if not identity or len(identity) > 64:
                raise ValueError("invalid id")
            if currency not in {"USD", "INR"}:
                raise ValueError("unsupported currency")
            amount = Decimal(raw)
            if not amount.is_finite() or amount < 0 or amount > Decimal("1000000"):
                raise ValueError("amount out of range")
            if amount != amount.quantize(Decimal("0.01")):
                raise ValueError("fractional cent")
            normalized = {"id": identity, "currency": currency, "amount": format(amount, ".2f")}
        except (ValueError, InvalidOperation) as exc:
            error = str(exc) or "invalid decimal"
        if error is not None:
            rejected.write(json.dumps({"row": number, "raw": row, "reason": error}) + "\n")
            counts["rejected"] += 1
        else:
            accepted.write(json.dumps(normalized) + "\n")
            counts["accepted"] += 1
    return counts


def main():
    fixture = "id,currency,amount\n a1 , usd ,10.00\na2,INR,NaN\na3,USD,0.001\na4,EUR,2\na5,USD,2,extra\na6,INR,0\n"
    with TemporaryDirectory() as directory:
        folder = Path(directory)
        with (folder / "ok.jsonl").open("w") as good, (folder / "bad.jsonl").open("w") as bad:
            counts = ingest(io.StringIO(fixture), good, bad)
        rows = [json.loads(x) for x in (folder / "ok.jsonl").read_text().splitlines()]
        errors = [json.loads(x) for x in (folder / "bad.jsonl").read_text().splitlines()]
        assert counts == {"accepted": 2, "rejected": 4}
        assert rows[0] == {"id": "a1", "currency": "USD", "amount": "10.00"}
        assert rows[1]["amount"] == "0.00"
        assert len(errors) == 4 and all(x["raw"] and x["reason"] for x in errors)
        try:
            ingest(io.StringIO("wrong,header\n"), io.StringIO(), io.StringIO())
        except ValueError:
            pass
        else:
            raise AssertionError("bad header accepted")
    print("PASS streaming CSV: 2 accepted, 4 quarantined, header rejected")


if __name__ == "__main__":
    main()
