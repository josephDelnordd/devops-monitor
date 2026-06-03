import asyncio
import httpx
from typing import Dict
from api.models import Server


async def poll_server(server_id: str, url: str, store: Dict[str, Server]) -> None:
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(f"{url}/health")
            store[server_id].status = "UP" if resp.status_code == 200 else "DEGRADED"
    except Exception:
        store[server_id].status = "DOWN"


async def run_poll_loop(store: Dict[str, Server], interval: int = 10) -> None:
    while True:
        tasks = [
            poll_server(s.id, s.base_url(), store)
            for s in store.values()
        ]
        if tasks:
            await asyncio.gather(*tasks)
        await asyncio.sleep(interval)
