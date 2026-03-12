---
sidebar_position: 2
---

# Casdoor Setup

A step-by-step guide to integrating Casdoor with `casbin-fastapi-decorator`.

## Prerequisites

- A running Casdoor instance (see [Casdoor quick start](https://casdoor.org/docs/basic/server-installation))
- An application registered in Casdoor
- A certificate for JWT verification
- The `casdoor` extra installed: `pip install "casbin-fastapi-decorator[casdoor]"`

## 1. Register your application in Casdoor

In the Casdoor admin UI:

1. Go to **Applications** → **Add**
2. Set the redirect URL to the callback route exposed by the integration router
3. Note the **Client ID** and **Client Secret**
4. Download or copy the **Certificate** (public key for JWT validation)

Examples:

- If `router_prefix=""`, use `http://localhost:8080/callback`
- If `router_prefix="/auth"`, use `http://localhost:8080/auth/callback`

The login flow itself starts from `/login` (or `{router_prefix}/login`), not from a hand-written redirect route.

## 2. Configure `CasdoorIntegration`

```python
from fastapi import FastAPI
from casbin_fastapi_decorator_casdoor import (
    CasdoorEnforceTarget,
    CasdoorIntegration,
)

casdoor = CasdoorIntegration(
    endpoint="https://your-casdoor-instance.com",
    client_id="your-client-id",
    client_secret="your-client-secret",
    certificate=open("casdoor.pem").read(),
    org_name="your-org",
    application_name="your-app",
    target=CasdoorEnforceTarget(enforce_id="your-org/your-enforcer"),
    redirect_after_login="/",
    cookie_secure=False,  # local HTTP only
    router_prefix="",
)

app = FastAPI()
app.include_router(casdoor.router)
guard = casdoor.create_guard()
```

That gives you these endpoints immediately:

- `GET /login`
- `GET /callback`
- `POST /logout`

## 3. Protect routes

```python
from typing import Annotated

from casdoor import AsyncCasdoorSDK
from fastapi import Depends


@app.get("/me")
@guard.auth_required()
async def me(
    token: Annotated[str, Depends(casdoor.user_provider)],
) -> dict:
    sdk: AsyncCasdoorSDK = casdoor.sdk
    return sdk.parse_jwt_token(token)


@app.get("/articles")
@guard.require_permission("articles", "read")
async def list_articles() -> dict:
    return {"items": []}


@app.post("/articles")
@guard.require_permission("articles", "write")
async def create_article() -> dict:
    return {"ok": True}
```

## 4. Choose the remote enforcement target

`CasdoorEnforceTarget` tells Casdoor which API object should answer `/api/enforce`. Exactly one field must be set.

```python
from casbin_fastapi_decorator_casdoor import CasdoorEnforceTarget

CasdoorEnforceTarget(enforce_id="your-org/your-enforcer")
CasdoorEnforceTarget(permission_id="your-org/can_edit_posts")
CasdoorEnforceTarget(model_id="your-org/rbac-model")
CasdoorEnforceTarget(resource_id="your-org/articles-resource")
CasdoorEnforceTarget(owner="your-org")
```

For multi-tenant setups, resolve the target from JWT claims:

```python
CasdoorEnforceTarget(
    enforce_id=lambda parsed: f"{parsed['owner']}/main-enforcer"
)
```

## 5. Understand the login flow

The current integration no longer expects you to write the OAuth callback flow by hand.

1. The browser opens `GET /login`.
2. The router issues an OAuth2 `state` value and stores it via `state_manager`.
3. The browser is redirected to Casdoor.
4. Casdoor redirects back to `GET /callback?code=...&state=...`.
5. The router validates `state`, exchanges the code for tokens, stores cookies, and redirects to `redirect_after_login`.

Do not link users directly to `/callback`; it requires the `state` issued by `/login`.

## 6. Configure OAuth2 state protection

`CookieStateManager` is the default implementation:

- Cookie name: `casdoor_oauth_state`
- `HttpOnly=True`
- `Secure=True`
- `SameSite=lax`
- `Max-Age=300`

You can override its settings or swap the implementation entirely:

```python
from casbin_fastapi_decorator_casdoor import CookieStateManager

casdoor = CasdoorIntegration(
    endpoint="https://your-casdoor-instance.com",
    client_id="your-client-id",
    client_secret="your-client-secret",
    certificate=open("casdoor.pem").read(),
    org_name="your-org",
    application_name="your-app",
    target=CasdoorEnforceTarget(enforce_id="your-org/your-enforcer"),
    state_manager=CookieStateManager(
        cookie_secure=False,
        cookie_max_age=600,
    ),
)
```

If you need Redis- or session-backed state storage, provide your own object implementing the `CasdoorStateManager` protocol.

## 7. Manual composition for advanced setups

If the facade is too restrictive, wire the pieces manually:

```python
from casdoor import AsyncCasdoorSDK
from casbin_fastapi_decorator import PermissionGuard
from fastapi import HTTPException
from casbin_fastapi_decorator_casdoor import (
    CasdoorEnforceTarget,
    CasdoorEnforcerProvider,
    CasdoorUserProvider,
    make_casdoor_router,
)

sdk = AsyncCasdoorSDK(...)
user_provider = CasdoorUserProvider(sdk=sdk)
enforcer_provider = CasdoorEnforcerProvider(
    sdk=sdk,
    target=CasdoorEnforceTarget(enforce_id="your-org/your-enforcer"),
)
router = make_casdoor_router(sdk, redirect_after_login="/docs")
guard = PermissionGuard(
    user_provider=user_provider,
    enforcer_provider=enforcer_provider,
    error_factory=lambda *_: HTTPException(403, "Forbidden"),
)
```

Use this path when you need custom error handling, a custom `user_factory`, or multiple guards with different targets.
