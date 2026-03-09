---
sidebar_position: 3
---

# Casbin Concepts

A brief introduction to Casbin concepts used throughout this library. If you are already familiar with Casbin, you can skip this page.

## The enforce call

At its core, Casbin answers one question:

> Can **subject** perform **action** on **object**?

```python
enforcer.enforce(subject, object, action)  # returns True or False
```

This library calls `enforcer.enforce(user, *args)` where `user` comes from your `user_provider` dependency and `*args` are the arguments you pass to `require_permission`.

## Model and policy

Casbin uses two files:

### Model (`model.conf`)

Defines *how* authorization rules are structured. A typical RBAC model looks like this:

```ini
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act
```

### Policy (`policy.csv`)

Defines the actual rules:

```csv
# Roles
g, admin, editor
g, editor, viewer

# Permissions
p, viewer, post, read
p, editor, post, write
p, admin, post, delete
```

## Subject, Object, Action

These map directly to `require_permission` arguments:

```python
@guard.require_permission("post", "read")
#                          ^^^^^^  ^^^^^^
#                          object  action
# subject = current user (from user_provider)
```

The enforcer call becomes:
```python
enforcer.enforce(current_user, "post", "read")
```

## RBAC vs ABAC

**RBAC** (Role-Based Access Control) — permissions are assigned to roles, users get roles:

```csv
g, alice, admin       # alice has admin role
p, admin, post, write # admin can write posts
```

**ABAC** (Attribute-Based Access Control) — permissions are based on attributes of the user or resource:

```ini
# matcher in model.conf
m = r.sub.department == r.obj.owner
```

This library supports both — the model and policy files determine the access control model, not the library itself.

## Further reading

- [Casbin documentation](https://casbin.org/docs/overview)
- [Supported models](https://casbin.org/docs/supported-models)
- [Policy syntax](https://casbin.org/docs/syntax-for-models)
