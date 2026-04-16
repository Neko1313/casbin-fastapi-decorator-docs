---
sidebar_position: 3
---

# require_permission

`guard.require_permission(*args)` returns a decorator that performs a full authorization check via the Casbin enforcer.

## Usage

```python
@app.get("/posts")
@guard.require_permission("post", "read")
async def list_posts():
    ...
```

## How it works

When the decorated route is called:

1. `user_provider` is resolved — returns the current user
2. `enforcer_provider` is resolved — returns a `casbin.Enforcer`
3. Each argument in `*args` is resolved:
   - Plain values (strings, enums, etc.) are passed as-is
   - [`AccessSubject`](./access-subject) instances are resolved via FastAPI DI and transformed
4. The enforcer is called: `enforcer.enforce(user, *resolved_args)`
5. If the result is `False`, `error_factory(user, *resolved_args)` is raised
6. If `True`, the route handler runs

## Static arguments

The simplest case — fixed strings or enums:

```python
@app.delete("/posts/{post_id}")
@guard.require_permission("post", "delete")
async def delete_post(post_id: int):
    ...
```

You can use any values that Casbin's model understands — strings, enums, etc.:

```python
from enum import StrEnum

class Resource(StrEnum):
    POST = "post"

class Action(StrEnum):
    READ = "read"
    WRITE = "write"

@app.get("/posts")
@guard.require_permission(Resource.POST, Action.READ)
async def list_posts():
    ...
```

## Dynamic arguments

When a permission argument depends on request data (path params, query params, request body), use [`AccessSubject`](./access-subject):

```python
from casbin_fastapi_decorator import AccessSubject

async def get_post_owner(post_id: int) -> str:
    post = await db.get(post_id)
    return post.owner_id

@app.put("/posts/{post_id}")
@guard.require_permission(
    "post",
    AccessSubject(val=get_post_owner, selector=lambda owner: owner),
)
async def update_post(post_id: int):
    ...
```

## Custom error responses per route

By default, `require_permission()` uses the `error_factory` defined in the guard. You can override it on a per-route basis to return custom status codes or error details:

```python
def article_not_found_error(user: Any, *resolved_args: Any) -> HTTPException:
    """Return 404 instead of 403 for denied access."""
    return HTTPException(status_code=404, detail="Article not found")

@app.get("/articles/draft")
@guard.require_permission(
    Resource.POST,
    Permission.WRITE,
    error_factory=article_not_found_error,
)
async def read_draft():
    return {"title": "Draft Post"}
```

When a user without `post:write` permission accesses this route, they'll receive a `404 Not Found` instead of the default `403 Forbidden`, effectively hiding the resource's existence.

The `error_factory` parameter accepts the same signature as the guard-level factory:
```python
error_factory=lambda user, *resolved_args: HTTPException(403, "Forbidden")
```

## Argument order

Arguments are passed to `enforcer.enforce(user, *args)` in exactly the order you specify them. Make sure the order matches your Casbin model's `[request_definition]`:

```ini
# model.conf
[request_definition]
r = sub, obj, act
```

```python
# sub = user (always first, added by the guard)
# obj = first arg
# act = second arg
@guard.require_permission("post", "read")
#                          ^^^^^^  ^^^^^^
#                          obj     act
```
