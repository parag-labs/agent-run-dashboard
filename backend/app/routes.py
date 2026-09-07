"""API routes: auth (register/login), run CRUD, and aggregate stats.

Every /runs and /stats endpoint is scoped to the authenticated user - a user only
ever sees and mutates their own runs, enforced by filtering on owner_id.
"""

from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from .auth import create_token, decode_token, hash_password, verify_password
from .db import get_session
from .models import Run, User
from .schemas import Credentials, RunCreate, RunOut, Stats, Token

router = APIRouter(prefix="/api")
_bearer = HTTPBearer(auto_error=False)


def current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: Session = Depends(get_session),
) -> User:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing bearer token")
    username = decode_token(creds.credentials)
    if username is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid or expired token")
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "unknown user")
    return user


@router.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(body: Credentials, session: Session = Depends(get_session)) -> Token:
    if not body.username or not body.password:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "username and password are required")
    existing = session.exec(select(User).where(User.username == body.username)).first()
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "username already taken")
    user = User(username=body.username, password_hash=hash_password(body.password))
    session.add(user)
    session.commit()
    return Token(access_token=create_token(user.username))


@router.post("/auth/login", response_model=Token)
def login(body: Credentials, session: Session = Depends(get_session)) -> Token:
    user = session.exec(select(User).where(User.username == body.username)).first()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "bad credentials")
    return Token(access_token=create_token(user.username))


@router.get("/runs", response_model=list[RunOut])
def list_runs(user: User = Depends(current_user), session: Session = Depends(get_session)) -> list[Run]:
    return list(
        session.exec(select(Run).where(Run.owner_id == user.id).order_by(Run.id.desc())).all()
    )


@router.post("/runs", response_model=RunOut, status_code=status.HTTP_201_CREATED)
def create_run(
    body: RunCreate, user: User = Depends(current_user), session: Session = Depends(get_session)
) -> Run:
    run = Run(owner_id=user.id, **body.model_dump())
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


@router.delete("/runs/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_run(
    run_id: int, user: User = Depends(current_user), session: Session = Depends(get_session)
) -> None:
    run = session.get(Run, run_id)
    if run is None or run.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "run not found")
    session.delete(run)
    session.commit()


@router.get("/stats", response_model=Stats)
def stats(user: User = Depends(current_user), session: Session = Depends(get_session)) -> Stats:
    runs = list(session.exec(select(Run).where(Run.owner_id == user.id)).all())
    return Stats(
        runs=len(runs),
        total_tokens=sum(r.tokens for r in runs),
        total_cost=round(sum(r.cost for r in runs), 6),
        by_status=dict(Counter(r.status for r in runs)),
        by_model=dict(Counter(r.model for r in runs)),
    )
