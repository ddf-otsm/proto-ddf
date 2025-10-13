# Pre-Commit Setup Guide

This guide explains the pre-commit configuration for the Proto-DDF project.

## Overview

Pre-commit hooks are configured to automatically check and fix code quality issues before commits. The configuration includes:

- **Ruff**: Fast Python linter and formatter
- **Black**: Code formatter
- **isort**: Import sorter
- **Safety**: Security vulnerability checker
- **General hooks**: Trailing whitespace, end-of-file fixes, etc.

## Installation

Pre-commit is already installed and configured. The hooks run automatically on every commit.

## Manual Usage

### Run all hooks on all files
```bash
pre-commit run --all-files
```

### Run specific hook
```bash
pre-commit run ruff --all-files
pre-commit run black --all-files
```

### Run on staged files only
```bash
pre-commit run
```

## Configuration

The pre-commit configuration is in `.pre-commit-config.yaml`. It includes:

- **Ruff**: Linting and formatting with automatic fixes
- **Black**: Consistent code formatting
- **isort**: Import sorting with Black compatibility
- **Safety**: Dependency security checks
- **General hooks**: File format standardization

## Development Workflow

1. **Stage your changes**: `git add <files>`
2. **Pre-commit runs automatically** on commit
3. **Review any fixes** made by the hooks
4. **Re-stage if needed**: `git add <files>`
5. **Complete the commit**

## Troubleshooting

### Hook fails during commit
If a hook fails and makes changes, review the changes and re-stage:
```bash
git add <modified-files>
git commit
```

### Skip hooks temporarily (not recommended)
```bash
git commit --no-verify
```

### Update hooks
```bash
pre-commit autoupdate
```

## Benefits

- **Consistent code style** across the project
- **Automatic error detection** before commits
- **Security vulnerability** scanning
- **Import organization** for better readability
- **Reduced review time** due to consistent formatting
