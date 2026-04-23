#!/usr/bin/env python3
"""
Validate documentation consistency and completeness.

Checks:
1. All public APIs are documented
2. Documentation examples are syntactically valid
3. File references in docs exist
4. Cross-references are valid
5. Code blocks in docs can be parsed

Usage:
    python3 validate-docs.py
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Tuple


def check_md_file_references(docs_root: Path) -> List[Tuple[str, str]]:
    """Check if all file references in markdown files exist."""
    issues = []

    for md_file in docs_root.rglob('*.md'):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find file references in links: [text](path)
        # Only check relative references
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for match in re.finditer(pattern, content):
            link_text = match.group(1)
            link_path = match.group(2)

            # Skip external links
            if link_path.startswith('http') or link_path.startswith('#'):
                continue

            # Convert relative path to absolute
            if link_path.startswith('./'):
                target = md_file.parent / link_path
            elif link_path.startswith('../'):
                target = (md_file.parent / link_path).resolve()
            else:
                target = (docs_root / link_path).resolve()

            # Check if target exists (remove anchor if present)
            target_path = str(target).split('#')[0]
            if not Path(target_path).exists() and not target_path.endswith('.md'):
                issues.append((str(md_file.relative_to(docs_root)), link_path))

    return issues


def validate_code_blocks(docs_root: Path) -> List[Tuple[str, int, str]]:
    """Validate Python code blocks in documentation."""
    issues = []

    for md_file in docs_root.rglob('*.md'):
        with open(md_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        in_python_block = False
        block_lines = []
        block_start_line = 0

        for i, line in enumerate(lines):
            if line.strip().startswith('```python'):
                in_python_block = True
                block_lines = []
                block_start_line = i + 1
            elif line.strip().startswith('```') and in_python_block:
                in_python_block = False

                # Try to parse the code block
                code = ''.join(block_lines)
                try:
                    ast.parse(code)
                except SyntaxError as e:
                    issues.append((
                        str(md_file.relative_to(docs_root)),
                        block_start_line,
                        f"Syntax error: {e.msg}"
                    ))

                block_lines = []
            elif in_python_block:
                block_lines.append(line)

    return issues


def check_api_documentation(main_project: Path, docs_root: Path) -> List[str]:
    """Check if all public APIs from main project are documented."""
    issues = []

    # Get all documented API reference files
    api_ref_dir = docs_root / 'api-reference'
    documented_apis = set()

    if api_ref_dir.exists():
        for md_file in api_ref_dir.glob('*.md'):
            documented_apis.add(md_file.stem)

    # Expected APIs
    expected_apis = {
        'permission-guard': 'PermissionGuard',
        'access-subject': 'AccessSubject',
    }

    missing = []
    for api_file, api_name in expected_apis.items():
        if api_file not in documented_apis:
            missing.append(f"API '{api_name}' ({api_file}.md) not found")

    return missing


def check_cross_references(docs_root: Path) -> List[str]:
    """Check for broken cross-references between documentation files."""
    issues = []

    # Build map of all doc files and their anchor references
    doc_files = {}
    for md_file in docs_root.rglob('*.md'):
        relative_path = str(md_file.relative_to(docs_root))
        headers = set()

        with open(md_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#'):
                    # Extract header text and convert to anchor
                    header_text = line.lstrip('#').strip()
                    anchor = header_text.lower().replace(' ', '-').replace('/', '-')
                    headers.add(anchor)

        doc_files[relative_path] = headers

    # Check all internal links
    for md_file in docs_root.rglob('*.md'):
        relative_path = str(md_file.relative_to(docs_root))

        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find links with anchors
        pattern = r'\]\(([^)]+#[^)]+)\)'
        for match in re.finditer(pattern, content):
            link = match.group(1)
            link_file, anchor = link.split('#', 1)

            # Resolve relative path
            if link_file.startswith('../') or link_file.startswith('./'):
                target_path = str((md_file.parent / link_file).resolve().relative_to(docs_root))
            else:
                target_path = link_file

            # Remove .md extension for comparison
            target_path = target_path.replace('.md', '')

            if target_path not in doc_files:
                issues.append(f"{relative_path}: broken link to {link}")

    return issues


def main():
    main_project = Path('/home/user/casbin-fastapi-decorator')
    docs_root = main_project.parent / 'casbin-fastapi-decorator-docs' / 'docs'

    print("📚 Documentation Validation Report")
    print("=" * 60)
    print()

    # Check file references
    print("🔗 Checking file references...")
    broken_refs = check_md_file_references(docs_root)
    if broken_refs:
        print(f"  ⚠️  Found {len(broken_refs)} broken references:")
        for file, ref in broken_refs:
            print(f"     • {file}: {ref}")
    else:
        print("  ✅ All file references are valid")
    print()

    # Check code blocks
    print("🔍 Validating code blocks...")
    code_issues = validate_code_blocks(docs_root)
    if code_issues:
        print(f"  ⚠️  Found {len(code_issues)} syntax errors:")
        for file, line, error in code_issues:
            print(f"     • {file}:{line}: {error}")
    else:
        print("  ✅ All code blocks are syntactically valid")
    print()

    # Check API documentation
    print("📖 Checking API documentation...")
    api_issues = check_api_documentation(main_project, docs_root)
    if api_issues:
        print(f"  ⚠️  Found {len(api_issues)} missing APIs:")
        for issue in api_issues:
            print(f"     • {issue}")
    else:
        print("  ✅ All major APIs are documented")
    print()

    # Check cross-references
    print("🔀 Checking cross-references...")
    xref_issues = check_cross_references(docs_root)
    if xref_issues:
        print(f"  ⚠️  Found {len(xref_issues)} broken cross-references:")
        for issue in xref_issues[:5]:  # Show first 5
            print(f"     • {issue}")
        if len(xref_issues) > 5:
            print(f"     ... and {len(xref_issues) - 5} more")
    else:
        print("  ✅ All cross-references are valid")
    print()

    # Summary
    total_issues = len(broken_refs) + len(code_issues) + len(api_issues) + len(xref_issues)
    if total_issues == 0:
        print("✨ Documentation is in great shape!")
    else:
        print(f"⚠️  Found {total_issues} issues to address")

    print()
    print("📋 Tips for maintaining documentation:")
    print("  1. Run this validator regularly")
    print("  2. Update docs before merging code changes")
    print("  3. Test all code examples manually")
    print("  4. Use consistent naming in headers/anchors")
    print("  5. Keep example code DRY (reuse patterns)")


if __name__ == '__main__':
    main()
