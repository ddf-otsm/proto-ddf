# Deployer DDF Module - AI Agents & Development Guide

## Overview

This guide covers the professional AI-assisted development workflows for the Deployer DDF Module project. Our AI agents follow strict terminal execution rules, implement comprehensive test infrastructure, and maintain enterprise-grade code quality standards.

## Current AI Agent Capabilities (2025-07-24)

### **Professional Test Infrastructure**

- ✅ **1,200+ Tests Orchestration** - Comprehensive test framework management
- ✅ **Framework-Specific Handling** - Jest, Python, BATS, Shell script execution
- ✅ **Conditional Test Execution** - Environment-aware test skipping
- ✅ **Progressive Timeout Strategy** - Optimized execution timeouts
- ✅ **Professional Logging** - Color-coded output with error handling

### **Dynamic Port Configuration System**

- ✅ **Hardcoded Port Elimination** - All ports now dynamically configurable
- ✅ **Environment Variable Support** - Runtime port configuration
- ✅ **Service Discovery Integration** - Automatic service endpoint resolution
- ✅ **Port Conflict Resolution** - Automatic port availability checking

### **Terminal Command Execution Safety (4_21 Rules)**

- ✅ **Mandatory Timeouts** - All commands must use timeout
- ✅ **Echo Statement Prohibition** - No echo statements in terminal commands
- ✅ **Command Length Limits** - Maximum 200 characters per command
- ✅ **Chain Operation Limits** - Maximum 2 operations per command chain
- ✅ **Console Output Transparency** - All command outputs visible

## AI Agent Development Workflows

## Rule Types

### 1. Project Rules (Recommended)

- **Location**: `.cursor/rules/*.mdc`
- **Scope**: Project-specific, version-controlled
- **Format**: MDC (Markdown with YAML frontmatter)

### 2. User Rules

- **Location**: Cursor Settings > Rules
- **Scope**: Global across all projects
- **Format**: Plain text

### 3. Legacy .cursorrules

- **Location**: Project root
- **Status**: Deprecated, migrate to Project Rules

## Rule Frontmatter Format

Every `.mdc` rule file must have proper YAML frontmatter:

```yaml
---
description: USE WHEN [trigger condition] to [outcome/purpose]
globs: [file patterns or empty]
alwaysApply: [true/false]
---
```

### Frontmatter Fields

- **description**: Clear trigger condition using "USE WHEN" pattern
- **globs**: File patterns for auto-attachment (use glob syntax)
- **alwaysApply**: Set to `true` for critical rules that should always load

### Rule Type Mapping

| Rule Type       | alwaysApply | globs    | description |
| --------------- | ----------- | -------- | ----------- |
| Always          | true        | empty    | Optional    |
| Auto Attached   | false       | required | Optional    |
| Agent Requested | false       | empty    | required    |
| Manual          | false       | empty    | empty       |

## Best Practices

### Writing Effective Rules

1. **Be Specific**: Use concrete, actionable instructions
2. **Keep Focused**: One rule per concern (max 500 lines)
3. **Use Examples**: Provide correct and incorrect examples
4. **Reference Files**: Use `@filename` to include context files
5. **Consistent Format**: Follow the pseudo-XML structure for complex rules

### Description Guidelines

- Start with "USE WHEN" for trigger conditions
- Be specific about the context (file types, actions, etc.)
- Keep under 120 characters for optimal AI processing
- Use present participle verbs (creating, modifying, debugging)

### Glob Pattern Examples

```yaml
# TypeScript files
globs: **/*.ts, **/*.tsx

# React components
globs: **/components/**/*.tsx

# Configuration files
globs: **/*.config.*, **/.*rc.*

# API routes
globs: **/api/**, **/routes/**

# Test files
globs: **/*.test.*, **/*.spec.*

# Documentation
globs: **/*.md, **/docs/**
```

## Agent Interaction

### How Agents Use Rules

1. **Context Loading**: Rules are loaded based on file patterns or descriptions
2. **Priority System**: Always > Auto Attached > Agent Requested > Manual
3. **Context Window**: Rules are included in model context as system instructions
4. **Active Rules**: Visible in Agent sidebar during conversations

### Rule Selection

- **Auto Attached**: Triggered when matching files are referenced
- **Agent Requested**: AI decides based on description relevance
- **Manual**: Only when explicitly mentioned with `@ruleName`
- **Always**: Included in every conversation

## Advanced Patterns

### Structured Rule Format

For complex rules, use pseudo-XML structure:

```xml
<rule>
  <meta>
    <title>Rule Title</title>
    <description>What this rule enforces</description>
  </meta>
  <requirements>
    <requirement priority="high">
      <description>Clear requirement</description>
      <examples>
        <correct-example><![CDATA[
          // Valid code example
        ]]></correct-example>
        <incorrect-example><![CDATA[
          // Invalid code example
        ]]></incorrect-example>
      </examples>
    </requirement>
  </requirements>
  <references>
    <reference href="other-rule.mdc">Related rule</reference>
  </references>
</rule>
```

### Rule Composition

- Use `@filename` to reference other files
- Chain rules using references
- Keep dependencies minimal
- Document rule relationships

## Troubleshooting

### Common Issues

1. **Rule not applying**: Check frontmatter format and file extension
2. **Empty description warning**: Add meaningful description
3. **Conflicting rules**: Use priority and scope appropriately
4. **Context overflow**: Keep rules concise, split large rules

### Debugging Rules

```bash
# Check rule status in Cursor
# 1. Open Agent sidebar
# 2. Look for active rules indicator
# 3. Use @ruleName to test manual loading

# Validate frontmatter format
# Ensure YAML is properly formatted
# Check for required fields
```

## Migration Guide

### From .cursorrules to Project Rules

1. Create `.cursor/rules/` directory
2. Split large .cursorrules into focused .mdc files
3. Add proper frontmatter to each rule
4. Test rule loading and behavior
5. Remove .cursorrules file

### Updating Legacy Rules

1. Add missing frontmatter
2. Update descriptions to "USE WHEN" format
3. Add appropriate glob patterns
4. Test rule effectiveness

## Examples

See the `.cursor/rules/` directory for examples of:

- Terminal command safety
- Git workflow rules
- TypeScript/ESLint standards
- Testing conventions
- Deployment practices

## Resources

- [Cursor Documentation](https://docs.cursor.com/context/rules-for-ai)
- [Community Rules](https://forum.cursor.com/c/how-to/8)
- [Rule Generator Tools](https://github.com/bmadcode/cursor-auto-rules)
- [Best Practices Guide](https://forum.cursor.com/t/my-take-on-cursor-rules/67535)
