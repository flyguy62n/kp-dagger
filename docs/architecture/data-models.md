# Data Models

Dagger uses SQLModel to combine SQLAlchemy ORM capabilities with Pydantic validation for robust data handling.

## Base Models

### KPDaggerBaseModel

All models inherit from `KPDaggerBaseModel`, which provides:

- **Tenant isolation** through `tenant_id` field
- **Encryption service integration** for sensitive data
- **Audit fields** for tracking creation and modification
- **Validation** using Pydantic

```python
class KPDaggerBaseModel(SQLModel):
    id: uuid.UUID | None = Field(default_factory=uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    def set_encryption_service(self, service: EncryptionService) -> None:
        """Set the encryption service for this model instance."""
        self._encryption_service = service
```

### Tenant Model

Provides multi-tenant support:

```python
class Tenant(DaggerTenantModel, table=True):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    is_active: bool = Field(default=True)
    settings: dict[str, Any] = Field(default_factory=dict)
```

## Device Models

### Normalized Device Model

Common fields across all device types:

```python
class Device(KPDaggerBaseModel, table=True):
    hostname: str | None = EncryptedField(default=None)
    management_ip: str | None = EncryptedField(default=None)
    device_type: DeviceType
    vendor: Vendor
    model: str | None = Field(default=None, max_length=100)
    version: str | None = Field(default=None, max_length=100)
    serial_number: str | None = EncryptedField(default=None)
    location: str | None = Field(default=None, max_length=255)
    last_backup: datetime | None = Field(default=None)
    
    # Relationships
    interfaces: list["Interface"] = Relationship(back_populates="device")
    configurations: list["Configuration"] = Relationship(back_populates="device")
```

### Interface Model

Network interface information:

```python
class Interface(KPDaggerBaseModel, table=True):
    device_id: uuid.UUID = Field(foreign_key="device.id")
    name: str = Field(max_length=100)
    interface_type: InterfaceType
    description: str | None = EncryptedField(default=None)
    ip_address: str | None = EncryptedField(default=None)
    subnet_mask: str | None = Field(default=None, max_length=45)
    vlan_id: int | None = Field(default=None)
    status: InterfaceStatus = Field(default=InterfaceStatus.UNKNOWN)
    
    # Relationships
    device: Device = Relationship(back_populates="interfaces")
    access_lists: list["AccessList"] = Relationship(back_populates="interface")
```

## Configuration Models

### Configuration File

Stores parsed configuration data:

```python
class Configuration(KPDaggerBaseModel, table=True):
    device_id: uuid.UUID = Field(foreign_key="device.id")
    filename: str = Field(max_length=255)
    file_hash: str = Field(max_length=64)  # SHA256
    file_size: int
    content_encrypted: bytes | None = Field(default=None)
    parsing_status: ParsingStatus = Field(default=ParsingStatus.PENDING)
    parsing_errors: list[str] = Field(default_factory=list)
    
    # Relationships
    device: Device = Relationship(back_populates="configurations")
    findings: list["SecurityFinding"] = Relationship(back_populates="configuration")
```

### Access Control Lists

Security rules and ACLs:

```python
class AccessList(KPDaggerBaseModel, table=True):
    device_id: uuid.UUID = Field(foreign_key="device.id")
    interface_id: uuid.UUID | None = Field(foreign_key="interface.id", default=None)
    name: str = Field(max_length=255)
    direction: Direction
    sequence: int | None = Field(default=None)
    action: Action
    protocol: str | None = Field(default=None, max_length=20)
    source: str | None = EncryptedField(default=None)
    destination: str | None = EncryptedField(default=None)
    port_range: str | None = Field(default=None, max_length=100)
    
    # Relationships
    device: Device = Relationship(back_populates="access_lists")
    interface: Interface | None = Relationship(back_populates="access_lists")
```

## Analysis Models

### Security Findings

Results from security analysis:

```python
class SecurityFinding(KPDaggerBaseModel, table=True):
    configuration_id: uuid.UUID = Field(foreign_key="configuration.id")
    rule_id: str = Field(max_length=100)  # CIS benchmark ID
    category: FindingCategory
    severity: Severity
    title: str = Field(max_length=255)
    description: str = Field(max_length=2000)
    recommendation: str = Field(max_length=2000)
    evidence: dict[str, Any] = Field(default_factory=dict)
    false_positive: bool = Field(default=False)
    suppressed: bool = Field(default=False)
    
    # Relationships
    configuration: Configuration = Relationship(back_populates="findings")
```

### Vulnerability Information

CVE and vulnerability tracking:

```python
class Vulnerability(KPDaggerBaseModel, table=True):
    cve_id: str = Field(max_length=20, unique=True)
    cvss_score: float | None = Field(default=None)
    cvss_vector: str | None = Field(default=None, max_length=200)
    description: str = Field(max_length=4000)
    published_date: datetime | None = Field(default=None)
    modified_date: datetime | None = Field(default=None)
    affected_versions: list[str] = Field(default_factory=list)
    
    # Relationships
    findings: list["VulnerabilityFinding"] = Relationship(back_populates="vulnerability")
```

## Enumerations

### Device Types and Vendors

```python
class Vendor(str, Enum):
    CISCO = "cisco"
    FORTINET = "fortinet"
    PALOALTO = "paloalto"
    JUNIPER = "juniper"
    UNKNOWN = "unknown"

class DeviceType(str, Enum):
    ROUTER = "router"
    SWITCH = "switch"
    FIREWALL = "firewall"
    LOAD_BALANCER = "load_balancer"
    UNKNOWN = "unknown"
```

### Security Classifications

```python
class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class FindingCategory(str, Enum):
    ACCESS_CONTROL = "access_control"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ENCRYPTION = "encryption"
    LOGGING = "logging"
    CONFIGURATION = "configuration"
    VULNERABILITY = "vulnerability"
```

## Encryption Integration

### Encrypted Fields

Sensitive data is automatically encrypted using `EncryptedField`:

```python
class IPAddress(KPDaggerBaseModel, table=True):
    original_address: str | None = EncryptedField(default=None)
    normalized_address: str | None = EncryptedField(default=None)
    version: IPVersion
    is_private: bool = Field(default=False)
    is_multicast: bool = Field(default=False)
    network_id: uuid.UUID | None = Field(foreign_key="network.id", default=None)
```

### Usage with Encryption

```python
# Set up encryption service
service = encryption_manager.get_service(tenant_id)
ip_addr = IPAddress(tenant_id=tenant_id)
ip_addr.set_encryption_service(service)

# Transparent field access
ip_addr.original_address = "192.168.1.1"  # Automatically encrypted
print(ip_addr.original_address)           # Automatically decrypted

# Database storage
encrypted_data = ip_addr.model_dump_encrypted()  # For database
```

## Relationships and Constraints

### Foreign Key Relationships

All models maintain referential integrity:

```python
# Device → Configuration (1:many)
device.configurations

# Configuration → SecurityFinding (1:many)  
configuration.findings

# Device → Interface (1:many)
device.interfaces

# Interface → AccessList (1:many)
interface.access_lists
```

### Database Constraints

- **Unique constraints** on business keys
- **Check constraints** for data validation
- **Index definitions** for performance
- **Cascade rules** for data consistency

## Validation Rules

### Pydantic Validators

Custom validation for complex fields:

```python
@field_validator("ip_address")
@classmethod
def validate_ip_address(cls, v: str | None) -> str | None:
    if v is None:
        return v
    try:
        ipaddress.ip_address(v)
        return v
    except ValueError as e:
        raise ValueError(f"Invalid IP address: {v}") from e
```

### Model Validators

Cross-field validation:

```python
@model_validator(mode="after")
def validate_port_range(self) -> "AccessList":
    if self.protocol in ["tcp", "udp"] and not self.port_range:
        raise ValueError("Port range required for TCP/UDP protocols")
    return self
```

## Migration Support

### Schema Evolution

Models support schema changes through:

- **Optional fields** for backward compatibility
- **Default values** for new fields
- **Migration scripts** for data transformation
- **Version tracking** for schema changes

### Data Migration

```python
# Example migration for new encrypted field
def migrate_sensitive_data(session: Session) -> None:
    devices = session.exec(select(Device)).all()
    for device in devices:
        if device.hostname_plaintext:  # Old field
            device.hostname = device.hostname_plaintext  # New encrypted field
            device.hostname_plaintext = None
    session.commit()
```
