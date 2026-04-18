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

## Why decorator, not middleware?

| Feature | **casbin-fastapi-decorator** | fastapi-authz / fastapi-casbin-auth |
|---|:---:|:---:|
| Approach | Decorator per route | Global middleware |
| Per-route permission config | ✅ | ❌ |
| Dynamic objects from request | ✅ `AccessSubject` | ❌ |
| No extra params in endpoint signature | ✅ | ❌ |
| Native FastAPI DI integration | ✅ | ⚠️ partial |
| JWT extras | ✅ | ❌ |
| DB-backed policies (SQLAlchemy async) | ✅ | ❌ |
| File policies with hot-reload | ✅ | ❌ |
| Casdoor OAuth2 integration | ✅ | ❌ |
| Works with `APIRouter` | ✅ | ✅ |

Middleware-based authorization checks every incoming request globally. With a decorator, you configure permissions exactly where the route is defined — no hidden side effects, no boilerplate dependencies in every function signature.

## Core concepts

The library is built around two classes:

- **`PermissionGuard`** — the decorator factory. You create one instance per application (or per module) and use it to decorate routes.
- **`AccessSubject`** — a wrapper for dynamic permission arguments that need to be resolved from the request at runtime.

## Optional extras

The core package handles authorization. Four optional extras extend it:

| Extra | What it adds |
|---|---|
| [`file`](./extras/file/overview) | `CachedFileEnforcerProvider` for cached file-based policies with hot-reload |
| [`jwt`](./extras/jwt/overview) | JWT token extraction and validation from Bearer headers or cookies |
| [`db`](./extras/db/overview) | `DatabaseEnforcerProvider` for cached SQLAlchemy-backed policies with hot-reload |
| [`casdoor`](./extras/casdoor/overview) | OAuth2 login, cookie-based authentication, and remote policy enforcement via [Casdoor](https://casdoor.org/) |

## Requirements

- Python 3.10+
- FastAPI ≥ 0.115.0
- Casbin ≥ 1.36.0

## Next steps

- [Installation](./getting-started/installation) — install the package
- [Quick Start](./getting-started/quick-start) — a working example in minutes
- [Casbin Concepts](./getting-started/concepts) — understand subjects, objects, actions, and policies
