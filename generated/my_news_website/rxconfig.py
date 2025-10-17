"""Reflex configuration for my news website."""

import reflex as rx

config = rx.Config(
    app_name="my_news_website_app",
    app_module_import="my_news_website_app.my_news_website",
    backend_port= 4392,
    frontend_port= 4393,
)
