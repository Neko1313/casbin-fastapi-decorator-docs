---
sidebar_position: 1
---

# Installation

## Requirements

- Python **3.10** or higher
- FastAPI **≥ 0.115.0**

## Core package

Install the core package with `pip`:

```bash
pip install casbin-fastapi-decorator
```

Or with `uv`:

```bash
uv add casbin-fastapi-decorator
```

## Optional extras

The core package is intentionally minimal. Install only what you need:

### JWT authentication

Adds `JWTUserProvider` — extracts and validates JWT tokens from Bearer headers or cookies.

```bash
pip install "casbin-fastapi-decorator[jwt]"
```

### Database policies

Adds `DatabaseEnforcerProvider` — loads Casbin policies from a SQLAlchemy async session instead of a `.csv` file.

```bash
pip install "casbin-fastapi-decorator[db]"
```

### Casdoor integration

Adds `CasdoorUserProvider` — authenticates users via [Casdoor](https://casdoor.org/) OAuth2 and validates access/refresh token cookies.

```bash
pip install "casbin-fastapi-decorator[casdoor]"
```

### Install everything

```bash
pip install "casbin-fastapi-decorator[jwt,db,casdoor]"
```

## Dependencies

The core package depends on:

| Package | Version | Purpose |
|---|---|---|
| `fastapi` | ≥ 0.115.0 | Web framework |
| `fastapi-decorators` | ≥ 0.5.0 | Decorator injection mechanism |
| `casbin` | ≥ 1.36.0 | Policy enforcement engine |
