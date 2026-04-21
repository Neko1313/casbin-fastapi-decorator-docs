---
sidebar_position: 7
---

# Per-Route Error Responses

Customize error handling for specific routes by using per-route `error_factory` parameter.

## Use Case

Sometimes you want different error responses for different routes:
- Return `404 Not Found` instead of `403 Forbidden` for hidden resources
- Return custom JSON error structures with additional context
- Log and alert on authorization failures for sensitive operations
- Return different status codes based on resource type

## Basic Example

Override the guard-level `error_factory` on specific routes:

```python
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from casbin_fastapi_decorator import PermissionGuard
from casbin_fastapi_decorator_file import CachedFileEnforcerProvider

bearer = HTTPBearer(auto_error=False)


class User(BaseModel):
    role: str


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Security(bearer),
    ],
) -> User:
    if not credentials:
        raise HTTPException(401, "Unauthorized")
    return User(role=credentials.credentials)


enforcer_provider = CachedFileEnforcerProvider(
    model_path="casbin/model.conf",
    policy_path="casbin/policy.csv",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with enforcer_provider:
        yield


# Default error for all routes (403 Forbidden)
guard = PermissionGuard(
    user_provider=get_current_user,
    enforcer_provider=enforcer_provider,
    error_factory=lambda *_: HTTPException(403, "Forbidden"),
)

app = FastAPI(lifespan=lifespan)


# --- Custom error factories ---


def not_found_error(user, *resolved_args) -> HTTPException:
    """Return 404 instead of 403 for hidden resources."""
    return HTTPException(status_code=404, detail="Not Found")


def premium_feature_error(user, *resolved_args) -> HTTPException:
    """Return 402 Payment Required for premium features."""
    return HTTPException(
        status_code=402,
        detail="This feature requires a premium subscription",
    )


def detailed_forbidden_error(user, *resolved_args) -> HTTPException:
    """Return detailed error context."""
    return HTTPException(
        status_code=403,
        detail={
            "message": "Access denied",
            "user": str(user.role),
            "resource": resolved_args[0] if resolved_args else "unknown",
        },
    )


# --- Routes ---


@app.get("/public/posts")
@guard.require_permission("post", "read")
async def list_public_posts() -> list[dict]:
    return [{"id": 1, "title": "Hello World"}]


@app.get("/draft/posts/{post_id}")
@guard.require_permission(
    "draft_post", "read",
    # Hide the resource: unauthorized users get 404, not 403
    error_factory=not_found_error,
)
async def read_draft_post(post_id: int) -> dict:
    """Unauthorized users see a 404 instead of 403."""
    return {"id": post_id, "title": "Draft Post", "published": False}


@app.post("/premium/reports")
@guard.require_permission(
    "report", "create",
    # Premium feature: return custom message
    error_factory=premium_feature_error,
)
async def create_premium_report() -> dict:
    """Unauthorized users see 402 with subscription prompt."""
    return {"id": 1, "status": "created"}


@app.get("/api/sensitive-data")
@guard.require_permission(
    "sensitive_data", "read",
    # Log detailed context
    error_factory=detailed_forbidden_error,
)
async def get_sensitive_data() -> dict:
    """Return detailed error context."""
    return {"data": "secret"}
```

## Error Factory Signature

The `error_factory` callable receives:

```python
def error_factory(user: Any, *resolved_args: Any) -> Exception:
    """
    Args:
        user: The value returned by user_provider
        *resolved_args: The permission arguments after AccessSubject resolution
    
    Returns:
        An Exception to be raised (HTTPException, ValueError, etc.)
    """
```

## Common Patterns

### Hide Resource Existence

Return 404 to prevent leaking information about whether a resource exists:

```python
def hide_resource_error(user, *_) -> HTTPException:
    return HTTPException(status_code=404, detail="Not Found")

@app.get("/articles/{article_id}")
@guard.require_permission("article", "read", error_factory=hide_resource_error)
async def read_article(article_id: int):
    ...
```

### Premium Features

Return a different status code with an upgrade prompt:

```python
def upgrade_required_error(user, *_) -> HTTPException:
    return HTTPException(
        status_code=402,
        detail="Upgrade your plan to access this feature",
    )

@app.post("/api/export")
@guard.require_permission("data", "export", error_factory=upgrade_required_error)
async def export_data():
    ...
```

### Detailed Error Context

Include information about what failed and why:

```python
def detailed_error(user, resource, action) -> HTTPException:
    return HTTPException(
        status_code=403,
        detail={
            "message": "Access denied",
            "user_role": user.role,
            "required_action": action,
            "resource": resource,
        },
    )

@app.delete("/data/{data_id}")
@guard.require_permission(
    "data", "delete",
    error_factory=detailed_error,
)
async def delete_data(data_id: int):
    ...
```

### Logging & Alerting

Log sensitive operations:

```python
import logging

logger = logging.getLogger(__name__)

def log_and_deny(user, *resolved_args) -> HTTPException:
    logger.warning(
        "Unauthorized access attempt",
        extra={
            "user_id": getattr(user, "id", None),
            "resource": resolved_args[0] if resolved_args else None,
        },
    )
    return HTTPException(403, "Forbidden")

@app.post("/admin/users")
@guard.require_permission("user", "create", error_factory=log_and_deny)
async def create_user():
    ...
```

## Casbin Model for Examples

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

**`policy.csv`:**

```csv
p, viewer, post, read
p, viewer, public_posts, read
p, editor, post, read
p, editor, post, write
p, editor, draft_post, read
p, editor, draft_post, write
p, premium, report, create
p, admin, sensitive_data, read
p, admin, user, create
p, admin, data, delete
```

## Key Points

- **Per-route overrides guard-level** — if both are set, the route-level `error_factory` wins
- **Useful for hiding implementation details** — return 404 instead of 403 to prevent information leakage
- **No performance overhead** — the extra factory check is negligible
- **Works with `AccessSubject`** — error factory receives resolved arguments

## See Also

- [PermissionGuard API](../api-reference/permission-guard) — full `error_factory` documentation
- [Basic Example](./basic) — standard setup with default error handling
