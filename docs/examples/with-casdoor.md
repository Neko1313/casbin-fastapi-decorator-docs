---
sidebar_position: 4
---

# Casdoor Example

A complete example using `casbin-fastapi-decorator` with the `casdoor` extra. It follows the current `examples/core-casdoor` application from the main repository and uses the high-level `CasdoorIntegration` facade.

## Install

```bash
pip install "casbin-fastapi-decorator[casdoor]" uvicorn
```

## Prerequisites

A running Casdoor instance with:

- an application configured for your callback URL
- a certificate used to validate JWTs
- a remote enforcement target such as an enforcer (`example-org/enforcer-example`)

## Project structure

```text
my-app/
├── authz.py
├── model.py
└── main.py
```

## `authz.py`

```python
from casbin_fastapi_decorator_casdoor import (
    CasdoorEnforceTarget,
    CasdoorIntegration,
)

casdoor = CasdoorIntegration(
    endpoint="http://localhost:8000",
    client_id="example-client-id",
    client_secret="example-client-secret",
    certificate=open("casdoor.pem").read(),
    org_name="example-org",
    application_name="app-example",
    target=CasdoorEnforceTarget(enforce_id="example-org/enforcer-example"),
    redirect_after_login="/",
    cookie_secure=False,  # local HTTP only
)

guard = casdoor.create_guard()
```

## `main.py`

```python
from typing import Annotated

from authz import casdoor, guard
from casdoor import AsyncCasdoorSDK
from fastapi import Depends, FastAPI

app = FastAPI(title="Core + Casdoor Example")
app.include_router(casdoor.router)  # GET /login, GET /callback, POST /logout

@app.get("/")
async def index() -> dict:
    return {
        "message": "Log in via Casdoor to access protected endpoints.",
        "login_url": "/login",
    }


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

## Flow

1. Open `GET /login` in a browser.
2. The router issues an OAuth2 `state` value and redirects the browser to Casdoor.
3. After login, Casdoor redirects back to `GET /callback?code=...&state=...`.
4. The integration validates `state`, exchanges the code for tokens, and sets `access_token` and `refresh_token` cookies.
5. Protected routes call Casdoor's remote `/api/enforce` endpoint using the configured target.

## Try it

```bash
uvicorn main:app --reload
```

Then:

1. Open `http://localhost:8000/login`
2. Sign in through Casdoor
3. Reuse the issued cookies against protected routes

Example:

```bash
curl http://localhost:8000/articles \
  -H "Cookie: access_token=$ACCESS; refresh_token=$REFRESH"
```

## Notes

- `GET /login` is now the canonical way to start the OAuth2 flow
- `/callback` should not be called directly; it expects the `state` issued by `/login`
- `CasdoorUserProvider` returns the raw `access_token`; the enforcer parses it and uses the default subject format `{owner}/{name}`
- `POST /logout` clears both auth cookies
