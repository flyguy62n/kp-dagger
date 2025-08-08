# Testing Patterns for UI-Service Separation

Comprehensive testing strategies for the UI-service separation architecture, ensuring robust functionality across all layers while maintaining clean separation of concerns.

## Testing Architecture Overview

```python
# tests/conftest.py - Shared test configuration
import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path
import tempfile
import shutil

from kp_dagger.containers.core import CoreContainer
from kp_dagger.containers.analyzers import AnalyzerContainer
from kp_dagger.containers.parsers import ParserContainer
from dependency_injector import providers

@pytest.fixture
def mock_core_container():
    """Mock core container for isolated testing."""
    container = CoreContainer()
    container.event_publisher.override(providers.Object(Mock()))
    container.logging_service.override(providers.Object(Mock()))
    container.rich_output_service.override(providers.Object(Mock()))
    return container

@pytest.fixture
def temp_config_dir():
    """Temporary directory with test configuration files."""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create sample config files
    (temp_dir / "router1.cfg").write_text("""
    hostname router1
    ip access-list extended TEST_ACL
     permit tcp any any eq 80
     deny ip any any
    """)
    
    (temp_dir / "firewall1.cfg").write_text("""
    hostname firewall1
    access-list outside_in permit tcp any any eq 443
    access-list outside_in deny ip any any
    """)
    
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_progress_interfaces():
    """Mock progress interfaces for testing."""
    progress_tracker = Mock()
    cancellation_token = Mock()
    cancellation_token.is_cancelled.return_value = False
    operation_reporter = Mock()
    
    return {
        "progress_tracker": progress_tracker,
        "cancellation_token": cancellation_token,
        "operation_reporter": operation_reporter
    }

@pytest.fixture
def sample_parsed_config():
    """Sample parsed configuration for testing."""
    return Mock(
        device_type="cisco_ios",
        hostname="test-router",
        version="15.1",
        access_lists=[
            Mock(name="TEST_ACL", rules=[
                Mock(action="permit", protocol="tcp", source="any", dest="any", port="80"),
                Mock(action="deny", protocol="ip", source="any", dest="any")
            ])
        ]
    )
```

## Service Layer Testing

### Testing Business Logic Without UI Dependencies

```python
# tests/unit/services/test_analysis_service.py
import pytest
from unittest.mock import Mock, patch
from kp_dagger.services.analysis.service import AnalysisService
from kp_dagger.models.analysis import VulnerabilityResult, ComplianceViolation

class TestAnalysisService:
    """Test analysis service business logic in isolation."""
    
    def test_analyze_configuration_success(self, sample_parsed_config):
        """Test successful configuration analysis."""
        
        # Arrange
        event_publisher = Mock()
        vulnerability_analyzer = Mock()
        compliance_analyzer = Mock()
        logger = Mock()
        
        # Configure mock returns
        vulnerability_analyzer.check_component.return_value = [
            VulnerabilityResult(
                cve_id="CVE-2023-1234",
                severity="high",
                component="ios",
                version="15.1",
                description="Test vulnerability"
            )
        ]
        
        compliance_analyzer.check_configuration.return_value = [
            ComplianceViolation(
                rule_id="CIS-1.1",
                severity="medium", 
                description="Weak password policy",
                recommendation="Enable strong password requirements"
            )
        ]
        
        service = AnalysisService(
            event_publisher=event_publisher,
            vulnerability_analyzer=vulnerability_analyzer,
            compliance_analyzer=compliance_analyzer,
            logger=logger
        )
        
        # Act
        result = service.analyze_configuration(
            sample_parsed_config,
            ["vuln", "config"]
        )
        
        # Assert
        assert "vuln" in result.results
        assert "config" in result.results
        assert len(result.results["vuln"].vulnerabilities) == 1
        assert len(result.results["config"].violations) == 1
        
        # Verify events were published
        assert event_publisher.publish.call_count == 2  # One for vuln, one for config
        
        # Verify analyzers were called
        vulnerability_analyzer.check_component.assert_called()
        compliance_analyzer.check_configuration.assert_called()
    
    def test_analyze_configuration_with_progress_tracking(
        self, 
        sample_parsed_config,
        mock_progress_interfaces
    ):
        """Test analysis with progress tracking interfaces."""
        
        # Arrange
        service = AnalysisService(
            event_publisher=Mock(),
            vulnerability_analyzer=Mock(),
            compliance_analyzer=Mock(),
            logger=Mock()
        )
        
        progress_tracker = mock_progress_interfaces["progress_tracker"]
        cancellation_token = mock_progress_interfaces["cancellation_token"] 
        operation_reporter = mock_progress_interfaces["operation_reporter"]
        
        # Act
        result = service.analyze_configuration(
            sample_parsed_config,
            ["vuln"],
            progress_tracker=progress_tracker,
            cancellation_token=cancellation_token,
            operation_reporter=operation_reporter
        )
        
        # Assert
        progress_tracker.update_progress.assert_called()
        cancellation_token.is_cancelled.assert_called()
        operation_reporter.report_completion.assert_called_once()
        
        # Verify completion report details
        completion_call = operation_reporter.report_completion.call_args
        assert completion_call[1]["success"] is True
        assert "analyses_completed" in completion_call[1]["summary"]
    
    def test_analyze_configuration_with_cancellation(
        self,
        sample_parsed_config,
        mock_progress_interfaces
    ):
        """Test analysis cancellation handling."""
        
        # Arrange
        service = AnalysisService(
            event_publisher=Mock(),
            vulnerability_analyzer=Mock(),
            compliance_analyzer=Mock(),
            logger=Mock()
        )
        
        # Configure cancellation token to cancel immediately
        cancellation_token = mock_progress_interfaces["cancellation_token"]
        cancellation_token.is_cancelled.return_value = True
        
        # Act & Assert
        with pytest.raises(OperationCancelledException):
            service.analyze_configuration(
                sample_parsed_config,
                ["vuln", "config"],
                cancellation_token=cancellation_token
            )
    
    def test_analyze_configuration_error_handling(
        self,
        sample_parsed_config,
        mock_progress_interfaces
    ):
        """Test error handling and reporting."""
        
        # Arrange
        vulnerability_analyzer = Mock()
        vulnerability_analyzer.check_component.side_effect = Exception("Analysis failed")
        
        service = AnalysisService(
            event_publisher=Mock(),
            vulnerability_analyzer=vulnerability_analyzer,
            compliance_analyzer=Mock(),
            logger=Mock()
        )
        
        operation_reporter = mock_progress_interfaces["operation_reporter"]
        
        # Act & Assert
        with pytest.raises(Exception, match="Analysis failed"):
            service.analyze_configuration(
                sample_parsed_config,
                ["vuln"],
                operation_reporter=operation_reporter
            )
        
        # Verify error was reported
        operation_reporter.report_error.assert_called_once()
        error_call = operation_reporter.report_error.call_args
        assert "Failed vuln analysis" in error_call[0][0]
        assert error_call[0][1]["analysis_type"] == "vuln"
```

### Testing Event System

```python
# tests/unit/core/test_event_system.py
import pytest
import threading
import time
from unittest.mock import Mock
from kp_dagger.core.events.bus import EventBusService
from kp_dagger.core.events.types import FindingDiscovered

class TestEventBusService:
    """Test event bus functionality and memory management."""
    
    def test_event_subscription_and_publishing(self):
        """Test basic event subscription and publishing."""
        
        # Arrange
        event_bus = EventBusService()
        handler = Mock()
        
        # Act
        subscription = event_bus.subscribe(FindingDiscovered, handler)
        
        event = FindingDiscovered(
            finding_type="vuln",
            severity="high",
            identifier="CVE-2023-1234",
            description="Test vulnerability"
        )
        
        event_bus.publish(event)
        
        # Assert
        handler.assert_called_once_with(event)
        
        # Cleanup
        subscription.unsubscribe()
    
    def test_subscription_context_manager(self):
        """Test subscription context manager for automatic cleanup."""
        
        # Arrange
        event_bus = EventBusService()
        handler = Mock()
        
        # Act
        with event_bus.subscribe(FindingDiscovered, handler) as subscription:
            event = FindingDiscovered(
                finding_type="vuln",
                severity="high", 
                identifier="CVE-2023-1234",
                description="Test vulnerability"
            )
            event_bus.publish(event)
            
            # Handler should be called while subscribed
            handler.assert_called_once()
        
        # After context manager, subscription should be cleaned up
        handler.reset_mock()
        event_bus.publish(event)
        
        # Handler should not be called after unsubscription
        handler.assert_not_called()
    
    def test_memory_management_with_batch_subscriptions(self):
        """Test memory management with subscription manager."""
        
        # Arrange
        event_bus = EventBusService()
        handlers = [Mock() for _ in range(5)]
        
        # Act
        with event_bus.subscription_manager() as manager:
            for handler in handlers:
                manager.subscribe(FindingDiscovered, handler)
            
            event = FindingDiscovered(
                finding_type="vuln",
                severity="high",
                identifier="CVE-2023-1234", 
                description="Test vulnerability"
            )
            event_bus.publish(event)
            
            # All handlers should be called
            for handler in handlers:
                handler.assert_called_once()
        
        # After context manager, all subscriptions should be cleaned up
        for handler in handlers:
            handler.reset_mock()
        
        event_bus.publish(event)
        
        # No handlers should be called after cleanup
        for handler in handlers:
            handler.assert_not_called()
    
    def test_thread_safety(self):
        """Test thread-safe event publishing and subscription."""
        
        # Arrange
        event_bus = EventBusService()
        handler = Mock()
        results = []
        
        def publish_events():
            for i in range(100):
                event = FindingDiscovered(
                    finding_type="vuln",
                    severity="high",
                    identifier=f"CVE-2023-{i:04d}",
                    description=f"Test vulnerability {i}"
                )
                event_bus.publish(event)
        
        def handle_event(event):
            results.append(event.identifier)
        
        # Act
        subscription = event_bus.subscribe(FindingDiscovered, handle_event)
        
        # Start multiple threads publishing events
        threads = [threading.Thread(target=publish_events) for _ in range(3)]
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Assert
        assert len(results) == 300  # 3 threads × 100 events each
        
        # Cleanup
        subscription.unsubscribe()
    
    def test_memory_leak_prevention(self):
        """Test that subscriptions don't leak memory."""
        
        # Arrange
        event_bus = EventBusService()
        initial_subscription_count = len(event_bus._subscriptions.get(FindingDiscovered, []))
        
        # Act - Create and destroy many subscriptions
        for _ in range(100):
            with event_bus.subscribe(FindingDiscovered, Mock()):
                pass  # Subscription automatically cleaned up
        
        # Assert
        final_subscription_count = len(event_bus._subscriptions.get(FindingDiscovered, []))
        assert final_subscription_count == initial_subscription_count
```

## Workflow Testing

```python
# tests/unit/workflow/test_workflow_orchestration.py
import pytest
from unittest.mock import Mock, MagicMock
from kp_dagger.services.workflow.orchestrator import WorkflowOrchestrator
from kp_dagger.services.workflow.steps import ParseConfigurationsStep

class TestWorkflowOrchestrator:
    """Test workflow orchestration logic."""
    
    def test_simple_workflow_execution(self):
        """Test execution of a simple workflow."""
        
        # Arrange
        orchestrator = WorkflowOrchestrator(
            event_publisher=Mock(),
            logger=Mock()
        )
        
        # Create mock steps
        step1 = Mock()
        step1.execute.return_value = {"step1_output": "value1"}
        step1.__class__.__name__ = "MockStep1"
        
        step2 = Mock() 
        step2.execute.return_value = {"step2_output": "value2"}
        step2.__class__.__name__ = "MockStep2"
        
        # Register workflow
        orchestrator.register_step("step1", step1)
        orchestrator.register_step("step2", step2)
        orchestrator.register_workflow("test_workflow", ["step1", "step2"])
        
        # Act
        result = orchestrator.execute_workflow(
            "test_workflow",
            {"initial_data": "test"}
        )
        
        # Assert
        assert result["initial_data"] == "test"
        assert result["step1_output"] == "value1"
        assert result["step2_output"] == "value2"
        
        # Verify execution order and context flow
        step1.execute.assert_called_once()
        step2.execute.assert_called_once()
        
        # Verify step2 received step1's output
        step2_context = step2.execute.call_args[0][0]
        assert step2_context["step1_output"] == "value1"
    
    def test_workflow_with_progress_tracking(self, mock_progress_interfaces):
        """Test workflow execution with progress tracking."""
        
        # Arrange
        orchestrator = WorkflowOrchestrator(
            event_publisher=Mock(),
            logger=Mock()
        )
        
        step = Mock()
        step.execute.return_value = {"result": "success"}
        step.__class__.__name__ = "MockStep"
        
        orchestrator.register_step("step", step)
        orchestrator.register_workflow("test", ["step"])
        
        progress_tracker = mock_progress_interfaces["progress_tracker"]
        
        # Act
        result = orchestrator.execute_workflow(
            "test",
            {},
            progress_tracker=progress_tracker
        )
        
        # Assert
        progress_tracker.update_progress.assert_called()
        
        # Verify progress updates
        progress_calls = progress_tracker.update_progress.call_args_list
        assert any("workflow_step_1" in call[0][0] for call in progress_calls)
        assert any("workflow_complete" in call[0][0] for call in progress_calls)
    
    def test_workflow_cancellation_handling(self, mock_progress_interfaces):
        """Test workflow cancellation at various points."""
        
        # Arrange
        orchestrator = WorkflowOrchestrator(
            event_publisher=Mock(),
            logger=Mock()
        )
        
        step1 = Mock()
        step1.execute.return_value = {"step1": "done"}
        step1.__class__.__name__ = "Step1"
        
        step2 = Mock()  # This should not be called
        step2.__class__.__name__ = "Step2"
        
        orchestrator.register_step("step1", step1)
        orchestrator.register_step("step2", step2)
        orchestrator.register_workflow("test", ["step1", "step2"])
        
        # Configure cancellation after first step
        cancellation_token = mock_progress_interfaces["cancellation_token"]
        cancellation_token.is_cancelled.side_effect = [False, True]  # Cancel after step1
        
        # Act & Assert
        with pytest.raises(OperationCancelledException):
            orchestrator.execute_workflow(
                "test",
                {},
                cancellation_token=cancellation_token
            )
        
        # Verify step1 executed but step2 did not
        step1.execute.assert_called_once()
        step2.execute.assert_not_called()
    
    def test_workflow_error_handling(self, mock_progress_interfaces):
        """Test workflow error handling and reporting."""
        
        # Arrange
        orchestrator = WorkflowOrchestrator(
            event_publisher=Mock(),
            logger=Mock()
        )
        
        failing_step = Mock()
        failing_step.execute.side_effect = Exception("Step failed")
        failing_step.__class__.__name__ = "FailingStep"
        
        orchestrator.register_step("failing_step", failing_step)
        orchestrator.register_workflow("test", ["failing_step"])
        
        operation_reporter = mock_progress_interfaces["operation_reporter"]
        
        # Act & Assert
        with pytest.raises(Exception, match="Step failed"):
            orchestrator.execute_workflow(
                "test",
                {},
                operation_reporter=operation_reporter
            )
        
        # Verify error reporting
        operation_reporter.report_error.assert_called_once()
        operation_reporter.report_completion.assert_called_once()
        
        # Verify completion reported failure
        completion_call = operation_reporter.report_completion.call_args
        assert completion_call[1]["success"] is False

class TestWorkflowSteps:
    """Test individual workflow step implementations."""
    
    def test_parse_configurations_step(self, temp_config_dir, mock_progress_interfaces):
        """Test configuration parsing step."""
        
        # Arrange
        config_parser = Mock()
        parsed_config1 = Mock(device_type="cisco_ios", hostname="router1")
        parsed_config2 = Mock(device_type="cisco_asa", hostname="firewall1")
        config_parser.parse_file.side_effect = [parsed_config1, parsed_config2]
        
        step = ParseConfigurationsStep(config_parser)
        
        config_paths = list(temp_config_dir.glob("*.cfg"))
        context = {"config_paths": config_paths}
        
        progress_tracker = mock_progress_interfaces["progress_tracker"]
        
        # Act
        result = step.execute(
            context,
            progress_tracker=progress_tracker
        )
        
        # Assert
        assert "parsed_configurations" in result
        assert len(result["parsed_configurations"]) == 2
        assert result["total_files_parsed"] == 2
        
        # Verify parser was called for each file
        assert config_parser.parse_file.call_count == 2
        
        # Verify progress tracking
        progress_tracker.update_file_progress.assert_called()
        progress_tracker.update_substep.assert_called()
```

## UI Component Testing

### CLI Testing

```python
# tests/unit/cli/test_commands.py
import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch
from pathlib import Path

from kp_dagger.cli.commands.scan import scan
from kp_dagger.containers.core import CoreContainer

class TestScanCommand:
    """Test CLI scan command without dependency injection complexity."""
    
    def test_scan_command_success(self, temp_config_dir):
        """Test successful scan command execution."""
        
        # Arrange
        runner = CliRunner()
        
        with patch('kp_dagger.cli.commands.scan.workflow') as mock_workflow, \
             patch('kp_dagger.cli.commands.scan.rich_output') as mock_rich_output:
            
            # Configure mock returns
            mock_workflow.scan_configurations.return_value = {
                "total_vulnerabilities": 5,
                "total_violations": 3,
                "total_files_parsed": 2
            }
            
            # Act
            result = runner.invoke(scan, [
                str(temp_config_dir / "router1.cfg"),
                str(temp_config_dir / "firewall1.cfg"),
                "--analysis-types", "vuln",
                "--output-format", "json"
            ])
            
            # Assert
            assert result.exit_code == 0
            mock_workflow.scan_configurations.assert_called_once()
            mock_rich_output.success.assert_called()
            
            # Verify workflow was called with correct parameters
            call_args = mock_workflow.scan_configurations.call_args
            assert len(call_args[1]["config_paths"]) == 2
            assert call_args[1]["analysis_types"] == ["vuln"]
            assert call_args[1]["output_format"] == "json"
    
    def test_scan_command_cancellation(self, temp_config_dir):
        """Test scan command handles cancellation gracefully."""
        
        runner = CliRunner()
        
        with patch('kp_dagger.cli.commands.scan.workflow') as mock_workflow, \
             patch('kp_dagger.cli.commands.scan.rich_output') as mock_rich_output:
            
            # Configure workflow to raise cancellation
            mock_workflow.scan_configurations.side_effect = OperationCancelledException("Cancelled")
            
            # Act
            result = runner.invoke(scan, [str(temp_config_dir / "router1.cfg")])
            
            # Assert
            assert result.exit_code == 1  # click.Abort()
            mock_rich_output.info.assert_called_with("Scan cancelled by user")
    
    def test_scan_command_error_handling(self, temp_config_dir):
        """Test scan command error handling."""
        
        runner = CliRunner()
        
        with patch('kp_dagger.cli.commands.scan.workflow') as mock_workflow, \
             patch('kp_dagger.cli.commands.scan.rich_output') as mock_rich_output:
            
            # Configure workflow to raise error
            mock_workflow.scan_configurations.side_effect = Exception("Analysis failed")
            
            # Act
            result = runner.invoke(scan, [str(temp_config_dir / "router1.cfg")])
            
            # Assert
            assert result.exit_code == 1
            mock_rich_output.error.assert_called_with("Scan failed: Analysis failed")

# tests/unit/cli/test_progress_components.py
class TestCliProgressComponents:
    """Test CLI progress tracking components."""
    
    def test_cli_progress_tracker(self):
        """Test CLI progress tracker updates."""
        
        # Arrange
        rich_output = Mock()
        progress_bar = Mock()
        rich_output.create_progress_bar.return_value = progress_bar
        
        tracker = CliProgressTracker(rich_output)
        
        # Act
        tracker.update_progress("test_step", 50.0, "Testing progress")
        tracker.update_progress("test_step", 100.0, "Complete")
        
        # Assert
        rich_output.create_progress_bar.assert_called_once_with(
            "Analysis Progress",
            total=100
        )
        
        assert progress_bar.update.call_count == 2
        progress_bar.update.assert_any_call(50.0, "Testing progress")
        progress_bar.update.assert_any_call(100.0, "Complete")
    
    def test_cli_operation_reporter(self):
        """Test CLI operation reporting."""
        
        # Arrange  
        rich_output = Mock()
        reporter = CliOperationReporter(rich_output)
        
        # Act
        reporter.report_completion(
            success=True,
            duration=2.5,
            summary={"analyses_completed": 3}
        )
        
        reporter.report_error(
            "Analysis failed",
            {"analysis_type": "vuln", "step": 1}
        )
        
        # Assert
        rich_output.success.assert_called_once_with(
            "Analysis completed in 2.5s (3 analyses)"
        )
        rich_output.error.assert_called_once_with("Error in vuln: Analysis failed")
```

## Integration Testing

```python
# tests/integration/test_end_to_end_workflow.py
import pytest
from pathlib import Path
import tempfile
import shutil

from kp_dagger.containers.core import CoreContainer
from kp_dagger.containers.parsers import ParserContainer
from kp_dagger.containers.analyzers import AnalyzerContainer
from kp_dagger.services.workflow.service import WorkflowService

class TestEndToEndWorkflow:
    """Integration tests for complete workflow execution."""
    
    @pytest.fixture
    def integrated_containers(self):
        """Set up integrated container environment."""
        # This would set up real containers with actual implementations
        # but isolated from external dependencies (network, files, etc.)
        
        core_container = CoreContainer()
        parser_container = ParserContainer()
        analyzer_container = AnalyzerContainer()
        
        # Override external dependencies with mocks
        # but keep internal business logic intact
        
        yield {
            "core": core_container,
            "parsers": parser_container,
            "analyzers": analyzer_container
        }
    
    def test_full_workflow_integration(self, integrated_containers, temp_config_dir):
        """Test full workflow from file parsing to report generation."""
        
        # This test would exercise the entire workflow with real components
        # but controlled inputs and mocked external dependencies
        
        # Arrange
        workflow_service = WorkflowService(
            orchestrator=integrated_containers["core"].workflow_orchestrator(),
            config_parser=integrated_containers["parsers"].configuration_parser(),
            analysis_service=integrated_containers["analyzers"].analysis_service(),
            report_service=integrated_containers["core"].report_service(),
            logger=integrated_containers["core"].logging_service()
        )
        
        # Mock progress interfaces
        progress_tracker = Mock()
        cancellation_token = Mock()
        cancellation_token.is_cancelled.return_value = False
        operation_reporter = Mock()
        
        config_files = list(temp_config_dir.glob("*.cfg"))
        
        # Act
        results = workflow_service.scan_configurations(
            config_paths=config_files,
            analysis_types=["vuln", "compliance"],
            progress_tracker=progress_tracker,
            cancellation_token=cancellation_token,
            operation_reporter=operation_reporter
        )
        
        # Assert
        assert "parsed_configurations" in results
        assert "vulnerability_results" in results
        assert "compliance_results" in results
        assert "formatted_report" in results
        
        # Verify progress was tracked throughout
        assert progress_tracker.update_progress.call_count > 0
        
        # Verify completion was reported
        operation_reporter.report_completion.assert_called_once()
        completion_args = operation_reporter.report_completion.call_args
        assert completion_args[1]["success"] is True
```

## Performance Testing

```python
# tests/performance/test_memory_management.py
import pytest
import gc
import sys
from unittest.mock import Mock

class TestMemoryManagement:
    """Test memory usage and leak prevention."""
    
    def test_event_subscription_memory_cleanup(self):
        """Test that event subscriptions don't leak memory."""
        
        # Arrange
        event_bus = EventBusService()
        initial_objects = len(gc.get_objects())
        
        # Act - Create many subscriptions and let them be cleaned up
        for i in range(1000):
            with event_bus.subscribe(FindingDiscovered, Mock()) as subscription:
                # Publish some events
                event = FindingDiscovered(
                    finding_type="test",
                    severity="low",
                    identifier=f"test-{i}",
                    description="Test event"
                )
                event_bus.publish(event)
        
        # Force garbage collection
        gc.collect()
        
        # Assert
        final_objects = len(gc.get_objects())
        
        # Allow some variance but ensure we're not leaking significantly
        object_growth = final_objects - initial_objects
        assert object_growth < 100, f"Memory leak detected: {object_growth} objects created"
    
    def test_workflow_context_cleanup(self):
        """Test that workflow contexts are properly cleaned up."""
        
        # Arrange
        orchestrator = WorkflowOrchestrator(
            event_publisher=Mock(),
            logger=Mock()
        )
        
        step = Mock()
        step.execute.return_value = {"large_data": "x" * 10000}  # Large string
        step.__class__.__name__ = "TestStep"
        
        orchestrator.register_step("test_step", step)
        orchestrator.register_workflow("test", ["test_step"])
        
        initial_memory = sys.getsizeof(gc.get_objects())
        
        # Act - Run workflow many times
        for i in range(100):
            result = orchestrator.execute_workflow("test", {"iteration": i})
            del result  # Explicitly delete to help with cleanup
        
        gc.collect()
        
        # Assert
        final_memory = sys.getsizeof(gc.get_objects())
        memory_growth = final_memory - initial_memory
        
        # Memory should not grow significantly
        assert memory_growth < 1000000, f"Memory leak in workflow: {memory_growth} bytes"
```

## Testing Best Practices

### 1. Test Isolation
- **Unit tests**: Mock all dependencies to test single components
- **Integration tests**: Use real implementations but control inputs/outputs
- **End-to-end tests**: Exercise full workflows with realistic scenarios

### 2. Progress Interface Testing
- **Mock progress interfaces**: Test business logic independently of UI
- **Verify progress calls**: Ensure progress updates happen at expected points
- **Test cancellation**: Verify operations can be cancelled cleanly

### 3. Memory Management Testing
- **Context managers**: Test automatic resource cleanup
- **Subscription cleanup**: Verify event subscriptions are properly removed
- **Workflow contexts**: Ensure large data structures are cleaned up

### 4. Error Handling Testing
- **Exception propagation**: Test that errors bubble up correctly
- **Error reporting**: Verify errors are reported to appropriate interfaces
- **Recovery scenarios**: Test partial failure and recovery

### 5. Performance Testing
- **Memory usage**: Monitor memory consumption during long-running operations
- **Event overhead**: Ensure event publishing doesn't create performance bottlenecks
- **Progress overhead**: Verify progress tracking doesn't slow down operations

## Benefits

### Comprehensive Coverage
- **Business logic**: Tested independently of UI concerns
- **UI components**: Tested independently of business logic
- **Integration**: Full workflows tested with controlled dependencies

### Maintainable Tests
- **Clear separation**: Tests match architectural boundaries
- **Focused scope**: Each test targets specific functionality
- **Reproducible**: Tests run consistently across environments

### Performance Assurance
- **Memory safety**: Memory leaks caught early in development
- **Performance regression**: Performance changes detected automatically
- **Resource cleanup**: Proper resource management verified

## Next Steps

- [Benefits and Design](benefits-and-design.md) - Understand the overall architectural benefits and design principles
