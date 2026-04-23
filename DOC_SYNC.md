# Documentation Synchronization Guide

This guide documents how to keep the `casbin-fastapi-decorator-docs` project in sync with changes from the `casbin-fastapi-decorator` project.

## Project Structure

### Main Project: `casbin-fastapi-decorator`
- **Branch for development:** `claude/great-turing-6pVtr`
- **Location:** `/home/user/casbin-fastapi-decorator`
- **Key files:**
  - `src/casbin_fastapi_decorator/` - Core library code
  - `packages/` - Optional extensions (file, jwt, db, casdoor)
  - `README.md` - Main documentation
  - `CLAUDE.md` - Developer notes

### Docs Project: `casbin-fastapi-decorator-docs`
- **Branch for development:** `claude/bold-cori-6pVtr`
- **Location:** `/home/user/casbin-fastapi-decorator-docs`
- **Type:** Docusaurus v3 site
- **Key directories:**
  - `docs/` - Main documentation content
  - `docs/getting-started/` - Installation, quick start, concepts
  - `docs/core/` - Core API reference
  - `docs/api-reference/` - Detailed API docs
  - `docs/extras/` - Optional packages (file, jwt, db, casdoor)
  - `docs/examples/` - Code examples

## Documentation Areas to Monitor

### 1. Core API (`src/casbin_fastapi_decorator/`)

**Files to watch:**
- `_types.py` - AccessSubject class definition
- `_guard.py` - PermissionGuard factory class
- `_builder.py` - Decorator implementation details

**Documentation locations:**
- `docs/api-reference/access-subject.md`
- `docs/api-reference/permission-guard.md`
- `docs/core/permission-guard.md`
- `docs/core/access-subject.md`
- `docs/core/auth-required.md`
- `docs/core/require-permission.md`

**What to check for:**
- Changes to method signatures (especially `error_factory` parameter)
- New parameters added to PermissionGuard
- Changes to AccessSubject selector behavior
- Updates to how dependencies are resolved

### 2. File Extra (`packages/casbin-fastapi-decorator-file/`)

**Files to watch:**
- `src/casbin_fastapi_decorator_file/` - CachedFileEnforcerProvider implementation
- `packages/casbin-fastapi-decorator-file/README.md`

**Documentation locations:**
- `docs/extras/file/overview.md`
- Examples in `docs/examples/with-file.md`

**What to check for:**
- Changes to CachedFileEnforcerProvider API
- New constructor parameters
- Changes to reload behavior
- Hot-reload implementation details

### 3. JWT Extra (`packages/casbin-fastapi-decorator-jwt/`)

**Files to watch:**
- `src/casbin_fastapi_decorator_jwt/` - JWTUserProvider implementation
- `packages/casbin-fastapi-decorator-jwt/README.md`

**Documentation locations:**
- `docs/extras/jwt/overview.md`
- `docs/extras/jwt/bearer-token.md`
- `docs/extras/jwt/cookie.md`
- `docs/examples/with-jwt.md`

**What to check for:**
- Changes to JWTUserProvider configuration
- New authentication methods
- Changes to payload validation

### 4. Database Extra (`packages/casbin-fastapi-decorator-db/`)

**Files to watch:**
- `src/casbin_fastapi_decorator_db/` - DatabaseEnforcerProvider implementation
- `packages/casbin-fastapi-decorator-db/README.md`

**Documentation locations:**
- `docs/extras/db/overview.md`
- `docs/extras/db/sqlalchemy-adapter.md`
- `docs/examples/with-database.md`

**What to check for:**
- Changes to DatabaseEnforcerProvider API
- New polling strategy
- Changes to policy mapping
- Hash-based reload mechanism updates

### 5. Casdoor Extra (`packages/casbin-fastapi-decorator-casdoor/`)

**Files to watch:**
- `src/casbin_fastapi_decorator_casdoor/` - CasdoorIntegration implementation
- `packages/casbin-fastapi-decorator-casdoor/README.md`

**Documentation locations:**
- `docs/extras/casdoor/overview.md`
- `docs/extras/casdoor/setup.md`
- `docs/examples/with-casdoor.md`

**What to check for:**
- Changes to CasdoorIntegration setup
- New OAuth2 flow updates
- Changes to CasdoorEnforceTarget
- State management updates

## Sync Process

### Quick Check Checklist

Before making documentation updates, verify:

1. **Version alignment:** Check if both projects reference the same version
2. **Feature coverage:** Ensure all new features have documentation
3. **API stability:** Verify parameter names and method signatures match
4. **Examples:** Ensure example code reflects current best practices
5. **Cross-references:** Update internal doc links when pages are reorganized

### Step-by-Step Update Process

1. **Identify changes** in the main project since last documentation sync
2. **Map changes** to documentation files that need updating
3. **Update documentation** with new information, examples, API details
4. **Test examples** in documentation by running them (if possible)
5. **Verify links** - ensure all cross-references are correct
6. **Commit changes** with clear message indicating what was synced

### Common Update Scenarios

#### New Parameter Added to PermissionGuard
1. Update `docs/api-reference/permission-guard.md` with new parameter in the table
2. Update signature in code block
3. Add explanation section for the new parameter
4. Update examples if the parameter usage is important

#### New Package/Extra Added
1. Create new documentation directory: `docs/extras/<package_name>/`
2. Create `overview.md` with setup instructions
3. Add any specific guides (e.g., `config.md`, `examples.md`)
4. Update `docs/intro.md` to mention new extra
5. Add example to `docs/examples/`
6. Update main `README.md` if needed

#### Feature Enhancement
1. Update affected API reference files
2. Add/update example code
3. Update "What's happening" sections in guides
4. Consider adding a dedicated guide page if significant

## Monitoring Commands

Check for changes since last sync:

```bash
# In main project
cd /home/user/casbin-fastapi-decorator
git log --oneline main..HEAD

# In docs project
cd /home/user/casbin-fastapi-decorator-docs
git log --oneline main..HEAD

# See what files changed
git diff main...HEAD --name-only
```

## Key Files to Understand

- **Main README:** `/home/user/casbin-fastapi-decorator/README.md` - marketing & quick reference
- **Docs intro:** `/home/user/casbin-fastapi-decorator-docs/docs/intro.md` - documentation entry point
- **Sidebar config:** `/home/user/casbin-fastapi-decorator-docs/sidebars.ts` - doc navigation structure
- **Docusaurus config:** `/home/user/casbin-fastapi-decorator-docs/docusaurus.config.ts` - site settings

## Current Status

Last updated: 2026-04-23

### Documentation Coverage
- ✅ Core API fully documented
- ✅ File extra documented with examples
- ✅ JWT extra documented
- ✅ Database extra documented
- ✅ Casdoor extra documented
- ✅ Per-route error_factory documented
- ✅ AccessSubject behavior fully explained

### Known Items to Monitor
- Any changes to enforcer provider pattern (singleton + async context manager)
- Changes to reload mechanics in file/db providers
- New OAuth2 state management in Casdoor
- Performance improvements or new caching strategies

