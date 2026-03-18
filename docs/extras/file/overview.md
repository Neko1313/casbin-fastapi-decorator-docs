---
sidebar_position: 1
---

# File Overview

The `file` extra adds `CachedFileEnforcerProvider` - a ready-made
`enforcer_provider` for `model.conf` + `policy.csv` setups.

It loads the Casbin enforcer once, keeps it cached in memory, and hot-reloads
automatically when either file changes on disk.

## Install

```bash
pip install "casbin-fastapi-decorator[file]"
```

## Import

```python
from casbin_fastapi_decorator_file import CachedFileEnforcerProvider
```

## Why use it?

Compared to a plain dependency that calls `casbin.Enforcer(...)` on every
request, `CachedFileEnforcerProvider`:

- avoids re-reading `model.conf` and `policy.csv` on every request
- keeps a single cached enforcer in memory
- reloads automatically when either file changes
- fits directly into FastAPI dependency injection

## Setup

### 1. Create the provider

```python
from casbin_fastapi_decorator_file import CachedFileEnforcerProvider

enforcer_provider = CachedFileEnforcerProvider(
    model_path="casbin/model.conf",
    policy_path="casbin/policy.csv",
)
```

### 2. Pass it to `PermissionGuard`

```python
from casbin_fastapi_decorator import PermissionGuard
from fastapi import HTTPException

guard = PermissionGuard(
    user_provider=get_current_user,
    enforcer_provider=enforcer_provider,
    error_factory=lambda *_: HTTPException(403, "Forbidden"),
)
```

### 3. Start the watcher in FastAPI lifespan

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    async with enforcer_provider:
        yield

app = FastAPI(lifespan=lifespan)
```

Without the context manager the provider still caches the enforcer, but it will
not watch the files for changes.

## Constructor parameters

```python
CachedFileEnforcerProvider(
    model_path: str,
    policy_path: str,
)
```

| Parameter | Type | Description |
|---|---|---|
| `model_path` | `str` | Path to the Casbin model file |
| `policy_path` | `str` | Path to the Casbin policy file |

## Reload behavior

- changes to `model.conf` mark the cached enforcer as stale
- changes to `policy.csv` do the same
- the provider rebuilds the enforcer lazily on the next request
- no application restart is required

## Full example

See the [File Hot-Reload Example](../../examples/with-file) for a complete app
that exposes `/policy` and demonstrates live updates while the server is
running.
