# Error Handling Strategy for KP Dagger

## Philosophy

KP Dagger uses a **event-driven error handling approach** with emphasis on **robust parsing** and **real-time user feedback**:

- **Parsers raise specific exceptions** for syntax and parsing errors at the lowest level
- **Parser methods catch exceptions** and publish to event bus for UI feedback  
- **Continue processing** after errors to extract maximum value from configurations
- **Event publishing** provides real-time feedback to UI while maintaining partial results
- **Service layer** can subscribe to error events for additional handling if needed

## Exception Hierarchy

### Current Exception Structure

```python
DaggerError                              # Base for all KP Dagger errors
├── ConfigurationError                   # Configuration and setup errors  
├── ParsingError                        # Base parsing errors (has device_type, line_number)
│   ├── UnrecognizedLineFormatError     # Context-agnostic unrecognized line format
│   ├── ContextStackError               # Parser context/stack management errors
│   └── UnsupportedVendorError          # Unsupported device types
├── DatabaseError                       # Database operation errors
├── ValidationError                     # Data validation errors (has field, value)
├── AnalysisError                       # Security analysis errors
├── ReportError                         # Report generation errors
└── APIError                           # External API errors (has api_name, status_code)
```

## Current Implementation Pattern

### 1. Parser Layer (Event-Driven + Continue Processing)

**✅ Current Implementation:** Parsers raise exceptions that are caught and converted to events

```python
def _parse_line(self, line: str) -> None:
    """Parse a single configuration line."""
    # Try pattern matching...
    if match := self.patterns["config"].match(line):
        self._handle_config(match.group(1))
    # ... other patterns ...
    else:
        # Raise context-agnostic exception
        raise UnrecognizedLineFormatError(
            line_content=line.strip(),
            device_type="fortigate",
            expected_patterns=list(self.patterns.keys()),
        )

def parse_lines(self, lines: list[str]) -> dict[str, Any]:
    """Parse configuration lines with event-driven error handling."""
    for line_num, line in enumerate(lines, 1):
        try:
            self._parse_line(line.rstrip("\n\r"))
        except UnrecognizedLineFormatError as e:
            # Publish to event bus with line context and continue
            self.event_publisher.publish(
                OperationError(
                    operation_type="parsing",
                    resource_path=self.current_path[-1] if self.current_path else None,
                    error_message=f"Unrecognized line format: {e.line_content}",
                    error_context={
                        "line_number": line_num,
                        "line_content": line.strip(),
                        "expected_patterns": e.expected_patterns,
                        "device_type": e.device_type,
                    },
                ),
            )
            continue  # Keep parsing remaining lines
        except Exception as e:
            # Handle unexpected errors similarly
            self.event_publisher.publish(OperationError(...))
            continue
    
    return self.config_data  # Return partial results
```

### 2. Key Benefits of Event-Driven Approach

**🔄 Consistent Processing:** All parsing errors are handled uniformly
**📡 Real-time Feedback:** UI receives immediate error notifications with rich context
**📊 Partial Results:** Extract maximum value from imperfect configuration files  
**🏗️ Robust Parsing:** Individual line errors don't break entire configuration analysis
**🎯 Rich Context:** Events include line numbers, content, expected patterns, and device context

### 3. Service Layer (Event Subscription)

Services can subscribe to parsing events for additional processing:

```python
class ConfigurationService:
    def __init__(self, event_publisher: SafeEventPublisher):
        self.event_publisher = event_publisher
        self.parsing_errors = []
        
        # Subscribe to parsing errors
        self.event_publisher.subscribe(
            OperationError, 
            self._handle_parsing_error
        )
    
    def _handle_parsing_error(self, event: OperationError) -> None:
        """Handle parsing errors for analysis and reporting."""
        if event.operation_type == "parsing":
            self.parsing_errors.append({
                "line_number": event.error_context.get("line_number"),
                "line_content": event.error_context.get("line_content"),
                "error_message": event.error_message,
                "device_type": event.error_context.get("device_type"),
            })
    
    def parse_with_summary(self, file_path: Path) -> ParseResult:
        """Parse and provide error summary."""
        self.parsing_errors.clear()
        
        result = self.parser.parse_file(file_path)
        
        return ParseResult(
            config_data=result,
            errors=self.parsing_errors,
            success=len(self.parsing_errors) == 0,
            partial_success=len(result) > 0
        )
```

### 4. CLI Layer (Event-Based Feedback)

CLI can subscribe to events for real-time user feedback:

```python
class CliEventHandler:
    def __init__(self, rich_output: RichOutput):
        self.rich_output = rich_output
        self.error_count = 0
    
    def handle_operation_error(self, event: OperationError) -> None:
        """Display parsing errors in real-time."""
        if event.operation_type == "parsing":
            self.error_count += 1
            
            line_num = event.error_context.get("line_number", "?")
            line_content = event.error_context.get("line_content", "")
            
            self.rich_output.warning(
                f"⚠ Line {line_num}: {event.error_message}"
            )
            
            if len(line_content) > 60:
                line_content = line_content[:57] + "..."
            self.rich_output.info(f"   Content: {line_content}")

@click.command()
def parse_config(config_file: Path):
    """Parse configuration with real-time feedback."""
    handler = CliEventHandler(rich_output)
    event_publisher.subscribe(OperationError, handler.handle_operation_error)
    
    try:
        result = parser.parse_file(config_file)
        
        if handler.error_count == 0:
            rich_output.success(f"✓ Successfully parsed {config_file.name}")
        else:
            rich_output.warning(
                f"⚠ Parsed {config_file.name} with {handler.error_count} warnings"
            )
            rich_output.info(f"Extracted {len(result)} configuration sections")
            
    except Exception as e:
        rich_output.error(f"❌ Critical error: {e}")
        raise click.Abort()
```

## Error Recovery Strategies

### Current Strategy: Catch-and-Continue with Event Publishing

**✅ Implemented Approach:** Robust parsing that maximizes data extraction

```python
def parse_lines(self, lines: list[str]) -> dict[str, Any]:
    """Current implementation: catch, notify, continue."""
    for line_num, line in enumerate(lines, 1):
        try:
            self._parse_line(line.rstrip("\n\r"))
        except UnrecognizedLineFormatError as e:
            # Notify UI/subscribers and continue
            self.event_publisher.publish(OperationError(...))
            continue
        except Exception as e:
            # Handle any unexpected errors
            self.event_publisher.publish(OperationError(...))
            continue
    
    return self.config_data  # Always returns partial results
```

### Alternative Patterns (for different use cases)

#### 1. Strict Mode (Fail Fast)
For critical applications requiring perfect input:

```python
def strict_parse(self, lines: list[str]) -> dict[str, Any]:
    """Parse with zero error tolerance - re-raise all exceptions."""
    for line_num, line in enumerate(lines, 1):
        try:
            self._parse_line(line.rstrip("\n\r"))
        except ParsingError as e:
            # Add line context and re-raise
            e.line_number = line_num
            raise
    return self.config_data
```

## Error Context and Rich Information

### Exception Attributes

All parsing exceptions include rich context for debugging and user feedback:

```python
# UnrecognizedLineFormatError attributes
error.line_content          # The problematic line
error.device_type          # Parser context (e.g., "fortigate")
error.expected_patterns    # List of valid patterns
error.details             # Dict with additional context

# ParsingError (base) attributes  
error.device_type         # Device/vendor type
error.line_number        # Line number (when available)
error.message           # Human-readable error message
error.details          # Additional context dictionary
```

### Event Bus Error Context

Events published to the bus include comprehensive context:

```python
OperationError(
    operation_type="parsing",
    resource_path=current_file_path,
    error_message="Unrecognized line format: invalid config line",
    error_context={
        "line_number": 42,
        "line_content": "invalid config line",
        "expected_patterns": ["config", "edit", "set", "unset", "next", "end"],
        "device_type": "fortigate",
        "parser_state": "in_config_section"
    }
)
```

## Best Practices

### Do's ✅

- **Use event-driven error handling** for parsers that need to continue processing
- **Raise context-agnostic exceptions** at the lowest level (without line numbers)
- **Enrich exceptions with context** when publishing events (add line numbers, file paths)
- **Subscribe to error events** for real-time UI feedback and error aggregation
- **Return partial results** whenever possible for robust parsing
- **Include rich error context** in exception details and event contexts
- **Use specific exception types** from the hierarchy for different error categories
- **Test both successful parsing and error conditions** thoroughly

### Don'ts ❌

- **Don't fail entire parsing** for individual line errors in configuration parsers
- **Don't include caller context** (like line numbers) in low-level parser exceptions
- **Don't ignore errors silently** - always publish to event bus or re-raise
- **Don't catch broad `Exception`** without specific handling and event publishing
- **Don't mix error handling strategies** within the same parser component
- **Don't use string-based error checking** instead of proper exception hierarchy

### Current Implementation Patterns

#### ✅ Good: Context-Agnostic Exception Raising
```python
def _parse_line(self, line: str) -> None:
    """Parse without caller context."""
    if not self._is_valid_line(line):
        raise UnrecognizedLineFormatError(
            line_content=line.strip(),
            device_type="fortigate",
            expected_patterns=list(self.patterns.keys())
        )
```

#### ✅ Good: Event Publishing with Context
```python
def parse_lines(self, lines: list[str]) -> dict[str, Any]:
    """Add context and publish events."""
    for line_num, line in enumerate(lines, 1):
        try:
            self._parse_line(line.rstrip("\n\r"))
        except UnrecognizedLineFormatError as e:
            self.event_publisher.publish(
                OperationError(
                    operation_type="parsing",
                    error_message=f"Unrecognized line format: {e.line_content}",
                    error_context={
                        "line_number": line_num,  # Context added here
                        "line_content": e.line_content,
                        "expected_patterns": e.expected_patterns,
                    }
                )
            )
            continue
```

## Testing Error Conditions

### Test Event Publishing
```python
def test_unrecognized_line_publishes_event():
    """Test that parsing errors are published to event bus."""
    mock_publisher = Mock()
    parser = FortigateConfigParser(
        file_processing_service=Mock(),
        event_publisher=mock_publisher
    )
    
    # Parse invalid line
    result = parser.parse_lines(["invalid line format"])
    
    # Verify event was published
    mock_publisher.publish.assert_called_once()
    event = mock_publisher.publish.call_args[0][0]
    
    assert isinstance(event, OperationError)
    assert event.operation_type == "parsing"
    assert "Unrecognized line format" in event.error_message
    assert event.error_context["line_number"] == 1
    assert "invalid line format" in event.error_context["line_content"]
```

### Test Partial Results
```python
def test_partial_parsing_with_errors():
    """Test that parser returns partial results despite errors."""
    parser = FortigateConfigParser(...)
    
    lines = [
        "config system global",
        "    set hostname test-fw",
        "invalid line here",  # This should be skipped
        "    set timezone GMT",
        "end"
    ]
    
    result = parser.parse_lines(lines)
    
    # Should have partial config despite error
    assert "system global" in result
    assert result["system global"]["hostname"] == "test-fw"
    assert result["system global"]["timezone"] == "GMT"
```

## Architecture Benefits

This **event-driven, catch-and-continue** approach provides:

🔧 **Robustness:** Parse real-world configs with unknown directives
🎯 **Precision:** Specific exceptions with rich context at each layer  
📡 **Real-time Feedback:** UI updates as parsing progresses
📊 **Data Recovery:** Extract maximum value from imperfect input files
🧪 **Testability:** Clear separation between error detection and handling
🔄 **Consistency:** Uniform error handling across all parser implementations

This strategy is particularly effective for **configuration parsers** that encounter vendor-specific extensions, comments, or malformed sections in real-world network device configurations.