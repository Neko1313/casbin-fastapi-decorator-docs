---
sidebar_position: 1
---

# PermissionGuard

`PermissionGuard` is the central class of the library. It acts as a factory that creates authorization decorators for your FastAPI routes.

## Import

```python
from casbin_fastapi_decorator import PermissionGuard
```

## Constructor

```python
PermissionGuard(
    *,
    user_provider: Callable[..., Any],
    enforcer_provider: Callable[..., Any],
    error_factory: Callable[..., Exception],
)
```

All three arguments are keyword-only.

### `user_provider`

A FastAPI dependency (a callable) that returns the current authenticated user. It is resolved via FastAPI's dependency injection system on every request.

The returned value becomes the first argument (`sub`) passed to `enforcer.enforce()`.

```python
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(HTTPBearer(auto_error=False))]
) -> User:
    if not credentials:
        raise HTTPException(401, "Unauthorized")
    return User(role=credentials.credentials)
```

### `enforcer_provider`

A FastAPI dependency that returns a configured `casbin.Enforcer` instance. It is
resolved on every request where permission checking is needed, but the provider
itself may return a cached enforcer.

```python
async def get_enforcer() -> casbin.Enforcer:
    return casbin.Enforcer("casbin/model.conf", "casbin/policy.csv")
```

For production use, prefer a provider that caches the enforcer instance instead
of recreating it on every request. See the [File extra](../extras/file/overview)
for `CachedFileEnforcerProvider` or the [Database extra](../extras/db/overview)
for `DatabaseEnforcerProvider`.

### `error_factory`

A callable that creates and returns an exception when authorization fails. It receives `(user, *rvals)` — the user object and all resolved permission arguments.

```python
# Simple: always return 403
error_factory=lambda *_: HTTPException(403, "Forbidden")

# Informative: include what was denied
error_factory=lambda user, obj, act: HTTPException(
    403, f"User '{user.role}' cannot '{act}' on '{obj}'"
)
```

The factory must **return** an exception, not raise it. The library raises it internally.

## Usage

Create a single guard instance and reuse it across your routes:

```python
guard = PermissionGuard(
    user_provider=get_current_user,
    enforcer_provider=get_enforcer,
    error_factory=lambda *_: HTTPException(403, "Forbidden"),
)
```

Then use the guard's decorator methods on your routes:

```python
@app.get("/posts")
@guard.require_permission("post", "read")
async def list_posts():
    ...
```

## Methods

### `auth_required()`

Returns a decorator that only checks authentication — it ensures the `user_provider` resolves successfully (doesn't raise), but does not call the enforcer.

See [auth_required](./auth-required) for details.

### `require_permission(*args)`

Returns a decorator that performs a full authorization check via the Casbin enforcer.

See [require_permission](./require-permission) for details.

## Multiple guards

You can create multiple `PermissionGuard` instances with different providers, for example to separate admin and user authorization:

```python
user_guard = PermissionGuard(
    user_provider=get_current_user,
    enforcer_provider=get_user_enforcer,
    error_factory=lambda *_: HTTPException(403, "Forbidden"),
)

admin_guard = PermissionGuard(
    user_provider=get_admin_user,
    enforcer_provider=get_admin_enforcer,
    error_factory=lambda *_: HTTPException(403, "Admin access required"),
)
```
