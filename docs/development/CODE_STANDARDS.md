# Code Standards and Documentation

## 📝 Documentation Standards

### **Function Documentation**

#### **Required Docstring Format:**
```python
def function_name(param1: Type, param2: Type) -> ReturnType:
    """
    Brief description of what the function does.
    
    Longer description if needed, explaining the purpose,
    behavior, and any important details about the function.
    
    Args:
        param1: Description of param1 and its expected values
        param2: Description of param2 and any constraints
        
    Returns:
        Description of return value and its type
        
    Raises:
        ValueError: When param1 is invalid
        ConnectionError: When network connection fails
        
    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        "processed test with 42"
        
    Note:
        Any important implementation details or gotchas
    """
```

#### **Class Documentation:**
```python
class ClassName(rx.State):
    """
    Brief description of the class purpose.
    
    This class manages [specific functionality] and provides
    [key features]. It handles [important behaviors] and
    maintains [state information].
    
    Attributes:
        attribute1: Description of what this stores
        attribute2: Description of this attribute's purpose
        
    Example:
        >>> state = ClassName()
        >>> state.method_name()
    """
```

### **Inline Comments**

#### **Good Comment Examples:**
```python
# Calculate port allocation using centralized registry
# This ensures no collisions between generator and generated apps
ports = PORT_REGISTRY.reserve_pair(app_name)

# Simulate realistic connection delay for demo purposes
# In production, this would be actual API/database connection
time.sleep(0.5)

# Map source fields to NetSuite standard fields
# Uses pattern matching to handle different naming conventions
for source_field, netsuite_field in self.field_mapping.items():
```

#### **Bad Comment Examples:**
```python
# Set variable
self.progress = 30

# Loop through records
for record in records:

# Update status
self.status = "success"
```

### **Type Hints**

#### **Required Type Annotations:**
```python
# Function parameters and returns
def process_data(data: List[Dict[str, Any]]) -> Dict[str, int]:
    pass

# Class attributes
class State(rx.State):
    records: List[Dict[str, Any]] = []
    status: str = "idle"
    count: int = 0

# Complex types
from typing import Optional, Union, Callable

def handle_callback(
    callback: Optional[Callable[[str], None]] = None
) -> Union[str, None]:
    pass
```

## 🏷️ Logging Standards

### **Log Level Usage:**

#### **DEBUG** - Detailed information for debugging
```python
logger.debug("Processing record", extra={
    "record_id": record.get("id"),
    "source": self.selected_source,
    "step": "field_mapping"
})
```

#### **INFO** - General information about program execution
```python
logger.info("Application started", extra={
    "app_name": self.project_name,
    "ports": {"backend": backend_port, "frontend": frontend_port}
})
```

#### **WARNING** - Something unexpected happened
```python
logger.warning("Port already in use, finding alternative", extra={
    "requested_port": port,
    "alternative_port": new_port
})
```

#### **ERROR** - Serious problem occurred
```python
logger.error("Failed to generate application", extra={
    "app_name": self.project_name,
    "error": str(e),
    "step": "code_generation"
}, exc_info=True)
```

#### **CRITICAL** - Program cannot continue
```python
logger.critical("Port registry corrupted", extra={
    "registry_file": registry_path,
    "backup_available": backup_exists
})
```

### **Structured Logging Format:**
```python
# Always include context
logger.info("Operation completed", extra={
    "operation": "app_generation",
    "duration_ms": duration,
    "success": True,
    "app_name": app_name,
    "ports_allocated": {"backend": backend, "frontend": frontend}
})
```

## 🎨 Console Output Standards

### **Shell Script Logging Functions:**
```bash
# Add to all shell scripts
log_info() {
    echo "ℹ️  $1" >&2
}

log_success() {
    echo "✅ $1" >&2
}

log_warning() {
    echo "⚠️  $1" >&2
}

log_error() {
    echo "❌ $1" >&2
}

log_progress() {
    echo "🔄 $1" >&2
}
```

### **Usage Examples:**
```bash
# Good
log_info "Starting application: $APP_NAME"
log_progress "Installing dependencies..."
if pip install -q -r requirements.txt; then
    log_success "Dependencies installed"
else
    log_error "Failed to install dependencies"
    exit 1
fi

# Bad
echo "Starting application"
echo "Installing dependencies..."
pip install -q -r requirements.txt
```

## 📊 Error Handling Standards

### **Python Error Handling:**
```python
def risky_operation(self):
    """Perform operation with proper error handling."""
    try:
        logger.info("Starting risky operation")
        result = self._do_operation()
        logger.info("Operation completed successfully", extra={
            "result_count": len(result)
        })
        return result
        
    except ValidationError as e:
        logger.warning("Validation failed", extra={
            "error": str(e),
            "input_data": self.input_data
        })
        self.integration_message = f"Validation error: {str(e)}"
        return None
        
    except ConnectionError as e:
        logger.error("Connection failed", extra={
            "error": str(e),
            "retry_count": self.retry_count
        })
        self.integration_message = "Connection failed. Please try again."
        return None
        
    except Exception as e:
        logger.critical("Unexpected error", extra={
            "error": str(e),
            "operation": "risky_operation"
        }, exc_info=True)
        self.integration_message = "An unexpected error occurred."
        return None
```

### **Shell Script Error Handling:**
```bash
# Check prerequisites
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is required but not installed"
    exit 1
fi

# Validate inputs
if [ -z "$APP_NAME" ]; then
    log_error "APP_NAME is required"
    exit 1
fi

# Handle command failures
if ! pip install -q -r requirements.txt; then
    log_error "Failed to install dependencies"
    log_info "Check requirements.txt and try again"
    exit 1
fi
```

## 🔍 Code Review Checklist

### **Before Committing:**
- [ ] All functions have proper docstrings
- [ ] Type hints are complete and accurate
- [ ] Logging uses appropriate levels
- [ ] Error handling covers expected cases
- [ ] Console output is structured and informative
- [ ] Comments explain "why", not "what"
- [ ] No TODO/FIXME comments in production code
- [ ] All public APIs are documented

### **Code Quality:**
- [ ] Functions are single-purpose
- [ ] Class names are descriptive
- [ ] Variable names are clear
- [ ] No magic numbers
- [ ] Consistent formatting
- [ ] No dead code

---

**Next Steps:**
- Apply these standards to existing code
- Create linting rules to enforce standards
- Add pre-commit hooks for documentation checks