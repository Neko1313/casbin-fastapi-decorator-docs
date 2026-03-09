---
sidebar_position: 4
---

# AccessSubject

`AccessSubject` wraps a FastAPI dependency whose value comes from the request. Use it when a permission argument is not a fixed string but needs to be resolved dynamically at request time.

## Import

```python
from casbin_fastapi_decorator import AccessSubject
```

## Definition

```python
@dataclass(frozen=True, slots=True)
class AccessSubject:
    val: Callable[..., Any]
    selector: Callable[[Any], Any] = lambda x: x
```

### `val`

A FastAPI dependency — a callable that FastAPI will resolve via dependency injection. It can use path parameters, query parameters, headers, or other dependencies.

### `selector`

An optional transformation function applied to the resolved value before it is passed to the enforcer. Defaults to identity (`lambda x: x`).

## Basic usage

```python
from casbin_fastapi_decorator import AccessSubject

async def get_resource_owner(post_id: int) -> str:
    post = await db.get_post(post_id)
    return post.owner_id

@app.delete("/posts/{post_id}")
@guard.require_permission(
    "post",
    AccessSubject(val=get_resource_owner),
)
async def delete_post(post_id: int):
    ...
```

Here `get_resource_owner` receives `post_id` from the path parameter (FastAPI resolves it), fetches the post, and returns the owner ID. The enforcer then receives `(user, "post", owner_id)`.

## Using the selector

The `selector` transforms the resolved value. This is useful when the dependency returns a complex object but you only need one field:

```python
from pydantic import BaseModel

class Post(BaseModel):
    id: int
    owner_id: str
    title: str

async def get_post(post_id: int) -> Post:
    return await db.get_post(post_id)

@app.put("/posts/{post_id}")
@guard.require_permission(
    "post",
    AccessSubject(
        val=get_post,
        selector=lambda post: post.owner_id,  # extract just the owner_id
    ),
)
async def update_post(post_id: int, data: PostUpdate):
    ...
```

The enforcer receives `(user, "post", post.owner_id)` instead of the full `Post` object.

## Combining static and dynamic arguments

You can mix plain values and `AccessSubject` in the same `require_permission` call:

```python
@app.get("/posts/{post_id}/comments")
@guard.require_permission(
    "comment",                                   # static
    "read",                                      # static
    AccessSubject(val=get_post_visibility),      # dynamic
)
async def list_comments(post_id: int):
    ...
```

Arguments are resolved and passed to the enforcer in order:
```python
enforcer.enforce(user, "comment", "read", post_visibility)
```

## Immutability

`AccessSubject` is a frozen dataclass — it cannot be modified after creation. This makes it safe to define once at module level:

```python
# Define once
post_owner = AccessSubject(val=get_post_owner, selector=lambda p: p.owner_id)

# Reuse across routes
@app.put("/posts/{post_id}")
@guard.require_permission("post", post_owner)
async def update_post(...): ...

@app.delete("/posts/{post_id}")
@guard.require_permission("post", post_owner)
async def delete_post(...): ...
```
