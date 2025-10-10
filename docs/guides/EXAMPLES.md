# NetSuite Integration Examples

This document provides practical examples of how to extend the NetSuite Integration Hub with real-world integrations.

## Table of Contents

1. [Real CSV File Upload](#real-csv-file-upload)
2. [REST API Integration](#rest-api-integration)
3. [Database Connection](#database-connection)
4. [Salesforce Integration](#salesforce-integration)
5. [Webhook Receiver](#webhook-receiver)
6. [Custom Field Mapping](#custom-field-mapping)

---

## Real CSV File Upload

### Example: Adding File Upload Capability

```python
# Add to State class
import pandas as pd
from typing import Optional

class State(rx.State):
    uploaded_file: Optional[str] = None
    
    async def handle_csv_upload(self, files: list[rx.UploadFile]):
        """Handle CSV file upload and parse data."""
        if not files:
            return
        
        file = files[0]
        content = await file.read()
        
        # Parse CSV
        df = pd.read_csv(io.BytesIO(content))
        
        # Convert to records
        self.source_records = df.to_dict('records')
        self.source_fields = list(df.columns)
        self.integration_message = f"Uploaded {len(self.source_records)} records from CSV"

# Add to UI
def csv_upload_component():
    return rx.upload(
        rx.button("Upload CSV File"),
        on_drop=State.handle_csv_upload,
        accept={".csv": ["text/csv"]}
    )
```

**Dependencies:**
```bash
pip install pandas
```

---

## REST API Integration

### Example: Connecting to a Real API

```python
import httpx
from typing import Dict, List

class State(rx.State):
    api_url: str = ""
    api_key: str = ""
    
    async def connect_rest_api(self):
        """Connect to a REST API and fetch data."""
        self.integration_status = IntegrationStatus.CONNECTING
        self.progress = 0
        yield
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                
                self.progress = 30
                yield
                
                response = await client.get(
                    self.api_url,
                    headers=headers,
                    timeout=30.0
                )
                
                self.progress = 60
                yield
                
                if response.status_code == 200:
                    data = response.json()
                    self.source_records = data.get("records", [])
                    
                    if self.source_records:
                        self.source_fields = list(self.source_records[0].keys())
                    
                    self.progress = 100
                    self.integration_status = IntegrationStatus.SUCCESS
                    self.integration_message = f"Connected successfully! Retrieved {len(self.source_records)} records"
                else:
                    self.integration_status = IntegrationStatus.ERROR
                    self.integration_message = f"API Error: {response.status_code}"
                    
        except Exception as e:
            self.integration_status = IntegrationStatus.ERROR
            self.integration_message = f"Connection failed: {str(e)}"

# Add input fields to UI
def api_config_form():
    return rx.vstack(
        rx.input(
            placeholder="API URL",
            on_change=State.set_api_url,
            width="100%"
        ),
        rx.input(
            placeholder="API Key",
            type="password",
            on_change=State.set_api_key,
            width="100%"
        ),
        rx.button(
            "Connect to API",
            on_click=State.connect_rest_api
        )
    )
```

**Dependencies:**
```bash
pip install httpx
```

---

## Database Connection

### Example: PostgreSQL Integration

```python
import asyncpg
from typing import Optional

class State(rx.State):
    db_host: str = ""
    db_port: int = 5432
    db_name: str = ""
    db_user: str = ""
    db_password: str = ""
    db_query: str = ""
    
    async def connect_database(self):
        """Connect to PostgreSQL and fetch data."""
        self.integration_status = IntegrationStatus.CONNECTING
        self.progress = 0
        yield
        
        try:
            # Connect to database
            conn = await asyncpg.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password
            )
            
            self.progress = 40
            yield
            
            # Execute query
            rows = await conn.fetch(self.db_query)
            
            self.progress = 80
            yield
            
            # Convert to records
            self.source_records = [dict(row) for row in rows]
            
            if self.source_records:
                self.source_fields = list(self.source_records[0].keys())
            
            await conn.close()
            
            self.progress = 100
            self.integration_status = IntegrationStatus.SUCCESS
            self.integration_message = f"Connected to database! Retrieved {len(self.source_records)} records"
            
        except Exception as e:
            self.integration_status = IntegrationStatus.ERROR
            self.integration_message = f"Database error: {str(e)}"

# Database configuration UI
def database_config_form():
    return rx.vstack(
        rx.input(placeholder="Host", on_change=State.set_db_host),
        rx.input(placeholder="Port", value="5432", on_change=State.set_db_port),
        rx.input(placeholder="Database Name", on_change=State.set_db_name),
        rx.input(placeholder="Username", on_change=State.set_db_user),
        rx.input(placeholder="Password", type="password", on_change=State.set_db_password),
        rx.text_area(
            placeholder="SELECT * FROM customers LIMIT 100",
            on_change=State.set_db_query,
            width="100%"
        ),
        rx.button("Connect to Database", on_click=State.connect_database),
        spacing="3",
        width="100%"
    )
```

**Dependencies:**
```bash
pip install asyncpg  # For PostgreSQL
# or
pip install aiomysql  # For MySQL
```

---

## Salesforce Integration

### Example: Using simple-salesforce Library

```python
from simple_salesforce import Salesforce
from typing import Optional

class State(rx.State):
    sf_username: str = ""
    sf_password: str = ""
    sf_security_token: str = ""
    sf_domain: str = "login"  # or "test" for sandbox
    
    def connect_salesforce(self):
        """Connect to Salesforce and fetch accounts."""
        self.integration_status = IntegrationStatus.CONNECTING
        self.progress = 0
        yield
        
        try:
            # Connect to Salesforce
            sf = Salesforce(
                username=self.sf_username,
                password=self.sf_password,
                security_token=self.sf_security_token,
                domain=self.sf_domain
            )
            
            self.progress = 40
            yield
            
            # Query accounts
            query = """
                SELECT Id, Name, Email__c, Phone, BillingCity
                FROM Account
                WHERE IsDeleted = False
                LIMIT 100
            """
            
            result = sf.query(query)
            
            self.progress = 80
            yield
            
            # Extract records
            self.source_records = result['records']
            
            # Remove Salesforce metadata fields
            for record in self.source_records:
                record.pop('attributes', None)
            
            if self.source_records:
                self.source_fields = list(self.source_records[0].keys())
            
            self.progress = 100
            self.integration_status = IntegrationStatus.SUCCESS
            self.integration_message = f"Connected to Salesforce! Retrieved {len(self.source_records)} accounts"
            
        except Exception as e:
            self.integration_status = IntegrationStatus.ERROR
            self.integration_message = f"Salesforce error: {str(e)}"

# Salesforce configuration UI
def salesforce_config_form():
    return rx.vstack(
        rx.input(placeholder="Username", on_change=State.set_sf_username),
        rx.input(placeholder="Password", type="password", on_change=State.set_sf_password),
        rx.input(placeholder="Security Token", type="password", on_change=State.set_sf_security_token),
        rx.select(
            ["login", "test"],
            placeholder="Domain (login or test)",
            on_change=State.set_sf_domain
        ),
        rx.button("Connect to Salesforce", on_click=State.connect_salesforce),
        spacing="3",
        width="100%"
    )
```

**Dependencies:**
```bash
pip install simple-salesforce
```

---

## Webhook Receiver

### Example: Creating a Webhook Endpoint

```python
from fastapi import Request
import json

class State(rx.State):
    webhook_data: List[Dict] = []
    webhook_secret: str = ""
    
    def start_webhook_listener(self):
        """Start listening for webhooks."""
        self.integration_message = "Webhook listener started on /api/webhook"
        self.integration_status = IntegrationStatus.SUCCESS

# Add to your Reflex app
app = rx.App()

@app.api_route("/api/webhook", methods=["POST"])
async def webhook_handler(request: Request):
    """Handle incoming webhook requests."""
    try:
        # Verify webhook secret if needed
        auth_header = request.headers.get("Authorization")
        
        # Parse webhook data
        data = await request.json()
        
        # Store webhook data (in production, use database)
        # State.webhook_data.append(data)
        
        return {"status": "success", "message": "Webhook received"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Webhook UI
def webhook_component():
    return rx.vstack(
        rx.text("Webhook Endpoint:", weight="bold"),
        rx.code("POST http://localhost:3000/api/webhook"),
        rx.text("Recent webhooks:", weight="bold"),
        rx.foreach(
            State.webhook_data,
            lambda item: rx.card(
                rx.code(json.dumps(item, indent=2)),
                padding="3"
            )
        )
    )
```

---

## Custom Field Mapping

### Example: Advanced Field Mapping with Transformations

```python
from datetime import datetime
import re

class State(rx.State):
    field_transformations: Dict[str, str] = {}
    
    def add_field_transformation(self, source_field: str, transform_type: str):
        """Add a transformation to a field."""
        self.field_transformations[source_field] = transform_type
    
    def apply_transformations(self, value: str, transform_type: str) -> str:
        """Apply transformation to a value."""
        transformations = {
            "uppercase": lambda v: v.upper(),
            "lowercase": lambda v: v.lower(),
            "phone_format": lambda v: re.sub(r'(\d{3})(\d{3})(\d{4})', r'(\1) \2-\3', v),
            "date_format": lambda v: datetime.strptime(v, "%Y-%m-%d").strftime("%m/%d/%Y"),
            "remove_spaces": lambda v: v.replace(" ", ""),
            "trim": lambda v: v.strip()
        }
        
        transform_func = transformations.get(transform_type)
        if transform_func:
            try:
                return transform_func(value)
            except:
                return value
        return value
    
    def sync_with_transformations(self):
        """Sync data with field transformations applied."""
        self.integration_status = IntegrationStatus.SYNCING
        self.mapped_records = []
        
        for record in self.source_records:
            mapped = {}
            
            for source_field, netsuite_field in self.field_mapping.items():
                if source_field in record:
                    value = record[source_field]
                    
                    # Apply transformation if configured
                    if source_field in self.field_transformations:
                        transform_type = self.field_transformations[source_field]
                        value = self.apply_transformations(value, transform_type)
                    
                    mapped[netsuite_field] = value
            
            mapped["_status"] = "success"
            self.mapped_records.append(mapped)
        
        self.integration_status = IntegrationStatus.SUCCESS
        self.integration_message = f"Synced {len(self.mapped_records)} records with transformations"

# Field mapping UI with transformations
def field_mapping_with_transforms():
    return rx.vstack(
        rx.foreach(
            State.field_mapping.items(),
            lambda item: rx.hstack(
                rx.badge(item[0], variant="soft"),
                rx.text("→"),
                rx.badge(item[1], color="green", variant="soft"),
                rx.select(
                    ["none", "uppercase", "lowercase", "phone_format", "date_format"],
                    placeholder="Transform",
                    on_change=lambda val: State.add_field_transformation(item[0], val)
                ),
                spacing="2"
            )
        )
    )
```

---

## Real NetSuite Integration

### Example: Using NetSuite SuiteTalk REST API

```python
import requests
from requests_oauthlib import OAuth1Session

class State(rx.State):
    ns_account_id: str = ""
    ns_consumer_key: str = ""
    ns_consumer_secret: str = ""
    ns_token_id: str = ""
    ns_token_secret: str = ""
    
    def create_netsuite_session(self) -> OAuth1Session:
        """Create authenticated NetSuite session."""
        return OAuth1Session(
            self.ns_consumer_key,
            client_secret=self.ns_consumer_secret,
            resource_owner_key=self.ns_token_id,
            resource_owner_secret=self.ns_token_secret,
            realm=self.ns_account_id
        )
    
    async def sync_to_real_netsuite(self):
        """Sync records to real NetSuite instance."""
        self.integration_status = IntegrationStatus.SYNCING
        self.progress = 0
        yield
        
        session = self.create_netsuite_session()
        base_url = f"https://{self.ns_account_id}.suitetalk.api.netsuite.com/services/rest/record/v1"
        
        successful = 0
        failed = 0
        
        for i, record in enumerate(self.mapped_records):
            try:
                # Create customer in NetSuite
                customer_data = {
                    "companyName": record.get("Customer Name"),
                    "email": record.get("Email"),
                    "phone": record.get("Phone"),
                    "defaultAddress": {
                        "addressLine1": record.get("Address")
                    }
                }
                
                response = session.post(
                    f"{base_url}/customer",
                    json=customer_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code in [200, 201, 204]:
                    record["_status"] = "success"
                    record["_netsuite_id"] = response.json().get("id")
                    successful += 1
                else:
                    record["_status"] = "error"
                    record["_error"] = f"NetSuite API Error: {response.status_code}"
                    failed += 1
                    
            except Exception as e:
                record["_status"] = "error"
                record["_error"] = str(e)
                failed += 1
            
            self.progress = int((i + 1) / len(self.mapped_records) * 100)
            yield
        
        self.successful_syncs = successful
        self.failed_syncs = failed
        self.integration_status = IntegrationStatus.SUCCESS
        self.integration_message = f"Synced to NetSuite: {successful} successful, {failed} failed"
```

**Dependencies:**
```bash
pip install requests requests-oauthlib
```

---

## Environment Variables

For production deployments, use environment variables for sensitive data:

```python
import os
from dotenv import load_dotenv

load_dotenv()

class State(rx.State):
    def load_credentials(self):
        """Load credentials from environment variables."""
        self.api_key = os.getenv("API_KEY")
        self.db_password = os.getenv("DB_PASSWORD")
        self.ns_consumer_secret = os.getenv("NETSUITE_CONSUMER_SECRET")
```

**.env file:**
```bash
API_KEY=your_api_key_here
DB_PASSWORD=your_db_password
NETSUITE_CONSUMER_SECRET=your_secret
```

**Dependencies:**
```bash
pip install python-dotenv
```

---

## Error Handling Best Practices

```python
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class State(rx.State):
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def sync_with_retry(self, record: Dict):
        """Sync a single record with automatic retry."""
        try:
            # Attempt sync
            result = await self.sync_record_to_netsuite(record)
            logger.info(f"Successfully synced record: {record.get('id')}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to sync record: {record.get('id')}, Error: {str(e)}")
            raise
    
    def validate_record(self, record: Dict) -> tuple[bool, str]:
        """Validate a record before syncing."""
        required_fields = ["Customer Name", "Email"]
        
        for field in required_fields:
            if not record.get(field):
                return False, f"Missing required field: {field}"
        
        # Email validation
        email = record.get("Email")
        if email and "@" not in email:
            return False, f"Invalid email format: {email}"
        
        return True, "Valid"
```

**Dependencies:**
```bash
pip install tenacity
```

---

## Testing

### Example: Unit Tests

```python
import pytest
from proto_ddf_app.proto_ddf_app import State

def test_field_mapping():
    """Test automatic field mapping."""
    state = State()
    state.source_fields = ["name", "email", "phone"]
    state.auto_map_fields()
    
    assert "name" in state.field_mapping
    assert state.field_mapping["name"] == "Customer Name"
    assert state.field_mapping["email"] == "Email"

def test_record_validation():
    """Test record validation."""
    state = State()
    
    valid_record = {"Customer Name": "Test Corp", "Email": "test@example.com"}
    is_valid, message = state.validate_record(valid_record)
    assert is_valid
    
    invalid_record = {"Customer Name": "", "Email": "invalid"}
    is_valid, message = state.validate_record(invalid_record)
    assert not is_valid
```

---

## Performance Optimization

### Batch Processing

```python
import asyncio
from typing import List

class State(rx.State):
    batch_size: int = 100
    
    async def sync_in_batches(self):
        """Sync records in batches for better performance."""
        total = len(self.source_records)
        batches = [
            self.source_records[i:i + self.batch_size]
            for i in range(0, total, self.batch_size)
        ]
        
        for i, batch in enumerate(batches):
            tasks = [self.sync_record_to_netsuite(record) for record in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if isinstance(result, Exception):
                    self.failed_syncs += 1
                else:
                    self.successful_syncs += 1
            
            self.progress = int((i + 1) / len(batches) * 100)
            yield
```

---

## Next Steps

1. Choose the integration pattern that fits your needs
2. Install required dependencies
3. Configure credentials securely
4. Test with sample data first
5. Implement error handling and logging
6. Deploy to production

For more information, see the [main README](README.md) and [Quick Start Guide](QUICKSTART.md).




