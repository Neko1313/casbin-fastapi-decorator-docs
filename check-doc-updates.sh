#!/bin/bash

# Script to detect changes in casbin-fastapi-decorator and suggest documentation updates
# Usage: ./check-doc-updates.sh

set -e

MAIN_PROJECT="/home/user/casbin-fastapi-decorator"
DOCS_PROJECT="/home/user/casbin-fastapi-decorator-docs"

echo "📋 Documentation Sync Checker"
echo "=============================="
echo ""

# Check for changes in main project
echo "🔍 Checking main project changes..."
cd "$MAIN_PROJECT"

CHANGED_FILES=$(git diff main...HEAD --name-only 2>/dev/null || echo "")

if [ -z "$CHANGED_FILES" ]; then
    echo "✅ No changes detected from main branch"
    echo ""
else
    echo "📝 Files changed:"
    echo "$CHANGED_FILES" | sed 's/^/  - /'
    echo ""
fi

# Check for Python file changes
PYTHON_CHANGES=$(git diff main...HEAD --name-only -- '*.py' 2>/dev/null || echo "")
if [ -n "$PYTHON_CHANGES" ]; then
    echo "🐍 Python files changed:"
    echo "$PYTHON_CHANGES" | sed 's/^/  - /'
    echo ""
fi

# Check for documentation changes in main project
README_CHANGES=$(git diff main...HEAD -- README.md 2>/dev/null || echo "")
if [ -n "$README_CHANGES" ]; then
    echo "📄 README.md changes detected:"
    echo "You should update corresponding docs pages"
    echo ""
fi

# Check specific modules
echo "🔎 Module-specific checks:"
echo ""

# Check core module
if git diff main...HEAD --quiet -- 'src/casbin_fastapi_decorator/' 2>/dev/null; then
    echo "  ✅ No changes to core module"
else
    echo "  ⚠️  Changes to core module"
    echo "     → Update: docs/api-reference/permission-guard.md"
    echo "     → Update: docs/api-reference/access-subject.md"
    echo ""
fi

# Check file module
if git diff main...HEAD --quiet -- 'packages/casbin-fastapi-decorator-file/' 2>/dev/null; then
    echo "  ✅ No changes to file module"
else
    echo "  ⚠️  Changes to file module"
    echo "     → Update: docs/extras/file/overview.md"
    echo "     → Update: docs/examples/with-file.md"
    echo ""
fi

# Check JWT module
if git diff main...HEAD --quiet -- 'packages/casbin-fastapi-decorator-jwt/' 2>/dev/null; then
    echo "  ✅ No changes to JWT module"
else
    echo "  ⚠️  Changes to JWT module"
    echo "     → Update: docs/extras/jwt/overview.md"
    echo "     → Update: docs/extras/jwt/bearer-token.md"
    echo "     → Update: docs/extras/jwt/cookie.md"
    echo "     → Update: docs/examples/with-jwt.md"
    echo ""
fi

# Check DB module
if git diff main...HEAD --quiet -- 'packages/casbin-fastapi-decorator-db/' 2>/dev/null; then
    echo "  ✅ No changes to database module"
else
    echo "  ⚠️  Changes to database module"
    echo "     → Update: docs/extras/db/overview.md"
    echo "     → Update: docs/examples/with-database.md"
    echo ""
fi

# Check Casdoor module
if git diff main...HEAD --quiet -- 'packages/casbin-fastapi-decorator-casdoor/' 2>/dev/null; then
    echo "  ✅ No changes to Casdoor module"
else
    echo "  ⚠️  Changes to Casdoor module"
    echo "     → Update: docs/extras/casdoor/overview.md"
    echo "     → Update: docs/extras/casdoor/setup.md"
    echo "     → Update: docs/examples/with-casdoor.md"
    echo ""
fi

echo ""
echo "📚 Documentation project status:"
cd "$DOCS_PROJECT"

DOC_CHANGES=$(git diff main...HEAD --name-only 2>/dev/null | wc -l || echo "0")
echo "  Files changed in docs: $DOC_CHANGES"

echo ""
echo "✨ Next steps:"
echo "  1. Review the changes suggested above"
echo "  2. Update relevant documentation files"
echo "  3. Test examples if applicable"
echo "  4. Commit changes with clear message"
echo ""

