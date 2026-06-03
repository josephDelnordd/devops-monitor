import asyncio
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, Optional
from uuid import uuid4

from api.models import Server, ServerIn, ServerOut
from api.metrics import get_system_metrics
from api.auth import verify_api_key
from api.poller import run_poll_loop, poll_server

app = FastAPI()
servers: Dict[str, Server] = {}
poller_task: Optional[asyncio.Task] = None


@app.on_event("startup")
async def startup():
    global poller_task
    poller_task = asyncio.create_task(run_poll_loop(servers))


@app.on_event("shutdown")
async def shutdown():
    if poller_task:
        poller_task.cancel()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    return get_system_metrics()


@app.websocket("/ws/metrics")
async def ws_metrics(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            await ws.send_json(get_system_metrics())
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass


@app.post("/servers", response_model=ServerOut, status_code=201, dependencies=[Depends(verify_api_key)])
async def create_server(server: ServerIn):
    server_id = str(uuid4())
    srv = Server(id=server_id, **server.dict())
    servers[server_id] = srv
    return ServerOut(**srv.__dict__)


@app.get("/servers")
async def list_servers(status: Optional[str] = None):
    result = servers.values()
    if status:
        result = filter(lambda s: s.status == status, result)
    return list(result)


@app.get("/servers/{server_id}")
async def get_server(server_id: str):
    if server_id not in servers:
        raise HTTPException(404)
    return servers[server_id]


@app.delete("/servers/{server_id}", dependencies=[Depends(verify_api_key)])
async def delete_server(server_id: str):
    if server_id not in servers:
        raise HTTPException(404)
    del servers[server_id]
    return {"deleted": server_id}


@app.post("/servers/{server_id}/check")
async def check_server(server_id: str):
    if server_id not in servers:
        raise HTTPException(404)
    await poll_server(server_id, servers[server_id].base_url(), servers)
    return servers[server_id]