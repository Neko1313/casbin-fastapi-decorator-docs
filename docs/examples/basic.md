---
sidebar_position: 1
---

# Basic Example

A complete example using only the core package — no extras. Demonstrates `PermissionGuard`, `auth_required`, and `require_permission` with a simple role-based Bearer token.

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

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act
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
from auth import get_current_user
from casbin import Enforcer
from fastapi import HTTPException

from casbin_fastapi_decorator import PermissionGuard

async def get_enforcer() -> Enforcer:
    return Enforcer("casbin/model.conf", "casbin/policy.csv")

guard = PermissionGuard(
    user_provider=get_current_user,
    enforcer_provider=get_enforcer,
    error_factory=lambda *_: HTTPException(403, "Forbidden"),
)
```

## `main.py`

```python
from typing import Annotated
from auth import get_current_user
from authz import guard
from fastapi import Depends, FastAPI, Form
from model import Permission, PostCreateSchema, PostSchema, Resource, Role, UserSchema

app = FastAPI(title="Core Example")

MOCK_DB = [
    PostSchema(id=1, title="First Post"),
    PostSchema(id=2, title="Second Post"),
]

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
pip install casbin-fastapi-decorator uvicorn
uvicorn main:app --reload
```

## Testing

```bash
# Login as viewer
curl -X POST "http://localhost:8000/login?role=viewer"
# → "viewer"

# List posts (allowed for viewer)
curl -H "Authorization: Bearer viewer" http://localhost:8000/articles
# → [{"id": 1, "title": "First Post"}, ...]

# Create post (denied for viewer)
curl -X POST -H "Authorization: Bearer viewer" \
  -F "title=New Post" http://localhost:8000/articles
# → {"detail": "Forbidden"}

# Create post (allowed for editor)
curl -X POST -H "Authorization: Bearer editor" \
  -F "title=New Post" http://localhost:8000/articles
# → {"id": 3, "title": "New Post"}
```
