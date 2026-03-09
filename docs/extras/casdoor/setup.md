---
sidebar_position: 2
---

# Casdoor Setup

A step-by-step guide to integrating Casdoor with `casbin-fastapi-decorator`.

## Prerequisites

- A running Casdoor instance (see [Casdoor quick start](https://casdoor.org/docs/basic/server-installation))
- An application registered in Casdoor
- The Casdoor Python SDK: included when you install `casbin-fastapi-decorator[casdoor]`

## 1. Register your application in Casdoor

In the Casdoor admin UI:

1. Go to **Applications** → **Add**
2. Set the redirect URL to your FastAPI callback endpoint (e.g., `http://localhost:8000/auth/callback`)
3. Note the **Client ID** and **Client Secret**
4. Download or copy the **Certificate** (public key for JWT validation)

## 2. Configure the SDK

```python
from casdoor import AsyncCasdoorSDK

sdk = AsyncCasdoorSDK(
    endpoint="https://your-casdoor-instance.com",
    client_id="your-client-id",
    client_secret="your-client-secret",
    certificate="""-----BEGIN CERTIFICATE-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END CERTIFICATE-----""",
    org_name="your-org",
    application_name="your-app",
)
```

## 3. Implement the OAuth2 flow

### Login redirect

Send the user to Casdoor's authorization endpoint:

```python
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()

@app.get("/auth/login")
async def login() -> RedirectResponse:
    auth_url = sdk.get_auth_link(
        redirect_uri="http://localhost:8000/auth/callback",
        response_type="code",
        scope="read",
    )
    return RedirectResponse(auth_url)
```

### Callback handler

Exchange the authorization code for tokens and set them as cookies:

```python
from fastapi import Response

@app.get("/auth/callback")
async def callback(code: str, state: str, response: Response) -> dict:
    # Exchange code for tokens
    token = await sdk.get_oauth_token(code=code)

    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    response.set_cookie(
        key="refresh_token",
        value=token.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return {"message": "Logged in successfully"}
```

## 4. Protect routes

```python
from casbin_fastapi_decorator import PermissionGuard
from casbin_fastapi_decorator_casdoor import CasdoorUserProvider
import casbin

user_provider = CasdoorUserProvider(sdk=sdk)

guard = PermissionGuard(
    user_provider=user_provider,
    enforcer_provider=lambda: casbin.Enforcer("casbin/model.conf", "casbin/policy.csv"),
    error_factory=lambda *_: HTTPException(403, "Forbidden"),
)


@app.get("/dashboard")
@guard.auth_required()
async def dashboard():
    return {"message": "Welcome!"}


@app.get("/admin")
@guard.require_permission("admin", "access")
async def admin_panel():
    return {"message": "Admin area"}
```

## 5. Logout

Clear the cookies on logout:

```python
@app.post("/auth/logout")
async def logout(response: Response) -> dict:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}
```

## User identity

`CasdoorUserProvider` returns the raw `access_token` string as the user identity. This string is passed as the first argument to `enforcer.enforce()`.

Make sure your Casbin policy uses Casdoor user identifiers as subjects. You can decode the token to inspect the claims:

```python
import jwt

token = "eyJ..."  # the access_token
payload = jwt.decode(token, options={"verify_signature": False})
print(payload)  # {"sub": "user-id", "name": "Alice", ...}
```

Update your `policy.csv` or database policies to use the appropriate identifier (e.g., the `sub` claim or the username).
