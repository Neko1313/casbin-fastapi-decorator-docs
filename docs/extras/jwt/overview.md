---
sidebar_position: 1
---

# JWT Overview

The `jwt` extra adds `JWTUserProvider` — a ready-made `user_provider` that extracts and validates JWT tokens from incoming requests.

## Install

```bash
pip install "casbin-fastapi-decorator[jwt]"
```

## Import

```python
from casbin_fastapi_decorator_jwt import JWTUserProvider
```

## What it does

`JWTUserProvider` is a FastAPI dependency that:

1. Extracts a JWT token from a **Bearer header** (`Authorization: Bearer <token>`) or a **cookie**
2. Decodes and validates the token using [PyJWT](https://pyjwt.readthedocs.io/)
3. Optionally validates the payload against a Pydantic model
4. Returns the user object (or raw payload dict) for the authorization guard

## Basic setup

```python
from casbin_fastapi_decorator_jwt import JWTUserProvider
from casbin_fastapi_decorator import PermissionGuard
from fastapi import HTTPException
import casbin

from pydantic import BaseModel

class User(BaseModel):
    role: str

user_provider = JWTUserProvider(
    secret_key="your-secret-key",
    algorithm="HS256",
    user_model=User,
)

guard = PermissionGuard(
    user_provider=user_provider,
    enforcer_provider=lambda: casbin.Enforcer("casbin/model.conf", "casbin/policy.csv"),
    error_factory=lambda *_: HTTPException(403, "Forbidden"),
)
```

## Constructor parameters

```python
JWTUserProvider(
    secret_key: str,
    algorithm: str = "HS256",
    user_model: type[BaseModel] | None = None,
    cookie_name: str | None = None,
    unauthorized_error: Callable[[], Exception] = ...,
    invalid_token_error: Callable[[str], Exception] = ...,
)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `secret_key` | `str` | required | Secret key for JWT validation |
| `algorithm` | `str` | `"HS256"` | JWT signing algorithm |
| `user_model` | `type[BaseModel] \| None` | `None` | Pydantic model to validate the payload |
| `cookie_name` | `str \| None` | `None` | Cookie name to extract token from (in addition to Bearer header) |
| `unauthorized_error` | `Callable` | `HTTPException(401)` | Factory for missing token errors |
| `invalid_token_error` | `Callable[[str], Exception]` | `HTTPException(401)` | Factory for invalid token errors |

## Token sources

By default, `JWTUserProvider` reads from the `Authorization: Bearer <token>` header.

To also support cookies, set `cookie_name`:

```python
user_provider = JWTUserProvider(
    secret_key="your-secret-key",
    algorithm="HS256",
    cookie_name="access_token",  # reads from cookie if header is absent
)
```

See [Bearer Token](./bearer-token) and [Cookie](./cookie) for detailed examples.

## User model

If `user_model` is set, the decoded JWT payload is validated with `user_model(**payload)`. The resulting Pydantic instance is returned as the user.

```python
class User(BaseModel):
    role: str
    sub: str

user_provider = JWTUserProvider(
    secret_key="secret",
    user_model=User,
)
# Returns User(role="admin", sub="user-123")
```

If `user_model` is `None`, the raw payload dictionary is returned.

## Generating tokens

`JWTUserProvider` only validates tokens. To generate them, use PyJWT directly:

```python
import jwt

token = jwt.encode({"role": "admin", "sub": "user-123"}, "your-secret-key", algorithm="HS256")
```
