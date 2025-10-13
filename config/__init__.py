"""Configuration package for proto-ddf application."""

from .constants import (
    FRONTEND_PORT, BACKEND_PORT, BACKEND_HOST,
    GENERATED_FRONTEND_PORT, GENERATED_BACKEND_PORT
)

__all__ = [
    'FRONTEND_PORT', 'BACKEND_PORT', 'BACKEND_HOST',
    'GENERATED_FRONTEND_PORT', 'GENERATED_BACKEND_PORT'
]

