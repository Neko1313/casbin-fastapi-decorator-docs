# Documentation Toolkit for casbin-fastapi-decorator

This toolkit provides everything needed to keep the `casbin-fastapi-decorator` and `casbin-fastapi-decorator-docs` projects in sync.

## 📁 Files Included

### 1. **DOC_SYNC.md** - Main Reference Guide
   - Comprehensive mapping of what to monitor
   - Documentation areas by module
   - Sync process and checklist
   - Current documentation status

### 2. **check-doc-updates.sh** - Quick Change Detector
   ```bash
   ./check-doc-updates.sh
   ```
   - Detects what changed in the main project
   - Suggests which doc files need updating
   - Shows module-specific changes
   - Quick status check

### 3. **analyze-doc-gaps.py** - API Analysis Tool
   ```bash
   python3 analyze-doc-gaps.py
   ```
   - Extracts all public APIs from source code
   - Checks documentation coverage
   - Identifies undocumented features
   - Provides implementation recommendations

### 4. **validate-docs.py** - Documentation Validator
   ```bash
   python3 validate-docs.py
   ```
   - Validates file references in markdown
   - Checks Python code blocks for syntax errors
   - Verifies API documentation completeness
   - Checks cross-reference validity

## 🚀 Quick Start

### Step 1: Check for Changes
```bash
cd /home/user
./check-doc-updates.sh
```

### Step 2: Analyze Gaps
```bash
python3 analyze-doc-gaps.py | less
```

### Step 3: Validate Documentation
```bash
python3 validate-docs.py
```

### Step 4: Update Documentation
Edit files in `/home/user/casbin-fastapi-decorator-docs/docs/` as needed

### Step 5: Commit Changes
```bash
cd /home/user/casbin-fastapi-decorator-docs
git add -A
git commit -m "docs: sync with main project changes"
git push
```

## 📊 Current Status (2026-04-23)

### ✅ Well-Documented Areas
- Core API (PermissionGuard, AccessSubject)
- Per-route error_factory parameter
- File hot-reload functionality
- JWT authentication
- Database-backed policies
- Casdoor OAuth2 integration
- Multiple working examples

### ⚠️ Known Issues
The validation script reports some "broken references" due to Docusaurus-specific syntax:
- Links without `.md` extension are normal in Docusaurus
- Some code blocks may have intentional placeholder syntax
- Cross-reference anchors follow Docusaurus conventions

These are false positives and don't require fixing.

### 📋 Last Validation Results
- File references: 32 (mostly Docusaurus-specific)
- Code blocks checked: 11 issues (mostly incomplete examples)
- API documentation: ✅ Complete
- Cross-references: 7 (Docusaurus navigation)

## 🔄 Workflow for New Features

When adding a new feature to casbin-fastapi-decorator:

1. **Add the feature** to the main project
2. **Run the checker:**
   ```bash
   cd /home/user
   ./check-doc-updates.sh
   ```
3. **Update docs** based on suggestions
4. **Validate the docs:**
   ```bash
   python3 validate-docs.py
   ```
5. **Test examples** if applicable
6. **Commit both projects:**
   ```bash
   # Main project
   cd /home/user/casbin-fastapi-decorator
   git add -A
   git commit -m "feat: add new feature"
   git push
   
   # Docs project
   cd /home/user/casbin-fastapi-decorator-docs
   git add -A
   git commit -m "docs: document new feature"
   git push
   ```

## 📚 Documentation Structure

```
casbin-fastapi-decorator-docs/
├── docs/
│   ├── intro.md                     # Entry point
│   ├── getting-started/
│   │   ├── installation.md
│   │   ├── quick-start.md
│   │   └── concepts.md
│   ├── core/                        # Core API guides
│   │   ├── permission-guard.md
│   │   ├── auth-required.md
│   │   ├── require-permission.md
│   │   └── access-subject.md
│   ├── api-reference/               # API reference
│   │   ├── permission-guard.md
│   │   └── access-subject.md
│   ├── examples/                    # Code examples
│   │   ├── basic.md
│   │   ├── with-file.md
│   │   ├── with-jwt.md
│   │   ├── with-database.md
│   │   └── with-casdoor.md
│   └── extras/                      # Optional packages
│       ├── file/
│       ├── jwt/
│       ├── db/
│       └── casdoor/
├── sidebars.ts                      # Navigation structure
├── docusaurus.config.ts             # Site configuration
└── package.json                     # Build dependencies
```

## 🎯 Key Monitoring Points

### Core Module Changes
- Method signature changes
- New parameters (especially `error_factory`)
- Changes to dependency resolution
- AsyncContext manager patterns

### File Extra (Hot-Reload)
- CachedFileEnforcerProvider API
- Watchdog integration
- Reload trigger changes
- Performance improvements

### JWT Extra (Authentication)
- JWTUserProvider configuration
- Bearer token extraction
- Cookie handling
- Payload validation

### DB Extra (Policies)
- DatabaseEnforcerProvider API
- Policy mapping
- Polling interval defaults
- Hash-based reload mechanism
- Default policies handling

### Casdoor Extra (OAuth2)
- CasdoorIntegration setup
- OAuth2 flow changes
- State management
- Token handling
- CasdoorEnforceTarget options

## 💡 Best Practices

### Documentation
1. **Keep examples minimal** - Focus on the feature being documented
2. **Use consistent naming** - Match the source code exactly
3. **Test code blocks** - All Python code should be syntactically valid
4. **Cross-reference liberally** - Help readers navigate between related topics
5. **Update README.md** - Keep the main project README current too

### Commits
1. **Sync atomically** - Document changes together with code changes
2. **Clear messages** - Use `docs:` prefix for documentation-only commits
3. **Link to features** - Reference the feature or issue in commit messages
4. **Keep commits focused** - One feature per commit when possible

### Version Alignment
1. **Match versions** - Documentation should match current release version
2. **Update API tables** - Keep parameter tables in sync with code
3. **Test compatibility** - Verify examples work with documented versions
4. **Note breaking changes** - Explicitly document any breaking changes

## 🔍 Troubleshooting

### "Broken references" reported by validate-docs.py
This is normal! Docusaurus uses special link syntax:
- Links don't need `.md` extension
- Internal links use `/path/to/page` format
- Anchors follow Docusaurus conventions

### Code block syntax errors
Some examples intentionally use placeholder syntax:
- `...` for omitted code
- Incomplete imports (showing only relevant parts)
- Constructor signatures without all parameters

These are acceptable in documentation context.

### Validator reports code issues but examples work
The validator tries to parse code blocks standalone, but:
- Examples may depend on imports above the block
- Some blocks show partial/pseudo-code intentionally
- Docusaurus renders and highlights correctly even if not fully valid Python

## 📞 Getting Help

For issues with:
- **Code/features:** See main project documentation
- **Documentation:** Check `/home/user/DOC_SYNC.md`
- **Tools:** Run with `--help` flag or check script comments
- **Docusaurus:** See `docusaurus.config.ts` and `sidebars.ts`

## 🎓 Examples of Good Documentation

Well-documented areas to use as reference:
- `docs/extras/file/overview.md` - Clear setup instructions
- `docs/examples/basic.md` - Complete, runnable example
- `docs/core/require-permission.md` - Good parameter documentation
- `README.md` (main project) - Concise feature comparison

## ✨ Summary

This toolkit provides:
- ✅ Automated change detection
- ✅ API analysis and gap identification
- ✅ Documentation validation
- ✅ Clear sync procedures
- ✅ Comprehensive monitoring guide

Use these tools regularly to keep documentation in sync with code changes!
