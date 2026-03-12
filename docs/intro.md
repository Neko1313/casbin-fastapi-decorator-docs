---
slug: /
sidebar_position: 1
---

# Introduction

**casbin-fastapi-decorator** is an authorization decorator factory for [FastAPI](https://fastapi.tiangolo.com/) built on top of [Casbin](https://casbin.org/).

## What is it?

Instead of writing authorization logic as middleware or injecting dependencies into every endpoint signature, this library lets you protect routes with a simple decorator:

```python
@app.get("/articles")
@guard.require_permission("post", "read")
async def list_posts():
    ...
```

No middleware registration. No extra parameters in your function signatures. Just a decorator.

## Why not middleware?

| Approach | How it works | Drawback |
|---|---|---|
| Middleware | Intercepts all requests, checks URL path | Hard to do per-route logic |
| Dependency injection | Add `Depends(...)` to every endpoint | Clutters function signatures |
| **Decorator (this library)** | Decorates the route function directly | Clean, explicit, per-route |

## Core concepts

The library is built around two classes:

- **`PermissionGuard`** — the decorator factory. You create one instance per application (or per module) and use it to decorate routes.
- **`AccessSubject`** — a wrapper for dynamic permission arguments that need to be resolved from the request at runtime.

## Optional extras

The core package handles authorization. Three optional extras extend it:

| Extra | What it adds |
|---|---|
| [`jwt`](./extras/jwt/overview) | JWT token extraction and validation from Bearer headers or cookies |
| [`db`](./extras/db/overview) | Loading Casbin policies from a SQLAlchemy async database |
| [`casdoor`](./extras/casdoor/overview) | OAuth2 login, cookie-based authentication, and remote policy enforcement via [Casdoor](https://casdoor.org/) |

## Requirements

- Python 3.10+
- FastAPI ≥ 0.115.0
- Casbin ≥ 1.36.0

## Next steps

- [Installation](./getting-started/installation) — install the package
- [Quick Start](./getting-started/quick-start) — a working example in minutes
- [Casbin Concepts](./getting-started/concepts) — understand subjects, objects, actions, and policies
