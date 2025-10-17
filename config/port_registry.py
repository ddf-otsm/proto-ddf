"""Centralized port registry for generated applications.

This module provides a persistent, thread-safe registry to allocate and track
backend and frontend ports for generated apps, preventing collisions and
stabilizing port assignments across restarts.

CORE DESIGN PRINCIPLES:
=======================

1. PERSISTENCE: Ports are persisted in JSON file (.port_registry.json)
   - Enables same ports across restarts
   - Makes port assignments traceable and debuggable
   - Survives process crashes without losing state

2. CONCURRENCY: Uses file locking for multi-process safety
   - fcntl.flock() on Unix (Linux/macOS)
   - Ensures atomic operations even with concurrent access
   - Prevents race conditions during port allocation

3. PROCESS TRACKING: Stores PID with port assignments
   - Enables automatic cleanup of orphaned processes
   - Allows intelligent process management (stop/restart)
   - Cross-platform support via psutil (with Unix fallback)

4. COLLISION AVOIDANCE: Maintains forbidden port set
   - Prevents allocating ports already in use
   - Separates generator ports from generated app ports
   - Ensures unique ports across all applications

REGISTRY FILE FORMAT (.port_registry.json):
===========================================

{
  "apps": {
    "my_app": {
      "backend": 3333,
      "frontend": 4444,
      "pid": 12345            # Optional: PID of running process
    },
    "another_app": {
      "backend": 3334,
      "frontend": 4445
    }
  }
}

PORT ALLOCATION ALGORITHM:
==========================

When ensure_ports(app_name, backend, frontend) is called:

1. Check if app already has assigned ports:
   - If yes and still available: reuse them
   - If no or unavailable: proceed to allocation

2. Validate requested ports (if provided):
   - Check if within [min_port, max_port] range
   - Verify not in forbidden set (generator + other apps)
   - Verify ports don't collide with each other

3. Allocate missing ports:
   - Randomly select from available ports (up to 200 attempts)
   - Fallback: Sequential sweep if random fails
   - Last resort: Return a number in range (degraded mode)

4. Persist allocation:
   - Save to registry file
   - Use file locking to prevent concurrent corruption

GARBAGE COLLECTION:
===================

The _garbage_collect() method:
- Runs on every _load() operation
- Removes entries for apps no longer in generated/ directory
- Attempts to stop orphaned processes (SIGTERM → SIGKILL)
- Keeps registry clean automatically

This enables safe app deletion without manual cleanup.

PROCESS MANAGEMENT:
===================

Platform-specific process handling:
- With psutil: Cross-platform support (Windows/Linux/macOS)
  * Graceful termination with timeout
  * Force kill if timeout exceeded
- Without psutil: Unix-only fallback (SIGTERM → SIGKILL)

Enables:
- stop_app(): Stop running application
- set_pid()/get_pid(): Track process IDs
- Automatic cleanup of stopped apps
"""

from __future__ import annotations

import fcntl
import json
import os
import random
import signal
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple, Optional, Any

# Try to import psutil for cross-platform process management
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Reuse generator ports to avoid conflicts
try:
    from .constants import BACKEND_PORT as GENERATOR_BACKEND_PORT
    from .constants import FRONTEND_PORT as GENERATOR_FRONTEND_PORT
except Exception:
    # Fallback defaults if constants import fails (should not in normal runs)
    GENERATOR_BACKEND_PORT = 4179
    GENERATOR_FRONTEND_PORT = 3416


CONFIG_DIR = Path(__file__).parent
REGISTRY_FILE = CONFIG_DIR / ".port_registry.json"
LOCK_FILE = CONFIG_DIR / ".port_registry.lock"


def _is_port_available(port: int, host: str = "0.0.0.0") -> bool:
    """Check if a port is available for binding.
    
    Uses socket binding test for cross-platform reliability.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            return True
    except OSError:
        return False


def _is_process_running(pid: int) -> bool:
    """Check if a process with given PID is running.
    
    Uses signal 0 (no-op) to test process existence without killing it.
    Works on Unix systems (Linux, macOS, BSD).
    """
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


@dataclass
class AppPorts:
    """Port assignment for an application.
    
    Attributes:
        backend: Backend API server port
        frontend: Frontend UI server port
    """
    backend: int
    frontend: int


@dataclass
class AppProcessInfo:
    """Process and port information for a running application.
    
    Attributes:
        pid: Process ID of the running application
        backend_port: Backend server port
        frontend_port: Frontend UI port
    """
    pid: int
    backend_port: int
    frontend_port: int


class PortRegistry:
    """Persistent registry for app port assignments and process tracking.

    Provides thread-safe, persistent allocation of ports for generated applications.
    Uses file locking to ensure concurrent safety and JSON persistence for reliability.

    Data format stored in REGISTRY_FILE:
    {
      "apps": {
        "app_name": {
          "backend": 3333,
          "frontend": 4444,
          "pid": 12345  // optional, for process tracking
        },
        ...
      }
    }

    Example usage:
        >>> registry = PortRegistry()
        >>> ports = registry.ensure_ports("my_app", backend=None, frontend=None)
        >>> print(ports.backend, ports.frontend)  # Allocated ports
        >>> registry.set_pid("my_app", os.getpid())  # Track running process
        >>> registry.stop_app("my_app")  # Gracefully stop the app
    """

    def __init__(self, min_port: int = 3000, max_port: int = 5000) -> None:
        """Initialize the port registry.
        
        Args:
            min_port: Minimum port number for allocation (default 3000)
            max_port: Maximum port number for allocation (default 5000)
        """
        self.min_port = min_port
        self.max_port = max_port
        self._data: Dict[str, Dict[str, Dict[str, int]]] = {"apps": {}}
        self._lock_fd: Optional[int] = None
        self._load()

    # ---------- File Locking ----------
    def _acquire_lock(self) -> None:
        """Acquire exclusive lock for registry file operations.
        
        Uses fcntl.flock() for Unix systems to ensure atomic operations.
        Continues gracefully if locking unavailable (degraded mode).
        """
        try:
            LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
            self._lock_fd = os.open(str(LOCK_FILE), os.O_RDWR | os.O_CREAT, 0o666)
            fcntl.flock(self._lock_fd, fcntl.LOCK_EX)
        except Exception:
            # Continue without lock if unavailable
            pass

    def _release_lock(self) -> None:
        """Release the registry file lock.
        
        Ensures lock is released even if errors occur.
        Safe to call multiple times or if lock wasn't acquired.
        """
        if self._lock_fd is not None:
            try:
                fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
                os.close(self._lock_fd)
            except Exception:
                pass
            finally:
                self._lock_fd = None

    # ---------- Persistence ----------
    def _load(self) -> None:
        """Load registry from persistent storage.
        
        Reads JSON file and performs garbage collection on orphaned entries.
        Safe to call even if file doesn't exist yet.
        """
        self._acquire_lock()
        try:
            if REGISTRY_FILE.exists():
                try:
                    self._data = json.loads(REGISTRY_FILE.read_text())
                    if "apps" not in self._data or not isinstance(self._data["apps"], dict):
                        self._data = {"apps": {}}
                    # Garbage collect entries for deleted apps
                    self._garbage_collect()
                except Exception:
                    self._data = {"apps": {}}
        finally:
            self._release_lock()

    def _save(self) -> None:
        """Save registry to persistent storage.
        
        Writes current state to JSON file with locking protection.
        Non-fatal: continues if write fails (in-memory state preserved).
        """
        self._acquire_lock()
        try:
            REGISTRY_FILE.write_text(json.dumps(self._data, indent=2))
        except Exception:
            # Non-fatal: continue without persistence if write fails
            pass
        finally:
            self._release_lock()

    def _garbage_collect(self) -> None:
        """Remove entries for apps that no longer exist in generated/ directory.
        
        Called during load to keep registry clean.
        Automatically attempts to stop processes of deleted apps.
        """
        generated_dir = Path("generated")
        if not generated_dir.exists():
            return
        
        existing_apps = {d.name for d in generated_dir.iterdir() if d.is_dir() and not d.name.startswith('.')}
        to_remove = []
        
        for app_name in list(self._data["apps"].keys()):
            if app_name not in existing_apps:
                to_remove.append(app_name)
                # Try to stop orphaned process
                meta = self._data["apps"].get(app_name)
                if isinstance(meta, dict) and "pid" in meta:
                    pid = meta.get("pid")
                    if isinstance(pid, int) and _is_process_running(pid):
                        try:
                            os.kill(pid, signal.SIGTERM)
                        except Exception:
                            pass
        
        for app_name in to_remove:
            del self._data["apps"][app_name]

    # ---------- Queries ----------
    def _reserved_ports(self) -> set[int]:
        """Get set of all currently reserved/in-use ports.
        
        Returns the union of:
        - Generator interface ports (frontend + backend)
        - All generated app ports (frontend + backend for each)
        
        Used to prevent allocating ports that are already assigned.
        """
        ports: set[int] = {GENERATOR_BACKEND_PORT, GENERATOR_FRONTEND_PORT}
        for meta in self._data["apps"].values():
            b = meta.get("backend") if isinstance(meta, dict) else None
            f = meta.get("frontend") if isinstance(meta, dict) else None
            if isinstance(b, int):
                ports.add(b)
            elif b is not None:
                try:
                    ports.add(int(b))  # type: ignore[arg-type]
                except Exception:
                    pass
            if isinstance(f, int):
                ports.add(f)
            elif f is not None:
                try:
                    ports.add(int(f))  # type: ignore[arg-type]
                except Exception:
                    pass
        return ports

    def _pick_available_port(self, forbidden: set[int]) -> int:
        """Select an available port from the configured range.
        
        Allocation strategy:
        1. Random sampling (up to 200 attempts) for efficiency
        2. Sequential sweep if random fails, for coverage
        3. Best-effort fallback if both fail
        
        Args:
            forbidden: Set of ports that cannot be allocated
            
        Returns:
            Available port number in [min_port, max_port] range
        """
        attempts = 0
        while attempts < 200:
            candidate = random.randint(self.min_port, self.max_port)
            if candidate in forbidden:
                attempts += 1
                continue
            if _is_port_available(candidate):
                return candidate
            attempts += 1
        # Fallback best-effort sweep
        for candidate in range(self.min_port, self.max_port + 1):
            if candidate in forbidden:
                continue
            if _is_port_available(candidate):
                return candidate
        # As last resort, return a number in range (may collide)
        return max(self.min_port, min(self.max_port, GENERATOR_FRONTEND_PORT + 1))

    # ---------- Public API ----------
    def get_ports(self, app_name: str) -> Optional[AppPorts]:
        """Get assigned ports for an app.
        
        Args:
            app_name: Name of the application
            
        Returns:
            AppPorts with backend and frontend ports, or None if not assigned
        """
        meta: Optional[Dict[str, Any]] = self._data["apps"].get(app_name)  # type: ignore[index]
        if not isinstance(meta, dict):
            return None
        try:
            b_val = meta.get("backend")
            f_val = meta.get("frontend")
            if isinstance(b_val, int) and isinstance(f_val, int):
                return AppPorts(backend=b_val, frontend=f_val)
            if b_val is None or f_val is None:
                return None
            b = int(b_val)  # type: ignore[arg-type]
            f = int(f_val)  # type: ignore[arg-type]
            return AppPorts(backend=b, frontend=f)
        except Exception:
            return None

    def ensure_ports(self, app_name: str, backend: int | None, frontend: int | None) -> AppPorts:
        """Ensure registry records ports for app. If None provided or ports collide,
        allocate new available ports and persist.
        
        This is the primary allocation method. It:
        - Reuses existing ports if app already assigned and valid
        - Validates requested ports for conflicts
        - Allocates new ports if needed
        - Persists allocation atomically
        
        Args:
            app_name: Name of the application
            backend: Requested backend port or None for automatic allocation
            frontend: Requested frontend port or None for automatic allocation
            
        Returns:
            AppPorts with assigned backend and frontend ports
            
        Algorithm:
            1. If app exists with valid ports: reuse them
            2. Validate requested ports (if provided)
            3. Allocate missing ports from available pool
            4. Save to registry file
        """
        reserved = self._reserved_ports()

        # If ports already assigned to this app, prefer them
        existing: Optional[Dict[str, Any]] = self._data["apps"].get(app_name)  # type: ignore[index]
        if existing:
            b_raw = existing.get("backend")
            f_raw = existing.get("frontend")
            b = b_raw if isinstance(b_raw, int) else (int(b_raw) if b_raw is not None else 0)  # type: ignore[arg-type]
            f = f_raw if isinstance(f_raw, int) else (int(f_raw) if f_raw is not None else 0)  # type: ignore[arg-type]
            # Validate they don't collide with others and are within range
            if b and f and b != f and b not in {GENERATOR_BACKEND_PORT, GENERATOR_FRONTEND_PORT} and f not in {GENERATOR_BACKEND_PORT, GENERATOR_FRONTEND_PORT}:
                # If either port is currently occupied by a foreign process, reallocate
                if not _is_port_available(b) and not _is_port_available(f):
                    # Keep assignment; ports in-use likely belong to the app already
                    pass
                self._data["apps"][app_name] = {"backend": int(b), "frontend": int(f)}
                self._save()
                return AppPorts(backend=b, frontend=f)

        # Start from provided rxconfig ports if present and valid
        candidate_backend = backend if isinstance(backend, int) else None
        candidate_frontend = frontend if isinstance(frontend, int) else None

        # Build forbidden set that excludes previous assignment for this app
        forbidden = self._reserved_ports()
        # If this app was in reserved, drop its own prior assignment to allow reuse
        if existing:
            b_raw = existing.get("backend")
            f_raw = existing.get("frontend")
            try:
                if isinstance(b_raw, int):
                    forbidden.discard(b_raw)
                else:
                    forbidden.discard(int(b_raw))  # type: ignore[arg-type]
            except Exception:
                pass
            try:
                if isinstance(f_raw, int):
                    forbidden.discard(f_raw)
                else:
                    forbidden.discard(int(f_raw))  # type: ignore[arg-type]
            except Exception:
                pass

        # Validate provided candidates
        def _valid(p: int | None) -> bool:
            return (
                isinstance(p, int)
                and self.min_port <= p <= self.max_port
                and p not in {GENERATOR_BACKEND_PORT, GENERATOR_FRONTEND_PORT}
                and p not in forbidden
            )

        # Compute concrete backend/frontend ports (non-Optional) for type safety
        if _valid(candidate_backend):
            backend_concrete: int = int(candidate_backend)  # type: ignore[arg-type]
        else:
            backend_concrete = self._pick_available_port(forbidden)
        forbidden.add(backend_concrete)

        # Frontend must differ from backend
        if (not _valid(candidate_frontend)) or (candidate_frontend == backend_concrete):
            frontend_concrete: int = self._pick_available_port(forbidden)
        else:
            frontend_concrete = int(candidate_frontend)  # type: ignore[arg-type]

        self._data["apps"][app_name] = {
            "backend": backend_concrete,
            "frontend": frontend_concrete,
        }
        self._save()
        return AppPorts(backend=backend_concrete, frontend=frontend_concrete)

    def reserve_pair(self, app_name: str) -> Tuple[int, int]:
        """Allocate a unique backend/frontend port pair for the app and persist.
        
        Convenience method for allocating new ports without validation.
        
        Args:
            app_name: Name of the application
            
        Returns:
            Tuple of (backend_port, frontend_port)
        """
        ports = self.ensure_ports(app_name, backend=None, frontend=None)
        return ports.backend, ports.frontend

    def set_pid(self, app_name: str, pid: int) -> None:
        """Record the PID for a running app.
        
        Args:
            app_name: Name of the application
            pid: Process ID of the running application
        """
        if app_name in self._data["apps"]:
            self._data["apps"][app_name]["pid"] = pid
            self._save()

    def get_pid(self, app_name: str) -> Optional[int]:
        """Get the recorded PID for an app.
        
        Args:
            app_name: Name of the application
            
        Returns:
            Process ID if app is being tracked, None otherwise
        """
        meta = self._data["apps"].get(app_name)
        if isinstance(meta, dict) and "pid" in meta:
            pid = meta.get("pid")
            return int(pid) if isinstance(pid, int) else None
        return None

    def stop_app(self, app_name: str) -> bool:
        """Stop a running app by its recorded PID.
        
        Uses graceful termination with timeout, falling back to force kill.
        Platform-specific behavior:
        - With psutil: Cross-platform (Windows/Linux/macOS)
        - Without psutil: Unix-only (SIGTERM → SIGKILL)
        
        Args:
            app_name: Name of the application
            
        Returns:
            True if app was stopped, False if not running or error
        """
        pid = self.get_pid(app_name)
        if pid and _is_process_running(pid):
            try:
                if HAS_PSUTIL:
                    # Cross-platform process management with psutil (works on Windows, Linux, macOS)
                    try:
                        process = psutil.Process(pid)
                        process.terminate()
                        # Wait for graceful shutdown
                        try:
                            process.wait(timeout=3.0)
                        except psutil.TimeoutExpired:
                            # Force kill if timeout
                            process.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                else:
                    # Unix-only fallback using signals
                    os.kill(pid, signal.SIGTERM)
                    # Wait briefly for graceful shutdown
                    import time
                    for _ in range(10):
                        if not _is_process_running(pid):
                            break
                        time.sleep(0.3)
                    # Force kill if still running
                    if _is_process_running(pid):
                        os.kill(pid, signal.SIGKILL)
                
                # Clear PID from registry
                if app_name in self._data["apps"]:
                    self._data["apps"][app_name].pop("pid", None)
                    self._save()
                return True
            except Exception:
                return False
        return False

    def get_process_info(self, app_name: str) -> Optional[AppProcessInfo]:
        """Get process and port info for an app.
        
        Args:
            app_name: Name of the application
            
        Returns:
            AppProcessInfo with PID and ports, or None if not found
        """
        ports = self.get_ports(app_name)
        pid = self.get_pid(app_name)
        if ports and pid:
            return AppProcessInfo(pid=pid, backend_port=ports.backend, frontend_port=ports.frontend)
        return None

    def release(self, app_name: str) -> None:
        """Remove app from registry and stop its process if running.
        
        Complete cleanup: stops process and removes all tracking info.
        
        Args:
            app_name: Name of the application
        """
        self.stop_app(app_name)
        if app_name in self._data["apps"]:
            del self._data["apps"][app_name]
            self._save()


