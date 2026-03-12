---
sidebar_position: 1
---

# Casdoor Overview

The `casdoor` extra adds a full Casdoor integration for `casbin-fastapi-decorator`: OAuth2 login/logout routes, cookie-based authentication, and remote Casbin policy checks through [Casdoor](https://casdoor.org/).

## Install

```bash
pip install "casbin-fastapi-decorator[casdoor]"
```

## Import

```python
from casbin_fastapi_decorator_casdoor import (
    CasdoorEnforceTarget,
    CasdoorIntegration,
)
```

## Recommended entry point

Use `CasdoorIntegration` unless you need to customise every building block yourself:

```python
from fastapi import FastAPI
from casbin_fastapi_decorator_casdoor import (
    CasdoorEnforceTarget,
    CasdoorIntegration,
)

casdoor = CasdoorIntegration(
    endpoint="http://localhost:8000",
    client_id="your-client-id",
    client_secret="your-client-secret",
    certificate=open("casdoor.pem").read(),
    org_name="your-org",
    application_name="your-app",
    target=CasdoorEnforceTarget(enforce_id="your-org/your-enforcer"),
    redirect_after_login="/",
    cookie_secure=False,  # local HTTP only
)

app = FastAPI()
app.include_router(casdoor.router)  # GET /login, GET /callback, POST /logout
guard = casdoor.create_guard()

@app.get("/articles")
@guard.require_permission("articles", "read")
async def list_articles() -> dict:
    return {"ok": True}
```

## What the package provides

| Component | Purpose |
|---|---|
| `CasdoorIntegration` | High-level facade that wires the SDK, router, user provider, enforcer provider, and guard |
| `CasdoorUserProvider` | Validates `access_token` and `refresh_token` cookies and returns the raw `access_token` |
| `CasdoorEnforcerProvider` | Builds a `CasdoorEnforcer` that calls Casdoor's remote `/api/enforce` endpoint |
| `make_casdoor_router` | Lower-level router factory if you do not want to use the facade |
| `CookieStateManager` | Default OAuth2 `state` storage and validation strategy |
| `CasdoorEnforceTarget` | Selects which Casdoor object (`enforcer`, `permission`, `model`, `resource`, `owner`) to use for enforcement |

## OAuth2 flow

1. `GET /login` issues a one-time OAuth2 `state` value and redirects the browser to Casdoor.
2. `GET /callback` validates that `state`, exchanges the OAuth2 code for tokens, writes `access_token` and `refresh_token` cookies, and redirects to `redirect_after_login`.
3. `POST /logout` clears both auth cookies.
4. Protected routes use the raw `access_token` as the user identity; the Casdoor enforcer parses the JWT and performs remote authorization against Casdoor.

## Default state protection

`CookieStateManager` is enabled by default. It stores the OAuth2 `state` in a short-lived cookie and validates it on callback.

- Cookie name: `casdoor_oauth_state`
- `HttpOnly=True`
- `Secure=True`
- `SameSite=lax`
- `Max-Age=300`

If you already store sessions elsewhere, pass a custom `state_manager` to `CasdoorIntegration` or `make_casdoor_router`.

## Choosing the enforcement target

`CasdoorEnforceTarget` requires exactly one field:

```python
from casbin_fastapi_decorator_casdoor import CasdoorEnforceTarget

CasdoorEnforceTarget(enforce_id="your-org/your-enforcer")
CasdoorEnforceTarget(permission_id="your-org/can_edit_posts")
CasdoorEnforceTarget(model_id="your-org/rbac-model")
CasdoorEnforceTarget(resource_id="your-org/articles-resource")
CasdoorEnforceTarget(owner="your-org")
```

You can also resolve the target per request:

```python
CasdoorEnforceTarget(
    enforce_id=lambda parsed: f"{parsed['owner']}/main-enforcer"
)
```

## Full example

See the [Casdoor Example](../../examples/with-casdoor) for a complete working application.
