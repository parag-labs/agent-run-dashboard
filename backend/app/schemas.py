"""Request/response shapes for the API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Credentials(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RunCreate(BaseModel):
    name: str
    model: str
    status: str = "success"
    tokens: int = 0
    cost: float = 0.0
    latency_ms: float = 0.0


class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    model: str
    status: str
    tokens: int
    cost: float
    latency_ms: float


class Stats(BaseModel):
    runs: int
    total_tokens: int
    total_cost: float
    by_status: dict[str, int]
    by_model: dict[str, int]
