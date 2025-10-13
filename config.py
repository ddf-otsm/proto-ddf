"""
Configuration settings for NetSuite Integration Hub
"""

# Network configuration
BACKEND_HOST = "0.0.0.0"  # Bind to all network interfaces
BACKEND_PORT = 8000  # Backend API port
FRONTEND_PORT = 3000  # Frontend development server port

# These ports should NOT be random/roundup ports
# They are fixed for:
# - Backend: 0.0.0.0:8000 (accessible from network)
# - Frontend: 3000 (standard development port)
