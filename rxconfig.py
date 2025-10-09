import reflex as rx

config = rx.Config(
    app_name="proto_ddf_app",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)