"""Proto DDF - Data Dashboard Prototype using Reflex"""

import reflex as rx
import random
import time
from typing import List, Dict

from rxconfig import config


class State(rx.State):
    """The app state."""
    
    # Data for the dashboard
    data_points: List[Dict] = []
    chart_data: List[Dict] = []
    loading: bool = False
    counter: int = 0
    
    def generate_data(self):
        """Generate sample data for the dashboard."""
        self.loading = True
        yield
        
        # Simulate data generation
        time.sleep(1)
        
        # Generate random data points
        self.data_points = [
            {"name": f"Data Point {i}", "value": random.randint(10, 100), "category": random.choice(["A", "B", "C"])}
            for i in range(1, 11)
        ]
        
        # Generate chart data
        self.chart_data = [
            {"x": f"Q{i}", "y": random.randint(20, 80)} for i in range(1, 5)
        ]
        
        self.loading = False
    
    def increment_counter(self):
        """Increment the counter."""
        self.counter += 1
    
    def reset_counter(self):
        """Reset the counter."""
        self.counter = 0


def data_card(title: str, value: str, color: str = "blue") -> rx.Component:
    """Create a data card component."""
    return rx.card(
        rx.vstack(
            rx.text(title, size="2", weight="bold"),
            rx.text(value, size="6", color=color),
            align="center",
            spacing="2"
        ),
        padding="4",
        width="200px"
    )


def index() -> rx.Component:
    """Main dashboard page."""
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            # Header
            rx.heading("Proto DDF - Data Dashboard", size="8"),
            rx.text("A prototype data visualization dashboard built with Reflex", size="4", color="gray"),
            
            # Counter section
            rx.card(
                rx.vstack(
                    rx.heading("Interactive Counter", size="5"),
                    rx.hstack(
                        rx.button("Increment", on_click=State.increment_counter),
                        rx.button("Reset", on_click=State.reset_counter, color="red"),
                        spacing="3"
                    ),
                    rx.text(f"Count: {State.counter}", size="4", weight="bold"),
                    align="center",
                    spacing="3"
                ),
                padding="4",
                width="100%"
            ),
            
            # Data generation section
            rx.card(
                rx.vstack(
                    rx.heading("Data Generation", size="5"),
                    rx.button(
                        "Generate Sample Data",
                        on_click=State.generate_data,
                        loading=State.loading,
                        disabled=State.loading
                    ),
                    rx.cond(
                        State.loading,
                        rx.text("Generating data...", color="blue"),
                        rx.text(f"Generated {len(State.data_points)} data points", color="green")
                    ),
                    align="center",
                    spacing="3"
                ),
                padding="4",
                width="100%"
            ),
            
            # Data display section
            rx.cond(
                State.data_points.length > 0,
                rx.vstack(
                    rx.heading("Data Points", size="5"),
                    rx.grid(
                        *[
                            data_card(
                                item["name"], 
                                str(item["value"]), 
                                "green" if item["value"] > 50 else "orange"
                            )
                            for item in State.data_points
                        ],
                        columns="5",
                        gap="3",
                        width="100%"
                    ),
                    spacing="3"
                )
            ),
            
            # Chart section
            rx.cond(
                State.chart_data.length > 0,
                rx.card(
                    rx.vstack(
                        rx.heading("Quarterly Data", size="5"),
                        rx.text("Sample chart data (simplified visualization)"),
                        rx.vstack(
                            *[
                                rx.hstack(
                                    rx.text(f"{item['x']}: ", weight="bold"),
                                    rx.progress(value=item["y"], max=100, width="200px"),
                                    rx.text(f"{item['y']}%"),
                                    align="center",
                                    spacing="3"
                                )
                                for item in State.chart_data
                            ],
                            spacing="2"
                        ),
                        align="center",
                        spacing="3"
                    ),
                    padding="4",
                    width="100%"
                )
            ),
            
            spacing="6",
            padding="4",
            width="100%",
            max_width="1200px"
        ),
        padding="4",
        width="100%"
    )


# Add state and page to the app
app = rx.App()
app.add_page(index, title="Proto DDF Dashboard")
