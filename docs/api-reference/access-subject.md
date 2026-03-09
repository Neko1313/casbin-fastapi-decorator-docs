---
sidebar_position: 2
---

# AccessSubject API

Complete API reference for the `AccessSubject` dataclass.

## Class

```python
@dataclass(frozen=True, slots=True)
class AccessSubject:
    val: Callable[..., Any]
    selector: Callable[[Any], Any] = lambda x: x
```

## Fields

### `val`

**Type:** `Callable[..., Any]`
**Required:** Yes

A FastAPI dependency callable. It is wrapped with `Depends()` internally and resolved by FastAPI's dependency injection system on each request.

The callable can use:
- Path parameters
- Query parameters
- Request headers
- Other FastAPI dependencies

```python
# Simple: uses a path parameter
async def get_post_owner(post_id: int) -> str:
    return await db.get_post_owner(post_id)

AccessSubject(val=get_post_owner)
```

### `selector`

**Type:** `Callable[[Any], Any]`
**Default:** `lambda x: x` (identity function)

A transformation function applied to the resolved value of `val` before passing it to the enforcer.

```python
# Extract a field from a Pydantic model
AccessSubject(
    val=get_post,
    selector=lambda post: post.owner_id,
)

# Convert to string
AccessSubject(
    val=get_category_id,
    selector=str,
)

# Always use a constant (unusual but valid)
AccessSubject(
    val=get_user_context,
    selector=lambda _: "public",
)
```

## Behavior

When `require_permission` processes an `AccessSubject`, it:

1. Adds `Depends(access_subject.val)` to the route's dependency tree
2. On request: resolves the dependency, getting `raw_value`
3. Computes `final_value = access_subject.selector(raw_value)`
4. Passes `final_value` to `enforcer.enforce()` at the corresponding position

## Immutability

`AccessSubject` is a frozen dataclass. Once created, its fields cannot be changed. This makes it safe to define at module level and reuse:

```python
# Define once at module level
post_owner = AccessSubject(
    val=get_post,
    selector=lambda p: p.owner_id,
)

# Reuse in multiple routes
@app.put("/posts/{post_id}")
@guard.require_permission("post", post_owner)
async def update_post(...): ...

@app.delete("/posts/{post_id}")
@guard.require_permission("post", post_owner)
async def delete_post(...): ...
```

## Import

```python
from casbin_fastapi_decorator import AccessSubject
```

## Source

```python
# src/casbin_fastapi_decorator/_types.py

from dataclasses import dataclass, field
from typing import Any
from collections.abc import Callable

@dataclass(frozen=True, slots=True)
class AccessSubject:
    val: Callable[..., Any]
    selector: Callable[[Any], Any] = field(default=lambda x: x)
```
