---
sidebar_position: 4
---

# Error Handling Guide

Strategies for handling authorization failures in your FastAPI application.

## Overview

There are two levels of error handling in `casbin-fastapi-decorator`:

1. **Guard-level `error_factory`** — applied to all routes using that guard
2. **Route-level `error_factory`** — overrides guard-level factory for specific routes

## Guard-Level Error Factory

Set a default error response for all protected routes:

```python
from fastapi import HTTPException
from casbin_fastapi_decorator import PermissionGuard

# All routes deny with 403 Forbidden
guard = PermissionGuard(
    user_provider=get_current_user,
    enforcer_provider=enforcer_provider,
    error_factory=lambda *_: HTTPException(403, "Forbidden"),
)
```

The error factory receives the user and resolved permission arguments:

```python
def my_error_factory(user, *args) -> Exception:
    # user: the current user from user_provider
    # *args: the permission arguments after AccessSubject resolution
    return HTTPException(403, "Access Denied")
```

## Route-Level Error Factory

Override the guard-level factory for specific routes:

```python
def not_found_error(user, *_) -> HTTPException:
    return HTTPException(404, "Not Found")

@app.get("/draft/posts/{post_id}")
@guard.require_permission(
    "draft_post", "read",
    error_factory=not_found_error,  # Route-level override
)
async def read_draft(post_id: int):
    ...
```

## Status Code Selection

Choose the right HTTP status code for your use case:

| Status | Use Case |
|---|---|
| `401 Unauthorized` | User is not authenticated (use `auth_required()` instead) |
| `403 Forbidden` | User is authenticated but lacks permission (default) |
| `404 Not Found` | Hide resource existence; prevent information leakage |
| `402 Payment Required` | Feature requires paid tier; upgrade needed |
| `503 Service Unavailable` | Temporarily deny while under maintenance |

## Common Patterns

### 1. Silent Denial (Return 404)

Prevent leaking whether a resource exists:

```python
@app.get("/secret-report/{id}")
@guard.require_permission("report", "view", error_factory=lambda *_: HTTPException(404))
async def get_secret_report(id: int):
    return await db.get_report(id)
```

Why: An attacker can't distinguish between "forbidden" and "doesn't exist".

### 2. Detailed Error Response

Include context about what failed:

```python
def detailed_error(user, resource, action) -> HTTPException:
    return HTTPException(
        403,
        detail={
            "error": "Access denied",
            "required": f"{resource}:{action}",
            "user_role": user.role,
        }
    )

@app.delete("/posts/{id}")
@guard.require_permission("post", "delete", error_factory=detailed_error)
async def delete_post(id: int):
    ...
```

### 3. Audit Logging

Log authorization failures:

```python
import logging

logger = logging.getLogger(__name__)

def log_and_deny(user, *args) -> HTTPException:
    logger.warning(
        "Authorization failed",
        extra={"user_id": getattr(user, "id", None), "args": args}
    )
    return HTTPException(403, "Forbidden")

@app.post("/admin/users")
@guard.require_permission("user", "create", error_factory=log_and_deny)
async def create_user(data: UserCreate):
    ...
```

### 4. Rate Limit Based on User Role

Different limits based on authorization:

```python
def rate_limit_error(user, *_) -> HTTPException:
    tier = getattr(user, "tier", "free")
    if tier == "free":
        return HTTPException(
            429,
            detail="Free tier exceeded rate limit. Upgrade to continue."
        )
    else:
        return HTTPException(403, "Rate limit exceeded")

@app.post("/api/export")
@guard.require_permission("data", "export", error_factory=rate_limit_error)
async def export_data():
    ...
```

## Error Factory Signature

```python
# Signature
def error_factory(user: Any, *resolved_args: Any) -> Exception:
    pass

# Parameters
# user          - Value from user_provider (usually contains role, id, etc.)
# *resolved_args - Permission check arguments after AccessSubject resolution
#                  For enforce(user, "resource", "action"), resolved_args = ("resource", "action")

# Returns
# An Exception instance to raise (typically HTTPException, but can be any Exception)
```

## Important Notes

- **Always return an exception** — don't raise it, return it. The decorator handles raising.
- **No await needed** — error factories are synchronous (even if user_provider is async)
- **No side effects in factory** — if you need to log, do it in the guard-level factory for consistency

## Examples

See [Per-Route Error Responses](../examples/per-route-errors) for complete working examples.

## See Also

- [PermissionGuard API Reference](../api-reference/permission-guard)
- [Quick Start](./quick-start)
