"""Proto-DDF Generator - Generate Reflex Applications

This is the main generator interface for creating Reflex applications.
"""

import reflex as rx
import logging
from typing import List, Dict
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add file handler
fh = logging.FileHandler('proto_ddf_generator.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.info("=" * 80)
logger.info("Proto-DDF Generator - Application Starting")
logger.info("=" * 80)


class GeneratorState(rx.State):
    """The generator app state."""
    
    # Project settings
    project_name: str = ""
    project_description: str = ""
    
    # Generated apps
    generated_apps: List[Dict] = [
        {
            "name": "NetSuite Integration Hub",
            "description": "Multi-source data integration showcase",
            "path": "generated/netsuite_integration_hub",
            "status": "ready",
            "port": 4138
        }
    ]
    
    # Generation status
    generation_status: str = "idle"
    generation_message: str = ""
    
    def generate_app(self):
        """Generate a new Reflex application."""
        logger.info(f"generate_app called - project_name: {self.project_name}")
        
        if not self.project_name:
            self.generation_message = "Please provide a project name"
            return
        
        self.generation_status = "generating"
        self.generation_message = f"Generating {self.project_name}..."
        yield
        
        # TODO: Implement actual generation logic
        logger.info(f"Would generate app: {self.project_name}")
        
        self.generation_status = "success"
        self.generation_message = f"Successfully generated {self.project_name}!"
    
    def set_project_name(self, name: str):
        """Set the project name."""
        self.project_name = name
    
    def set_project_description(self, description: str):
        """Set the project description."""
        self.project_description = description


def app_card(app: Dict) -> rx.Component:
    """
    Create a card component for displaying generated application information.

    Args:
        app: Dictionary containing app information with keys:
            - name: Application name
            - description: Brief app description
            - status: Current status ("ready", "running", etc.)
            - port: Port number the app runs on

    Returns:
        rx.Component: A card component displaying app details and actions
    """
    return rx.card(
        rx.vstack(
            # App title and description
            rx.heading(app["name"], size="5"),
            rx.text(app["description"], size="2", color="gray"),

            # Status and port information
            rx.hstack(
                rx.badge(
                    app["status"],
                    color=rx.cond(
                        app["status"] == "ready",
                        "green",
                        "gray"
                    )
                ),
                rx.text(f"Port: {app['port']}", size="2", color="gray"),
                spacing="2"
            ),

            # Action buttons
            rx.hstack(
                rx.button(
                    "Open",
                    on_click=lambda: rx.redirect(f"http://127.0.0.1:{app['port']}"),
                    variant="soft",
                    size="2"
                ),
                rx.button(
                    "View Code",
                    variant="outline",
                    size="2"
                ),
                spacing="2"
            ),

            spacing="3",
            align="start",
            width="100%"
        ),
        padding="4",
        width="100%"
    )


def index() -> rx.Component:
    """Main generator interface."""
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            # Header
            rx.vstack(
                rx.heading("🎨 Proto-DDF Generator", size="9", gradient=True),
                rx.text(
                    "Generate Reflex applications with AI-powered code generation",
                    size="4",
                    color="gray",
                    align="center"
                ),
                align="center",
                spacing="2",
                padding_bottom="4"
            ),
            
            # Quick Stats
            rx.card(
                rx.hstack(
                    rx.vstack(
                        rx.text("📦", size="8"),
                        rx.text("Generated Apps", size="2", color="gray"),
                        rx.text(str(GeneratorState.generated_apps.length()), size="7", weight="bold", color="blue"),
                        align="center",
                        spacing="2"
                    ),
                    rx.vstack(
                        rx.text("🚀", size="8"),
                        rx.text("Running", size="2", color="gray"),
                        rx.text("1", size="7", weight="bold", color="green"),
                        align="center",
                        spacing="2"
                    ),
                    rx.vstack(
                        rx.text("⚡", size="8"),
                        rx.text("Templates", size="2", color="gray"),
                        rx.text("5", size="7", weight="bold", color="purple"),
                        align="center",
                        spacing="2"
                    ),
                    spacing="8",
                    justify="center",
                    width="100%"
                ),
                padding="6",
                width="100%"
            ),
            
            # New App Generator
            rx.card(
                rx.vstack(
                    rx.heading("➕ Generate New App", size="6"),
                    rx.vstack(
                        rx.vstack(
                            rx.text("Project Name", size="2", weight="medium"),
                            rx.input(
                                placeholder="e.g., my-dashboard",
                                on_change=GeneratorState.set_project_name,
                                size="3",
                                width="100%"
                            ),
                            spacing="2",
                            width="100%"
                        ),
                        rx.vstack(
                            rx.text("Description", size="2", weight="medium"),
                            rx.text_area(
                                placeholder="Describe what you want to build...",
                                on_change=GeneratorState.set_project_description,
                                size="3",
                                width="100%",
                                rows="4"
                            ),
                            spacing="2",
                            width="100%"
                        ),
                        spacing="4",
                        width="100%"
                    ),
                    rx.button(
                        "🎨 Generate App",
                        on_click=GeneratorState.generate_app,
                        size="3",
                        width="100%"
                    ),
                    rx.cond(
                        GeneratorState.generation_message != "",
                        rx.callout(
                            GeneratorState.generation_message,
                            icon="info",
                            color=rx.cond(
                                GeneratorState.generation_status == "success",
                                "green",
                                "blue"
                            )
                        )
                    ),
                    spacing="4",
                    width="100%"
                ),
                padding="6",
                width="100%"
            ),
            
            # Generated Apps
            rx.card(
                rx.vstack(
                    rx.heading("📱 Generated Applications", size="6"),
                    rx.vstack(
                        rx.foreach(
                            GeneratorState.generated_apps,
                            app_card
                        ),
                        spacing="3",
                        width="100%"
                    ),
                    spacing="4",
                    width="100%"
                ),
                padding="6",
                width="100%"
            ),
            
            # Templates
            rx.card(
                rx.vstack(
                    rx.heading("📚 Available Templates", size="6"),
                    rx.grid(
                        rx.card(
                            rx.vstack(
                                rx.text("📊", size="8"),
                                rx.heading("Dashboard", size="4"),
                                rx.text("Analytics and data visualization", size="2", color="gray"),
                                rx.button("Use Template", variant="soft", size="2"),
                                spacing="3",
                                align="center"
                            ),
                            padding="4"
                        ),
                        rx.card(
                            rx.vstack(
                                rx.text("🔄", size="8"),
                                rx.heading("Integration Hub", size="4"),
                                rx.text("Connect multiple data sources", size="2", color="gray"),
                                rx.button("Use Template", variant="soft", size="2"),
                                spacing="3",
                                align="center"
                            ),
                            padding="4"
                        ),
                        rx.card(
                            rx.vstack(
                                rx.text("💬", size="8"),
                                rx.heading("Chat App", size="4"),
                                rx.text("Real-time messaging interface", size="2", color="gray"),
                                rx.button("Use Template", variant="soft", size="2"),
                                spacing="3",
                                align="center"
                            ),
                            padding="4"
                        ),
                        rx.card(
                            rx.vstack(
                                rx.text("🛍️", size="8"),
                                rx.heading("E-commerce", size="4"),
                                rx.text("Online store with cart", size="2", color="gray"),
                                rx.button("Use Template", variant="soft", size="2"),
                                spacing="3",
                                align="center"
                            ),
                            padding="4"
                        ),
                        rx.card(
                            rx.vstack(
                                rx.text("📝", size="8"),
                                rx.heading("CMS", size="4"),
                                rx.text("Content management system", size="2", color="gray"),
                                rx.button("Use Template", variant="soft", size="2"),
                                spacing="3",
                                align="center"
                            ),
                            padding="4"
                        ),
                        columns="3",
                        gap="4",
                        width="100%"
                    ),
                    spacing="4",
                    width="100%"
                ),
                padding="6",
                width="100%"
            ),
            
            spacing="6",
            padding="4",
            width="100%",
            max_width="1400px"
        ),
        padding="4",
        width="100%"
    )


# Create the app
app = rx.App()
app.add_page(index, title="Proto-DDF Generator")

