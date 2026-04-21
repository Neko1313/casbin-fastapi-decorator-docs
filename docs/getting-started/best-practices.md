---
sidebar_position: 5
---

# Best Practices

Recommendations for using `casbin-fastapi-decorator` effectively and securely.

## Design Patterns

### 1. Single Guard Instance Per Application

Create one `PermissionGuard` instance per application (or per feature module) and reuse it:

```python
# ❌ Wrong — creates a new guard per route
@app.get("/posts")
@PermissionGuard(
    user_provider=get_user,
    enforcer_provider=get_enforcer,
    error_factory=...,
).require_permission("post", "read")
async def list_posts(): ...

# ✅ Correct — guard is a singleton
guard = PermissionGuard(
    user_provider=get_current_user,
    enforcer_provider=enforcer_provider,
    error_factory=lambda *_: HTTPException(403),
)

@app.get("/posts")
@guard.require_permission("post", "read")
async def list_posts(): ...
```

### 2. Organize Guards by Feature Module

For large applications, create separate guards per feature:

```python
# auth/guard.py
guard = PermissionGuard(
    user_provider=get_current_user,
    enforcer_provider=enforcer_provider,
    error_factory=lambda *_: HTTPException(403),
)

# posts/router.py
from auth.guard import guard

router = APIRouter()

@router.get("/posts")
@guard.require_permission("post", "read")
async def list_posts(): ...
```

### 3. Use Enums for Permission Strings

Avoid magic strings; use enums:

```python
from enum import StrEnum

class Resource(StrEnum):
    POST = "post"
    COMMENT = "comment"
    USER = "user"

class Action(StrEnum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"

@app.get("/posts")
@guard.require_permission(Resource.POST, Action.READ)
async def list_posts(): ...
```

## Security Recommendations

### 1. Always Require Authentication First

Use `@guard.auth_required()` before `@guard.require_permission()`:

```python
# ❌ Wrong — missing auth check
@app.get("/admin")
@guard.require_permission("admin", "access")
async def admin_panel(): ...

# ✅ Correct — authentication is implicit in require_permission
# (it calls user_provider, which must not raise if user is authenticated)

# Or explicitly:
@app.get("/me")
@guard.auth_required()
async def get_current(user: User = Depends(get_current_user)): ...
```

### 2. Hide Resource Existence

Return `404 Not Found` instead of `403 Forbidden` for sensitive resources:

```python
@app.get("/draft-posts/{id}")
@guard.require_permission(
    "post", "read",
    error_factory=lambda *_: HTTPException(404, "Not Found"),
)
async def read_draft(id: int):
    """Unauthorized users can't tell if the post exists."""
    return await db.get_draft_post(id)
```

### 3. Validate User Input in Dependencies

Check bounds before using in authorization:

```python
# ❌ Wrong — unchecked user input
@app.delete("/posts/{id}")
@guard.require_permission("post", "delete")
async def delete_post(id: str):  # Could be extremely large
    ...

# ✅ Correct — FastAPI validates path parameter type
@app.delete("/posts/{id}")
@guard.require_permission("post", "delete")
async def delete_post(id: int):  # Guaranteed to be valid int
    ...
```

### 4. Use AccessSubject for Dynamic Checks

Avoid passing unvalidated request data directly to the enforcer:

```python
# ❌ Wrong — user input directly to enforcer
@app.delete("/posts/{id}")
@guard.require_permission("post", "delete", id)  # ← user input
async def delete_post(id: int):
    ...

# ✅ Correct — load from DB, then check ownership
async def get_post_owner(id: int) -> str:
    post = await db.get_post(id)
    if not post:
        raise HTTPException(404)
    return post.owner_id

@app.delete("/posts/{id}")
@guard.require_permission(
    AccessSubject(val=get_post_owner, selector=str.lower),
    "delete",
)
async def delete_post(id: int):
    ...
```

## Error Handling

### 1. Use Consistent Error Responses

All routes should follow the same error response format:

```python
# Define once, reuse everywhere
def unauthorized_error(user, *_) -> HTTPException:
    return HTTPException(
        403,
        detail={"message": "Forbidden", "code": "PERMISSION_DENIED"}
    )

guard = PermissionGuard(
    user_provider=get_current_user,
    enforcer_provider=enforcer_provider,
    error_factory=unauthorized_error,
)
```

### 2. Log Authorization Failures

Track denied access for security monitoring:

```python
import logging
logger = logging.getLogger(__name__)

def logged_error(user, *args) -> HTTPException:
    logger.warning(
        "Authorization denied",
        extra={
            "user_id": getattr(user, "id", None),
            "resource": args[0] if args else None,
        }
    )
    return HTTPException(403, "Forbidden")

guard = PermissionGuard(
    user_provider=get_current_user,
    enforcer_provider=enforcer_provider,
    error_factory=logged_error,
)
```

### 3. Provide Helpful Messages for Premium Features

Tell users how to gain access:

```python
def upgrade_required(user, *_) -> HTTPException:
    return HTTPException(
        402,
        detail={
            "message": "This feature requires a premium account",
            "upgrade_url": "https://example.com/upgrade",
        }
    )

@app.post("/api/export-data")
@guard.require_permission("data", "export", error_factory=upgrade_required)
async def export_data():
    ...
```

## Testing

### 1. Test Both Auth and Authz Separately

```python
# test_auth.py
@pytest.mark.asyncio
async def test_auth_required():
    """Authentication must pass before authorization."""
    client = TestClient(app)
    
    # No token → 401
    response = client.get("/posts")
    assert response.status_code == 401

# test_authz.py
@pytest.mark.asyncio
async def test_permission_denied():
    """User without permission → 403."""
    client = TestClient(app)
    
    # Token but no permission → 403
    response = client.get(
        "/admin",
        headers={"Authorization": "Bearer viewer_token"}
    )
    assert response.status_code == 403
```

### 2. Test AccessSubject Resolution

Mock the dependency and verify resolution:

```python
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_access_subject_resolution():
    """Verify AccessSubject correctly resolves and selects."""
    mock_db = AsyncMock()
    mock_db.get_post.return_value = {"id": 1, "owner": "alice"}
    
    # Verify selector transforms the value
    resolved = await get_post_owner(post_id=1)
    assert resolved == "alice"
```

### 3. Test Custom Error Factories

```python
@pytest.mark.asyncio
async def test_custom_error_factory():
    """Verify custom error factory returns expected exception."""
    def custom_error(user, *_) -> HTTPException:
        return HTTPException(404, "Not Found")
    
    # Should raise 404, not 403
    client = TestClient(app)
    response = client.get(
        "/secret",
        headers={"Authorization": "Bearer viewer_token"}
    )
    assert response.status_code == 404
```

## Performance

### 1. Cache Enforcers

Use enforcer providers that cache the `casbin.Enforcer` instance:

```python
# ❌ Wrong — creates a new enforcer per request
async def get_enforcer():
    return casbin.Enforcer("model.conf", "policy.csv")  # Expensive!

# ✅ Correct — enforcer is cached
from casbin_fastapi_decorator_file import CachedFileEnforcerProvider

enforcer_provider = CachedFileEnforcerProvider(
    model_path="model.conf",
    policy_path="policy.csv",
)
```

### 2. Minimize FastAPI Dependencies

Avoid creating expensive dependencies per-request:

```python
# ❌ Wrong — runs for every protected route
async def expensive_check():
    return await db.query(...)  # Called for every request

guard = PermissionGuard(user_provider=get_current_user, ...)

# ✅ Correct — only call for specific routes
async def optional_check():
    return await db.query(...)  # Only when needed

@app.get("/resource")
@guard.require_permission("resource", "read")
async def get_resource(opt: str = Depends(optional_check)):
    ...
```

### 3. Use SimpleNamespace for User Context

Prefer lightweight user objects:

```python
from types import SimpleNamespace

# ✅ Fast and simple
async def get_current_user() -> SimpleNamespace:
    return SimpleNamespace(id=1, role="admin")

# Also acceptable: dataclass with __slots__
from dataclasses import dataclass

@dataclass(slots=True)
class User:
    id: int
    role: str
```

## See Also

- [Error Handling Guide](./error-handling)
- [API Reference](../api-reference/permission-guard)
- [PermissionGuard](../api-reference/permission-guard)
- [AccessSubject](../api-reference/access-subject)
