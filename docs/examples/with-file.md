---
sidebar_position: 2
---

# File Hot-Reload Example

A focused example for `casbin-fastapi-decorator-file`. It keeps the same simple
Bearer-token auth as the [basic example](./basic), but adds a `/policy`
endpoint so you can verify file changes while the app is running.

## Install

```bash
pip install "casbin-fastapi-decorator[file]" uvicorn python-multipart
```

## Project structure

```text
my-app/
├── casbin/
│   ├── model.conf
│   └── policy.csv
├── auth.py
├── authz.py
├── model.py
└── main.py
```

## `casbin/model.conf`

Same as the [basic example](./basic#casbin-files).

## `casbin/policy.csv`

Same as the [basic example](./basic#casbin-files).

## `model.py`

Same as the [basic example](./basic#modelpy).

## `auth.py`

Same as the [basic example](./basic#authpy).

## `authz.py`

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from auth import get_current_user
from fastapi import FastAPI, HTTPException

from casbin_fastapi_decorator import PermissionGuard
from casbin_fastapi_decorator_file import CachedFileEnforcerProvider

enforcer_provider = CachedFileEnforcerProvider(
    model_path="casbin/model.conf",
    policy_path="casbin/policy.csv",
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    async with enforcer_provider:
        yield


guard = PermissionGuard(
    user_provider=get_current_user,
    enforcer_provider=enforcer_provider,
    error_factory=lambda *_: HTTPException(403, "Forbidden"),
)
```

## `main.py`

```python
from pathlib import Path
from typing import Annotated

from auth import get_current_user
from authz import guard, lifespan
from fastapi import Depends, FastAPI, Form
from model import Permission, PostCreateSchema, PostSchema, Resource, Role, UserSchema

app = FastAPI(title="Core + File Hot-Reload Example", lifespan=lifespan)

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

@app.get("/policy")
async def current_policy() -> dict:
    return {"policy": Path("casbin/policy.csv").read_text()}
```

## Running

```bash
uvicorn main:app --reload
```

## Hot-reload demo

Inspect the current policy:

```bash
curl http://localhost:8000/policy
```

Then edit `casbin/policy.csv` while the app is running:

```bash
cat > casbin/policy.csv <<'EOF'
p, admin, post, read
p, admin, post, write
p, admin, post, delete
p, editor, post, read
p, editor, post, write
EOF
```

The next request uses the updated policy without restarting the app:

```bash
curl -H "Authorization: Bearer viewer" http://localhost:8000/articles
# -> {"detail": "Forbidden"}
```
