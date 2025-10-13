"""NetSuite Integration Showcase - Multi-Source Data Integration"""

import logging
import random
import time
from datetime import datetime
from enum import Enum
from typing import Dict, List

import reflex as rx

# Configure logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add file handler for detailed logs
fh = logging.FileHandler("integration_hub.log")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
)
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.info("=" * 80)
logger.info("NetSuite Integration Hub - Application Starting")
logger.info("=" * 80)


class IntegrationStatus(str, Enum):
    """Integration status enum."""

    IDLE = "idle"
    CONNECTING = "connecting"
    SYNCING = "syncing"
    SUCCESS = "success"
    ERROR = "error"


class SourceType(str, Enum):
    """Data source types."""

    CSV = "CSV File"
    JSON = "JSON API"
    DATABASE = "Database"
    REST_API = "REST API"
    SALESFORCE = "Salesforce"
    WEBHOOK = "Webhook"


class State(rx.State):
    """The app state."""

    # Integration tracking
    selected_source: str = ""
    integration_status: str = IntegrationStatus.IDLE
    integration_message: str = ""
    progress: int = 0

    # Data records
    source_records: List[Dict] = []
    mapped_records: List[Dict] = []
    sync_logs: List[Dict] = []

    # Statistics
    total_synced: int = 0
    successful_syncs: int = 0
    failed_syncs: int = 0
    last_sync_time: str = ""

    # Field mapping
    source_fields: List[str] = []
    netsuite_fields: List[str] = [
        "Customer Name",
        "Email",
        "Phone",
        "Address",
        "Account ID",
    ]
    field_mapping: Dict[str, str] = {}

    # Sample data for different sources
    sample_data: Dict[str, List[Dict]] = {
        SourceType.CSV: [
            {
                "id": "1",
                "name": "Acme Corp",
                "email": "contact@acme.com",
                "phone": "+1-555-0101",
                "location": "New York",
            },
            {
                "id": "2",
                "name": "TechStart Inc",
                "email": "info@techstart.com",
                "phone": "+1-555-0102",
                "location": "San Francisco",
            },
            {
                "id": "3",
                "name": "Global Solutions",
                "email": "hello@global.com",
                "phone": "+1-555-0103",
                "location": "London",
            },
        ],
        SourceType.JSON: [
            {
                "customer_id": "JSON001",
                "company": "DataFlow Systems",
                "contact_email": "admin@dataflow.io",
                "tel": "+1-555-0201",
                "city": "Boston",
            },
            {
                "customer_id": "JSON002",
                "company": "Cloud Innovations",
                "contact_email": "support@cloudinno.com",
                "tel": "+1-555-0202",
                "city": "Seattle",
            },
        ],
        SourceType.DATABASE: [
            {
                "cust_id": "DB100",
                "cust_name": "Enterprise Analytics",
                "email_address": "sales@enterprise.com",
                "phone_number": "+1-555-0301",
                "region": "Chicago",
            },
            {
                "cust_id": "DB101",
                "cust_name": "Smart Retail Co",
                "email_address": "info@smartretail.com",
                "phone_number": "+1-555-0302",
                "region": "Austin",
            },
            {
                "cust_id": "DB102",
                "cust_name": "FinTech Plus",
                "email_address": "contact@fintech.com",
                "phone_number": "+1-555-0303",
                "region": "Miami",
            },
        ],
        SourceType.REST_API: [
            {
                "api_id": "REST50",
                "org_name": "Medical Systems Inc",
                "primary_email": "info@medsys.com",
                "contact_phone": "+1-555-0401",
                "headquarters": "Houston",
            },
            {
                "api_id": "REST51",
                "org_name": "EduTech Platform",
                "primary_email": "hello@edutech.com",
                "contact_phone": "+1-555-0402",
                "headquarters": "Portland",
            },
        ],
        SourceType.SALESFORCE: [
            {
                "sf_id": "SF7001",
                "account_name": "Manufacturing Pro",
                "email": "contact@mfgpro.com",
                "phone": "+1-555-0501",
                "billing_city": "Detroit",
            },
            {
                "sf_id": "SF7002",
                "account_name": "Logistics Network",
                "email": "info@logistics.net",
                "phone": "+1-555-0502",
                "billing_city": "Atlanta",
            },
            {
                "sf_id": "SF7003",
                "account_name": "Green Energy Co",
                "email": "sales@greenenergy.com",
                "phone": "+1-555-0503",
                "billing_city": "Denver",
            },
        ],
        SourceType.WEBHOOK: [
            {
                "webhook_id": "WH9001",
                "entity_name": "Digital Marketing Agency",
                "contact_email": "team@digitalmarket.com",
                "phone_num": "+1-555-0601",
                "address": "Los Angeles",
            },
            {
                "webhook_id": "WH9002",
                "entity_name": "Consulting Group",
                "contact_email": "info@consulting.com",
                "phone_num": "+1-555-0602",
                "address": "Washington DC",
            },
        ],
    }

    def select_source(self, source: str):
        """Select a data source."""
        try:
            logger.info(f"select_source called with: {source}")
            self.selected_source = source
            self.integration_status = IntegrationStatus.IDLE
            self.integration_message = f"Selected {source} as data source"
            self.source_records = []
            self.mapped_records = []

            # Load source fields based on source type
            if source in self.sample_data:
                sample = self.sample_data[source]
                if sample:
                    self.source_fields = list(sample[0].keys())
                    logger.debug(f"Loaded source fields: {self.source_fields}")

            logger.info(f"Successfully selected source: {source}")
        except Exception as e:
            logger.error(f"Error in select_source: {str(e)}", exc_info=True)
            self.integration_message = f"Error selecting source: {str(e)}"
            self.integration_status = IntegrationStatus.ERROR

    def connect_source(self):
        """Connect to the selected data source."""
        try:
            logger.info(
                f"connect_source called - selected_source: {self.selected_source}"
            )

            if not self.selected_source:
                logger.warning("No source selected")
                self.integration_message = "Please select a data source first"
                return

            self.integration_status = IntegrationStatus.CONNECTING
            self.integration_message = f"Connecting to {self.selected_source}..."
            self.progress = 0
            logger.debug("Yielding progress: 0%")
            yield

            # Simulate connection
            logger.debug("Simulating connection - step 1")
            time.sleep(0.5)
            self.progress = 30
            logger.debug("Yielding progress: 30%")
            yield

            logger.debug("Simulating connection - step 2")
            time.sleep(0.5)
            self.progress = 60
            logger.debug("Yielding progress: 60%")
            yield

            # Load sample data
            logger.debug(f"Loading sample data for: {self.selected_source}")
            self.source_records = self.sample_data.get(self.selected_source, [])
            logger.info(f"Loaded {len(self.source_records)} records")

            time.sleep(0.3)
            self.progress = 100
            self.integration_status = IntegrationStatus.SUCCESS
            self.integration_message = (
                f"Successfully connected! Found {len(self.source_records)} records"
            )

            # Add log entry
            log_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "action": "Connection",
                "source": self.selected_source,
                "status": "Success",
                "records": len(self.source_records),
            }
            self.sync_logs.insert(0, log_entry)
            logger.info(f"Connection successful: {log_entry}")

        except Exception as e:
            logger.error(f"Error in connect_source: {str(e)}", exc_info=True)
            self.integration_status = IntegrationStatus.ERROR
            self.integration_message = f"Connection error: {str(e)}"
            self.progress = 0

    def auto_map_fields(self):
        """Automatically map fields based on common patterns."""
        try:
            logger.info(f"auto_map_fields called - source_fields: {self.source_fields}")

            if not self.source_fields:
                logger.warning("No source fields available")
                self.integration_message = (
                    "No source fields available. Please connect to a source first."
                )
                return

            # Simple auto-mapping logic
            mapping_patterns = {
                "name": [
                    "Customer Name",
                    "name",
                    "company",
                    "org_name",
                    "account_name",
                    "entity_name",
                ],
                "email": [
                    "Email",
                    "email",
                    "contact_email",
                    "email_address",
                    "primary_email",
                ],
                "phone": [
                    "Phone",
                    "phone",
                    "tel",
                    "phone_number",
                    "contact_phone",
                    "phone_num",
                ],
                "address": [
                    "Address",
                    "location",
                    "city",
                    "region",
                    "billing_city",
                    "headquarters",
                ],
                "id": [
                    "Account ID",
                    "id",
                    "customer_id",
                    "cust_id",
                    "api_id",
                    "sf_id",
                    "webhook_id",
                ],
            }

            self.field_mapping = {}
            for source_field in self.source_fields:
                source_lower = source_field.lower()
                for pattern, netsuite_options in mapping_patterns.items():
                    if any(p.lower() in source_lower for p in netsuite_options[1:]):
                        self.field_mapping[source_field] = netsuite_options[0]
                        logger.debug(f"Mapped: {source_field} -> {netsuite_options[0]}")
                        break

            self.integration_message = f"Auto-mapped {len(self.field_mapping)} fields"
            logger.info(f"Field mapping complete: {self.field_mapping}")

        except Exception as e:
            logger.error(f"Error in auto_map_fields: {str(e)}", exc_info=True)
            self.integration_message = f"Mapping error: {str(e)}"

    def sync_to_netsuite(self):
        """Sync data to NetSuite."""
        try:
            logger.info(
                f"sync_to_netsuite called - records: {len(self.source_records)}, mapping: {self.field_mapping}"
            )

            if not self.source_records:
                logger.warning("No source records available")
                self.integration_message = (
                    "No source data available. Please connect to a source first."
                )
                return

            self.integration_status = IntegrationStatus.SYNCING
            self.integration_message = "Syncing data to NetSuite..."
            self.progress = 0
            logger.debug("Starting sync - yielding initial state")
            yield

            # Simulate syncing process
            total_records = len(self.source_records)
            self.mapped_records = []
            logger.info(f"Beginning sync of {total_records} records")

            for i, record in enumerate(self.source_records):
                try:
                    logger.debug(f"Processing record {i + 1}/{total_records}: {record}")

                    # Simulate sync delay
                    time.sleep(0.3)

                    # Map fields
                    mapped = {}
                    for source_field, netsuite_field in self.field_mapping.items():
                        if source_field in record:
                            mapped[netsuite_field] = record[source_field]
                            logger.debug(
                                f"  Mapped {source_field}={record[source_field]} -> {netsuite_field}"
                            )

                    # Simulate success/failure (90% success rate)
                    success = random.random() > 0.1

                    if success:
                        self.successful_syncs += 1
                        mapped["_status"] = "success"
                        logger.debug(f"  Record {i + 1} synced successfully")
                    else:
                        self.failed_syncs += 1
                        mapped["_status"] = "error"
                        mapped["_error"] = "Validation error: Missing required field"
                        logger.warning(f"  Record {i + 1} sync failed (simulated)")

                    self.mapped_records.append(mapped)
                    self.progress = int((i + 1) / total_records * 100)
                    logger.debug(f"Progress: {self.progress}% - yielding")
                    yield

                except Exception as record_error:
                    logger.error(
                        f"Error processing record {i + 1}: {str(record_error)}",
                        exc_info=True,
                    )
                    # Continue with next record
                    self.failed_syncs += 1
                    self.mapped_records.append(
                        {
                            "_status": "error",
                            "_error": f"Processing error: {str(record_error)}",
                        }
                    )

            self.total_synced += total_records
            self.last_sync_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.integration_status = IntegrationStatus.SUCCESS
            self.integration_message = f"Sync completed! {self.successful_syncs} successful, {self.failed_syncs} failed"

            # Add log entry
            log_entry = {
                "timestamp": self.last_sync_time,
                "action": "Sync",
                "source": self.selected_source,
                "status": "Completed",
                "records": total_records,
            }
            self.sync_logs.insert(0, log_entry)
            logger.info(f"Sync completed: {log_entry}")

        except Exception as e:
            logger.error(f"Error in sync_to_netsuite: {str(e)}", exc_info=True)
            self.integration_status = IntegrationStatus.ERROR
            self.integration_message = f"Sync error: {str(e)}"
            self.progress = 0

    def reset_integration(self):
        """Reset the integration."""
        try:
            logger.info("reset_integration called")
            self.selected_source = ""
            self.integration_status = IntegrationStatus.IDLE
            self.integration_message = ""
            self.progress = 0
            self.source_records = []
            self.mapped_records = []
            self.field_mapping = {}
            self.source_fields = []
            logger.info("Integration reset complete")
        except Exception as e:
            logger.error(f"Error in reset_integration: {str(e)}", exc_info=True)

    def clear_stats(self):
        """Clear statistics."""
        try:
            logger.info("clear_stats called")
            self.total_synced = 0
            self.successful_syncs = 0
            self.failed_syncs = 0
            self.last_sync_time = ""
            self.sync_logs = []
            logger.info("Statistics cleared")
        except Exception as e:
            logger.error(f"Error in clear_stats: {str(e)}", exc_info=True)


def stat_card(
    title: str, value: str, icon: str = "📊", color: str = "blue"
) -> rx.Component:
    """Create a statistics card."""
    return rx.card(
        rx.vstack(
            rx.text(icon, size="8"),
            rx.text(title, size="2", weight="medium", color="gray"),
            rx.text(value, size="6", weight="bold", color=color),
            align="center",
            spacing="2",
        ),
        padding="4",
        width="100%",
        min_width="200px",
    )


def source_card(source_type: str, description: str, icon: str) -> rx.Component:
    """Create a source selection card."""
    return rx.card(
        rx.vstack(
            rx.text(icon, size="8"),
            rx.heading(source_type, size="4"),
            rx.text(description, size="2", color="gray", align="center"),
            rx.button(
                "Select Source",
                on_click=lambda: State.select_source(source_type),
                variant="soft",
                size="2",
            ),
            align="center",
            spacing="3",
            width="100%",
        ),
        padding="4",
        height="100%",
        style={
            "transition": "transform 0.2s, box-shadow 0.2s",
            "_hover": {"transform": "translateY(-4px)", "box_shadow": "lg"},
        },
    )


def index() -> rx.Component:
    """Main integration dashboard."""
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            # Header
            rx.vstack(
                rx.heading("🔄 NetSuite Integration Hub", size="9", gradient=True),
                rx.text(
                    "Connect and sync data from multiple sources to NetSuite",
                    size="4",
                    color="gray",
                    align="center",
                ),
                align="center",
                spacing="2",
                padding_bottom="4",
            ),
            # Statistics Dashboard
            rx.card(
                rx.vstack(
                    rx.heading("📈 Integration Statistics", size="6"),
                    rx.grid(
                        stat_card("Total Records", State.total_synced, "📦", "blue"),
                        stat_card("Successful", State.successful_syncs, "✅", "green"),
                        stat_card("Failed", State.failed_syncs, "❌", "red"),
                        stat_card("Active Sources", "6", "🔌", "purple"),
                        columns="4",
                        gap="4",
                        width="100%",
                    ),
                    rx.cond(
                        State.last_sync_time != "",
                        rx.text(
                            f"Last sync: {State.last_sync_time}", size="2", color="gray"
                        ),
                    ),
                    rx.button(
                        "Clear Statistics",
                        on_click=State.clear_stats,
                        variant="soft",
                        color="gray",
                        size="1",
                    ),
                    spacing="4",
                    width="100%",
                ),
                padding="6",
                width="100%",
            ),
            # Data Source Selection
            rx.card(
                rx.vstack(
                    rx.heading("📁 Select Data Source", size="6"),
                    rx.grid(
                        source_card(SourceType.CSV, "Import from CSV files", "📄"),
                        source_card(SourceType.JSON, "Connect to JSON API", "🔗"),
                        source_card(SourceType.DATABASE, "Database connection", "💾"),
                        source_card(SourceType.REST_API, "REST API integration", "🌐"),
                        source_card(SourceType.SALESFORCE, "Salesforce connector", "☁️"),
                        source_card(SourceType.WEBHOOK, "Webhook receiver", "🔔"),
                        columns="3",
                        gap="4",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                padding="6",
                width="100%",
            ),
            # Current Integration Status
            rx.cond(
                State.selected_source != "",
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.heading(
                                f"🔄 Active Integration: {State.selected_source}",
                                size="6",
                            ),
                            rx.button(
                                "Reset",
                                on_click=State.reset_integration,
                                variant="soft",
                                color="red",
                                size="2",
                            ),
                            justify="between",
                            width="100%",
                        ),
                        # Status message
                        rx.cond(
                            State.integration_message != "",
                            rx.callout(
                                State.integration_message,
                                icon="info",
                                color=rx.cond(
                                    State.integration_status
                                    == IntegrationStatus.SUCCESS,
                                    "blue",
                                    "orange",
                                ),
                                size="2",
                            ),
                        ),
                        # Progress bar
                        rx.cond(
                            (State.integration_status == IntegrationStatus.CONNECTING)
                            | (State.integration_status == IntegrationStatus.SYNCING),
                            rx.vstack(
                                rx.text("Progress", size="2", weight="medium"),
                                rx.progress(
                                    value=State.progress, max=100, width="100%"
                                ),
                                rx.text(f"{State.progress}%", size="2", color="gray"),
                                spacing="2",
                                width="100%",
                            ),
                        ),
                        # Action buttons
                        rx.hstack(
                            rx.button(
                                "1. Connect to Source",
                                on_click=State.connect_source,
                                disabled=(
                                    State.integration_status
                                    == IntegrationStatus.CONNECTING
                                )
                                | (
                                    State.integration_status
                                    == IntegrationStatus.SYNCING
                                ),
                                size="3",
                            ),
                            rx.button(
                                "2. Auto-Map Fields",
                                on_click=State.auto_map_fields,
                                disabled=State.source_records.length() == 0,
                                variant="soft",
                                size="3",
                            ),
                            rx.button(
                                "3. Sync to NetSuite",
                                on_click=State.sync_to_netsuite,
                                disabled=State.source_records.length() == 0,
                                color="green",
                                size="3",
                            ),
                            spacing="3",
                            wrap="wrap",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    padding="6",
                    width="100%",
                ),
            ),
            # Source Data Preview
            rx.cond(
                State.source_records.length() > 0,
                rx.card(
                    rx.vstack(
                        rx.heading(
                            rx.text(
                                "📋 Source Data (",
                                State.source_records.length(),
                                " records)",
                                as_="span",
                            ),
                            size="5",
                        ),
                        rx.box(
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        rx.foreach(
                                            State.source_fields,
                                            lambda field: rx.table.column_header_cell(
                                                field
                                            ),
                                        )
                                    )
                                ),
                                rx.table.body(
                                    rx.foreach(
                                        State.source_records,
                                        lambda record: rx.table.row(
                                            rx.foreach(
                                                State.source_fields,
                                                lambda field: rx.table.cell(
                                                    record[field]
                                                ),
                                            )
                                        ),
                                    )
                                ),
                                variant="surface",
                                size="2",
                                width="100%",
                            ),
                            overflow_x="auto",
                            width="100%",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    padding="6",
                    width="100%",
                ),
            ),
            # Field Mapping
            rx.cond(
                State.field_mapping.length() > 0,
                rx.card(
                    rx.vstack(
                        rx.heading("🔀 Field Mapping", size="5"),
                        rx.flex(
                            rx.foreach(
                                State.field_mapping.items(),
                                lambda item: rx.hstack(
                                    rx.badge(item[0], variant="soft", size="2"),
                                    rx.text("→", size="4"),
                                    rx.badge(
                                        item[1], variant="soft", color="green", size="2"
                                    ),
                                    spacing="2",
                                    align="center",
                                ),
                            ),
                            direction="row",
                            wrap="wrap",
                            gap="3",
                            width="100%",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    padding="6",
                    width="100%",
                ),
            ),
            # Mapped Data Preview
            rx.cond(
                State.mapped_records.length() > 0,
                rx.card(
                    rx.vstack(
                        rx.heading(
                            rx.text(
                                "✅ Synced to NetSuite (",
                                State.mapped_records.length(),
                                " records)",
                                as_="span",
                            ),
                            size="5",
                        ),
                        rx.vstack(
                            rx.foreach(
                                State.mapped_records,
                                lambda record: rx.card(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.cond(
                                                record.get("Customer Name"),
                                                rx.vstack(
                                                    rx.text(
                                                        "Customer Name",
                                                        size="1",
                                                        color="gray",
                                                        weight="medium",
                                                    ),
                                                    rx.text(
                                                        record.get("Customer Name", ""),
                                                        size="2",
                                                        weight="bold",
                                                    ),
                                                    spacing="1",
                                                    align="start",
                                                ),
                                            ),
                                            rx.cond(
                                                record.get("Email"),
                                                rx.vstack(
                                                    rx.text(
                                                        "Email",
                                                        size="1",
                                                        color="gray",
                                                        weight="medium",
                                                    ),
                                                    rx.text(
                                                        record.get("Email", ""),
                                                        size="2",
                                                        weight="bold",
                                                    ),
                                                    spacing="1",
                                                    align="start",
                                                ),
                                            ),
                                            rx.cond(
                                                record.get("Phone"),
                                                rx.vstack(
                                                    rx.text(
                                                        "Phone",
                                                        size="1",
                                                        color="gray",
                                                        weight="medium",
                                                    ),
                                                    rx.text(
                                                        record.get("Phone", ""),
                                                        size="2",
                                                        weight="bold",
                                                    ),
                                                    spacing="1",
                                                    align="start",
                                                ),
                                            ),
                                            rx.cond(
                                                record.get("Address"),
                                                rx.vstack(
                                                    rx.text(
                                                        "Address",
                                                        size="1",
                                                        color="gray",
                                                        weight="medium",
                                                    ),
                                                    rx.text(
                                                        record.get("Address", ""),
                                                        size="2",
                                                        weight="bold",
                                                    ),
                                                    spacing="1",
                                                    align="start",
                                                ),
                                            ),
                                            rx.cond(
                                                record.get("Account ID"),
                                                rx.vstack(
                                                    rx.text(
                                                        "Account ID",
                                                        size="1",
                                                        color="gray",
                                                        weight="medium",
                                                    ),
                                                    rx.text(
                                                        record.get("Account ID", ""),
                                                        size="2",
                                                        weight="bold",
                                                    ),
                                                    spacing="1",
                                                    align="start",
                                                ),
                                            ),
                                            rx.badge(
                                                rx.cond(
                                                    record.get("_status") == "success",
                                                    "Success",
                                                    "Error",
                                                ),
                                                color=rx.cond(
                                                    record.get("_status") == "success",
                                                    "green",
                                                    "red",
                                                ),
                                                size="2",
                                            ),
                                            spacing="4",
                                            align="center",
                                            wrap="wrap",
                                        ),
                                        rx.cond(
                                            record.get("_status") == "error",
                                            rx.text(
                                                record.get("_error", ""),
                                                size="1",
                                                color="red",
                                            ),
                                        ),
                                        spacing="2",
                                        width="100%",
                                    ),
                                    padding="3",
                                    width="100%",
                                ),
                            ),
                            spacing="2",
                            width="100%",
                            max_height="400px",
                            overflow_y="auto",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    padding="6",
                    width="100%",
                ),
            ),
            # Integration Logs
            rx.cond(
                State.sync_logs.length() > 0,
                rx.card(
                    rx.vstack(
                        rx.heading("📝 Integration Logs", size="5"),
                        rx.box(
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        rx.table.column_header_cell("Timestamp"),
                                        rx.table.column_header_cell("Action"),
                                        rx.table.column_header_cell("Source"),
                                        rx.table.column_header_cell("Status"),
                                        rx.table.column_header_cell("Records"),
                                    )
                                ),
                                rx.table.body(
                                    rx.foreach(
                                        State.sync_logs,
                                        lambda log: rx.table.row(
                                            rx.table.cell(log["timestamp"]),
                                            rx.table.cell(log["action"]),
                                            rx.table.cell(log["source"]),
                                            rx.table.cell(
                                                rx.badge(
                                                    log["status"],
                                                    color=rx.cond(
                                                        (log["status"] == "Success")
                                                        | (
                                                            log["status"] == "Completed"
                                                        ),
                                                        "green",
                                                        "blue",
                                                    ),
                                                )
                                            ),
                                            rx.table.cell(log["records"]),
                                        ),
                                    )
                                ),
                                variant="surface",
                                size="2",
                                width="100%",
                            ),
                            overflow_x="auto",
                            width="100%",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    padding="6",
                    width="100%",
                ),
            ),
            spacing="6",
            padding="4",
            width="100%",
            max_width="1400px",
        ),
        padding="4",
        width="100%",
    )


# Add state and page to the app
app = rx.App()
app.add_page(index, title="NetSuite Integration Hub")
