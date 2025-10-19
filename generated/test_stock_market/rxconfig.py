"""Reflex configuration for Test Stock Market."""

import reflex as rx

config = rx.Config(
    app_name="test_stock_market_app",
    app_module_import="test_stock_market_app.test_stock_market",
    backend_port=3143,
    frontend_port=3144,
)
