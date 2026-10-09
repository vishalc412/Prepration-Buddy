"""Python 3.11+; stdlib. Simulated provider, no external charges or waits."""
class TransientError(Exception):
    pass


class PermanentError(Exception):
    pass


class UnknownOutcome(Exception):
    pass


class Provider:
    def __init__(self, mode):
        self.mode = mode
        self.receipts = {}
        self.attempts = 0
        self.effects = 0

    def submit(self, key, amount):
        self.attempts += 1
        if key in self.receipts:
            stored_amount, receipt = self.receipts[key]
            if stored_amount != amount:
                raise PermanentError("idempotency key payload mismatch")
            return receipt
        if self.mode == "permanent":
            raise PermanentError("request rejected")
        if self.mode == "always-transient":
            raise TransientError("unavailable before acceptance")
        self.effects += 1
        receipt = {"key": key, "amount": amount, "status": "accepted"}
        self.receipts[key] = (amount, receipt)
        if self.mode == "ambiguous" and self.attempts == 1:
            raise TransientError("connection failed after durable acceptance")
        return receipt


def submit_with_retry(provider, key, amount, max_attempts=3, sleep=lambda _: None):
    if type(max_attempts) is not int or max_attempts < 1 or max_attempts > 5:
        raise ValueError("attempt budget must be 1..5")
    for attempt in range(max_attempts):
        try:
            return provider.submit(key, amount)
        except TransientError as exc:
            if attempt + 1 == max_attempts:
                raise UnknownOutcome("budget exhausted; reconcile using original key") from exc
            sleep(min(0.1 * 2 ** attempt, 0.5))
    raise AssertionError("unreachable")


def main():
    waits = []
    provider = Provider("ambiguous")
    receipt = submit_with_retry(provider, "order-7", "20.00", sleep=waits.append)
    assert receipt["status"] == "accepted" and provider.effects == 1
    assert provider.attempts == 2 and waits == [0.1]
    try:
        submit_with_retry(provider, "order-7", "21.00")
    except PermanentError:
        pass
    else:
        raise AssertionError("different payload reused key")
    down = Provider("always-transient")
    waits = []
    try:
        submit_with_retry(down, "order-8", "20.00", sleep=waits.append)
    except UnknownOutcome:
        pass
    else:
        raise AssertionError("exhaustion silently accepted")
    assert down.attempts == 3 and down.effects == 0 and waits == [0.1, 0.2]
    rejected = Provider("permanent")
    try:
        submit_with_retry(rejected, "order-9", "20.00")
    except PermanentError:
        pass
    else:
        raise AssertionError("permanent rejection hidden")
    assert rejected.attempts == 1
    print("PASS bounded retries: ambiguous replay exactly one simulated effect; exhausted/permanent visible")


if __name__ == "__main__":
    main()
