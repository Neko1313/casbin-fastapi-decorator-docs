---
sidebar_position: 2
---

# SQLAlchemy Adapter

A detailed guide on configuring the SQLAlchemy integration for `DatabaseEnforcerProvider`.

## Supported databases

Any database supported by SQLAlchemy with an async driver works:

| Database | Driver | Connection string |
|---|---|---|
| PostgreSQL | `asyncpg` | `postgresql+asyncpg://user:pass@host/db` |
| MySQL | `aiomysql` | `mysql+aiomysql://user:pass@host/db` |
| SQLite | `aiosqlite` | `sqlite+aiosqlite:///./app.db` |

## Engine and session factory

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Create the engine
engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost/mydb",
    echo=False,           # set True for SQL logging
    pool_size=10,
    max_overflow=20,
)

# Create the session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
```

## Policy model

The policy model can have any shape — `DatabaseEnforcerProvider` uses your `policy_mapper` to convert rows, so you control the mapping:

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Policy(Base):
    __tablename__ = "casbin_policies"

    id: Mapped[int] = mapped_column(primary_key=True)
    sub: Mapped[str] = mapped_column(String(100), index=True)
    obj: Mapped[str] = mapped_column(String(100), index=True)
    act: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(default=True)
```

## Custom policy mapper

The `policy_mapper` receives each row and must return a tuple of strings matching your Casbin model's `[policy_definition]`:

```python
# Standard RBAC: (sub, obj, act)
policy_mapper=lambda p: (p.sub, p.obj, p.act)

# Only include active policies
# (filter in query or in mapper)
policy_mapper=lambda p: (p.subject, p.resource, p.permission)

# 4-field model: (sub, dom, obj, act)
policy_mapper=lambda p: (p.sub, p.domain, p.obj, p.act)
```

## Database initialization

Use FastAPI's `lifespan` to create tables and seed initial data:

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed initial policies
    await seed_policies()

    yield

    await engine.dispose()


async def seed_policies() -> None:
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(Policy))
        if result.scalars().first() is not None:
            return  # already seeded

        session.add_all([
            Policy(sub="admin", obj="post", act="read"),
            Policy(sub="admin", obj="post", act="write"),
            Policy(sub="admin", obj="post", act="delete"),
            Policy(sub="editor", obj="post", act="read"),
            Policy(sub="editor", obj="post", act="write"),
            Policy(sub="viewer", obj="post", act="read"),
        ])
        await session.commit()


app = FastAPI(lifespan=lifespan)
```

## Lifespan integration for hot-reload

Use the provider as an async context manager so it can start the `model.conf`
watcher and the background polling task:

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI

enforcer_provider = DatabaseEnforcerProvider(
    model_path="casbin/model.conf",
    session_factory=async_session,
    policy_model=Policy,
    policy_mapper=lambda p: (p.sub, p.obj, p.act),
)

@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    async with enforcer_provider:
        yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
```

Without `async with enforcer_provider`, the enforcer is still cached, but the
provider will not watch the model file or poll the database for changes.

## Managing policies at runtime

Since policies live in the database, you can add a management API:

```python
from pydantic import BaseModel

class PolicyCreate(BaseModel):
    sub: str
    obj: str
    act: str

@app.post("/admin/policies")
async def add_policy(data: PolicyCreate) -> dict:
    async with async_session() as session:
        policy = Policy(sub=data.sub, obj=data.obj, act=data.act)
        session.add(policy)
        await session.commit()
    return {"created": True}

@app.delete("/admin/policies")
async def remove_policy(sub: str, obj: str, act: str) -> dict:
    from sqlalchemy import delete
    async with async_session() as session:
        await session.execute(
            delete(Policy).where(
                Policy.sub == sub,
                Policy.obj == obj,
                Policy.act == act,
            )
        )
        await session.commit()
    return {"deleted": True}
```

:::note
Policy changes take effect after the next polling cycle (`poll_interval`,
default `30.0` seconds) and are then visible on the next request.
:::
