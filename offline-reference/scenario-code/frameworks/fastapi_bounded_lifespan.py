"""Bounded in-process work fixture; requires FastAPI/httpx. Not durable job delivery."""
import asyncio
import time
from contextlib import asynccontextmanager, suppress
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

async def worker(state):
    while True:
        await state.gate.wait()
        job_id = await state.queue.get()
        state.active += 1
        state.jobs[job_id] = "running"
        try:
            await asyncio.sleep(0.01)  # Cooperative fixture, not CPU model inference.
            state.jobs[job_id] = "succeeded"
        except asyncio.CancelledError:
            state.jobs[job_id] = "cancelled"
            raise
        finally:
            state.active -= 1
            state.queue.task_done()

def create_app(paused=False):
    @asynccontextmanager
    async def lifespan(app):
        state = app.state
        state.queue = asyncio.Queue(maxsize=2)
        state.gate = asyncio.Event()
        state.jobs, state.active, state.closed = {}, 0, False
        if not paused:
            state.gate.set()
        tasks = [asyncio.create_task(worker(state)) for _ in range(2)]
        try:
            yield
        finally:
            for task in tasks:
                task.cancel()
            for task in tasks:
                with suppress(asyncio.CancelledError):
                    await task
            for job_id, status in state.jobs.items():
                if status == "queued":
                    state.jobs[job_id] = "cancelled"
            state.closed = True
    app = FastAPI(lifespan=lifespan)

    @app.post("/jobs", status_code=202)
    async def submit(request: Request):
        state = request.app.state
        job_id = len(state.jobs) + 1
        try:
            state.queue.put_nowait(job_id)
        except asyncio.QueueFull:
            raise HTTPException(429, "Queue full", headers={"Retry-After": "1"})
        state.jobs[job_id] = "queued"
        return {"id": job_id}

    @app.post("/fixture/release")
    async def release(request: Request):
        # Test-only control. Do not expose this route in a deployed service.
        request.app.state.gate.set()
        return {"released": True}

    @app.get("/status")
    async def status(request: Request):
        state = request.app.state
        return {"queued": state.queue.qsize(), "active": state.active, "jobs": state.jobs}
    return app

async def cancellation_test():
    from types import SimpleNamespace
    state = SimpleNamespace(gate=asyncio.Event(), queue=asyncio.Queue(2), active=0, jobs={1:"queued"})
    state.queue.put_nowait(1)
    state.gate.set()
    task = asyncio.create_task(worker(state))
    await asyncio.sleep(0)  # Worker reaches cooperative sleep with active=1.
    assert state.active == 1
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task
    assert state.active == 0 and state.jobs[1] == "cancelled"
    await asyncio.wait_for(state.queue.join(), timeout=1)

def self_test():
    app = create_app(paused=True)
    with TestClient(app) as client:  # Context manager enters and exits lifespan.
        assert client.post("/jobs").status_code == 202
        assert client.post("/jobs").status_code == 202
        overflow = client.post("/jobs")
        assert overflow.status_code == 429 and overflow.headers["retry-after"] == "1"
        assert client.get("/status").json()["queued"] == 2
        client.post("/fixture/release")
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            result = client.get("/status").json()
            assert result["active"] <= 2
            if list(result["jobs"].values()) == ["succeeded", "succeeded"]:
                break
            time.sleep(0.005)
        else:
            raise AssertionError("Fixture jobs did not finish")
    assert app.state.closed and app.state.active == 0
    asyncio.run(cancellation_test())
    print("PASS: bounded queue, rejection, lifecycle, cooperative cancellation")

if __name__ == "__main__":
    self_test()
