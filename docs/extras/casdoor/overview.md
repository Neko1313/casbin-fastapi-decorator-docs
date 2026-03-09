---
sidebar_position: 1
---

# Casdoor Overview

The `casdoor` extra adds `CasdoorUserProvider` — a `user_provider` that authenticates users via [Casdoor](https://casdoor.org/), an open-source Identity and Access Management platform.

## Install

```bash
pip install "casbin-fastapi-decorator[casdoor]"
```

## Import

```python
from casbin_fastapi_decorator_casdoor import CasdoorUserProvider
```

## What is Casdoor?

[Casdoor](https://casdoor.org/) is an open-source SSO (Single Sign-On) and IAM (Identity and Access Management) platform. It supports:

- OAuth 2.0 / OpenID Connect
- JWT-based tokens
- Multiple identity providers (GitHub, Google, LDAP, etc.)
- Web-based user and policy management UI

## How it works

`CasdoorUserProvider` is a FastAPI dependency that:

1. Reads `access_token` and `refresh_token` from cookies
2. Validates both tokens using the [Casdoor Python SDK](https://github.com/casdoor/casdoor-python-sdk) (`parse_jwt_token`)
3. Returns the raw `access_token` string as the user identity for downstream enforcement

## Setup

### 1. Configure the Casdoor SDK

```python
from casdoor import AsyncCasdoorSDK

sdk = AsyncCasdoorSDK(
    endpoint="http://localhost:8000",       # Casdoor server URL
    client_id="your-client-id",
    client_secret="your-client-secret",
    certificate="path/to/certificate.pem", # or certificate content as string
    org_name="your-organization",
    application_name="your-application",
)
```

### 2. Create the user provider

```python
from casbin_fastapi_decorator_casdoor import CasdoorUserProvider

user_provider = CasdoorUserProvider(sdk=sdk)
```

### 3. Wire into the guard

```python
from casbin_fastapi_decorator import PermissionGuard
from fastapi import HTTPException
import casbin

guard = PermissionGuard(
    user_provider=user_provider,
    enforcer_provider=lambda: casbin.Enforcer("casbin/model.conf", "casbin/policy.csv"),
    error_factory=lambda *_: HTTPException(403, "Forbidden"),
)
```

## Constructor parameters

```python
CasdoorUserProvider(
    *,
    sdk: AsyncCasdoorSDK,
    access_token_cookie: str = "access_token",
    refresh_token_cookie: str = "refresh_token",
    unauthorized_error: Callable[[], Exception] = ...,
    invalid_token_error: Callable[[str], Exception] = ...,
)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `sdk` | `AsyncCasdoorSDK` | required | Configured Casdoor SDK instance |
| `access_token_cookie` | `str` | `"access_token"` | Cookie name for the access token |
| `refresh_token_cookie` | `str` | `"refresh_token"` | Cookie name for the refresh token |
| `unauthorized_error` | `Callable` | `HTTPException(401)` | Factory for missing token errors |
| `invalid_token_error` | `Callable[[str], Exception]` | `HTTPException(401)` | Factory for invalid token errors |

## Error handling

```python
user_provider = CasdoorUserProvider(
    sdk=sdk,
    unauthorized_error=lambda: HTTPException(401, "Please log in"),
    invalid_token_error=lambda reason: HTTPException(401, f"Token error: {reason}"),
)
```

## Full example

See the [Casdoor Example](../../examples/with-casdoor) for a complete working application.
