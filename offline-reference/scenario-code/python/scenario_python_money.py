"""Python 3.11+; stdlib. Explicit line rounding and replay-safe invoice ledger."""
from decimal import Decimal, ROUND_HALF_UP


class Conflict(ValueError):
    pass


def line_total(price_text, quantity):
    if not isinstance(price_text, str) or len(price_text) > 32:
        raise ValueError("price must be a short decimal string")
    price = Decimal(price_text)
    if not price.is_finite() or price < 0 or price > Decimal("1000000"):
        raise ValueError("invalid price")
    if type(quantity) is not int or not 1 <= quantity <= 10000:
        raise ValueError("invalid quantity")
    return (price * quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class Ledger:
    def __init__(self):
        self.entries = {}

    def post(self, invoice_id, currency, lines):
        if not invoice_id or currency not in {"USD", "INR"} or not lines:
            raise ValueError("invalid invoice")
        payload = (currency, tuple((price, qty) for price, qty in lines))
        total = sum((line_total(price, qty) for price, qty in lines), Decimal("0.00"))
        previous = self.entries.get(invoice_id)
        if previous is not None:
            if previous[0] != payload:
                raise Conflict("invoice id reused with a different payload")
            return previous[1]
        receipt = {"invoice": invoice_id, "currency": currency, "total": format(total, ".2f")}
        self.entries[invoice_id] = (payload, receipt)
        return receipt


def main():
    ledger = Ledger()
    first = ledger.post("inv-1", "USD", [("0.005", 1), ("0.005", 1)])
    assert first["total"] == "0.02"  # Round each line, then sum.
    assert ledger.post("inv-1", "USD", [("0.005", 1), ("0.005", 1)]) is first
    assert len(ledger.entries) == 1
    for operation in (
        lambda: ledger.post("inv-1", "INR", [("0.005", 1), ("0.005", 1)]),
        lambda: ledger.post("inv-1", "USD", [("1.00", 1)]),
    ):
        try:
            operation()
        except Conflict:
            pass
        else:
            raise AssertionError("changed replay accepted")
    for price, qty in [("NaN", 1), ("-1", 1), ("Infinity", 1), ("1", True), ("1", 0)]:
        try:
            line_total(price, qty)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid amount/quantity accepted")
    assert ledger.post("inv-2", "INR", [("19.995", 3)])["total"] == "59.99"
    print("PASS Decimal ledger: rounding, unchanged replay, conflicts, invalid inputs")


if __name__ == "__main__":
    main()
