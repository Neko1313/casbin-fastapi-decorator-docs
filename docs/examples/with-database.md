---
sidebar_position: 3
---

# Database Example

A complete example using `casbin-fastapi-decorator` with the `db` extra. Policies are stored in a SQLite database and can be queried at runtime.

## Install

```bash
pip install "casbin-fastapi-decorator[db]" uvicorn aiosqlite
```

## Project structure

```
my-app/
├── casbin/
│   └── model.conf
├── auth.py
├── authz.py
├── db.py
├── model.py
└── main.py
```

No `policy.csv` needed — policies live in the database.

## `casbin/model.conf`

Same as the [basic example](./basic#casbin-files).

## `model.py`

```python
from enum import StrEnum
from pydantic import BaseModel

class UserSchema(BaseModel):
    role: str

class PostCreateSchema(BaseModel):
    title: str

class PostSchema(PostCreateSchema):
    id: int

class Permission(StrEnum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"

class Resource(StrEnum):
    POST = "post"

class Role(StrEnum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
```

## `db.py`

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from model import Permission, Resource, Role
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

engine = create_async_engine("sqlite+aiosqlite:///./example.db")
async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

class Policy(Base):
    __tablename__ = "policies"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sub: Mapped[str] = mapped_column(String(100))
    obj: Mapped[str] = mapped_column(String(100))
    act: Mapped[str] = mapped_column(String(100))

async def seed_policies() -> None:
    async with async_session() as session:
        result = await session.execute(select(Policy))
        if result.scalars().first() is not None:
            return
        session.add_all([
            Policy(sub=Role.ADMIN,   obj=Resource.POST, act=Permission.READ),
            Policy(sub=Role.ADMIN,   obj=Resource.POST, act=Permission.WRITE),
            Policy(sub=Role.ADMIN,   obj=Resource.POST, act=Permission.DELETE),
            Policy(sub=Role.EDITOR,  obj=Resource.POST, act=Permission.READ),
            Policy(sub=Role.EDITOR,  obj=Resource.POST, act=Permission.WRITE),
            Policy(sub=Role.VIEWER,  obj=Resource.POST, act=Permission.READ),
        ])
        await session.commit()

@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_policies()
    yield
    await engine.dispose()
```

## `auth.py`

```python
from typing import Annotated
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from model import UserSchema

async def get_current_user(
    header_auth: Annotated[
        HTTPAuthorizationCredentials | None,
        Security(HTTPBearer(auto_error=False))
    ],
) -> UserSchema:
    if not header_auth:
        raise HTTPException(401, "Unauthorized")
    return UserSchema(role=header_auth.credentials)
```

## `authz.py`

```python
from auth import get_current_user
from casbin_fastapi_decorator_db import DatabaseEnforcerProvider
from db import Policy, async_session
from fastapi import HTTPException

from casbin_fastapi_decorator import PermissionGuard

enforcer_provider = DatabaseEnforcerProvider(
    model_path="casbin/model.conf",
    session_factory=async_session,
    policy_model=Policy,
    policy_mapper=lambda p: (p.sub, p.obj, p.act),
)

guard = PermissionGuard(
    user_provider=get_current_user,
    enforcer_provider=enforcer_provider,
    error_factory=lambda *_: HTTPException(403, "Forbidden"),
)
```

## `main.py`

```python
from typing import Annotated
from auth import get_current_user
from authz import guard
from db import Policy, async_session, lifespan
from fastapi import Depends, FastAPI, Form
from model import Permission, PostCreateSchema, PostSchema, Resource, Role, UserSchema
from sqlalchemy import select

app = FastAPI(title="Core + DB Example", lifespan=lifespan)

MOCK_DB = [
    PostSchema(id=1, title="First Post"),
    PostSchema(id=2, title="Second Post"),
]

@app.post("/login")
async def login(role: Role) -> str:
    return role

@app.get("/me")
@guard.auth_required()
async def me(user: Annotated[UserSchema, Depends(get_current_user)]) -> UserSchema:
    return user

@app.get("/articles")
@guard.require_permission(Resource.POST, Permission.READ)
async def list_posts() -> list[PostSchema]:
    return MOCK_DB

@app.post("/articles")
@guard.require_permission(Resource.POST, Permission.WRITE)
async def create_post(data: Annotated[PostCreateSchema, Form]) -> PostSchema:
    pk = sorted(MOCK_DB, key=lambda p: p.id)[-1].id + 1
    post = PostSchema(id=pk, title=data.title)
    MOCK_DB.append(post)
    return post

@app.delete("/articles/{post_id}")
@guard.require_permission(Resource.POST, Permission.DELETE)
async def delete_post(post_id: int) -> dict:
    return {"id": post_id, "deleted": True}

@app.get("/policies")
async def list_policies() -> list[dict]:
    """Inspect current policies from the database."""
    async with async_session() as session:
        result = await session.execute(select(Policy))
        policies = result.scalars().all()
    return [{"sub": p.sub, "obj": p.obj, "act": p.act} for p in policies]
```

## Running

```bash
uvicorn main:app --reload
```

## Testing

```bash
# View current policies
curl http://localhost:8000/policies

# Login as admin
curl -H "Authorization: Bearer admin" http://localhost:8000/articles

# Delete (only admin has this permission)
curl -X DELETE -H "Authorization: Bearer admin" http://localhost:8000/articles/1

# Viewer cannot delete
curl -X DELETE -H "Authorization: Bearer viewer" http://localhost:8000/articles/1
# → {"detail": "Forbidden"}
```
