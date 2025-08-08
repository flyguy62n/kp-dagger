# Protocols vs Abstract Base Classes (ABCs)

This document provides guidance on when to use Python Protocols versus Abstract Base Classes (ABCs) for interface design in KP-Dagger and similar projects.

## Overview

Both Protocols and ABCs define interfaces, but they serve different purposes and have distinct trade-offs. The choice between them depends on your specific use case, the relationship between components, and the level of coupling you want to enforce.

## Quick Decision Matrix

| Use Case | Recommendation | Reason |
|----------|----------------|---------|
| **Optional dependencies** | Protocol | Easy null implementations |
| **External library integration** | Protocol | No inheritance required |
| **UI interfaces** | Protocol | Loose coupling, duck typing |
| **Plugin-style architecture** | Protocol | Maximum flexibility |
| **Core business interfaces** | ABC | Strict contracts, shared implementation |
| **Domain model interfaces** | ABC | Inheritance hierarchy makes sense |
| **Shared functionality needed** | ABC | Common base implementation |
| **Runtime type checking needed** | ABC | `isinstance()` checks work |

## Detailed Comparison

### Protocols

**What they are**: Static type checking interfaces that use structural subtyping (duck typing).

#### Advantages

- **No inheritance required**: Any class that matches the interface "just works"
- **Easy null implementations**: Simple classes can implement without inheritance
- **External library compatibility**: Third-party classes can satisfy the protocol automatically
- **Loose coupling**: No runtime dependencies between interface and implementation
- **Performance**: No inheritance overhead
- **Flexibility**: Easy to retrofit existing code

#### Disadvantages

- **No shared implementation**: Can't provide common functionality
- **Static typing only**: No runtime type checking with `isinstance()`
- **No enforcement**: Nothing prevents partial implementation
- **Less discoverable**: Harder to find all implementations

#### Example Use Cases

```python
# Optional UI dependency
class IEventPublisher(Protocol):
    def publish(self, event: BaseEvent) -> None: ...

# Easy null implementation - no inheritance needed
class NullEventPublisher:
    def publish(self, event: BaseEvent) -> None:
        pass

# External library integration
class IProgressReporter(Protocol):
    def update(self, percent: float, message: str) -> None: ...

# Rich's Progress class might already match this interface
```

### Abstract Base Classes (ABCs)

**What they are**: Classes that define interfaces with optional shared implementation and runtime type checking.

#### Advantages

- **Shared implementation**: Can provide common functionality to subclasses
- **Runtime type checking**: `isinstance()` and `issubclass()` work
- **Strict contracts**: Abstract methods must be implemented
- **Discoverable**: Easy to find all subclasses
- **Clear inheritance hierarchy**: Explicit relationships between classes
- **Method resolution order**: Proper MRO for complex hierarchies

#### Disadvantages

- **Inheritance required**: All implementations must inherit from the ABC
- **Tighter coupling**: Creates dependency between interface and implementation
- **Harder null implementations**: Null objects must inherit from ABC
- **External library friction**: Third-party classes must be wrapped or modified
- **Performance overhead**: Inheritance and method resolution costs

#### Example Use Cases

```python
from abc import ABC, abstractmethod

# Core business interface with shared functionality
class BaseParser(ABC):
    def __init__(self, logger: LoggingService):
        self.logger = logger
    
    @abstractmethod
    def parse(self, config_text: str) -> dict[str, Any]:
        """Parse configuration text."""
        ...
    
    def _log_parsing_start(self, file_path: str) -> None:
        """Shared logging implementation."""
        self.logger.info(f"Starting to parse {file_path}")

# Domain model with clear hierarchy
class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, config: ParsedConfig) -> AnalysisResult:
        ...
    
    @abstractmethod
    def get_supported_formats(self) -> list[str]:
        ...
```

## Detailed Guidelines

### Use Protocols When:

#### 1. **Optional Dependencies**
When a component might or might not be present, Protocols make null implementations trivial:
```python
class ILogger(Protocol):
    def log(self, message: str) -> None: ...

class NullLogger:  # No inheritance needed
    def log(self, message: str) -> None:
        pass
```

#### 2. **External Library Integration**
When you want to work with third-party libraries that can't inherit from your classes:
```python
class ICache(Protocol):
    def get(self, key: str) -> Any: ...
    def set(self, key: str, value: Any) -> None: ...

# Redis client, memcached, etc. can satisfy this without modification
```

#### 3. **Duck Typing Scenarios**
When you care about behavior, not inheritance:
```python
class IDrawable(Protocol):
    def draw(self, canvas: Canvas) -> None: ...

# Any object with a draw() method works
# Circles, rectangles, custom graphics libraries, etc.
```

#### 4. **UI Interfaces**
When connecting business logic to presentation layers:
```python
class IEventPublisher(Protocol):
    def publish(self, event: Event) -> None: ...

# CLI, GUI, web interfaces can all implement differently
```

### Use ABCs When:

#### 1. **Core Business Interfaces**
When defining the essential contracts of your domain:
```python
class BaseReporter(ABC):
    @abstractmethod
    def generate_report(self, data: AnalysisResult) -> str:
        ...
    
    @abstractmethod
    def get_supported_formats(self) -> list[str]:
        ...
```

#### 2. **Shared Implementation Needed**
When multiple implementations share common functionality:
```python
class BaseAnalyzer(ABC):
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.findings: list[Finding] = []
    
    @abstractmethod
    def analyze(self, data: ConfigData) -> AnalysisResult:
        ...
    
    def add_finding(self, finding: Finding) -> None:
        """Shared implementation for all analyzers."""
        self.findings.append(finding)
        self._validate_finding(finding)
```

#### 3. **Runtime Type Checking**
When you need to check types at runtime:
```python
class BaseParser(ABC):
    @abstractmethod
    def parse(self, content: str) -> ParsedConfig:
        ...

# Later in code:
if isinstance(parser, BaseParser):
    result = parser.parse(content)
```

#### 4. **Clear Domain Hierarchies**
When inheritance relationships make conceptual sense:
```python
class BaseNetworkDevice(ABC):
    @abstractmethod
    def get_config(self) -> str:
        ...

class CiscoDevice(BaseNetworkDevice):
    # Cisco-specific implementation
    ...

class FortinetDevice(BaseNetworkDevice):
    # Fortinet-specific implementation
    ...
```

## Anti-Patterns to Avoid

### Protocol Anti-Patterns

❌ **Using Protocols for core business logic with shared state**
```python
# Don't do this - no way to share implementation
class IAnalyzer(Protocol):
    def analyze(self, config: Config) -> Result: ...
    def get_findings(self) -> list[Finding]: ...  # Each impl must duplicate this
```

❌ **Complex Protocol hierarchies**
```python
# Protocols don't compose well
class IReader(Protocol): ...
class IWriter(Protocol): ...
class IReaderWriter(IReader, IWriter, Protocol): ...  # Confusing
```

### ABC Anti-Patterns

❌ **Using ABCs for optional dependencies**
```python
# Don't do this - makes null implementations awkward
class IEventPublisher(ABC):
    @abstractmethod
    def publish(self, event: Event) -> None: ...

class NullEventPublisher(IEventPublisher):  # Forced inheritance
    def publish(self, event: Event) -> None:
        pass
```

❌ **Using ABCs for external library interfaces**
```python
# Don't do this - can't modify third-party libraries
class IHttpClient(ABC):
    @abstractmethod
    def get(self, url: str) -> Response: ...

# requests.Session can't inherit from this
```

## Mixed Approach Example

Often, the best solution combines both patterns:

```python
# ABC for core business logic
class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, config: ParsedConfig) -> AnalysisResult:
        ...

# Protocol for optional UI dependency
class IEventPublisher(Protocol):
    def publish(self, event: Event) -> None: ...

# Service uses both appropriately
class AnalysisService:
    def __init__(
        self,
        analyzer: BaseAnalyzer,  # ABC - strict business contract
        event_publisher: IEventPublisher | None = None,  # Protocol - optional UI
    ):
        self.analyzer = analyzer
        self.event_publisher = event_publisher or NullEventPublisher()
```

## Performance Considerations

### Protocols
- ✅ **Faster**: No inheritance overhead
- ✅ **Smaller memory footprint**: No MRO chains
- ⚠️ **Type checking cost**: MyPy needs to verify structural compatibility

### ABCs
- ⚠️ **Method resolution overhead**: Inheritance chain traversal
- ⚠️ **Memory overhead**: MRO and inheritance metadata
- ✅ **Runtime checks**: Fast `isinstance()` checks

## Testing Implications

### Protocols
```python
# Easy to mock - no inheritance required
class MockEventPublisher:
    def __init__(self):
        self.events = []
    
    def publish(self, event: Event) -> None:
        self.events.append(event)

# Works immediately as IEventPublisher
```

### ABCs
```python
# Must inherit for proper testing
class MockAnalyzer(BaseAnalyzer):
    def analyze(self, config: ParsedConfig) -> AnalysisResult:
        return AnalysisResult()

# But benefits from shared implementation and isinstance() checks
```

## Migration Path

### From ABC to Protocol
1. Create Protocol with same method signatures
2. Remove ABC inheritance from implementations
3. Update type hints to use Protocol
4. Remove shared implementation (move to utility functions if needed)

### From Protocol to ABC
1. Create ABC with same method signatures
2. Add `@abstractmethod` decorators
3. Update implementations to inherit from ABC
4. Move common functionality to ABC
5. Update type hints to use ABC

## Summary

**Choose Protocols for**:
- UI interfaces and optional dependencies
- External library integration
- Duck typing scenarios
- Maximum flexibility and loose coupling

**Choose ABCs for**:
- Core business interfaces with shared implementation
- Domain model hierarchies
- Strict contract enforcement
- Runtime type checking requirements

The key is to match the tool to the problem domain and coupling requirements rather than using one approach exclusively.
