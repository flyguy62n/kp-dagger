# Workflow Orchestration

The Workflow Orchestration pattern coordinates complex business operations across multiple services while maintaining clean separation between business logic and UI concerns.

## Core Workflow Architecture

```python
# services/core/workflow/interfaces.py
from typing import Protocol
from pathlib import Path
from kp_dagger.models.analysis import AnalysisResult
from kp_dagger.models.configuration import ParsedConfiguration

class IWorkflowStep(Protocol):
    """Interface for individual workflow steps."""
    
    def execute(
        self,
        context: dict,
        progress_tracker: IProgressTracker | None = None,
        cancellation_token: ICancellationToken | None = None
    ) -> dict:
        """Execute the workflow step and return updated context."""
        ...

class IWorkflowOrchestrator(Protocol):
    """Interface for coordinating workflow execution."""
    
    def execute_workflow(
        self,
        workflow_name: str,
        initial_context: dict,
        progress_tracker: IProgressTracker | None = None,
        cancellation_token: ICancellationToken | None = None,
        operation_reporter: IOperationReporter | None = None
    ) -> dict:
        """Execute a named workflow with the given context."""
        ...

# services/core/workflow/orchestrator.py
class WorkflowOrchestrator:
    """Coordinates execution of complex multi-step workflows."""
    
    @inject
    def __init__(
        self,
        event_publisher: SafeEventPublisher = Provide[CoreContainer.safe_event_publisher],
        logger: LoggingService = Provide[CoreContainer.logging_service],
    ):
        self.event_publisher = event_publisher
        self.logger = logger
        self.workflows: dict[str, list[IWorkflowStep]] = {}
        self.step_registry: dict[str, IWorkflowStep] = {}
    
    def register_workflow(self, name: str, steps: list[str]) -> None:
        """Register a workflow with its ordered steps."""
        workflow_steps = []
        for step_name in steps:
            if step_name not in self.step_registry:
                raise ValueError(f"Unknown workflow step: {step_name}")
            workflow_steps.append(self.step_registry[step_name])
        
        self.workflows[name] = workflow_steps
    
    def register_step(self, name: str, step: IWorkflowStep) -> None:
        """Register a workflow step implementation."""
        self.step_registry[name] = step
    
    def execute_workflow(
        self,
        workflow_name: str,
        initial_context: dict,
        progress_tracker: IProgressTracker | None = None,
        cancellation_token: ICancellationToken | None = None,
        operation_reporter: IOperationReporter | None = None
    ) -> dict:
        """Execute a registered workflow."""
        
        # Use null implementations if none provided
        progress_tracker = progress_tracker or NullProgressTracker()
        cancellation_token = cancellation_token or NullCancellationToken()
        operation_reporter = operation_reporter or NullOperationReporter()
        
        if workflow_name not in self.workflows:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        
        workflow_steps = self.workflows[workflow_name]
        context = initial_context.copy()
        total_steps = len(workflow_steps)
        
        self.logger.info(f"Starting workflow '{workflow_name}' with {total_steps} steps")
        
        # Publish workflow start event
        self.event_publisher.publish(WorkflowStarted(
            workflow_name=workflow_name,
            total_steps=total_steps,
            context_keys=list(context.keys())
        ))
        
        start_time = time.time()
        
        try:
            for i, step in enumerate(workflow_steps):
                if cancellation_token.is_cancelled():
                    raise OperationCancelledException(f"Workflow '{workflow_name}' cancelled at step {i+1}")
                
                step_percent = (i / total_steps) * 100
                step_name = step.__class__.__name__
                
                progress_tracker.update_progress(
                    f"workflow_step_{i+1}",
                    step_percent,
                    f"Executing {step_name}..."
                )
                
                self.logger.debug(f"Executing step {i+1}/{total_steps}: {step_name}")
                
                # Publish step start event
                self.event_publisher.publish(WorkflowStepStarted(
                    workflow_name=workflow_name,
                    step_name=step_name,
                    step_number=i+1,
                    total_steps=total_steps
                ))
                
                try:
                    # Execute the step
                    step_context = step.execute(
                        context,
                        progress_tracker,
                        cancellation_token
                    )
                    
                    # Update context with step results
                    context.update(step_context)
                    
                    # Publish step completion event
                    self.event_publisher.publish(WorkflowStepCompleted(
                        workflow_name=workflow_name,
                        step_name=step_name,
                        step_number=i+1,
                        success=True,
                        output_keys=list(step_context.keys())
                    ))
                    
                except Exception as e:
                    # Publish step failure event
                    self.event_publisher.publish(WorkflowStepCompleted(
                        workflow_name=workflow_name,
                        step_name=step_name,
                        step_number=i+1,
                        success=False,
                        error=str(e)
                    ))
                    
                    operation_reporter.report_error(
                        f"Step {step_name} failed: {str(e)}",
                        {"workflow": workflow_name, "step": i+1, "step_name": step_name}
                    )
                    raise
            
            duration = time.time() - start_time
            
            # Final progress update
            progress_tracker.update_progress(
                "workflow_complete",
                100.0,
                f"Workflow '{workflow_name}' completed successfully"
            )
            
            # Publish workflow completion event
            self.event_publisher.publish(WorkflowCompleted(
                workflow_name=workflow_name,
                success=True,
                duration=duration,
                final_context_keys=list(context.keys())
            ))
            
            operation_reporter.report_completion(
                success=True,
                duration=duration,
                summary={
                    "workflow": workflow_name,
                    "steps_completed": total_steps,
                    "output_keys": list(context.keys())
                }
            )
            
            return context
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Publish workflow failure event
            self.event_publisher.publish(WorkflowCompleted(
                workflow_name=workflow_name,
                success=False,
                duration=duration,
                error=str(e)
            ))
            
            operation_reporter.report_completion(
                success=False,
                duration=duration,
                summary={
                    "workflow": workflow_name,
                    "error": str(e),
                    "steps_completed": i if 'i' in locals() else 0
                }
            )
            
            raise
```

## Main Workflow Service

```python
# services/core/workflow/service.py
class WorkflowService:
    """High-level workflow coordination service."""
    
    @inject
    def __init__(
        self,
        orchestrator: WorkflowOrchestrator = Provide[CoreContainer.workflow_orchestrator],
        config_parser: IConfigurationParser = Provide[ParserContainer.configuration_parser],
        analysis_service: AnalysisService = Provide[AnalyzerContainer.analysis_service],
        report_service: ReportService = Provide[ReportContainer.report_service],
        logger: LoggingService = Provide[CoreContainer.logging_service],
    ):
        self.orchestrator = orchestrator
        self.config_parser = config_parser
        self.analysis_service = analysis_service
        self.report_service = report_service
        self.logger = logger
        
        # Register workflow steps
        self._register_workflow_steps()
        
        # Register predefined workflows
        self._register_workflows()
    
    def _register_workflow_steps(self) -> None:
        """Register all available workflow steps."""
        
        # Configuration parsing step
        self.orchestrator.register_step(
            "parse_configurations",
            ParseConfigurationsStep(self.config_parser)
        )
        
        # Analysis steps
        self.orchestrator.register_step(
            "analyze_vulnerabilities",
            AnalyzeVulnerabilitiesStep(self.analysis_service)
        )
        
        self.orchestrator.register_step(
            "analyze_compliance",
            AnalyzeComplianceStep(self.analysis_service)
        )
        
        self.orchestrator.register_step(
            "analyze_firewall_rules", 
            AnalyzeFirewallRulesStep(self.analysis_service)
        )
        
        # Reporting steps
        self.orchestrator.register_step(
            "generate_reports",
            GenerateReportsStep(self.report_service)
        )
        
        self.orchestrator.register_step(
            "export_results",
            ExportResultsStep(self.report_service)
        )
    
    def _register_workflows(self) -> None:
        """Register predefined workflows."""
        
        # Quick scan workflow
        self.orchestrator.register_workflow(
            "quick_scan",
            [
                "parse_configurations",
                "analyze_vulnerabilities",
                "generate_reports"
            ]
        )
        
        # Full analysis workflow
        self.orchestrator.register_workflow(
            "full_analysis",
            [
                "parse_configurations",
                "analyze_vulnerabilities",
                "analyze_compliance",
                "analyze_firewall_rules",
                "generate_reports",
                "export_results"
            ]
        )
        
        # Compliance-only workflow
        self.orchestrator.register_workflow(
            "compliance_only",
            [
                "parse_configurations",
                "analyze_compliance",
                "generate_reports"
            ]
        )
    
    def scan_configurations(
        self,
        config_paths: list[Path],
        analysis_types: list[str] | None = None,
        output_format: str = "json",
        output_path: Path | None = None,
        progress_tracker: IProgressTracker | None = None,
        cancellation_token: ICancellationToken | None = None,
        operation_reporter: IOperationReporter | None = None
    ) -> dict:
        """Execute a configuration scan workflow.
        
        This is the main entry point for CLI and GUI operations.
        """
        
        # Determine workflow based on analysis types
        if analysis_types is None:
            workflow_name = "full_analysis"
        elif len(analysis_types) == 1 and analysis_types[0] == "compliance":
            workflow_name = "compliance_only"
        elif set(analysis_types) == {"vuln"}:
            workflow_name = "quick_scan"
        else:
            workflow_name = "full_analysis"
        
        # Prepare initial context
        initial_context = {
            "config_paths": config_paths,
            "analysis_types": analysis_types or ["vuln", "compliance", "rules"],
            "output_format": output_format,
            "output_path": output_path,
        }
        
        # Execute the workflow
        return self.orchestrator.execute_workflow(
            workflow_name,
            initial_context,
            progress_tracker=progress_tracker,
            cancellation_token=cancellation_token,
            operation_reporter=operation_reporter
        )
    
    def analyze_single_configuration(
        self,
        config_path: Path,
        analysis_types: list[str],
        progress_tracker: IProgressTracker | None = None,
        cancellation_token: ICancellationToken | None = None,
        operation_reporter: IOperationReporter | None = None
    ) -> AnalysisResult:
        """Analyze a single configuration file (simplified workflow)."""
        
        # Simple workflow for single file
        context = self.orchestrator.execute_workflow(
            "quick_scan",
            {
                "config_paths": [config_path],
                "analysis_types": analysis_types
            },
            progress_tracker=progress_tracker,
            cancellation_token=cancellation_token,
            operation_reporter=operation_reporter
        )
        
        return context.get("analysis_results", {})
```

## Workflow Step Implementations

```python
# services/core/workflow/steps.py

class ParseConfigurationsStep:
    """Workflow step for parsing configuration files."""
    
    def __init__(self, config_parser: IConfigurationParser):
        self.config_parser = config_parser
    
    def execute(
        self,
        context: dict,
        progress_tracker: IProgressTracker | None = None,
        cancellation_token: ICancellationToken | None = None
    ) -> dict:
        
        progress_tracker = progress_tracker or NullProgressTracker()
        cancellation_token = cancellation_token or NullCancellationToken()
        
        config_paths = context["config_paths"]
        parsed_configs = []
        
        total_files = len(config_paths)
        
        for i, config_path in enumerate(config_paths):
            if cancellation_token.is_cancelled():
                raise OperationCancelledException("Configuration parsing cancelled")
            
            progress_tracker.update_file_progress(
                i + 1, 
                total_files, 
                config_path.name
            )
            
            progress_tracker.update_substep(
                "parse_configurations",
                f"parsing_{config_path.name}",
                (i / total_files) * 100
            )
            
            parsed_config = self.config_parser.parse_file(config_path)
            parsed_configs.append(parsed_config)
        
        return {
            "parsed_configurations": parsed_configs,
            "total_files_parsed": len(parsed_configs)
        }

class AnalyzeVulnerabilitiesStep:
    """Workflow step for vulnerability analysis."""
    
    def __init__(self, analysis_service: AnalysisService):
        self.analysis_service = analysis_service
    
    def execute(
        self,
        context: dict,
        progress_tracker: IProgressTracker | None = None,
        cancellation_token: ICancellationToken | None = None
    ) -> dict:
        
        parsed_configs = context["parsed_configurations"]
        vulnerability_results = []
        
        total_configs = len(parsed_configs)
        
        for i, config in enumerate(parsed_configs):
            if cancellation_token and cancellation_token.is_cancelled():
                raise OperationCancelledException("Vulnerability analysis cancelled")
            
            if progress_tracker:
                progress_tracker.update_substep(
                    "analyze_vulnerabilities",
                    f"scanning_config_{i+1}",
                    (i / total_configs) * 100
                )
            
            result = self.analysis_service.analyze_configuration(
                config,
                ["vuln"],
                progress_tracker=progress_tracker,
                cancellation_token=cancellation_token
            )
            
            vulnerability_results.append(result)
        
        return {
            "vulnerability_results": vulnerability_results,
            "total_vulnerabilities": sum(
                len(result.vulnerabilities) for result in vulnerability_results
            )
        }

class AnalyzeComplianceStep:
    """Workflow step for compliance analysis."""
    
    def __init__(self, analysis_service: AnalysisService):
        self.analysis_service = analysis_service
    
    def execute(
        self,
        context: dict,
        progress_tracker: IProgressTracker | None = None,
        cancellation_token: ICancellationToken | None = None
    ) -> dict:
        
        parsed_configs = context["parsed_configurations"]
        compliance_results = []
        
        total_configs = len(parsed_configs)
        
        for i, config in enumerate(parsed_configs):
            if cancellation_token and cancellation_token.is_cancelled():
                raise OperationCancelledException("Compliance analysis cancelled")
            
            if progress_tracker:
                progress_tracker.update_substep(
                    "analyze_compliance",
                    f"checking_config_{i+1}",
                    (i / total_configs) * 100
                )
            
            result = self.analysis_service.analyze_configuration(
                config,
                ["compliance"],
                progress_tracker=progress_tracker,
                cancellation_token=cancellation_token
            )
            
            compliance_results.append(result)
        
        return {
            "compliance_results": compliance_results,
            "total_violations": sum(
                len(result.violations) for result in compliance_results
            )
        }

class GenerateReportsStep:
    """Workflow step for report generation."""
    
    def __init__(self, report_service: ReportService):
        self.report_service = report_service
    
    def execute(
        self,
        context: dict,
        progress_tracker: IProgressTracker | None = None,
        cancellation_token: ICancellationToken | None = None
    ) -> dict:
        
        # Gather all analysis results
        vulnerability_results = context.get("vulnerability_results", [])
        compliance_results = context.get("compliance_results", [])
        firewall_results = context.get("firewall_results", [])
        
        # Generate consolidated report
        if progress_tracker:
            progress_tracker.update_substep(
                "generate_reports",
                "consolidating_results",
                25.0
            )
        
        consolidated_results = self.report_service.consolidate_results(
            vulnerability_results,
            compliance_results,
            firewall_results
        )
        
        if progress_tracker:
            progress_tracker.update_substep(
                "generate_reports",
                "formatting_report",
                75.0
            )
        
        output_format = context.get("output_format", "json")
        formatted_report = self.report_service.format_report(
            consolidated_results,
            output_format
        )
        
        return {
            "consolidated_results": consolidated_results,
            "formatted_report": formatted_report,
            "report_format": output_format
        }
```

## CLI Integration

```python
# cli/commands/scan.py
@click.command()
@click.argument("config_paths", nargs=-1, required=True)
@click.option("--analysis-types", "-a", multiple=True, 
              type=click.Choice(["vuln", "compliance", "rules"]),
              help="Types of analysis to perform")
@click.option("--output-format", "-f", default="json",
              type=click.Choice(["json", "yaml", "html"]),
              help="Output format for results")
@click.option("--output-path", "-o", type=click.Path(),
              help="Path to save results")
@inject
def scan(
    config_paths: tuple[str, ...],
    analysis_types: tuple[str, ...],
    output_format: str,
    output_path: str | None,
    workflow: WorkflowService = Provide[CoreContainer.workflow_service],
    rich_output: RichOutputService = Provide[CoreContainer.rich_output_service],
):
    """Scan network device configurations for security issues."""
    
    try:
        # Create progress components
        progress_tracker = CliProgressTracker(rich_output)
        cancellation_token = CliCancellationToken()
        operation_reporter = CliOperationReporter(rich_output)
        
        # Convert paths
        config_path_objects = [Path(p) for p in config_paths]
        output_path_object = Path(output_path) if output_path else None
        
        # Execute workflow
        results = workflow.scan_configurations(
            config_paths=config_path_objects,
            analysis_types=list(analysis_types) if analysis_types else None,
            output_format=output_format,
            output_path=output_path_object,
            progress_tracker=progress_tracker,
            cancellation_token=cancellation_token,
            operation_reporter=operation_reporter
        )
        
        # Display results summary
        rich_output.success("Scan completed successfully!")
        _display_results_summary(results, rich_output)
        
    except OperationCancelledException:
        rich_output.info("Scan cancelled by user")
        raise click.Abort()
    except Exception as e:
        rich_output.error(f"Scan failed: {str(e)}")
        raise

def _display_results_summary(results: dict, rich_output: RichOutputService) -> None:
    """Display a summary of scan results."""
    
    total_vulns = results.get("total_vulnerabilities", 0)
    total_violations = results.get("total_violations", 0)
    total_files = results.get("total_files_parsed", 0)
    
    summary_table = Table(title="Scan Results Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Count", style="magenta")
    
    summary_table.add_row("Files Processed", str(total_files))
    summary_table.add_row("Vulnerabilities Found", str(total_vulns))
    summary_table.add_row("Compliance Violations", str(total_violations))
    
    rich_output.console.print(summary_table)
```

## Testing Workflow Orchestration

```python
# tests/test_workflow_orchestration.py

def test_workflow_orchestrator_execution():
    """Test basic workflow orchestration."""
    
    # Create mock steps
    step1 = Mock(spec=IWorkflowStep)
    step1.execute.return_value = {"step1_result": "value1"}
    
    step2 = Mock(spec=IWorkflowStep)
    step2.execute.return_value = {"step2_result": "value2"}
    
    # Create orchestrator
    orchestrator = WorkflowOrchestrator(
        event_publisher=Mock(),
        logger=Mock()
    )
    
    # Register steps and workflow
    orchestrator.register_step("step1", step1)
    orchestrator.register_step("step2", step2)
    orchestrator.register_workflow("test_workflow", ["step1", "step2"])
    
    # Execute workflow
    result = orchestrator.execute_workflow(
        "test_workflow",
        {"initial": "context"}
    )
    
    # Verify execution
    assert result["initial"] == "context"
    assert result["step1_result"] == "value1"
    assert result["step2_result"] == "value2"
    
    # Verify steps were called with updated context
    step1.execute.assert_called_once()
    step2.execute.assert_called_once()
    
    # Check that step2 received step1's output
    step2_call_args = step2.execute.call_args[0]
    step2_context = step2_call_args[0]
    assert step2_context["step1_result"] == "value1"

def test_workflow_cancellation():
    """Test workflow cancellation."""
    
    # Create orchestrator
    orchestrator = WorkflowOrchestrator(
        event_publisher=Mock(),
        logger=Mock()
    )
    
    # Create mock step that won't be reached
    step = Mock(spec=IWorkflowStep)
    orchestrator.register_step("step", step)
    orchestrator.register_workflow("test", ["step"])
    
    # Create cancellation token that's already cancelled
    cancellation_token = Mock()
    cancellation_token.is_cancelled.return_value = True
    
    # Execute and expect cancellation
    with pytest.raises(OperationCancelledException):
        orchestrator.execute_workflow(
            "test",
            {},
            cancellation_token=cancellation_token
        )
    
    # Verify step was not executed
    step.execute.assert_not_called()

def test_workflow_service_integration():
    """Test WorkflowService integration with orchestrator."""
    
    # Create mocks
    orchestrator = Mock()
    config_parser = Mock()
    analysis_service = Mock()
    report_service = Mock()
    
    # Create service
    service = WorkflowService(
        orchestrator=orchestrator,
        config_parser=config_parser,
        analysis_service=analysis_service,
        report_service=report_service,
        logger=Mock()
    )
    
    # Mock orchestrator return
    orchestrator.execute_workflow.return_value = {
        "analysis_results": {"test": "results"}
    }
    
    # Execute scan
    results = service.scan_configurations(
        config_paths=[Path("test.cfg")],
        analysis_types=["vuln"]
    )
    
    # Verify orchestrator was called
    orchestrator.execute_workflow.assert_called_once()
    
    # Verify workflow was configured correctly
    call_args = orchestrator.execute_workflow.call_args
    workflow_name = call_args[0][0]
    initial_context = call_args[0][1]
    
    assert workflow_name == "quick_scan"
    assert initial_context["config_paths"] == [Path("test.cfg")]
    assert initial_context["analysis_types"] == ["vuln"]
```

## Benefits

### Coordinated Business Logic
- **Step orchestration**: Complex operations broken into manageable steps
- **Context flow**: Data flows cleanly between workflow steps
- **Error handling**: Centralized error handling with step-level granularity

### UI Integration
- **Progress tracking**: Fine-grained progress updates across workflow steps
- **Cancellation support**: User can cancel at any workflow step
- **Event publishing**: Real-time workflow status updates

### Flexibility and Reusability
- **Composable workflows**: Mix and match steps for different use cases
- **Step reusability**: Individual steps can be used in multiple workflows
- **Dynamic workflows**: Register new workflows and steps at runtime

### Testing and Maintenance
- **Isolated testing**: Test individual steps and orchestration separately
- **Mock-friendly**: Easy to mock workflow components for testing
- **Clear responsibilities**: Each step has a single, well-defined responsibility

## Next Steps

- [Testing Patterns](testing-patterns.md) - Learn comprehensive testing strategies for UI-service separation
- [Benefits and Design](benefits-and-design.md) - Understand the overall architectural benefits
