"""Python 3.11+; stdlib. Fixed workers, bounded queue, explicit outcomes."""
import asyncio


async def process(values, workers=3, capacity=4):
    if workers < 1 or capacity < 1:
        raise ValueError("positive worker count and capacity required")
    queue = asyncio.Queue(maxsize=capacity)
    outcomes = [None] * len(values)
    stats = {"active": 0, "max_active": 0, "max_queued": 0}
    sentinel = object()

    async def worker():
        while True:
            item = await queue.get()
            try:
                if item is sentinel:
                    return
                index, value = item
                stats["active"] += 1
                stats["max_active"] = max(stats["max_active"], stats["active"])
                try:
                    await asyncio.sleep(0)
                    if value < 0:
                        raise ValueError("negative fixture")
                    outcomes[index] = {"index": index, "status": "ok", "value": value * 2}
                except ValueError as exc:
                    outcomes[index] = {"index": index, "status": "error", "reason": str(exc)}
                finally:
                    stats["active"] -= 1
            finally:
                queue.task_done()

    async with asyncio.TaskGroup() as group:
        for _ in range(workers):
            group.create_task(worker())
        for index, value in enumerate(values):
            await queue.put((index, value))
            stats["max_queued"] = max(stats["max_queued"], queue.qsize())
        for _ in range(workers):
            await queue.put(sentinel)
        await queue.join()
    assert all(result is not None for result in outcomes)
    return outcomes, stats


async def main():
    values = list(range(100)) + [-1]
    outcomes, stats = await process(values)
    assert len(outcomes) == 101 and [x["index"] for x in outcomes] == list(range(101))
    assert outcomes[-1] == {"index": 100, "status": "error", "reason": "negative fixture"}
    assert outcomes[99]["value"] == 198
    assert stats["max_active"] <= 3 and stats["max_queued"] <= 4 and stats["active"] == 0
    empty, _ = await process([])
    assert empty == []
    try:
        await process(["programmer-bug"])
    except ExceptionGroup as exc:
        assert any(isinstance(error, TypeError) for error in exc.exceptions)
    else:
        raise AssertionError("unexpected programmer error swallowed")
    cancelled = asyncio.create_task(process(list(range(1000))))
    await asyncio.sleep(0)
    cancelled.cancel()
    try:
        await cancelled
    except asyncio.CancelledError:
        pass
    else:
        raise AssertionError("external cancellation swallowed")
    assert not [t for t in asyncio.all_tasks() if t is not asyncio.current_task() and not t.done()]
    print("PASS bounded queue: 101 ordered outcomes, explicit row failure, worker/queue bounds")


if __name__ == "__main__":
    asyncio.run(main())
