---
sidebar_position: 2
---

# auth_required

`guard.auth_required()` returns a decorator that enforces **authentication only** — it ensures a user is present, but does not check any permissions via the Casbin enforcer.

## Usage

```python
@app.get("/me")
@guard.auth_required()
async def me(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user
```

## How it works

The decorator wraps the route with a `Depends(user_provider)` call. If `user_provider` raises an exception (e.g., `HTTPException(401)`), the request is rejected. If it resolves successfully, the request proceeds.

The Casbin enforcer is **not called** — this is purely an existence check for the user.

## When to use it

Use `auth_required` for routes that require a logged-in user but don't need fine-grained permission control:

```python
@app.get("/me")
@guard.auth_required()
async def get_profile(...):
    ...

@app.get("/settings")
@guard.auth_required()
async def get_settings(...):
    ...
```

For routes that require specific permissions, use [`require_permission`](./require-permission) instead.

## Accessing the user inside the route

`auth_required` does not inject the user into the route. If you need the user object inside the handler, add it as a regular `Depends`:

```python
from typing import Annotated
from fastapi import Depends

@app.get("/me")
@guard.auth_required()
async def me(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user
```

The `user_provider` will be called once by the guard (for auth check) and once by `Depends` (for injection). FastAPI's dependency caching ensures the actual resolution only happens once per request.
