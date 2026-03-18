---
sidebar_position: 2
---

# Quick Start

A complete working example in under 5 minutes.

## 1. Install

```bash
pip install "casbin-fastapi-decorator[file]" uvicorn
```

## 2. Create the Casbin model

Create `casbin/model.conf`:

```ini
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = r.obj == p.obj && r.sub.role == p.sub && r.act == p.act
```

## 3. Create the policy file

Create `casbin/policy.csv`:

```csv
p, viewer, post, read
p, editor, post, read
p, editor, post, write
p, admin, post, read
p, admin, post, write
p, admin, post, delete
```

## 4. Create the app

```python
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from casbin_fastapi_decorator import PermissionGuard
from casbin_fastapi_decorator_file import CachedFileEnforcerProvider

bearer = HTTPBearer(auto_error=False)


# --- User model ---

class User(BaseModel):
    role: str


# --- Providers ---

async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Security(bearer),
    ],
) -> User:
    if not credentials:
        raise HTTPException(401, "Unauthorized")
    return User(role=credentials.credentials)


enforcer_provider = CachedFileEnforcerProvider(
    model_path="casbin/model.conf",
    policy_path="casbin/policy.csv",
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with enforcer_provider:
        yield


# --- Guard ---

guard = PermissionGuard(
    user_provider=get_current_user,
    enforcer_provider=enforcer_provider,
    error_factory=lambda *_: HTTPException(403, "Forbidden"),
)

app = FastAPI(lifespan=lifespan)


# --- Routes ---

@app.get("/me")
@guard.auth_required()
async def me(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user


@app.get("/posts")
@guard.require_permission("post", "read")
async def list_posts() -> list[dict]:
    return [{"id": 1, "title": "Hello World"}]


@app.post("/posts")
@guard.require_permission("post", "write")
async def create_post() -> dict:
    return {"id": 2, "title": "New Post"}
```

## 5. Test it

```bash
uvicorn main:app --reload
```

Send a request as `viewer` (can read but not write):

```bash
# This works
curl -H "Authorization: Bearer viewer" http://localhost:8000/posts

# This returns 403
curl -X POST -H "Authorization: Bearer viewer" http://localhost:8000/posts
```

Send as `editor` (can read and write):

```bash
# Both work
curl -H "Authorization: Bearer editor" http://localhost:8000/posts
curl -X POST -H "Authorization: Bearer editor" http://localhost:8000/posts
```

## What's happening

1. The request arrives at `GET /posts`
2. `guard.require_permission("post", "read")` intercepts it
3. `get_current_user` resolves the user from the Bearer token — returns `User(role="viewer")`
4. `CachedFileEnforcerProvider` returns the cached enforcer loaded from `model.conf` and `policy.csv`
5. The matcher checks `user.role == p.sub`, so `enforce(user, "post", "read")` returns `True`
6. The route handler runs and returns the posts

If you edit `casbin/policy.csv` while the app is running, the next request will
pick up the change automatically.

## Next steps

- [PermissionGuard](../core/permission-guard) — learn all configuration options
- [AccessSubject](../core/access-subject) — dynamic permissions based on request data
- [File extra](../extras/file/overview) — cached file-based enforcer with hot-reload
- [JWT extra](../extras/jwt/overview) — replace manual token parsing with `JWTUserProvider`
