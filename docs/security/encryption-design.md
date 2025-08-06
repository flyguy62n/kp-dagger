# Encryption Design

Dagger implements a comprehensive field-level encryption system to protect sensitive network configuration data at rest and in transit.

## Overview

The encryption system provides:

- **Field-level encryption** for sensitive configuration data
- **Tenant isolation** ensuring data separation between customers
- **Transparent access** through Python descriptors
- **Modern cryptographic standards** with Argon2id and AES256-GCM

## Architecture

### Core Components

1. **EncryptionService** (`Dagger.core.encryption`)
   - Handles all cryptographic operations
   - Tenant-specific key derivation
   - Authenticated encryption/decryption

2. **EncryptedField** (`Dagger.models.base.encryption`)
   - Python descriptor for transparent field access
   - Automatic encryption/decryption
   - Caching for performance

3. **DaggerBaseModel** (`Dagger.models.base.base`)
   - SQLModel integration
   - Encryption service injection
   - Encrypted data serialization

## Cryptographic Standards

### Key Derivation

**Primary: Argon2id**
```
- Algorithm: Argon2id (hybrid version)
- Time cost: 3 iterations
- Memory cost: 64 MiB
- Parallelism: 1 thread
- Output: 32 bytes (256 bits)
```

**Fallback: PBKDF2**
```
- Algorithm: PBKDF2-HMAC-SHA256
- Iterations: 600,000
- Salt: 32 bytes (random per tenant)
- Output: 32 bytes (256 bits)
```

### Encryption

**Algorithm: AES256-GCM**
```
- Key size: 256 bits
- Nonce: 12 bytes (random per operation)
- Authentication tag: 16 bytes
- Associated data: Tenant ID
```

## Implementation

### Tenant Isolation

Each tenant gets a unique encryption key derived from:
- Master runtime key (application-wide)
- Tenant UUID
- Random salt (stored with encrypted data)

```python
tenant_key = derive_key(runtime_key, tenant_id, salt)
```

### Field Encryption

Sensitive fields are transparently encrypted:

```python
class IPAddress(DaggerBaseModel):
    original_address: str | None = EncryptedField(default=None)
    normalized_address: str | None = EncryptedField(default=None)
```

### Usage Example

```python
from uuid import uuid4
from Dagger.core.encryption import EncryptionServiceManager
from Dagger.models.normalized.ip_address import IPAddress

# Initialize encryption
runtime_key = EncryptionServiceManager.generate_runtime_key()
manager = EncryptionServiceManager(runtime_key)
tenant_id = uuid4()
service = manager.get_service(tenant_id)

# Create model with encryption
ip_addr = IPAddress(tenant_id=tenant_id)
ip_addr.set_encryption_service(service)

# Transparent field access
ip_addr.original_address = "192.168.1.1"  # Automatically encrypted
print(ip_addr.original_address)           # Automatically decrypted
```

## Security Features

### Data Protection

- **At Rest**: All sensitive fields encrypted in database
- **In Memory**: Decrypted values cached securely
- **In Transit**: Encrypted data never exposed in APIs

### Threat Model

Protected against:
- Database breaches (encrypted data)
- Memory dumps (limited plaintext exposure)
- Cross-tenant access (cryptographic isolation)
- Offline attacks (strong key derivation)

### Performance Considerations

- **Lazy decryption**: Only when field accessed
- **Caching**: Decrypted values cached per instance
- **Batch operations**: Encryption service reused per tenant

## Testing

Comprehensive test suite covers:

- Encryption/decryption operations
- Tenant isolation (cross-tenant data access)
- Error handling (corrupted data, wrong keys)
- Performance characteristics
- SQLModel integration

## Best Practices

### Key Management

1. **Runtime keys** should be generated per application instance
2. **Tenant isolation** must be maintained at all layers
3. **Key rotation** procedures should be implemented
4. **Secure deletion** of keys when tenants are removed

### Development

1. **Never log** decrypted sensitive data
2. **Use encrypted serialization** for database storage
3. **Validate tenant context** before decryption
4. **Handle decryption errors** gracefully

## Compliance

This encryption design supports:

- **GDPR**: Data protection by design and default
- **SOC 2**: Data encryption and access controls
- **PCI DSS**: Strong cryptography standards
- **NIST**: Approved cryptographic algorithms

## Migration and Upgrades

The system supports:

- **Algorithm upgrades** through fallback mechanisms
- **Key rotation** with versioned encryption
- **Backward compatibility** with existing encrypted data
- **Secure migration** procedures for algorithm changes
