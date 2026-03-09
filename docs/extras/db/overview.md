---
sidebar_position: 1
---

# Database Overview

The `db` extra adds `DatabaseEnforcerProvider` — a ready-made `enforcer_provider` that loads Casbin policies from a SQLAlchemy async database instead of a static `.csv` file.

## Install

```bash
pip install "casbin-fastapi-decorator[db]"
```

## Import

```python
from casbin_fastapi_decorator_db import DatabaseEnforcerProvider
```

## Why use it?

With a static `policy.csv` file, changing permissions requires a file update and application restart. Storing policies in a database allows you to:

- Update permissions at runtime without restarting
- Manage policies via an admin API or UI
- Use standard database tooling (migrations, auditing, backups)

## How it works

`DatabaseEnforcerProvider` is a callable (a FastAPI dependency) that:

1. Opens an async SQLAlchemy session
2. Queries all rows from your policy table
3. Converts each row to a `(sub, obj, act)` tuple using your `policy_mapper`
4. Creates a `casbin.Enforcer` instance and loads the policies into it
5. Returns the enforcer

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

## Constructor parameters

```python
DatabaseEnforcerProvider(
    model_path: str,
    session_factory: async_sessionmaker,
    policy_model: type,
    policy_mapper: Callable[[Any], tuple[str, ...]],
    default_policies: list[tuple[str, ...]] | None = None,
)
```

| Parameter | Type | Description |
|---|---|---|
| `model_path` | `str` | Path to the Casbin model `.conf` file |
| `session_factory` | `async_sessionmaker` | SQLAlchemy async session factory |
| `policy_model` | `type` | SQLAlchemy model class for policy rows |
| `policy_mapper` | `Callable` | Converts a row to a `(sub, obj, act)` tuple |
| `default_policies` | `list \| None` | Fallback policies if the database is empty |

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

## Full example

See the [Database Example](../../examples/with-database) for a complete working application with SQLite, policy seeding, and a `/policies` endpoint.
