---
sidebar_position: 4
---

# Casdoor Example

A complete example using `casbin-fastapi-decorator` with the `casdoor` extra. Users authenticate via Casdoor OAuth2 and access/refresh tokens are stored as HTTP-only cookies.

## Install

```bash
pip install "casbin-fastapi-decorator[casdoor]" uvicorn
```

## Prerequisites

A running Casdoor instance. For local development, use Docker:

```bash
docker run -d \
  --name casdoor \
  -p 8000:8000 \
  casbin/casdoor-all-in-one
```

Then open `http://localhost:8000` and register your application.

## Project structure

```
my-app/
├── casbin/
│   ├── model.conf
│   └── policy.csv
├── auth.py
├── authz.py
└── main.py
```

## `casbin/model.conf` and `policy.csv`

Same as the [basic example](./basic#casbin-files). Use Casdoor user identifiers (e.g., username or sub claim) as subjects.

## `auth.py`

```python
from casdoor import AsyncCasdoorSDK
from casbin_fastapi_decorator_casdoor import CasdoorUserProvider

sdk = AsyncCasdoorSDK(
    endpoint="http://localhost:8000",
    client_id="your-client-id",
    client_secret="your-client-secret",
    certificate=open("casdoor.pem").read(),
    org_name="built-in",
    application_name="app-built-in",
)

user_provider = CasdoorUserProvider(sdk=sdk)
```

## `authz.py`

```python
from auth import user_provider
from casbin import Enforcer
from fastapi import HTTPException

from casbin_fastapi_decorator import PermissionGuard

async def get_enforcer() -> Enforcer:
    return Enforcer("casbin/model.conf", "casbin/policy.csv")

guard = PermissionGuard(
    user_provider=user_provider,
    enforcer_provider=get_enforcer,
    error_factory=lambda *_: HTTPException(403, "Forbidden"),
)
```

## `main.py`

```python
from auth import sdk
from authz import guard
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import RedirectResponse

app = FastAPI(title="Core + Casdoor Example")

REDIRECT_URI = "http://localhost:8001/auth/callback"


@app.get("/auth/login")
async def login() -> RedirectResponse:
    """Redirect to Casdoor login page."""
    auth_url = sdk.get_auth_link(
        redirect_uri=REDIRECT_URI,
        response_type="code",
        scope="read",
    )
    return RedirectResponse(auth_url)


@app.get("/auth/callback")
async def callback(code: str, state: str, response: Response) -> dict:
    """Handle Casdoor OAuth2 callback, set token cookies."""
    token = await sdk.get_oauth_token(code=code)
    response.set_cookie("access_token", token.access_token, httponly=True, samesite="lax")
    response.set_cookie("refresh_token", token.refresh_token, httponly=True, samesite="lax")
    return {"message": "Logged in"}


@app.post("/auth/logout")
async def logout(response: Response) -> dict:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}


@app.get("/me")
@guard.auth_required()
async def me() -> dict:
    return {"message": "Authenticated"}


@app.get("/dashboard")
@guard.require_permission("dashboard", "view")
async def dashboard() -> dict:
    return {"message": "Welcome to the dashboard"}


@app.get("/admin")
@guard.require_permission("admin", "access")
async def admin() -> dict:
    return {"message": "Admin panel"}
```

## Flow

```
User → GET /auth/login
     → Redirected to Casdoor login page
     → User logs in at Casdoor
     → Casdoor redirects to /auth/callback?code=...
     → Tokens set as cookies
     → User accesses protected routes
```

## Notes

- `CasdoorUserProvider` returns the raw `access_token` string as the user identity
- The `access_token` is passed to `enforcer.enforce(access_token, obj, act)`
- Decode the JWT to find the actual user identifier and map it to your policy subjects
