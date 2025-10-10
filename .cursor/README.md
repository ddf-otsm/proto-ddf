# Cursor Configuration Directory

This directory contains project-specific Cursor AI configuration, including rules, agents, and other AI-related settings.

## 📁 Directory Structure

```
.cursor/
├── rules/              # Project-specific AI rules (.mdc files)
├── AGENTS.md          # Guide for AI agents and rules
└── README.md          # This file
```

## 🤖 Rules System

### What are Cursor Rules?

Cursor rules are instructions that control how AI agents behave in your project. They provide:

- **Consistent AI behavior** across team members
- **Project-specific knowledge** and conventions
- **Automated workflows** and templates
- **Code quality standards** enforcement

### Rule Types

| Type                | Description                                | Use Case                   |
| ------------------- | ------------------------------------------ | -------------------------- |
| **Always**          | Loaded in every conversation               | Critical project standards |
| **Auto Attached**   | Loaded when matching files are referenced  | File-specific conventions  |
| **Agent Requested** | AI decides when to load based on relevance | Contextual guidance        |
| **Manual**          | Only loaded when explicitly mentioned      | Specialized workflows      |

## 📋 Quick Start

### 1. Understanding Rule Format

Each rule file (`.mdc`) requires YAML frontmatter:

```yaml
---
description: USE WHEN [condition] to [outcome]
globs: **/*.ts, **/*.tsx  # File patterns (optional)
alwaysApply: false        # Load in all conversations
---

# Rule Content
Your instructions here...
```

### 2. Creating Your First Rule

```bash
# Create a new rule file
touch .cursor/rules/my-coding-standards.mdc
```

````yaml
---
description: USE WHEN writing TypeScript code to ensure consistent style and quality
globs: **/*.ts, **/*.tsx
alwaysApply: false
---

# TypeScript Coding Standards

## Required Practices
- Use strict type checking
- Prefer `const` over `let`
- Use meaningful variable names
- Add JSDoc for public APIs

## Examples

✅ **Good:**
```typescript
const userName: string = "john_doe";
````

❌ **Bad:**

```typescript
let un = "john_doe";
```

````

### 3. Testing Your Rule

1. Open Cursor
2. Start a new chat
3. Reference a TypeScript file
4. Your rule should auto-attach and appear in the sidebar

## 🔧 Rule Categories

### Core Rules (Always Apply)

- **Terminal Safety**: Prevents dangerous commands
- **Git Workflow**: Ensures proper version control
- **File Lifecycle**: Manages file organization

### Development Rules (Auto Attached)

- **TypeScript Standards**: Code quality for `.ts`/`.tsx`
- **React Patterns**: Component best practices
- **Testing Conventions**: Test file standards
- **API Design**: Backend service patterns

### Workflow Rules (Agent Requested)

- **Deployment Procedures**: Release management
- **Security Reviews**: Security-focused guidance
- **Performance Optimization**: Performance best practices

## 📚 Best Practices

### Writing Effective Rules

1. **Be Specific**: Clear, actionable instructions
2. **Use Examples**: Show correct vs incorrect patterns
3. **Keep Focused**: One concern per rule (max 500 lines)
4. **Reference Files**: Use `@filename` for context
5. **Test Thoroughly**: Verify rule behavior in practice

### Description Guidelines

- **Format**: "USE WHEN [trigger] to [outcome]"
- **Length**: Under 120 characters
- **Clarity**: Specific context and purpose
- **Verbs**: Use present participle (creating, modifying, debugging)

### Glob Pattern Examples

```yaml
# TypeScript files
globs: **/*.ts, **/*.tsx

# React components
globs: **/components/**/*.tsx

# Test files
globs: **/*.test.*, **/*.spec.*

# Configuration files
globs: **/*.config.*, **/.*rc.*

# API routes
globs: **/api/**, **/routes/**

# Documentation
globs: **/*.md, **/docs/**

# Multiple patterns
globs: **/*.js, **/*.ts, **/*.jsx, **/*.tsx
````

## 🚀 Advanced Usage

### Rule Composition

```yaml
# Reference other rules or files
@typescript-standards.mdc
@react-patterns.mdc
```

### Structured Rules (Complex Logic)

```xml
<rule>
  <meta>
    <title>API Design Standards</title>
    <description>REST API consistency rules</description>
  </meta>
  <requirements>
    <requirement priority="high">
      <description>Use proper HTTP status codes</description>
      <examples>
        <correct-example>
          return res.status(201).json(data);
        </correct-example>
        <incorrect-example>
          return res.json(data);
        </incorrect-example>
      </examples>
    </requirement>
  </requirements>
</rule>
```

### Rule Generation

Use the `/Generate Cursor Rules` command in chat to create rules from conversations:

```
Me: I want to enforce using absolute imports in this project
AI: I'll create a rule for absolute import standards...
```

## 🛠️ Troubleshooting

### Common Issues

| Issue                       | Solution                                           |
| --------------------------- | -------------------------------------------------- |
| Rule not loading            | Check frontmatter format and file extension        |
| "May never be used" warning | Add proper `description` field                     |
| Rule conflicts              | Use appropriate `alwaysApply` and `globs` settings |
| Context overflow            | Split large rules into smaller, focused ones       |

### Debugging Rules

1. **Check Active Rules**: Look at Agent sidebar
2. **Test Manual Loading**: Use `@ruleName` in chat
3. **Validate YAML**: Ensure proper frontmatter syntax
4. **Review Logs**: Check Cursor console for errors

### Performance Tips

- Keep rules under 500 lines
- Use specific glob patterns
- Avoid overlapping rule coverage
- Regular cleanup of unused rules

## 📖 Learning Resources

### Documentation

- [Cursor Rules Official Docs](https://docs.cursor.com/context/rules-for-ai)
- [AGENTS.md](./AGENTS.md) - Detailed agent guide

### Community

- [Cursor Forum](https://forum.cursor.com/c/how-to/8)
- [Best Practices Discussion](https://forum.cursor.com/t/my-take-on-cursor-rules/67535)
- [Rule Generator Tools](https://github.com/bmadcode/cursor-auto-rules)

### Examples

- Browse `.cursor/rules/` for real-world examples
- [Community Rule Collections](https://github.com/PatrickJS/awesome-cursorrules)

## 🔄 Migration Guide

### From .cursorrules (Legacy)

1. **Backup**: Save existing `.cursorrules` content
2. **Split**: Break into focused `.mdc` files
3. **Convert**: Add proper frontmatter to each rule
4. **Test**: Verify new rules work as expected
5. **Cleanup**: Remove old `.cursorrules` file

### Updating Existing Rules

1. **Audit**: Review all `.mdc` files for missing frontmatter
2. **Standardize**: Use consistent "USE WHEN" descriptions
3. **Optimize**: Add appropriate glob patterns
4. **Validate**: Test rule loading and effectiveness

## 📊 Rule Metrics

Track rule effectiveness:

- **Usage frequency**: Which rules are loaded most
- **Context relevance**: How well rules match actual needs
- **Team adoption**: Consistency across team members
- **Quality impact**: Improvement in code quality

---

**Need Help?** Check [AGENTS.md](./AGENTS.md) for detailed guidance or visit the [Cursor Forum](https://forum.cursor.com/) for community support.
