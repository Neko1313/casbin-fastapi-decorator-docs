---
sidebar_position: 2
---

# Bearer Token

The default extraction method for `JWTUserProvider` is the `Authorization: Bearer <token>` HTTP header.

## Setup

```python
from casbin_fastapi_decorator_jwt import JWTUserProvider
from pydantic import BaseModel

class User(BaseModel):
    role: str

user_provider = JWTUserProvider(
    secret_key="your-secret-key",
    algorithm="HS256",
    user_model=User,
)
```

No extra configuration needed — Bearer header extraction is on by default.

## Full example

```python
import jwt
import casbin
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException

from casbin_fastapi_decorator import PermissionGuard
from casbin_fastapi_decorator_jwt import JWTUserProvider
from pydantic import BaseModel

app = FastAPI()

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

class User(BaseModel):
    role: str

user_provider = JWTUserProvider(
    secret_key=SECRET_KEY,
    algorithm=ALGORITHM,
    user_model=User,
)

async def get_enforcer() -> casbin.Enforcer:
    return casbin.Enforcer("casbin/model.conf", "casbin/policy.csv")

guard = PermissionGuard(
    user_provider=user_provider,
    enforcer_provider=get_enforcer,
    error_factory=lambda *_: HTTPException(403, "Forbidden"),
)


@app.post("/login")
async def login(role: str) -> str:
    """Generate a JWT token."""
    return jwt.encode({"role": role}, SECRET_KEY, algorithm=ALGORITHM)


@app.get("/me")
@guard.auth_required()
async def me(user: Annotated[User, Depends(user_provider)]) -> User:
    return user


@app.get("/posts")
@guard.require_permission("post", "read")
async def list_posts() -> list[dict]:
    return [{"id": 1, "title": "Hello"}]
```

## Testing

```bash
# Get a token
TOKEN=$(curl -s -X POST "http://localhost:8000/login?role=editor" | tr -d '"')

# Use it
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/posts
```

## Error responses

| Situation | Status | Detail |
|---|---|---|
| No `Authorization` header | 401 | `Not authenticated` |
| Invalid or expired token | 401 | `Invalid token: <reason>` |
| Insufficient permissions | 403 | `Forbidden` (from your `error_factory`) |
