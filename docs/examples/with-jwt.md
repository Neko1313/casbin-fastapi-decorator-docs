---
sidebar_position: 2
---

# JWT Example

A complete example using `casbin-fastapi-decorator` with the `jwt` extra. Replaces manual token parsing with `JWTUserProvider`.

## Install

```bash
pip install "casbin-fastapi-decorator[jwt]" uvicorn PyJWT
```

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

Same as the [basic example](./basic#casbin-files).

## `model.py`

Same as the [basic example](./basic#modelpy).

## `auth.py`

```python
from casbin_fastapi_decorator_jwt import JWTUserProvider
from model import UserSchema

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"

user_provider = JWTUserProvider(
    secret_key=SECRET_KEY,
    algorithm=ALGORITHM,
    user_model=UserSchema,
)
```

`JWTUserProvider` handles everything: extracting the Bearer token, decoding the JWT, and validating the payload into `UserSchema`.

## `authz.py`

```python
from auth import user_provider
from casbin import Enforcer
from fastapi import HTTPException

from casbin_fastapi_decorator import PermissionGuard

async def get_enforcer() -> Enforcer:
    return Enforcer("casbin/model.conf", "casbin/policy.csv")

guard = PermissionGuard(
    user_provider=user_provider,
    enforcer_provider=get_enforcer,
    error_factory=lambda *_: HTTPException(403, "Forbidden"),
)
```

## `main.py`

```python
import jwt as pyjwt
from typing import Annotated
from auth import ALGORITHM, SECRET_KEY, user_provider
from authz import guard
from fastapi import Depends, FastAPI, Form
from model import Permission, PostCreateSchema, PostSchema, Resource, Role, UserSchema

app = FastAPI(title="Core + JWT Example")

MOCK_DB = [
    PostSchema(id=1, title="First Post"),
    PostSchema(id=2, title="Second Post"),
]

@app.post("/login")
async def login(role: Role) -> str:
    """Generate a signed JWT token for the given role."""
    return pyjwt.encode({"role": role}, SECRET_KEY, algorithm=ALGORITHM)

@app.get("/me")
@guard.auth_required()
async def me(user: Annotated[UserSchema, Depends(user_provider)]) -> UserSchema:
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
uvicorn main:app --reload
```

## Testing

```bash
# Get a signed JWT for the editor role
TOKEN=$(curl -s -X POST "http://localhost:8000/login?role=editor" | tr -d '"')

# Get current user info
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/me
# → {"role": "editor"}

# List posts (allowed)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/articles
# → [...]

# Create post (allowed for editor)
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -F "title=New Post" http://localhost:8000/articles
# → {"id": 3, "title": "New Post"}

# Try with viewer role
VIEWER_TOKEN=$(curl -s -X POST "http://localhost:8000/login?role=viewer" | tr -d '"')
curl -X POST -H "Authorization: Bearer $VIEWER_TOKEN" \
  -F "title=New Post" http://localhost:8000/articles
# → {"detail": "Forbidden"}
```

## Key difference from basic example

The only change is in `auth.py` — instead of manually parsing the Bearer token, `JWTUserProvider` handles the full JWT lifecycle. The rest of the application (routes, guard, Casbin config) stays identical.
