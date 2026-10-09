"""Python 3.11+; stdlib. Timeout cancels work; cooperative cleanup always runs."""
import asyncio
from contextlib import asynccontextmanager


@asynccontextmanager
async def lease(events):
    events.append("acquired")
    try:
        yield
    finally:
        # This fixture cleanup has no await: synchronous release cannot be interrupted.
        events.append("released")


async def operation(events, started, release):
    async with lease(events):
        started.set()
        await release.wait()
        events.append("completed")
        return "ok"


async def timed_operation(events, started, release, seconds):
    # Catch outside timeout: its context converts its own cancellation to TimeoutError.
    try:
        async with asyncio.timeout(seconds):
            return await operation(events, started, release)
    except TimeoutError:
        return "timeout"


async def main():
    events, started, release = [], asyncio.Event(), asyncio.Event()
    release.set()
    assert await timed_operation(events, started, release, 1) == "ok"
    assert events == ["acquired", "completed", "released"]
    events, started, release = [], asyncio.Event(), asyncio.Event()
    assert await timed_operation(events, started, release, 0.01) == "timeout"
    assert events == ["acquired", "released"]
    events, started, release = [], asyncio.Event(), asyncio.Event()
    task = asyncio.create_task(timed_operation(events, started, release, 10))
    await started.wait()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    else:
        raise AssertionError("external cancellation was swallowed")
    assert events == ["acquired", "released"] and task.cancelled()
    assert not [t for t in asyncio.all_tasks() if t is not asyncio.current_task() and not t.done()]
    print("PASS cleanup: normal, timeout, external cancellation, no leaked tasks")


if __name__ == "__main__":
    asyncio.run(main())
