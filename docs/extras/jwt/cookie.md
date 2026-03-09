---
sidebar_position: 3
---

# Cookie

`JWTUserProvider` can also extract tokens from cookies. This is useful for browser-based applications where tokens are stored in HTTP-only cookies.

## Setup

Pass `cookie_name` to enable cookie extraction:

```python
from casbin_fastapi_decorator_jwt import JWTUserProvider
from pydantic import BaseModel

class User(BaseModel):
    role: str

user_provider = JWTUserProvider(
    secret_key="your-secret-key",
    algorithm="HS256",
    user_model=User,
    cookie_name="access_token",  # reads from this cookie
)
```

## Behavior

When `cookie_name` is set, the provider checks both the Bearer header and the cookie. The exact priority depends on the provider's implementation — typically the header takes precedence if both are present.

## Full example

```python
import jwt
import casbin
from fastapi import FastAPI, HTTPException, Response
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
    cookie_name="access_token",
)

async def get_enforcer() -> casbin.Enforcer:
    return casbin.Enforcer("casbin/model.conf", "casbin/policy.csv")

guard = PermissionGuard(
    user_provider=user_provider,
    enforcer_provider=get_enforcer,
    error_factory=lambda *_: HTTPException(403, "Forbidden"),
)


@app.post("/login")
async def login(role: str, response: Response) -> dict:
    """Generate a JWT token and set it as a cookie."""
    token = jwt.encode({"role": role}, SECRET_KEY, algorithm=ALGORITHM)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="strict",
    )
    return {"message": "Logged in"}


@app.get("/posts")
@guard.require_permission("post", "read")
async def list_posts() -> list[dict]:
    return [{"id": 1, "title": "Hello"}]
```

## Testing with cookies

```bash
# Login and save cookies
curl -c cookies.txt -X POST "http://localhost:8000/login?role=editor"

# Use the cookie
curl -b cookies.txt http://localhost:8000/posts
```

## Security recommendations

- Always use `httponly=True` to prevent JavaScript access
- Use `samesite="strict"` or `samesite="lax"` to mitigate CSRF
- Use `secure=True` in production (requires HTTPS)

```python
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,
    secure=True,        # HTTPS only
    samesite="strict",
    max_age=3600,       # 1 hour
)
```
