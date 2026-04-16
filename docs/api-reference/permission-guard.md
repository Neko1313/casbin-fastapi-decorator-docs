---
sidebar_position: 1
---

# PermissionGuard API

Complete API reference for the `PermissionGuard` class.

## Class

```python
class PermissionGuard:
    def __init__(
        self,
        *,
        user_provider: Callable[..., Any],
        enforcer_provider: Callable[..., Any],
        error_factory: Callable[..., Exception],
    ) -> None: ...

    def auth_required(self) -> Callable: ...

    def require_permission(self, *args: AccessSubject | Any) -> Callable: ...
```

## Constructor

### Parameters

All parameters are keyword-only.

---

#### `user_provider`

**Type:** `Callable[..., Any]`
**Required:** Yes

A FastAPI dependency that returns the current user. The returned value is:
- Used as the first argument to `enforcer.enforce(user, ...)`
- Passed to `error_factory(user, ...)` when authorization fails

If the callable raises an exception, the request is rejected at that point (before enforcement).

---

#### `enforcer_provider`

**Type:** `Callable[..., Any]`
**Required:** Yes

A FastAPI dependency that returns a `casbin.Enforcer` instance. The enforcer must implement `.enforce(*args)` which returns `bool` or an awaitable resolving to `bool`.

Both synchronous and asynchronous enforcers are supported.

---

#### `error_factory`

**Type:** `Callable[..., Exception]`
**Required:** Yes

A callable that **returns** (not raises) an exception when `enforcer.enforce()` returns `False`.

**Signature:** `(user: Any, *resolved_args: Any) -> Exception`

- `user` — the value returned by `user_provider`
- `*resolved_args` — the resolved values passed to the enforcer (after `AccessSubject` resolution)

```python
# Minimal
error_factory=lambda *_: HTTPException(403, "Forbidden")

# With context
error_factory=lambda user, obj, act: HTTPException(
    403,
    detail={"message": "Forbidden", "user": str(user), "resource": obj, "action": act}
)
```

## Methods

### `auth_required()`

```python
def auth_required(self) -> Callable
```

Returns a decorator that ensures the user is authenticated. Only calls `user_provider` — the enforcer is not used.

**Returns:** A decorator function to be applied to a FastAPI route.

**Raises:** Whatever `user_provider` raises (e.g., `HTTPException(401)`).

---

### `require_permission(*args, error_factory=None)`

```python
def require_permission(
    self,
    *args: AccessSubject | Any,
    error_factory: Callable[..., Exception] | None = None,
) -> Callable
```

Returns a decorator that performs a full authorization check.

**Parameters:**

- `*args` — Permission arguments passed to `enforcer.enforce(user, *args)`. Each can be:
  - A plain value (string, enum, int, etc.) — passed as-is
  - An `AccessSubject` instance — resolved via FastAPI DI, then transformed by `selector`

- `error_factory` *(optional)* — A callable that **returns** an exception when enforcement fails.
  - **Type:** `Callable[[Any, *Any], Exception] | None`
  - **Default:** Uses the `error_factory` from the guard constructor
  - **Signature:** `(user: Any, *resolved_args: Any) -> Exception`
  - Allows per-route customization of denial responses (e.g., returning 404 instead of 403)

**Returns:** A decorator function to be applied to a FastAPI route.

**Raises:** The exception returned by `error_factory` (guard-level or route-level) when enforcement fails.

**Enforcement call:**

```python
enforcer.enforce(user, *resolved_args)
```

Where `resolved_args` is the list of arguments with all `AccessSubject` instances replaced by their resolved (and selected) values.

## Source

```python
# src/casbin_fastapi_decorator/_guard.py

class PermissionGuard:
    def __init__(self, *, user_provider, enforcer_provider, error_factory):
        self._user_provider = user_provider
        self._enforcer_provider = enforcer_provider
        self._error_factory = error_factory

    def auth_required(self) -> Callable:
        return build_auth_decorator(self._user_provider)

    def require_permission(
        self,
        *args: AccessSubject | Any,
        error_factory: Callable[..., Exception] | None = None,
    ) -> Callable:
        if error_factory is None:
            error_factory = self._error_factory

        return build_permission_decorator(
            user_provider=self._user_provider,
            enforcer_provider=self._enforcer_provider,
            error_factory=error_factory,
            args=args,
        )
```
