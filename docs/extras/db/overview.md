---
sidebar_position: 1
---

# Database Overview

The `db` extra adds `DatabaseEnforcerProvider` - a ready-made
`enforcer_provider` that loads Casbin policies from a SQLAlchemy async
database, caches the enforcer, and hot-reloads when data changes.

## Install

```bash
pip install "casbin-fastapi-decorator[db]"
```

## Import

```python
from casbin_fastapi_decorator_db import DatabaseEnforcerProvider
```

## Why use it?

Compared to a static `policy.csv`, storing policies in a database lets you:

- Update permissions at runtime without rebuilding the enforcer on every request
- Manage policies via an admin API or UI
- Use standard database tooling (migrations, auditing, backups)
- Keep a cached enforcer in memory while still reacting to policy changes

## How it works

`DatabaseEnforcerProvider` is a callable (a FastAPI dependency) that:

1. Loads and caches a `casbin.Enforcer` on first use
2. Reads policy rows from your database and maps them with `policy_mapper`
3. Watches `model.conf` for changes when used inside `async with provider`
4. Polls the database every `poll_interval` seconds and compares a SHA-256 hash
5. Reloads the cached enforcer automatically when the model file or DB rows change

## Setup

### 1. Define the policy model

Create a SQLAlchemy model that represents a Casbin policy rule:

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String

class Base(DeclarativeBase):
    pass

class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sub: Mapped[str] = mapped_column(String(100))  # subject (role)
    obj: Mapped[str] = mapped_column(String(100))  # object (resource)
    act: Mapped[str] = mapped_column(String(100))  # action
```

### 2. Create the session factory

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

### 3. Create the provider

```python
from casbin_fastapi_decorator_db import DatabaseEnforcerProvider

enforcer_provider = DatabaseEnforcerProvider(
    model_path="casbin/model.conf",
    session_factory=async_session,
    policy_model=Policy,
    policy_mapper=lambda p: (p.sub, p.obj, p.act),
)
```

### 4. Wire it into the guard

```python
from casbin_fastapi_decorator import PermissionGuard
from fastapi import HTTPException

guard = PermissionGuard(
    user_provider=get_current_user,
    enforcer_provider=enforcer_provider,
    error_factory=lambda *_: HTTPException(403, "Forbidden"),
)
```

### 5. Start hot-reload in FastAPI lifespan

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    async with enforcer_provider:
        yield

app = FastAPI(lifespan=lifespan)
```

Without the context manager the provider still caches the enforcer, but it will
not watch `model.conf` or poll the database for changes.

## Constructor parameters

```python
DatabaseEnforcerProvider(
    model_path: str,
    session_factory: Callable[..., AsyncSession],
    policy_model: type,
    policy_mapper: Callable[[Any], tuple[str, ...]],
    default_policies: list[tuple[str, ...]] | None = None,
    poll_interval: float = 30.0,
)
```

| Parameter | Type | Description |
|---|---|---|
| `model_path` | `str` | Path to the Casbin model `.conf` file |
| `session_factory` | `Callable[..., AsyncSession]` | SQLAlchemy async session factory |
| `policy_model` | `type` | SQLAlchemy model class for policy rows |
| `policy_mapper` | `Callable` | Converts a row to a `(sub, obj, act)` tuple |
| `default_policies` | `list \| None` | Fallback policies if the database is empty |
| `poll_interval` | `float` | Seconds between database hash checks (default: `30.0`) |

## Default policies

Use `default_policies` as a safety net when the database is empty (e.g., on first startup):

```python
enforcer_provider = DatabaseEnforcerProvider(
    model_path="casbin/model.conf",
    session_factory=async_session,
    policy_model=Policy,
    policy_mapper=lambda p: (p.sub, p.obj, p.act),
    default_policies=[
        ("admin", "post", "read"),
        ("admin", "post", "write"),
        ("admin", "post", "delete"),
    ],
)
```

## Reload behavior

- `model.conf` changes are detected via `watchdog`
- database changes are detected by hashing all mapped policy tuples every `poll_interval`
- once a change is detected, the provider rebuilds the cached enforcer in the background
- the next request receives the updated enforcer without restarting the app

## Full example

See the [Database Example](../../examples/with-database) for a complete working application with SQLite, policy seeding, and a `/policies` endpoint.
