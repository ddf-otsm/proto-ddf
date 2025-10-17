# Logging Standards and Best Practices

## 🎯 Overview

This guide establishes comprehensive logging standards for Proto-DDF, ensuring consistent, useful, and maintainable logging across all components.

## 📊 Current Logging Analysis

### **Issues Found:**
- **61 logger calls** across 2 main files
- **No structured logging** - all plain text
- **Inconsistent log levels** - mostly DEBUG/INFO
- **Missing context** - logs lack important metadata
- **No log aggregation** - scattered across files

### **Current Logging Pattern:**
```python
# Current (problematic):
logger.info(f"Loaded {len(self.source_records)} records")
logger.debug("Yielding progress: 30%")
logger.error(f"Error generating app: {e}", exc_info=True)
```

## 🏗️ Improved Logging Architecture

### **1. Structured Logging Format**

#### **Standard Log Entry:**
```python
logger.info("Operation completed", extra={
    "operation": "app_generation",
    "duration_ms": duration,
    "success": True,
    "app_name": app_name,
    "user_id": user_id,
    "ports_allocated": {
        "backend": backend_port,
        "frontend": frontend_port
    },
    "metadata": {
        "python_version": sys.version,
        "reflex_version": reflex.__version__
    }
})
```

#### **Error Logging:**
```python
logger.error("Operation failed", extra={
    "operation": "app_generation",
    "error_type": type(e).__name__,
    "error_message": str(e),
    "app_name": app_name,
    "retry_count": retry_count,
    "stack_trace": traceback.format_exc()
}, exc_info=True)
```

### **2. Log Level Guidelines**

#### **DEBUG** - Detailed diagnostic information
```python
# Use for step-by-step debugging
logger.debug("Processing step", extra={
    "step": "field_mapping",
    "record_count": len(records),
    "mapping_rules": mapping_rules,
    "processing_time_ms": step_duration
})
```

#### **INFO** - General operational messages
```python
# Use for normal operations
logger.info("Application started", extra={
    "app_name": app_name,
    "version": app_version,
    "environment": environment,
    "ports": {"backend": backend_port, "frontend": frontend_port}
})
```

#### **WARNING** - Something unexpected but recoverable
```python
# Use for recoverable issues
logger.warning("Port conflict resolved", extra={
    "requested_port": requested_port,
    "allocated_port": allocated_port,
    "conflict_reason": "port_in_use"
})
```

#### **ERROR** - Serious problems that need attention
```python
# Use for serious but recoverable errors
logger.error("Generation failed", extra={
    "app_name": app_name,
    "error_type": "ValidationError",
    "error_message": str(e),
    "retry_possible": True
})
```

#### **CRITICAL** - System cannot continue
```python
# Use for unrecoverable errors
logger.critical("Port registry corrupted", extra={
    "registry_file": registry_path,
    "backup_available": backup_exists,
    "system_state": "unrecoverable"
})
```

## 🔧 Implementation Standards

### **1. Logging Configuration**

#### **Enhanced Logger Setup:**
```python
import logging
import json
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra'):
            log_entry.update(record.extra)
            
        return json.dumps(log_entry)

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# File handler with structured format
fh = logging.FileHandler("proto_ddf.log")
fh.setFormatter(StructuredFormatter())
logger.addHandler(fh)

# Console handler with readable format
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))
logger.addHandler(ch)
```

### **2. Context Managers for Operations**

#### **Operation Tracking:**
```python
from contextlib import contextmanager
import time

@contextmanager
def log_operation(operation_name: str, **context):
    """Context manager for logging operations."""
    start_time = time.time()
    logger.info(f"Starting {operation_name}", extra=context)
    
    try:
        yield
        duration = time.time() - start_time
        logger.info(f"Completed {operation_name}", extra={
            **context,
            "duration_ms": duration * 1000,
            "success": True
        })
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Failed {operation_name}", extra={
            **context,
            "duration_ms": duration * 1000,
            "error": str(e),
            "success": False
        }, exc_info=True)
        raise

# Usage:
with log_operation("app_generation", app_name=app_name, user_id=user_id):
    # Generation logic here
    pass
```

### **3. Performance Logging**

#### **Timing Decorator:**
```python
import functools
import time

def log_performance(operation_name: str):
    """Decorator to log function performance."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger.debug(f"Starting {operation_name}")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"Completed {operation_name}", extra={
                    "duration_ms": duration * 1000,
                    "success": True
                })
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Failed {operation_name}", extra={
                    "duration_ms": duration * 1000,
                    "error": str(e),
                    "success": False
                })
                raise
        return wrapper
    return decorator

# Usage:
@log_performance("field_mapping")
def auto_map_fields(self):
    # Field mapping logic
    pass
```

## 📱 Application-Specific Logging

### **Generator Application Logging:**

#### **App Generation Flow:**
```python
def generate_app(self):
    """Generate application with comprehensive logging."""
    with log_operation("app_generation", 
                      app_name=self.project_name,
                      user_id=getattr(self, 'user_id', 'anonymous')):
        
        # Step 1: Validation
        logger.info("Validating project settings", extra={
            "project_name": self.project_name,
            "description": self.project_description
        })
        
        # Step 2: Port allocation
        ports = PORT_REGISTRY.reserve_pair(self.project_name)
        logger.info("Ports allocated", extra={
            "backend_port": ports.backend,
            "frontend_port": ports.frontend,
            "app_name": self.project_name
        })
        
        # Step 3: Code generation
        logger.info("Generating application code", extra={
            "template": "reflex_basic",
            "features": ["routing", "state_management", "ui_components"]
        })
        
        # Step 4: File creation
        files_created = []
        for file_path in generated_files:
            logger.debug("Creating file", extra={
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size
            })
            files_created.append(str(file_path))
        
        logger.info("Files created", extra={
            "file_count": len(files_created),
            "files": files_created
        })
```

### **Integration Hub Logging:**

#### **Data Integration Flow:**
```python
def connect_source(self):
    """Connect to data source with detailed logging."""
    logger.info("Initiating source connection", extra={
        "source_type": self.selected_source,
        "user_id": getattr(self, 'user_id', 'anonymous')
    })
    
    try:
        # Connection steps
        for step, progress in connection_steps:
            logger.debug("Connection progress", extra={
                "step": step,
                "progress_percent": progress,
                "source_type": self.selected_source
            })
            yield
            
        # Data loading
        logger.info("Loading source data", extra={
            "source_type": self.selected_source,
            "record_count": len(self.source_records),
            "field_count": len(self.source_fields)
        })
        
        # Field analysis
        logger.info("Analyzing field patterns", extra={
            "source_fields": self.source_fields,
            "netsuite_fields": self.netsuite_fields,
            "mapping_confidence": mapping_confidence
        })
        
    except Exception as e:
        logger.error("Connection failed", extra={
            "source_type": self.selected_source,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "retry_count": self.retry_count
        })
        raise
```

## 🔍 Log Analysis and Monitoring

### **1. Log Aggregation Setup**

#### **Centralized Logging:**
```python
# config/logging_config.py
import logging
import logging.handlers
from pathlib import Path

def setup_logging(app_name: str, log_level: str = "INFO"):
    """Setup centralized logging for application."""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / f"{app_name}.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(StructuredFormatter())
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    logger.addHandler(console_handler)
    
    return logger
```

### **2. Log Analysis Tools**

#### **Log Parser Script:**
```python
# scripts/analyze_logs.py
import json
import sys
from collections import Counter
from datetime import datetime

def analyze_logs(log_file: str):
    """Analyze application logs for insights."""
    
    error_counts = Counter()
    operation_times = {}
    error_types = Counter()
    
    with open(log_file, 'r') as f:
        for line in f:
            try:
                log_entry = json.loads(line)
                
                # Count errors
                if log_entry['level'] == 'ERROR':
                    error_counts[log_entry['message']] += 1
                    error_types[log_entry.get('error_type', 'Unknown')] += 1
                
                # Track operation times
                if 'operation' in log_entry and 'duration_ms' in log_entry:
                    op = log_entry['operation']
                    duration = log_entry['duration_ms']
                    if op not in operation_times:
                        operation_times[op] = []
                    operation_times[op].append(duration)
                    
            except json.JSONDecodeError:
                continue
    
    # Print analysis
    print("=== Log Analysis ===")
    print(f"Total errors: {sum(error_counts.values())}")
    print(f"Error types: {dict(error_types)}")
    print(f"Operation times: {operation_times}")
```

## 📊 Monitoring and Alerting

### **1. Health Check Logging**

#### **System Health Monitoring:**
```python
def log_health_check():
    """Log system health metrics."""
    import psutil
    
    logger.info("Health check", extra={
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "active_connections": len(psutil.net_connections()),
        "timestamp": datetime.utcnow().isoformat()
    })
```

### **2. Performance Metrics**

#### **Performance Logging:**
```python
def log_performance_metrics():
    """Log application performance metrics."""
    logger.info("Performance metrics", extra={
        "generated_apps_count": len(GeneratorState.generated_apps),
        "running_apps_count": GeneratorState.running_count,
        "port_utilization": calculate_port_utilization(),
        "memory_usage_mb": get_memory_usage(),
        "response_times": get_average_response_times()
    })
```

## 🎯 Implementation Checklist

### **Immediate Actions:**
- [ ] Replace all `logger.info(f"...")` with structured logging
- [ ] Add context to all log messages
- [ ] Implement log level guidelines
- [ ] Add performance timing to critical operations
- [ ] Create log analysis tools

### **Long-term Improvements:**
- [ ] Implement log aggregation
- [ ] Add monitoring dashboards
- [ ] Create alerting for critical errors
- [ ] Add log retention policies
- [ ] Implement log-based debugging tools

---

**Next Steps:**
1. Apply structured logging to `proto_ddf_app/generator.py`
2. Apply structured logging to `proto_ddf_app/proto_ddf_app.py`
3. Create log analysis scripts
4. Set up log monitoring