# Error Handling Architecture

## 🎯 Overview

This document establishes comprehensive error handling patterns for Proto-DDF, ensuring robust error recovery, user-friendly messages, and effective debugging.

## 📊 Current Error Handling Analysis

### **Issues Found:**
- **Inconsistent error handling** across components
- **Generic error messages** without context
- **No error recovery strategies**
- **Missing error categorization**
- **No user-friendly error reporting**

### **Current Error Patterns:**
```python
# Current (problematic):
try:
    # operation
    pass
except Exception as e:
    logger.error(f"Error: {e}")
    self.message = f"Error: {str(e)}"
```

## 🏗️ Enhanced Error Handling Architecture

### **1. Error Categories**

#### **System Errors (Critical):**
```python
class SystemError(Exception):
    """Critical system errors that prevent operation."""
    def __init__(self, message: str, component: str, **context):
        self.message = message
        self.component = component
        self.context = context
        super().__init__(message)

# Usage:
if not is_port_available(port):
    raise SystemError(
        "No available ports in range",
        component="port_registry",
        requested_range="3000-5000",
        available_ports=available_ports
    )
```

#### **Validation Errors (User Input):**
```python
class ValidationError(Exception):
    """User input validation errors."""
    def __init__(self, message: str, field: str, value: Any, **context):
        self.message = message
        self.field = field
        self.value = value
        self.context = context
        super().__init__(message)

# Usage:
if not self.project_name or len(self.project_name) < 3:
    raise ValidationError(
        "Project name must be at least 3 characters",
        field="project_name",
        value=self.project_name,
        min_length=3
    )
```

#### **Integration Errors (External Systems):**
```python
class IntegrationError(Exception):
    """External system integration errors."""
    def __init__(self, message: str, system: str, operation: str, **context):
        self.message = message
        self.system = system
        self.operation = operation
        self.context = context
        super().__init__(message)

# Usage:
if not self._test_connection(source_url):
    raise IntegrationError(
        "Failed to connect to data source",
        system="external_api",
        operation="connection_test",
        source_url=source_url,
        timeout=30
    )
```

### **2. Error Recovery Strategies**

#### **Retry with Exponential Backoff:**
```python
import time
import random
from functools import wraps

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    """Decorator for retry with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (ConnectionError, TimeoutError) as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error("Max retries exceeded", extra={
                            "function": func.__name__,
                            "attempts": max_retries + 1,
                            "error": str(e)
                        })
                        break

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)

                    logger.warning("Retrying operation", extra={
                        "function": func.__name__,
                        "attempt": attempt + 1,
                        "delay_seconds": delay,
                        "error": str(e)
                    })
                    time.sleep(delay)
                except Exception as e:
                    # Don't retry for non-retryable errors
                    logger.error("Non-retryable error", extra={
                        "function": func.__name__,
                        "error": str(e)
                    })
                    raise

            raise last_exception
        return wrapper
    return decorator

# Usage:
@retry_with_backoff(max_retries=3, base_delay=1.0)
def connect_to_source(self, source_url: str):
    # Connection logic
    pass
```

#### **Circuit Breaker Pattern:**
```python
class CircuitBreaker:
    """Circuit breaker for external service calls."""

    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise IntegrationError(
                    "Circuit breaker is OPEN",
                    system="circuit_breaker",
                    operation=func.__name__
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning("Circuit breaker opened", extra={
                "failure_count": self.failure_count,
                "threshold": self.failure_threshold
            })

# Usage:
circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=30.0)

def call_external_api(self, endpoint: str):
    return circuit_breaker.call(self._make_api_call, endpoint)
```

### **3. User-Friendly Error Messages**

#### **Error Message Templates:**
```python
class ErrorMessageProvider:
    """Provides user-friendly error messages."""

    ERROR_TEMPLATES = {
        "validation": {
            "project_name_required": "Please provide a project name",
            "project_name_too_short": "Project name must be at least 3 characters",
            "invalid_characters": "Project name contains invalid characters. Use letters, numbers, and hyphens only"
        },
        "system": {
            "port_unavailable": "No available ports found. Please try again in a moment",
            "disk_space_low": "Insufficient disk space to create application",
            "permission_denied": "Permission denied. Please check file permissions"
        },
        "integration": {
            "connection_failed": "Unable to connect to data source. Please check your connection",
            "authentication_failed": "Authentication failed. Please check your credentials",
            "timeout": "Request timed out. The service may be slow, please try again"
        }
    }

    @classmethod
    def get_message(cls, category: str, error_code: str, **context) -> str:
        """Get user-friendly error message."""
        template = cls.ERROR_TEMPLATES.get(category, {}).get(error_code, "An error occurred")

        # Format template with context
        try:
            return template.format(**context)
        except KeyError:
            return template
```

#### **Error Context Enhancement:**
```python
def enhance_error_context(error: Exception, context: dict) -> dict:
    """Enhance error with additional context."""
    enhanced_context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.utcnow().isoformat(),
        **context
    }

    # Add system context
    enhanced_context.update({
        "python_version": sys.version,
        "platform": platform.platform(),
        "memory_usage": psutil.virtual_memory().percent
    })

    return enhanced_context
```

### **4. Error Handling in State Management**

#### **State Error Handling:**
```python
class State(rx.State):
    """Enhanced state with error handling."""

    # Error state
    error_message: str = ""
    error_type: str = ""
    error_context: Dict[str, Any] = {}

    def handle_error(self, error: Exception, operation: str, **context):
        """Handle errors with proper state management."""
        error_context = enhance_error_context(error, {
            "operation": operation,
            "user_id": getattr(self, 'user_id', 'anonymous'),
            **context
        })

        # Log error
        logger.error("Operation failed", extra=error_context, exc_info=True)

        # Update state
        self.error_message = ErrorMessageProvider.get_message(
            self._categorize_error(error),
            self._get_error_code(error),
            **error_context
        )
        self.error_type = type(error).__name__
        self.error_context = error_context

        # Clear error after delay
        self._schedule_error_clear()

    def _categorize_error(self, error: Exception) -> str:
        """Categorize error for message lookup."""
        if isinstance(error, ValidationError):
            return "validation"
        elif isinstance(error, SystemError):
            return "system"
        elif isinstance(error, IntegrationError):
            return "integration"
        else:
            return "general"

    def _get_error_code(self, error: Exception) -> str:
        """Get error code for message lookup."""
        if isinstance(error, ValidationError):
            if "project_name" in str(error):
                return "project_name_required"
            elif "too short" in str(error):
                return "project_name_too_short"
        elif isinstance(error, SystemError):
            if "port" in str(error):
                return "port_unavailable"
            elif "disk" in str(error):
                return "disk_space_low"
        return "general_error"

    def _schedule_error_clear(self):
        """Schedule error message clearing."""
        # Clear error after 5 seconds
        self._clear_error_timer = asyncio.create_task(
            asyncio.sleep(5.0)
        )
        # Clear error when timer completes
        self._clear_error_timer.add_done_callback(
            lambda _: setattr(self, 'error_message', "")
        )
```

### **5. Error Recovery in UI**

#### **Error Display Components:**
```python
def error_display(state: State) -> rx.Component:
    """Display user-friendly error messages."""
    return rx.cond(
        state.error_message != "",
        rx.callout(
            rx.vstack(
                rx.text(state.error_message, size="3", weight="medium"),
                rx.cond(
                    state.error_type != "",
                    rx.text(f"Error type: {state.error_type}", size="1", color="gray")
                ),
                rx.cond(
                    state.error_context.get("retry_possible", False),
                    rx.button(
                        "Try Again",
                        on_click=state.retry_operation,
                        variant="soft",
                        size="2"
                    )
                ),
                spacing="2"
            ),
            icon="alert-triangle",
            color="red",
            size="3"
        )
    )

def retry_operation(self):
    """Retry the failed operation."""
    if hasattr(self, '_last_operation'):
        self._last_operation()
    self.error_message = ""
    self.error_type = ""
    self.error_context = {}
```

## 🔧 Implementation Examples

### **1. App Generation Error Handling**

#### **Enhanced Generation with Error Handling:**
```python
async def generate_app(self):
    """Generate app with comprehensive error handling."""
    try:
        # Validation
        if not self.project_name:
            raise ValidationError(
                "Project name is required",
                field="project_name",
                value=self.project_name
            )

        if len(self.project_name) < 3:
            raise ValidationError(
                "Project name must be at least 3 characters",
                field="project_name",
                value=self.project_name,
                min_length=3
            )

        # Port allocation with retry
        try:
            ports = PORT_REGISTRY.reserve_pair(self.project_name)
        except SystemError as e:
            logger.warning("Port allocation failed, retrying", extra={
                "app_name": self.project_name,
                "error": str(e)
            })
            await asyncio.sleep(1.0)
            ports = PORT_REGISTRY.reserve_pair(self.project_name)

        # Code generation
        with log_operation("code_generation", app_name=self.project_name):
            await self._generate_app_code(ports)

        # Success
        self.generation_status = "success"
        self.generation_message = f"Successfully generated {self.project_name}!"

    except ValidationError as e:
        self.handle_error(e, "app_generation",
                         validation_field=e.field,
                         validation_value=e.value)
        self.generation_status = "error"

    except SystemError as e:
        self.handle_error(e, "app_generation",
                         system_component=e.component)
        self.generation_status = "error"

    except Exception as e:
        self.handle_error(e, "app_generation")
        self.generation_status = "error"
```

### **2. Integration Error Handling**

#### **Data Source Connection with Error Handling:**
```python
@retry_with_backoff(max_retries=3, base_delay=1.0)
def connect_source(self):
    """Connect to data source with error handling."""
    try:
        if not self.selected_source:
            raise ValidationError(
                "No data source selected",
                field="selected_source",
                value=self.selected_source
            )

        # Test connection
        if not self._test_connection(self.selected_source):
            raise IntegrationError(
                "Failed to connect to data source",
                system="data_source",
                operation="connection_test",
                source_type=self.selected_source
            )

        # Load data
        self.source_records = self._load_source_data(self.selected_source)

        # Success
        self.integration_status = IntegrationStatus.SUCCESS
        self.integration_message = f"Connected to {self.selected_source}"

    except ValidationError as e:
        self.handle_error(e, "source_connection")
        self.integration_status = IntegrationStatus.ERROR

    except IntegrationError as e:
        self.handle_error(e, "source_connection",
                         source_type=self.selected_source)
        self.integration_status = IntegrationStatus.ERROR

    except Exception as e:
        self.handle_error(e, "source_connection")
        self.integration_status = IntegrationStatus.ERROR
```

## 📊 Error Monitoring and Analytics

### **1. Error Tracking**

#### **Error Metrics Collection:**
```python
class ErrorTracker:
    """Track and analyze application errors."""

    def __init__(self):
        self.error_counts = Counter()
        self.error_types = Counter()
        self.error_timeline = []

    def track_error(self, error: Exception, context: dict):
        """Track error occurrence."""
        error_key = f"{type(error).__name__}:{str(error)}"
        self.error_counts[error_key] += 1
        self.error_types[type(error).__name__] += 1

        self.error_timeline.append({
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        })

    def get_error_summary(self) -> dict:
        """Get error summary for monitoring."""
        return {
            "total_errors": sum(self.error_counts.values()),
            "unique_errors": len(self.error_counts),
            "error_types": dict(self.error_types),
            "recent_errors": self.error_timeline[-10:]  # Last 10 errors
        }
```

### **2. Error Alerting**

#### **Critical Error Alerting:**
```python
def check_critical_errors():
    """Check for critical errors that need immediate attention."""
    recent_errors = get_recent_errors(minutes=5)

    critical_errors = [
        error for error in recent_errors
        if error['level'] == 'CRITICAL'
    ]

    if len(critical_errors) > 3:
        send_alert("High critical error rate", {
            "error_count": len(critical_errors),
            "time_window": "5 minutes",
            "errors": critical_errors
        })
```

## 🎯 Implementation Checklist

### **Immediate Actions:**
- [ ] Implement error categories (SystemError, ValidationError, IntegrationError)
- [ ] Add retry mechanisms for transient failures
- [ ] Create user-friendly error messages
- [ ] Implement error state management
- [ ] Add error tracking and monitoring

### **Long-term Improvements:**
- [ ] Implement circuit breaker pattern
- [ ] Add error recovery automation
- [ ] Create error analytics dashboard
- [ ] Implement error alerting system
- [ ] Add error testing framework

---

**Next Steps:**
1. Apply error handling patterns to generator.py
2. Apply error handling patterns to proto_ddf_app.py
3. Create error monitoring dashboard
4. Implement error recovery automation
