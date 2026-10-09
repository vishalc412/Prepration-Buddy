"""Python 3.11+; stdlib. Process-local in-flight dedupe, not durable idempotency."""
import asyncio


class SingleFlight:
    def __init__(self, limit=8):
        self.tasks = {}
        self.lock = asyncio.Lock()
        self.limit = limit
        self.closed = False

    async def get(self, key, factory):
        async with self.lock:
            if self.closed:
                raise RuntimeError("single-flight owner closed")
            task = self.tasks.get(key)
            if task is None:
                if len(self.tasks) >= self.limit:
                    raise RuntimeError("in-flight key capacity reached")
                task = asyncio.create_task(factory())
                self.tasks[key] = task
                task.add_done_callback(lambda completed, k=key: self._done(k, completed))
        # Caller cancellation leaves shared task available to other callers.
        return await asyncio.shield(task)

    def _done(self, key, task):
        if self.tasks.get(key) is task:
            del self.tasks[key]
        if not task.cancelled():
            task.exception()  # Retrieve exception even when every waiter disconnects.

    async def close(self):
        async with self.lock:
            self.closed = True
            tasks = list(self.tasks.values())
            for task in tasks:
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        # These are intentional shutdown cancellations, not discarded work outcomes.
        self.tasks.clear()


async def main():
    flight = SingleFlight(limit=1)
    started, release = asyncio.Event(), asyncio.Event()
    calls = 0

    async def provider():
        nonlocal calls
        calls += 1
        started.set()
        await release.wait()
        return "shared result"

    first = asyncio.create_task(flight.get(("tenant-a", "same-question"), provider))
    await started.wait()
    second = asyncio.create_task(flight.get(("tenant-a", "same-question"), provider))
    await asyncio.sleep(0)
    first.cancel()
    try:
        await first
    except asyncio.CancelledError:
        pass
    else:
        raise AssertionError("cancelled caller continued")
    try:
        await flight.get(("tenant-b", "other-question"), provider)
    except RuntimeError:
        pass
    else:
        raise AssertionError("capacity overflow accepted")
    release.set()
    assert await second == "shared result" and calls == 1
    await asyncio.sleep(0)
    assert not flight.tasks
    async def failing():
        raise ValueError("provider failed")
    try:
        await flight.get("retryable-key", failing)
    except ValueError:
        pass
    else:
        raise AssertionError("provider failure hidden")
    await asyncio.sleep(0)
    assert await flight.get("retryable-key", provider) == "shared result" and calls == 2
    pending = asyncio.create_task(flight.get("shutdown-key", lambda: asyncio.Event().wait()))
    await asyncio.sleep(0)
    await flight.close()
    try:
        await pending
    except asyncio.CancelledError:
        pass
    else:
        raise AssertionError("shutdown did not cancel pending work")
    assert not flight.tasks
    try:
        await flight.get("after-close", provider)
    except RuntimeError:
        pass
    else:
        raise AssertionError("shutdown owner admitted new work")
    print("PASS single-flight: one shared call, isolated cancellation, capacity, failure retry, shutdown")


if __name__ == "__main__":
    asyncio.run(main())
