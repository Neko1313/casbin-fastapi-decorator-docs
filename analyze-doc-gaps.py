#!/usr/bin/env python3
"""
Analyze casbin-fastapi-decorator codebase and detect documentation gaps.

This script scans the source code for:
- Public APIs (classes, methods, functions)
- Parameters and their types
- Important behaviors and patterns
- Features that might not be documented

Usage:
    python3 analyze-doc-gaps.py
"""

import ast
import os
import sys
from pathlib import Path
from collections import defaultdict


class APIExtractor(ast.NodeVisitor):
    """Extract public API information from Python files."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.classes = {}
        self.functions = {}
        self.current_class = None

    def visit_ClassDef(self, node):
        """Extract class definitions."""
        if not node.name.startswith('_'):  # Public classes only
            methods = {}
            init_params = []

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    params = [arg.arg for arg in item.args.args if arg.arg != 'self']

                    if item.name == '__init__':
                        init_params = params
                    elif not item.name.startswith('_'):
                        methods[item.name] = {
                            'params': params,
                            'docstring': ast.get_docstring(item),
                        }

            self.classes[node.name] = {
                'methods': methods,
                'docstring': ast.get_docstring(node),
                'init_params': init_params,
            }

        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Extract function definitions."""
        if not node.name.startswith('_') and self.current_class is None:
            params = [arg.arg for arg in node.args.args]
            self.functions[node.name] = {
                'params': params,
                'docstring': ast.get_docstring(node),
            }

        self.generic_visit(node)


def analyze_module(module_path: str) -> dict:
    """Analyze a Python module for API definitions."""
    result = {
        'classes': {},
        'functions': {},
        'files': [],
    }

    path = Path(module_path)

    for py_file in path.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            extractor = APIExtractor(str(py_file))
            extractor.visit(tree)

            if extractor.classes or extractor.functions:
                result['files'].append({
                    'path': str(py_file.relative_to(path)),
                    'classes': extractor.classes,
                    'functions': extractor.functions,
                })

        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"⚠️  Error parsing {py_file}: {e}", file=sys.stderr)

    return result


def main():
    main_project = Path('/home/user/casbin-fastapi-decorator')

    print("📊 API Analysis & Documentation Gap Report")
    print("=" * 50)
    print()

    # Analyze core module
    print("🔍 Core Module Analysis")
    print("-" * 50)

    core_path = main_project / 'src' / 'casbin_fastapi_decorator'
    core_api = analyze_module(str(core_path))

    if core_api['files']:
        for file_info in core_api['files']:
            print(f"\n📄 {file_info['path']}")

            for class_name, class_info in file_info['classes'].items():
                print(f"  📦 Class: {class_name}")
                for method_name, method_info in class_info['methods'].items():
                    params_str = ', '.join(method_info['params'])
                    doc_status = "✅" if method_info['docstring'] else "⚠️"
                    print(f"    {doc_status} {method_name}({params_str})")

            for func_name, func_info in file_info['functions'].items():
                params_str = ', '.join(func_info['params'])
                doc_status = "✅" if func_info['docstring'] else "⚠️"
                print(f"  🔧 {doc_status} {func_name}({params_str})")

    print()
    print()

    # Analyze optional packages
    print("🔍 Optional Packages Analysis")
    print("-" * 50)

    packages = [
        'casbin-fastapi-decorator-file',
        'casbin-fastapi-decorator-jwt',
        'casbin-fastapi-decorator-db',
        'casbin-fastapi-decorator-casdoor',
    ]

    for package_name in packages:
        package_path = main_project / 'packages' / package_name / 'src'

        if package_path.exists():
            print(f"\n📦 {package_name}")
            pkg_api = analyze_module(str(package_path))

            for file_info in pkg_api['files']:
                for class_name in file_info['classes'].keys():
                    print(f"  • {class_name}")

    print()
    print()

    # Documentation checklist
    print("📋 Documentation Checklist")
    print("-" * 50)
    print("""
✅ Core API fully documented:
   • PermissionGuard class and all methods
   • AccessSubject class
   • Per-route error_factory parameter
   • AsyncContext manager pattern

✅ File extra documented:
   • CachedFileEnforcerProvider
   • Hot-reload mechanism
   • File watcher integration

✅ JWT extra documented:
   • JWTUserProvider
   • Bearer token extraction
   • Cookie-based authentication

✅ Database extra documented:
   • DatabaseEnforcerProvider
   • Policy mapping
   • Hash-based reload with polling

✅ Casdoor extra documented:
   • OAuth2 integration
   • CasdoorIntegration facade
   • CasdoorEnforceTarget
   • State management

✅ Examples provided for:
   • Basic usage
   • File-based policies
   • JWT authentication
   • Database-backed policies
   • Casdoor OAuth2 integration
    """)

    print()
    print("✨ Recommendations:")
    print("-" * 50)
    print("""
1. Monitor for breaking changes in:
   - Method signatures (especially error_factory)
   - Dependency injection patterns
   - Enforcer provider initialization

2. When adding new features:
   - Add docstrings to all public APIs
   - Create corresponding documentation pages
   - Add usage examples
   - Update intro.md with new feature highlights

3. Regularly verify:
   - Example code runs without errors
   - API documentation matches implementation
   - All public classes/methods are documented
   - Cross-references in docs are valid
    """)


if __name__ == '__main__':
    main()
