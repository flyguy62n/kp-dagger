# Progress Callback Pattern

The Progress Callback Pattern provides fine-grained progress reporting and real-time updates through separated interfaces that follow the single responsibility principle.

## Progress Reporter Interfaces

```python
# services/core/workflow/interfaces.py
from typing import Protocol

class IProgressTracker(Protocol):
    """Pure progress tracking interface - single responsibility."""
    
    def update_progress(self, step: str, percent: float, message: str) -> None:
        """Update progress for the current operation."""
        ...
    
    def update_file_progress(self, current: int, total: int, file_name: str) -> None:
        """Update progress across multiple files."""
        ...
    
    def update_substep(self, parent_step: str, substep: str, percent: float) -> None:
        """Update progress for sub-operations within a step."""
        ...

class ICancellationToken(Protocol):
    """Cancellation control interface - single responsibility."""
    
    def is_cancelled(self) -> bool:
        """Check if operation should be cancelled."""
        ...

class IOperationReporter(Protocol):
    """Operation lifecycle reporting interface - single responsibility."""
    
    def report_completion(self, success: bool, duration: float, summary: dict) -> None:
        """Report operation completion with results."""
        ...
    
    def report_error(self, error: str, context: dict) -> None:
        """Report an error with contextual information."""
        ...

# Composed interface for convenience (optional)
class IProgressReporter(IProgressTracker, ICancellationToken, IOperationReporter, Protocol):
    """Convenience interface combining all progress-related concerns.
    
    UIs can implement this single interface if they want all functionality,
    or implement individual interfaces for specific needs.
    """
    pass

# Null implementations for optional dependencies
class NullProgressTracker:
    """No-op progress tracking for headless operation."""
    def update_progress(self, step: str, percent: float, message: str) -> None:
        pass
    def update_file_progress(self, current: int, total: int, file_name: str) -> None:
        pass
    def update_substep(self, parent_step: str, substep: str, percent: float) -> None:
        pass

class NullCancellationToken:
    """No-op cancellation token that never cancels."""
    def is_cancelled(self) -> bool:
        return False

class NullOperationReporter:
    """No-op operation reporter for headless operation."""
    def report_completion(self, success: bool, duration: float, summary: dict) -> None:
        pass
    def report_error(self, error: str, context: dict) -> None:
        pass
```

## Service Implementation with Separated Progress Interfaces

```python
# services/analysis/service.py
class AnalysisService:
    @inject
    def __init__(
        self,
        event_publisher: SafeEventPublisher = Provide[CoreContainer.safe_event_publisher],
        vulnerability_analyzer: VulnerabilityAnalyzer = Provide[AnalyzerContainer.vulnerability_analyzer],
        compliance_analyzer: ComplianceAnalyzer = Provide[AnalyzerContainer.compliance_analyzer],
        logger: LoggingService = Provide[CoreContainer.logging_service],
    ):
        self.event_publisher = event_publisher
        self.vulnerability_analyzer = vulnerability_analyzer
        self.compliance_analyzer = compliance_analyzer
        self.logger = logger

    def analyze_configuration(
        self,
        parsed_config: ParsedConfiguration,
        analysis_types: list[str],
        progress_tracker: IProgressTracker | None = None,
        cancellation_token: ICancellationToken | None = None,
        operation_reporter: IOperationReporter | None = None
    ) -> AnalysisResult:
        
        # Use null implementations if none provided
        progress_tracker = progress_tracker or NullProgressTracker()
        cancellation_token = cancellation_token or NullCancellationToken()
        operation_reporter = operation_reporter or NullOperationReporter()
        
        total_steps = len(analysis_types)
        results = {}
        
        for i, analysis_type in enumerate(analysis_types):
            # Clean cancellation checking
            if cancellation_token.is_cancelled():
                raise OperationCancelledException("Analysis cancelled by user")
            
            step_percent = (i / total_steps) * 100
            
            # Clean progress reporting
            progress_tracker.update_progress(
                f"analysis_{analysis_type}",
                step_percent,
                f"Running {analysis_type} analysis..."
            )
            
            try:
                if analysis_type == "vuln":
                    result = self._analyze_vulnerabilities(
                        parsed_config, 
                        progress_tracker, 
                        cancellation_token
                    )
                elif analysis_type == "config":
                    result = self._analyze_compliance(
                        parsed_config, 
                        progress_tracker, 
                        cancellation_token
                    )
                elif analysis_type == "rules":
                    result = self._analyze_firewall_rules(
                        parsed_config, 
                        progress_tracker, 
                        cancellation_token
                    )
                else:
                    raise ValueError(f"Unknown analysis type: {analysis_type}")
                
                results[analysis_type] = result
                
                # Event publishing for findings using generic event type
                if analysis_type == "vuln":
                    for vuln in result.vulnerabilities:
                        self.event_publisher.publish(FindingDiscovered(
                            finding_type="vuln",
                            severity=vuln.severity,
                            identifier=vuln.cve_id,
                            description=vuln.description,
                            details={"component": vuln.component, "analysis_type": analysis_type}
                        ))
                elif analysis_type == "config":
                    for violation in result.violations:
                        self.event_publisher.publish(FindingDiscovered(
                            finding_type="config",
                            severity=violation.severity,
                            identifier=violation.rule_id,
                            description=violation.description,
                            details={"recommendation": violation.recommendation, "analysis_type": analysis_type},
                            location={"line_number": violation.line_number} if violation.line_number else None
                        ))
                elif analysis_type == "rules":
                    for rule_violation in result.rule_violations:
                        self.event_publisher.publish(FindingDiscovered(
                            finding_type="rules",
                            severity=rule_violation.severity,
                            identifier=rule_violation.rule_name,
                            description=rule_violation.description,
                            details={"source": rule_violation.source, "destination": rule_violation.destination, "analysis_type": analysis_type},
                            location={"line_number": rule_violation.line_number} if rule_violation.line_number else None
                        ))
                
            except Exception as e:
                # Clean error reporting (separate from progress)
                operation_reporter.report_error(
                    f"Failed {analysis_type} analysis: {str(e)}",
                    {"analysis_type": analysis_type, "step": i}
                )
                raise
        
        # Clean completion reporting
        operation_reporter.report_completion(
            success=True,
            duration=2.5,
            summary={"analyses_completed": len(results)}
        )
        
        return AnalysisResult(results)

    def _analyze_vulnerabilities(
        self, 
        config: ParsedConfiguration,
        progress_tracker: IProgressTracker,
        cancellation_token: ICancellationToken
    ) -> VulnerabilityAnalysisResult:
        
        components = config.get_components()
        total_components = len(components)
        vulnerabilities = []
        
        for i, component in enumerate(components):
            if cancellation_token.is_cancelled():
                raise OperationCancelledException("Vulnerability analysis cancelled")
            
            substep_percent = (i / total_components) * 100
            progress_tracker.update_substep(
                "analysis_vuln",
                f"checking_{component.name}",
                substep_percent
            )
            
            # Check component for vulnerabilities
            component_vulns = self.vulnerability_analyzer.check_component(component)
            vulnerabilities.extend(component_vulns)
        
        return VulnerabilityAnalysisResult(vulnerabilities)
```

## UI Progress Implementations

### Option 1: Focused Implementations (Recommended)

```python
# cli/progress/cli_progress_components.py

class CliProgressTracker(IProgressTracker):
    """Focused progress tracking for CLI."""
    
    def __init__(self, rich_output: RichOutputService):
        self.rich_output = rich_output
        self.main_progress = None
        self.sub_progress = None
        self.file_progress = None

    def update_progress(self, step: str, percent: float, message: str) -> None:
        if not self.main_progress:
            self.main_progress = self.rich_output.create_progress_bar(
                "Analysis Progress", 
                total=100
            )
        self.main_progress.update(percent, message)

    def update_file_progress(self, current: int, total: int, file_name: str) -> None:
        if not self.file_progress:
            self.file_progress = self.rich_output.create_progress_bar(
                "File Progress",
                total=total
            )
        self.file_progress.update(current, f"Processing {file_name}")

    def update_substep(self, parent_step: str, substep: str, percent: float) -> None:
        if not self.sub_progress:
            self.sub_progress = self.rich_output.create_progress_bar(
                f"  ↳ {parent_step} details",
                total=100
            )
        self.sub_progress.update(percent, substep.replace("_", " ").title())

class CliCancellationToken(ICancellationToken):
    """CLI cancellation handling."""
    
    def __init__(self):
        self.cancelled = False
        # Set up signal handlers for Ctrl+C, etc.
    
    def is_cancelled(self) -> bool:
        return self.cancelled

class CliOperationReporter(IOperationReporter):
    """CLI operation lifecycle reporting."""
    
    def __init__(self, rich_output: RichOutputService):
        self.rich_output = rich_output

    def report_completion(self, success: bool, duration: float, summary: dict) -> None:
        analyses = summary.get("analyses_completed", 0)
        if success:
            self.rich_output.success(
                f"Analysis completed in {duration:.1f}s ({analyses} analyses)"
            )
        else:
            self.rich_output.error(f"Analysis failed after {duration:.1f}s")

    def report_error(self, error: str, context: dict) -> None:
        step = context.get("analysis_type", "unknown")
        self.rich_output.error(f"Error in {step}: {error}")

# Usage in CLI commands:
@click.command()
@inject
def scan(
    config_paths: list[str],
    workflow: WorkflowService = Provide[CoreContainer.workflow_service],
    rich_output: RichOutputService = Provide[CoreContainer.rich_output_service],
):
    # Create focused components
    progress_tracker = CliProgressTracker(rich_output)
    cancellation_token = CliCancellationToken()
    operation_reporter = CliOperationReporter(rich_output)
    
    # Pass to service with clear separation
    results = workflow.scan_configurations(
        config_paths=[Path(p) for p in config_paths],
        progress_tracker=progress_tracker,
        cancellation_token=cancellation_token,
        operation_reporter=operation_reporter
    )
```

### Option 2: Composed Implementation (For Convenience)

```python
# cli/progress/cli_progress_reporter.py
class CliProgressReporter(IProgressReporter):
    """Composed implementation of all progress interfaces for convenience."""
    
    def __init__(self, rich_output: RichOutputService):
        self.rich_output = rich_output
        self.main_progress = None
        self.sub_progress = None
        self.file_progress = None
        self.cancelled = False

    # IProgressTracker methods
    def update_progress(self, step: str, percent: float, message: str) -> None:
        if not self.main_progress:
            self.main_progress = self.rich_output.create_progress_bar(
                "Analysis Progress", 
                total=100
            )
        self.main_progress.update(percent, message)

    def update_file_progress(self, current: int, total: int, file_name: str) -> None:
        if not self.file_progress:
            self.file_progress = self.rich_output.create_progress_bar(
                "File Progress",
                total=total
            )
        self.file_progress.update(current, f"Processing {file_name}")

    def update_substep(self, parent_step: str, substep: str, percent: float) -> None:
        if not self.sub_progress:
            self.sub_progress = self.rich_output.create_progress_bar(
                f"  ↳ {parent_step} details",
                total=100
            )
        self.sub_progress.update(percent, substep.replace("_", " ").title())

    # ICancellationToken methods
    def is_cancelled(self) -> bool:
        return self.cancelled

    # IOperationReporter methods
    def report_completion(self, success: bool, duration: float, summary: dict) -> None:
        if self.main_progress:
            self.main_progress.update(100, "Complete")
        
        analyses = summary.get("analyses_completed", 0)
        self.rich_output.success(f"Analysis completed in {duration:.1f}s ({analyses} analyses)")

    def report_error(self, error: str, context: dict) -> None:
        step = context.get("analysis_type", "unknown")
        self.rich_output.error(f"Error in {step}: {error}")
```

### GUI Progress Components (Future)

```python
# gui/progress/gui_progress_components.py
class GuiProgressTracker(IProgressTracker):
    """GUI progress tracking with Qt widgets."""
    
    def __init__(self, progress_dialog: QProgressDialog):
        self.progress_dialog = progress_dialog
        self.sub_dialog = None

    def update_progress(self, step: str, percent: float, message: str) -> None:
        self.progress_dialog.setValue(int(percent))
        self.progress_dialog.setLabelText(message)
        QApplication.processEvents()  # Keep UI responsive

    def update_file_progress(self, current: int, total: int, file_name: str) -> None:
        # Could use a separate file progress dialog or update main one
        self.progress_dialog.setMaximum(total)
        self.progress_dialog.setValue(current)
        self.progress_dialog.setLabelText(f"Processing {file_name}")

    def update_substep(self, parent_step: str, substep: str, percent: float) -> None:
        if not self.sub_dialog:
            self.sub_dialog = QProgressDialog(
                f"Details for {parent_step}",
                "Cancel",
                0, 100,
                self.progress_dialog
            )
        self.sub_dialog.setValue(int(percent))
        self.sub_dialog.setLabelText(substep.replace("_", " ").title())

class GuiCancellationToken(ICancellationToken):
    """GUI cancellation via dialog cancel button."""
    
    def __init__(self, progress_dialog: QProgressDialog):
        self.progress_dialog = progress_dialog

    def is_cancelled(self) -> bool:
        return self.progress_dialog.wasCanceled()

class GuiOperationReporter(IOperationReporter):
    """GUI operation reporting via message boxes."""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget

    def report_completion(self, success: bool, duration: float, summary: dict) -> None:
        analyses = summary.get("analyses_completed", 0)
        if success:
            QMessageBox.information(
                self.parent,
                "Analysis Complete",
                f"Analysis completed successfully in {duration:.1f}s\n"
                f"Completed {analyses} analyses"
            )
        else:
            QMessageBox.warning(
                self.parent,
                "Analysis Failed", 
                f"Analysis failed after {duration:.1f}s"
            )

    def report_error(self, error: str, context: dict) -> None:
        step = context.get("analysis_type", "unknown")
        QMessageBox.critical(
            self.parent,
            "Analysis Error",
            f"Error in {step}:\n{error}"
        )
```

## Testing Progress Interfaces

```python
# tests/test_progress_interfaces.py
from unittest.mock import Mock

# Mock implementations for focused testing
class MockProgressTracker(IProgressTracker):
    def __init__(self):
        self.progress_calls = []
        self.file_calls = []
        self.substep_calls = []
    
    def update_progress(self, step: str, percent: float, message: str) -> None:
        self.progress_calls.append((step, percent, message))
    
    def update_file_progress(self, current: int, total: int, file_name: str) -> None:
        self.file_calls.append((current, total, file_name))
    
    def update_substep(self, parent_step: str, substep: str, percent: float) -> None:
        self.substep_calls.append((parent_step, substep, percent))

class MockCancellationToken(ICancellationToken):
    def __init__(self, should_cancel_after: int = -1):
        self.call_count = 0
        self.should_cancel_after = should_cancel_after
    
    def is_cancelled(self) -> bool:
        self.call_count += 1
        return self.call_count > self.should_cancel_after if self.should_cancel_after > 0 else False

class MockOperationReporter(IOperationReporter):
    def __init__(self):
        self.completion_calls = []
        self.error_calls = []
    
    def report_completion(self, success: bool, duration: float, summary: dict) -> None:
        self.completion_calls.append((success, duration, summary))
    
    def report_error(self, error: str, context: dict) -> None:
        self.error_calls.append((error, context))

def test_service_with_progress_interfaces():
    """Test that services use progress interfaces correctly."""
    service = AnalysisService(
        event_publisher=Mock(),
        vulnerability_analyzer=Mock(),
        compliance_analyzer=Mock(),
        logger=Mock()
    )
    
    # Mock progress components
    progress_tracker = MockProgressTracker()
    cancellation_token = MockCancellationToken()
    operation_reporter = MockOperationReporter()
    
    # Mock parsed config
    parsed_config = Mock()
    
    # Execute with progress tracking
    result = service.analyze_configuration(
        parsed_config,
        ["vuln", "config"],
        progress_tracker=progress_tracker,
        cancellation_token=cancellation_token,
        operation_reporter=operation_reporter
    )
    
    # Verify progress was tracked
    assert len(progress_tracker.progress_calls) > 0
    assert any("vuln" in call[0] for call in progress_tracker.progress_calls)
    assert any("config" in call[0] for call in progress_tracker.progress_calls)
    
    # Verify completion was reported
    assert len(operation_reporter.completion_calls) == 1
    assert operation_reporter.completion_calls[0][0]  # success=True

def test_cancellation_handling():
    """Test that services handle cancellation properly."""
    service = AnalysisService(
        event_publisher=Mock(),
        vulnerability_analyzer=Mock(),
        compliance_analyzer=Mock(),
        logger=Mock()
    )
    
    # Set up cancellation after first check
    cancellation_token = MockCancellationToken(should_cancel_after=1)
    
    with pytest.raises(OperationCancelledException):
        service.analyze_configuration(
            Mock(),
            ["vuln", "config"],
            cancellation_token=cancellation_token
        )
```

## Benefits

### Clear Separation of Concerns
- **Single responsibility**: Each interface handles one specific concern
- **Optional dependencies**: Services work without any progress reporting
- **Composable design**: UIs can implement individual or combined interfaces

### Flexibility
- **UI-specific implementations**: Each UI can provide appropriate feedback
- **Null implementations**: Headless operation with no overhead
- **Graceful degradation**: Missing implementations don't break functionality

### Enhanced User Experience
- **Real-time feedback**: Fine-grained progress updates
- **Cancellation support**: Users can interrupt long-running operations
- **Error reporting**: Contextual error information for debugging

### Testing Benefits
- **Mockable interfaces**: Easy to test progress-dependent logic
- **Focused testing**: Test each concern independently
- **No UI dependencies**: Business logic tested without UI components

## Best Practices

1. **Use separated interfaces** for single responsibility
2. **Provide null implementations** for optional dependencies
3. **Test progress logic** with mock implementations
4. **Keep progress updates lightweight** to avoid performance impact

## Next Steps

- [Workflow Orchestration](workflow-orchestration.md) - Learn about coordinating business logic with UI feedback
- [Testing Patterns](testing-patterns.md) - Explore comprehensive testing strategies
