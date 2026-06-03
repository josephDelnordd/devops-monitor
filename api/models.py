from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from typing import Optional
from uuid import uuid4


@dataclass
class Server:
    id: str
    name: str
    host: str
    port: int
    status: str = field(default="unknown")

    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


class ServerIn(BaseModel):
    name: str
    host: str
    port: int = Field(..., ge=1, le=65535)


class ServerOut(ServerIn):
    id: str
    status: str
