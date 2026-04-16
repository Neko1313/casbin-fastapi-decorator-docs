---
sidebar_position: 1
---

# Basic Example

A minimal example with manual Bearer authentication and file-based policies via
`CachedFileEnforcerProvider`.

## Project structure

```
my-app/
├── casbin/
│   ├── model.conf
│   └── policy.csv
├── auth.py
├── authz.py
├── model.py
└── main.py
```

## Casbin files

**`casbin/model.conf`**

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

**`casbin/policy.csv`**

```csv
p, viewer, post, read
p, editor, post, read
p, editor, post, write
p, admin, post, read
p, admin, post, write
p, admin, post, delete
```

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

class Resource(StrEnum):
    POST = "post"

class Role(StrEnum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
```

## `auth.py`

```python
from typing import Annotated
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from model import UserSchema

HEADER_AUTH_SCHEME = HTTPBearer(auto_error=False)

async def get_current_user(
    header_auth: Annotated[
        HTTPAuthorizationCredentials | None, Security(HEADER_AUTH_SCHEME)
    ],
) -> UserSchema:
    if not header_auth:
        raise HTTPException(401, "Unauthorized")
    return UserSchema(role=header_auth.credentials)
```

In this example the token is simply the role string (`viewer`, `editor`, `admin`). In a real app you would validate a proper JWT here.

## `authz.py`

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

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
from typing import Annotated, Any
from auth import get_current_user
from authz import guard, lifespan
from fastapi import Depends, FastAPI, Form, HTTPException
from model import Permission, PostCreateSchema, PostSchema, Resource, Role, UserSchema

app = FastAPI(title="Core Example", lifespan=lifespan)

MOCK_DB = [
    PostSchema(id=1, title="First Post"),
    PostSchema(id=2, title="Second Post"),
]


def draft_not_found_error(user: Any, *resolved_args: Any) -> HTTPException:
    """Custom error for draft access — return 404 instead of 403."""
    return HTTPException(status_code=404, detail="Article not found")


@app.post("/login")
async def login(role: Role) -> str:
    """Return the role as a plain-text token."""
    return role

@app.get("/me")
@guard.auth_required()
async def me(user: Annotated[UserSchema, Depends(get_current_user)]) -> UserSchema:
    return user

@app.get("/articles")
@guard.require_permission(Resource.POST, Permission.READ)
async def list_posts() -> list[PostSchema]:
    return MOCK_DB

@app.get("/articles/draft")
@guard.require_permission(
    Resource.POST,
    Permission.WRITE,
    error_factory=draft_not_found_error,
)
async def read_draft() -> dict[str, str]:
    """Requires write permission. Returns 404 on denial (route-level error_factory)."""
    return {"title": "Draft Post"}

@app.post("/articles")
@guard.require_permission(Resource.POST, Permission.WRITE)
async def create_post(data: Annotated[PostCreateSchema, Form]) -> PostSchema:
    pk = sorted(MOCK_DB, key=lambda p: p.id)[-1].id + 1
    post = PostSchema(id=pk, title=data.title)
    MOCK_DB.append(post)
    return post
```

## Running

```bash
pip install "casbin-fastapi-decorator[file]" uvicorn python-multipart
uvicorn main:app --reload
```

## Testing

```bash
# Login as admin (has write permission)
TOKEN=$(curl -s -X POST "http://localhost:8000/login?role=admin")
# → "admin"

# List posts (allowed for admin)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/articles
# → [{"id": 1, "title": "First Post"}, ...]

# Access draft (allowed for admin, custom error_factory)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/articles/draft
# → {"title": "Draft Post"}

# Create post (allowed for admin)
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -F "title=New Post" http://localhost:8000/articles
# → {"id": 3, "title": "New Post"}

# Login as viewer (has read-only permission)
TOKEN_VIEW=$(curl -s -X POST "http://localhost:8000/login?role=viewer")

# List posts (allowed for viewer)
curl -H "Authorization: Bearer $TOKEN_VIEW" http://localhost:8000/articles
# → [{"id": 1, "title": "First Post"}, ...]

# Access draft (denied for viewer — returns 404 due to custom error_factory)
curl -H "Authorization: Bearer $TOKEN_VIEW" http://localhost:8000/articles/draft
# → {"detail": "Article not found"}  (404 status)

# Create post (denied for viewer — returns default 403)
curl -X POST -H "Authorization: Bearer $TOKEN_VIEW" \
  -F "title=New Post" http://localhost:8000/articles
# → {"detail": "Forbidden"}  (403 status)
```
