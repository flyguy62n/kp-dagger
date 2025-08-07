# Database Design and Performance Considerations

This document outlines the database architecture design choices for KP-Dagger, focusing on performance optimization and process safety in a SQLite-based, potentially parallel processing environment.

## Overview

KP-Dagger is fundamentally database-centric, with three core data flows:

1. **Configuration Parsing** → Normalized configuration parameters stored in database
2. **Analysis Engine** → Reads normalized data, writes findings back to database  
3. **Reporting System** → Reads findings from database to generate outputs

With SQLite as the storage engine and potential parallel processing requirements, careful design is essential to avoid performance bottlenecks and ensure process safety.

## Database Architecture

### Storage Engine: SQLite

**Benefits for KP-Dagger:**
- Single-file database (easy deployment/backup)
- No separate server process required
- ACID compliance with transaction safety
- Excellent read performance for analytical workloads
- Built-in full-text search capabilities
- Cross-platform compatibility

**Limitations to Address:**
- Single writer limitation (concurrent writes block in both rollback and WAL modes)
- WAL mode requires shared memory (all processes must be on same host)
- WAL mode has additional -wal and -shm files to manage
- Memory usage with large datasets
- Lock contention possible during checkpointing in WAL mode

### Connection Management Strategy

```python
# core/database/connection_manager.py
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import sqlite3
import threading
import time

class DatabaseConnectionManager:
    """Manages SQLite connections with performance optimizations."""
    
    def __init__(self, database_url: str, enable_wal: bool = True):
        self.database_url = database_url
        self.enable_wal = enable_wal
        self._engine = None
        self._lock = threading.Lock()
        
    def get_engine(self) -> Engine:
        """Get configured SQLAlchemy engine with SQLite optimizations."""
        if self._engine is None:
            with self._lock:
                if self._engine is None:
                    self._engine = self._create_engine()
        return self._engine
    
    def _create_engine(self) -> Engine:
        """Create optimized SQLite engine."""
        # Connection arguments for performance
        connect_args = {
            "check_same_thread": False,  # Allow multi-threading
            "timeout": 30.0,  # 30 second timeout for lock waits
        }
        
        # Engine configuration
        engine = create_engine(
            self.database_url,
            connect_args=connect_args,
            poolclass=StaticPool,  # Keep connections alive
            pool_pre_ping=True,    # Validate connections
            echo=False,            # Set to True for debugging
        )
        
        # Register SQLite optimization events
        self._register_sqlite_events(engine)
        
        return engine
    
    def _register_sqlite_events(self, engine: Engine) -> None:
        """Register SQLite-specific optimization events."""
        
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set SQLite pragmas for performance."""
            cursor = dbapi_connection.cursor()
            
            # Enable WAL mode for better concurrency
            if self.enable_wal:
                cursor.execute("PRAGMA journal_mode=WAL")
                # WAL mode benefits:
                # - Readers don't block writers, writers don't block readers
                # - Only one writer at a time (same as rollback mode)
                # - Faster writes (sequential, no double-write)
                # - BUT: requires shared memory, all processes on same host
            
            # Performance optimizations
            cursor.execute("PRAGMA synchronous=NORMAL")  # Balance safety/speed
            cursor.execute("PRAGMA cache_size=10000")    # 10MB cache
            cursor.execute("PRAGMA temp_store=MEMORY")   # Temp tables in memory
            cursor.execute("PRAGMA mmap_size=268435456") # 256MB memory map
            
            # WAL-specific optimizations
            if self.enable_wal:
                cursor.execute("PRAGMA wal_autocheckpoint=1000")  # Default checkpoint threshold
                cursor.execute("PRAGMA wal_checkpoint(PASSIVE)")  # Gentle checkpoint
            
            # Foreign key enforcement
            cursor.execute("PRAGMA foreign_keys=ON")
            
            cursor.close()

    @contextmanager
    def get_session(self):
        """Context manager for database sessions."""
        from sqlalchemy.orm import sessionmaker
        
        Session = sessionmaker(bind=self.get_engine())
        session = Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
```

## Process Safety Design

### Read-Heavy Workload Optimization

Most operations in KP-Dagger are read-heavy (analysis reading configurations, reporting reading findings). SQLite handles concurrent reads efficiently.

```python
# services/core/database/read_service.py
class DatabaseReadService:
    """Optimized read operations for analytical workloads."""
    
    def __init__(self, connection_manager: DatabaseConnectionManager):
        self.connection_manager = connection_manager
    
    def get_normalized_configs_batch(
        self, 
        device_ids: list[str], 
        batch_size: int = 1000
    ) -> Iterator[list[NormalizedConfig]]:
        """Stream configurations in batches for memory efficiency."""
        
        with self.connection_manager.get_session() as session:
            # Use server-side cursor for large datasets
            query = session.query(NormalizedConfig).filter(
                NormalizedConfig.device_id.in_(device_ids)
            ).order_by(NormalizedConfig.id)
            
            # Process in batches to avoid memory issues
            offset = 0
            while True:
                batch = query.offset(offset).limit(batch_size).all()
                if not batch:
                    break
                yield batch
                offset += batch_size
    
    def get_analysis_context(self, device_id: str) -> AnalysisContext:
        """Get all data needed for device analysis in single query."""
        
        with self.connection_manager.get_session() as session:
            # Single query with joins to minimize database round trips
            result = session.query(
                NormalizedConfig,
                DeviceInfo,
                PreviousFindings
            ).join(
                DeviceInfo, NormalizedConfig.device_id == DeviceInfo.id
            ).outerjoin(
                PreviousFindings, DeviceInfo.id == PreviousFindings.device_id
            ).filter(
                NormalizedConfig.device_id == device_id
            ).first()
            
            return AnalysisContext(
                config=result.NormalizedConfig,
                device_info=result.DeviceInfo,
                previous_findings=result.PreviousFindings
            )
```

### Write Coordination Strategy

SQLite's concurrency characteristics depend on the journal mode:

**WAL Mode (Recommended):**
- Multiple concurrent readers (unlimited)
- Single writer at a time (same as rollback mode)
- Readers don't block writers, writers don't block readers
- Checkpointing can be blocked by long-running readers
- All processes must be on same host (shared memory requirement)

**Rollback Mode (Default):**
- Multiple concurrent readers with SHARED locks
- Single writer requires EXCLUSIVE lock (blocks all readers)
- Writers can be starved by continuous readers (PENDING lock helps)

Our design uses a background writer thread to serialize writes in either mode:

```python
# services/core/database/write_service.py
import queue
import threading
from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class WriteOperation:
    """Represents a pending database write operation."""
    operation: Callable
    args: tuple
    kwargs: dict
    result_queue: queue.Queue
    correlation_id: str

class DatabaseWriteService:
    """Coordinates database writes to avoid lock contention."""
    
    def __init__(self, connection_manager: DatabaseConnectionManager):
        self.connection_manager = connection_manager
        self.write_queue = queue.Queue()
        self.writer_thread = None
        self.shutdown_event = threading.Event()
        
    def start_writer(self) -> None:
        """Start the background writer thread."""
        if self.writer_thread is None or not self.writer_thread.is_alive():
            self.writer_thread = threading.Thread(
                target=self._writer_loop,
                daemon=True
            )
            self.writer_thread.start()
    
    def stop_writer(self) -> None:
        """Stop the background writer thread."""
        self.shutdown_event.set()
        if self.writer_thread and self.writer_thread.is_alive():
            self.writer_thread.join(timeout=30)
    
    def _writer_loop(self) -> None:
        """Main loop for processing write operations."""
        with self.connection_manager.get_session() as session:
            while not self.shutdown_event.is_set():
                try:
                    # Get next write operation (with timeout)
                    operation = self.write_queue.get(timeout=1.0)
                    
                    try:
                        # Execute the write operation
                        result = operation.operation(session, *operation.args, **operation.kwargs)
                        session.commit()
                        
                        # Return result to caller
                        operation.result_queue.put(("success", result))
                        
                    except Exception as e:
                        session.rollback()
                        operation.result_queue.put(("error", e))
                    
                    finally:
                        self.write_queue.task_done()
                        
                except queue.Empty:
                    continue  # Timeout, check shutdown event
    
    def execute_write(
        self, 
        operation: Callable, 
        *args, 
        timeout: float = 30.0,
        **kwargs
    ) -> Any:
        """Execute a write operation through the writer thread."""
        result_queue = queue.Queue()
        correlation_id = str(uuid.uuid4())
        
        write_op = WriteOperation(
            operation=operation,
            args=args,
            kwargs=kwargs,
            result_queue=result_queue,
            correlation_id=correlation_id
        )
        
        # Queue the operation
        self.write_queue.put(write_op)
        
        # Wait for result
        try:
            status, result = result_queue.get(timeout=timeout)
            if status == "error":
                raise result
            return result
        except queue.Empty:
            raise TimeoutError(f"Write operation timed out after {timeout}s")

    def save_parsed_config(self, config_data: dict) -> str:
        """Save parsed configuration data."""
        def _save_operation(session, data):
            normalized_config = NormalizedConfig(**data)
            session.add(normalized_config)
            session.flush()  # Get ID without committing
            return normalized_config.id
        
        return self.execute_write(_save_operation, config_data)
    
    def save_analysis_findings(self, findings: list[dict]) -> list[str]:
        """Save analysis findings in batch."""
        def _save_batch_operation(session, findings_data):
            finding_objects = [AnalysisFinding(**data) for data in findings_data]
            session.add_all(finding_objects)
            session.flush()
            return [f.id for f in finding_objects]
        
        return self.execute_write(_save_batch_operation, findings)
```

## WAL Mode Specific Considerations

### Checkpoint Management

WAL mode requires periodic checkpointing to prevent unlimited WAL file growth:

```python
# services/core/database/wal_manager.py
class WALCheckpointManager:
    """Manages WAL checkpointing for optimal performance."""
    
    def __init__(self, connection_manager: DatabaseConnectionManager):
        self.connection_manager = connection_manager
        self.checkpoint_threshold = 1000  # pages
        
    def run_checkpoint(self, mode: str = "PASSIVE") -> dict:
        """Run WAL checkpoint with specified mode.
        
        Modes:
        - PASSIVE: Non-blocking, may not complete if readers active
        - FULL: Blocks until completion or timeout
        - RESTART: Forces completion, may block readers
        - TRUNCATE: Like RESTART but also truncates WAL file
        """
        with self.connection_manager.get_session() as session:
            if mode == "PASSIVE":
                result = session.execute(text("PRAGMA wal_checkpoint(PASSIVE)")).first()
            elif mode == "FULL":
                result = session.execute(text("PRAGMA wal_checkpoint(FULL)")).first()
            elif mode == "RESTART":
                result = session.execute(text("PRAGMA wal_checkpoint(RESTART)")).first()
            elif mode == "TRUNCATE":
                result = session.execute(text("PRAGMA wal_checkpoint(TRUNCATE)")).first()
            else:
                raise ValueError(f"Invalid checkpoint mode: {mode}")
                
            return {
                "busy": bool(result[0]),      # 0 if checkpoint completed
                "log_pages": result[1],       # Pages in WAL file
                "checkpointed": result[2]     # Pages checkpointed
            }
    
    def get_wal_info(self) -> dict:
        """Get WAL file status information."""
        with self.connection_manager.get_session() as session:
            # Check if in WAL mode
            mode_result = session.execute(text("PRAGMA journal_mode")).first()
            journal_mode = mode_result[0].lower()
            
            if journal_mode != "wal":
                return {"journal_mode": journal_mode, "wal_active": False}
            
            # Get WAL size
            wal_result = session.execute(text("PRAGMA wal_checkpoint")).first()
            
            return {
                "journal_mode": journal_mode,
                "wal_active": True,
                "wal_pages": wal_result[1],
                "checkpointed_pages": wal_result[2],
                "needs_checkpoint": wal_result[1] > self.checkpoint_threshold
            }
    
    def optimize_for_workload(self, workload_type: str) -> None:
        """Optimize WAL settings for specific workload patterns."""
        with self.connection_manager.get_session() as session:
            if workload_type == "read_heavy":
                # Aggressive checkpointing for read performance
                session.execute(text("PRAGMA wal_autocheckpoint=100"))
            elif workload_type == "write_heavy":
                # Less frequent checkpointing for write performance
                session.execute(text("PRAGMA wal_autocheckpoint=5000"))
            elif workload_type == "batch_processing":
                # Disable auto-checkpoint, manual control
                session.execute(text("PRAGMA wal_autocheckpoint=0"))
            else:
                # Default balanced approach
                session.execute(text("PRAGMA wal_autocheckpoint=1000"))
                
            session.commit()
```

### Reader/Writer Coordination in WAL Mode

```python
# services/core/database/wal_coordinator.py
class WALCoordinator:
    """Coordinates WAL operations across multiple processes."""
    
    def __init__(self, connection_manager: DatabaseConnectionManager):
        self.connection_manager = connection_manager
        self.checkpoint_manager = WALCheckpointManager(connection_manager)
        
    def begin_read_transaction(self) -> None:
        """Begin read transaction with WAL considerations."""
        # In WAL mode, readers get snapshot at transaction start
        # Long-running readers can prevent checkpoints
        pass
        
    def begin_write_transaction(self) -> None:
        """Begin write transaction with checkpoint consideration."""
        # Check if checkpoint needed before starting large write
        wal_info = self.checkpoint_manager.get_wal_info()
        
        if wal_info.get("needs_checkpoint", False):
            # Try passive checkpoint before write
            self.checkpoint_manager.run_checkpoint("PASSIVE")
    
    def end_write_transaction(self, success: bool) -> None:
        """End write transaction with post-write cleanup."""
        if success:
            # Check if WAL is getting large
            wal_info = self.checkpoint_manager.get_wal_info()
            
            if wal_info.get("wal_pages", 0) > 2000:  # 2x normal threshold
                # Force checkpoint to prevent excessive growth
                self.checkpoint_manager.run_checkpoint("FULL")
    
    def handle_long_running_read(self, max_duration: float = 300.0) -> None:
        """Handle long-running read transactions that block checkpoints."""
        # In practice, this would involve monitoring and potentially
        # breaking up long operations or using separate read-only connections
        pass
```

### WAL File Monitoring

```python
# services/core/database/wal_monitor.py
class WALFileMonitor:
    """Monitors WAL file health and performance."""
    
    def __init__(self, database_path: str):
        self.database_path = Path(database_path)
        self.wal_path = self.database_path.with_suffix(self.database_path.suffix + "-wal")
        self.shm_path = self.database_path.with_suffix(self.database_path.suffix + "-shm")
    
    def get_file_sizes(self) -> dict:
        """Get sizes of database, WAL, and shared memory files."""
        sizes = {
            "database": self.database_path.stat().st_size if self.database_path.exists() else 0,
            "wal": self.wal_path.stat().st_size if self.wal_path.exists() else 0,
            "shm": self.shm_path.stat().st_size if self.shm_path.exists() else 0
        }
        
        # Calculate ratios for health assessment
        if sizes["database"] > 0:
            sizes["wal_ratio"] = sizes["wal"] / sizes["database"]
        else:
            sizes["wal_ratio"] = 0
            
        return sizes
    
    def assess_health(self) -> dict:
        """Assess WAL file health and recommend actions."""
        sizes = self.get_file_sizes()
        health = {"status": "healthy", "recommendations": []}
        
        # WAL file too large relative to database
        if sizes["wal_ratio"] > 0.5:  # WAL > 50% of database size
            health["status"] = "warning"
            health["recommendations"].append("Run checkpoint to reduce WAL size")
        
        # WAL file extremely large
        if sizes["wal"] > 100 * 1024 * 1024:  # > 100MB
            health["status"] = "critical"
            health["recommendations"].append("Investigate checkpoint starvation")
            
        # No WAL file when expected
        if not self.wal_path.exists():
            health["recommendations"].append("Database may not be in WAL mode")
            
        return health
```

### Process-Safe Architecture

**Key Considerations from SQLite Documentation:**

1. **WAL Mode Constraints:**
   - Requires all processes on same host (shared memory)
   - Cannot work over network filesystems
   - Still single writer limitation (one write transaction at a time)
   - Long-running readers can prevent checkpoint completion

2. **ProcessPoolExecutor Implications:**
   - Each worker process needs separate database connection
   - WAL mode shared memory works across process boundaries on same host
   - **CRITICAL**: Only ONE writer at a time across ALL processes (SQLite limitation)
   - Worker processes must coordinate writes or use serialized write patterns
   - Checkpoint coordination needed to prevent WAL file growth

3. **Lock Types in SQLite:**
   - UNLOCKED: No access
   - SHARED: Read access (multiple allowed)
   - RESERVED: Intent to write (one allowed, coexists with SHARED)
   - PENDING: Waiting for EXCLUSIVE (prevents new SHARED locks)
   - EXCLUSIVE: Write access (one allowed, blocks all others)

### Multi-Process Write Coordination

**SQLite Write Limitations Across Processes:**

Even in WAL mode, SQLite enforces a single writer limitation across ALL processes accessing the database:

- **One Writer Rule**: Only one process can have an active write transaction at any given time
- **Cross-Process Locking**: SQLite uses file system locks that work across process boundaries
- **Write Serialization**: Multiple processes attempting writes will be serialized by SQLite's locking mechanism

**Recommended Patterns for ProcessPoolExecutor:**

1. **Read-Only Workers**: Most efficient - workers only read from database
2. **Return-Based Pattern**: Workers return data to main process for writing
3. **Single Writer Process**: Designate one process for all writes
4. **Batch Collection**: Workers collect results, main process writes in batches

```python
# services/core/workflow/parallel_workflow.py
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

class ParallelWorkflowService:
    """Workflow service optimized for parallel processing."""
    
    def __init__(
        self,
        database_path: str,
        max_workers: int = None
    ):
        self.database_path = database_path
        self.max_workers = max_workers or mp.cpu_count()
        
    def parse_configs_parallel(self, config_paths: list[Path]) -> list[str]:
        """Parse configurations in parallel processes using return-based pattern."""
        
        # Worker processes will parse and return data (no direct database writes)
        parse_tasks = [
            (config_path, self.database_path) 
            for config_path in config_paths
        ]
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parsing tasks
            future_to_path = {
                executor.submit(_parse_config_worker, task): task[0]
                for task in parse_tasks
            }
            
            # Collect results from workers
            parsed_configs = []
            for future in as_completed(future_to_path):
                config_path = future_to_path[future]
                try:
                    # Worker returns parsed data, not database ID
                    parsed_data = future.result()
                    parsed_configs.append(parsed_data)
                except Exception as e:
                    logger.error(f"Failed to parse {config_path}: {e}")
                    # Continue with other files
            
            # MAIN PROCESS writes all results to database (serialized)
            config_ids = []
            connection_manager = DatabaseConnectionManager(f"sqlite:///{self.database_path}")
            write_service = DatabaseWriteService(connection_manager)
            write_service.start_writer()
            
            try:
                for parsed_data in parsed_configs:
                    config_id = write_service.save_parsed_config(parsed_data)
                    config_ids.append(config_id)
            finally:
                write_service.stop_writer()
            
            return config_ids

def _parse_config_worker(task: tuple[Path, str]) -> dict:
    """Worker function - parses config and RETURNS data (no database writes)."""
    config_path, database_path = task
    
    # NO database connection in worker for writes
    # Workers only parse and return data
    
    try:
        # Parse configuration
        parser = ConfigParserFactory.get_parser(config_path)
        parsed_data = parser.parse(config_path)
        
        # Normalize data
        normalizer = ConfigNormalizer()
        normalized_data = normalizer.normalize(parsed_data)
        
        # RETURN data instead of writing to database
        return normalized_data
        
    except Exception as e:
        logger.error(f"Worker failed to parse {config_path}: {e}")
        raise
```

### Batch Processing Strategy

For large datasets, process in batches to manage memory and reduce lock contention:

```python
# services/core/database/batch_service.py
class BatchProcessingService:
    """Handles batch operations for large datasets."""
    
    def __init__(
        self, 
        connection_manager: DatabaseConnectionManager,
        batch_size: int = 1000
    ):
        self.connection_manager = connection_manager
        self.batch_size = batch_size
    
    def batch_insert_findings(self, findings: list[dict]) -> None:
        """Insert findings in batches to avoid memory issues."""
        
        for i in range(0, len(findings), self.batch_size):
            batch = findings[i:i + self.batch_size]
            
            with self.connection_manager.get_session() as session:
                # Use bulk insert for performance
                session.bulk_insert_mappings(AnalysisFinding, batch)
                session.commit()
    
    def batch_update_device_status(self, device_updates: list[dict]) -> None:
        """Update device statuses in batches."""
        
        for i in range(0, len(device_updates), self.batch_size):
            batch = device_updates[i:i + self.batch_size]
            
            with self.connection_manager.get_session() as session:
                session.bulk_update_mappings(DeviceInfo, batch)
                session.commit()
```

## Performance Optimization Strategies

### Indexing Strategy

```sql
-- Database indexes for query performance
-- devices table
CREATE INDEX idx_devices_vendor_model ON devices(vendor, model);
CREATE INDEX idx_devices_last_scan ON devices(last_scan_date);

-- normalized_configs table  
CREATE INDEX idx_configs_device_id ON normalized_configs(device_id);
CREATE INDEX idx_configs_config_type ON normalized_configs(config_type);
CREATE INDEX idx_configs_created ON normalized_configs(created_at);

-- analysis_findings table
CREATE INDEX idx_findings_device_id ON analysis_findings(device_id);
CREATE INDEX idx_findings_severity ON analysis_findings(severity);
CREATE INDEX idx_findings_rule_id ON analysis_findings(rule_id);
CREATE INDEX idx_findings_created ON analysis_findings(created_at);
CREATE INDEX idx_findings_status ON analysis_findings(status);

-- Composite indexes for common queries
CREATE INDEX idx_findings_device_severity ON analysis_findings(device_id, severity);
CREATE INDEX idx_configs_device_type ON normalized_configs(device_id, config_type);

-- Full-text search indexes
CREATE VIRTUAL TABLE findings_fts USING fts5(
    rule_id, 
    description, 
    recommendation,
    content='analysis_findings'
);
```

### Query Optimization

```python
# services/core/database/query_optimizer.py
class QueryOptimizer:
    """Provides optimized queries for common operations."""
    
    @staticmethod
    def get_device_analysis_summary(device_id: str) -> dict:
        """Get device analysis summary with single query."""
        query = """
        SELECT 
            d.vendor,
            d.model,
            d.firmware_version,
            COUNT(CASE WHEN af.severity = 'critical' THEN 1 END) as critical_count,
            COUNT(CASE WHEN af.severity = 'high' THEN 1 END) as high_count,
            COUNT(CASE WHEN af.severity = 'medium' THEN 1 END) as medium_count,
            COUNT(CASE WHEN af.severity = 'low' THEN 1 END) as low_count,
            MAX(af.created_at) as last_analysis_date
        FROM devices d
        LEFT JOIN analysis_findings af ON d.id = af.device_id
        WHERE d.id = :device_id
        GROUP BY d.id, d.vendor, d.model, d.firmware_version
        """
        
        # Execute with SQLAlchemy
        with connection_manager.get_session() as session:
            result = session.execute(text(query), {"device_id": device_id}).first()
            return dict(result) if result else {}
    
    @staticmethod
    def get_trending_findings(days: int = 30) -> list[dict]:
        """Get trending findings over time period."""
        query = """
        SELECT 
            af.rule_id,
            ar.description,
            COUNT(*) as occurrence_count,
            COUNT(DISTINCT af.device_id) as affected_devices,
            AVG(CASE 
                WHEN af.severity = 'critical' THEN 4
                WHEN af.severity = 'high' THEN 3
                WHEN af.severity = 'medium' THEN 2
                WHEN af.severity = 'low' THEN 1
                ELSE 0
            END) as avg_severity_score
        FROM analysis_findings af
        JOIN analysis_rules ar ON af.rule_id = ar.id
        WHERE af.created_at >= datetime('now', '-{} days')
        GROUP BY af.rule_id, ar.description
        HAVING occurrence_count > 1
        ORDER BY occurrence_count DESC, avg_severity_score DESC
        LIMIT 20
        """.format(days)
        
        with connection_manager.get_session() as session:
            results = session.execute(text(query)).fetchall()
            return [dict(row) for row in results]
```

## Database Schema Design

### Normalized Configuration Storage

```python
# models/normalized/config.py
class NormalizedConfig(SQLModel, table=True):
    """Normalized device configuration parameters."""
    __tablename__ = "normalized_configs"
    
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    device_id: str = Field(foreign_key="devices.id", index=True)
    config_type: str = Field(index=True)  # "interface", "acl", "auth", etc.
    config_subtype: str = Field(index=True)  # "ssh", "telnet", "rule", etc.
    
    # Normalized parameters as JSON
    parameters: dict = Field(sa_column=Column(JSON))
    
    # Metadata
    source_file: str
    source_lines: list[int] = Field(sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.now, index=True)
    
    # Relationships
    device: "DeviceInfo" = Relationship(back_populates="configs")
    findings: list["AnalysisFinding"] = Relationship(back_populates="config")

class DeviceInfo(SQLModel, table=True):
    """Device information and metadata."""
    __tablename__ = "devices"
    
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    hostname: str
    vendor: str = Field(index=True)
    model: str = Field(index=True)
    firmware_version: str
    last_scan_date: datetime = Field(index=True)
    
    # Relationships
    configs: list[NormalizedConfig] = Relationship(back_populates="device")
    findings: list["AnalysisFinding"] = Relationship(back_populates="device")

class AnalysisFinding(SQLModel, table=True):
    """Analysis findings and recommendations."""
    __tablename__ = "analysis_findings"
    
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    device_id: str = Field(foreign_key="devices.id", index=True)
    config_id: str = Field(foreign_key="normalized_configs.id", index=True)
    rule_id: str = Field(index=True)
    
    severity: str = Field(index=True)  # critical, high, medium, low
    status: str = Field(index=True, default="open")  # open, acknowledged, fixed
    
    description: str
    recommendation: str
    
    # Finding details
    evidence: dict = Field(sa_column=Column(JSON))
    references: list[str] = Field(sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.now, index=True)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    device: DeviceInfo = Relationship(back_populates="findings")
    config: NormalizedConfig = Relationship(back_populates="findings")
```

## Monitoring and Maintenance

### Database Health Monitoring

```python
# services/core/database/monitor.py
class DatabaseMonitor:
    """Monitors database performance and health."""
    
    def __init__(self, connection_manager: DatabaseConnectionManager):
        self.connection_manager = connection_manager
    
    def get_database_stats(self) -> dict:
        """Get database size and performance statistics."""
        with self.connection_manager.get_session() as session:
            stats = {}
            
            # Database size
            result = session.execute(text("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")).first()
            stats["database_size_bytes"] = result[0]
            
            # Table sizes
            tables = ["devices", "normalized_configs", "analysis_findings"]
            for table in tables:
                result = session.execute(text(f"SELECT COUNT(*) FROM {table}")).first()
                stats[f"{table}_count"] = result[0]
            
            # Index usage
            result = session.execute(text("PRAGMA index_list('analysis_findings')")).fetchall()
            stats["index_count"] = len(result)
            
            return stats
    
    def optimize_database(self) -> None:
        """Run database optimization tasks."""
        with self.connection_manager.get_session() as session:
            # Analyze for query optimizer
            session.execute(text("ANALYZE"))
            
            # Vacuum to reclaim space (if needed)
            # Note: VACUUM requires exclusive lock
            session.execute(text("PRAGMA optimize"))
            
            session.commit()
```

## Critical Understanding: SQLite Write Limitations

### The Single Writer Reality

**Important**: Despite having separate database connections in each worker process, SQLite enforces a **single writer limitation across ALL processes**. This means:

```python
# ❌ THIS WILL NOT WORK - Multiple processes trying to write simultaneously
def broken_parallel_writes():
    """This pattern will cause write serialization and potential blocking."""
    
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = []
        for i in range(10):
            # Each worker tries to write - they will be SERIALIZED by SQLite
            future = executor.submit(worker_with_database_write, i)
            futures.append(future)
        
        # Workers will block each other, defeating parallelism purpose
        results = [f.result() for f in futures]

# ✅ THIS WORKS - Return-based pattern with main process writes
def correct_parallel_pattern():
    """This pattern maximizes parallelism while respecting SQLite limitations."""
    
    with ProcessPoolExecutor(max_workers=4) as executor:
        # Workers do CPU-bound work and return data
        futures = [
            executor.submit(worker_parse_only, config_path)
            for config_path in config_paths
        ]
        
        # Collect all parsed data
        parsed_data = [f.result() for f in futures]
        
        # Main process writes all data (fast, no contention)
        write_service.batch_save_configs(parsed_data)
```

### Why WAL Mode Doesn't Change This

Even though WAL mode allows readers and writers to work concurrently:

- **Still One Writer**: Only one write transaction can be active across all processes
- **File System Locks**: SQLite uses OS-level locks that work across process boundaries  
- **Write Queuing**: Multiple processes attempting writes will queue/serialize automatically
- **Performance Impact**: Writing from multiple processes creates lock contention overhead

### Recommended Parallel Patterns

1. **Parse-Only Workers** (Recommended):
   ```python
   # Workers: CPU-intensive parsing, return results
   # Main: Fast database writes in batches
   ```

2. **Read-Only Analysis Workers**:
   ```python
   # Workers: Read from database, perform analysis, return findings
   # Main: Write analysis results
   ```

3. **Separate Read/Write Processes**:
   ```python
   # Reader processes: Query database for work items
   # Processor processes: Transform/analyze data  
   # Writer process: Single dedicated writer for all results
   ```

## Workflow-Specific Database Optimization

### Understanding KP-Dagger's Shifting Workload Patterns

KP-Dagger's database requirements shift dramatically across workflow phases:

**1. Parsing Phase - Write-Heavy:**
- High volume writes of normalized configuration entries
- Minimal reads (mostly validation/deduplication checks)
- Batch insert operations for performance
- WAL file growth expected

**2. Analysis Phase - Mixed Read/Write:**
- Heavy reads: Loading configuration data for analysis
- Frequent writes: Analysis findings, check results, status updates
- Pattern: Read config → Analyze → Write findings (per device/rule)
- Most complex phase for database optimization

**3. Reporting Phase - Read-Heavy:**
- Almost exclusively reads from findings and config tables
- Minimal writes: Report generation metadata/logs
- Complex analytical queries for aggregation
- WAL checkpoint opportunities

### Phase-Specific Optimization Strategies

```python
# services/core/database/workload_optimizer.py
from enum import Enum
from contextlib import contextmanager

class WorkflowPhase(Enum):
    PARSING = "parsing"
    ANALYSIS = "analysis" 
    REPORTING = "reporting"
    IDLE = "idle"

class WorkloadOptimizer:
    """Optimizes database settings based on current workflow phase."""
    
    def __init__(self, connection_manager: DatabaseConnectionManager):
        self.connection_manager = connection_manager
        self.wal_manager = WALCheckpointManager(connection_manager)
        self.current_phase = WorkflowPhase.IDLE
        
    @contextmanager
    def optimize_for_phase(self, phase: WorkflowPhase):
        """Context manager to optimize database for specific workflow phase."""
        previous_phase = self.current_phase
        self.current_phase = phase
        
        # Apply phase-specific optimizations
        self._apply_phase_optimizations(phase)
        
        try:
            yield
        finally:
            # Cleanup and transition
            self._cleanup_phase(phase)
            self.current_phase = previous_phase
            
    def _apply_phase_optimizations(self, phase: WorkflowPhase) -> None:
        """Apply database optimizations for specific phase."""
        with self.connection_manager.get_session() as session:
            
            if phase == WorkflowPhase.PARSING:
                # Optimize for write-heavy workload
                session.execute(text("PRAGMA synchronous=NORMAL"))  # Faster writes
                session.execute(text("PRAGMA wal_autocheckpoint=5000"))  # Less frequent checkpoints
                session.execute(text("PRAGMA cache_size=20000"))  # Larger cache for writes
                session.execute(text("PRAGMA temp_store=MEMORY"))  # Fast temp operations
                
            elif phase == WorkflowPhase.ANALYSIS:
                # Balanced read/write optimization
                session.execute(text("PRAGMA synchronous=NORMAL"))  # Balanced
                session.execute(text("PRAGMA wal_autocheckpoint=2000"))  # Moderate checkpoints
                session.execute(text("PRAGMA cache_size=15000"))  # Good read cache
                session.execute(text("PRAGMA optimize"))  # Update statistics
                
            elif phase == WorkflowPhase.REPORTING:
                # Optimize for read-heavy workload
                session.execute(text("PRAGMA synchronous=NORMAL"))  # Reads don't need sync
                session.execute(text("PRAGMA wal_autocheckpoint=500"))  # Frequent checkpoints for read speed
                session.execute(text("PRAGMA cache_size=25000"))  # Maximum cache for reads
                session.execute(text("PRAGMA mmap_size=536870912"))  # 512MB mmap for large reads
                
            elif phase == WorkflowPhase.IDLE:
                # Maintenance and cleanup optimizations
                session.execute(text("PRAGMA wal_autocheckpoint=1000"))  # Default
                session.execute(text("PRAGMA cache_size=10000"))  # Default
                
            session.commit()
            
    def _cleanup_phase(self, phase: WorkflowPhase) -> None:
        """Cleanup operations after phase completion."""
        if phase == WorkflowPhase.PARSING:
            # Force checkpoint after heavy writes
            self.wal_manager.run_checkpoint("FULL")
            
        elif phase == WorkflowPhase.ANALYSIS:
            # Gentle checkpoint to maintain performance
            self.wal_manager.run_checkpoint("PASSIVE")
            
        elif phase == WorkflowPhase.REPORTING:
            # Analyze tables for next operations
            with self.connection_manager.get_session() as session:
                session.execute(text("ANALYZE"))
                session.commit()

class PhaseAwareWorkflowService:
    """Workflow service that optimizes database for each phase."""
    
    def __init__(
        self,
        parsing_service: ParsingService,
        analysis_service: AnalysisService,
        reporting_service: ReportingService,
        workload_optimizer: WorkloadOptimizer
    ):
        self.parsing = parsing_service
        self.analysis = analysis_service
        self.reporting = reporting_service
        self.optimizer = workload_optimizer
        
    def execute_full_workflow(
        self,
        config_paths: list[Path],
        analysis_types: list[str] = None,
        report_formats: list[str] = None
    ) -> WorkflowResult:
        """Execute complete workflow with phase-specific optimizations."""
        
        results = WorkflowResult()
        
        # Phase 1: Parsing (Write-Heavy)
        with self.optimizer.optimize_for_phase(WorkflowPhase.PARSING):
            logger.info("Starting parsing phase (write-optimized)")
            results.parsed_configs = self._execute_parsing_phase(config_paths)
            
        # Phase 2: Analysis (Mixed Read/Write)  
        with self.optimizer.optimize_for_phase(WorkflowPhase.ANALYSIS):
            logger.info("Starting analysis phase (balanced read/write)")
            results.analysis_findings = self._execute_analysis_phase(
                results.parsed_configs, analysis_types
            )
            
        # Phase 3: Reporting (Read-Heavy)
        with self.optimizer.optimize_for_phase(WorkflowPhase.REPORTING):
            logger.info("Starting reporting phase (read-optimized)")
            results.reports = self._execute_reporting_phase(
                results.analysis_findings, report_formats
            )
            
        return results
        
    def _execute_parsing_phase(self, config_paths: list[Path]) -> list[str]:
        """Execute parsing with write-optimized database."""
        # Use batch processing for maximum write efficiency
        batch_service = BatchProcessingService(
            self.optimizer.connection_manager,
            batch_size=2000  # Larger batches for write phase
        )
        
        # Parse in parallel, collect results
        parsed_data = []
        with ProcessPoolExecutor() as executor:
            futures = [
                executor.submit(self._parse_single_config, path)
                for path in config_paths
            ]
            
            for future in as_completed(futures):
                try:
                    data = future.result()
                    parsed_data.append(data)
                except Exception as e:
                    logger.error(f"Parsing failed: {e}")
        
        # Batch write all parsed data
        config_ids = batch_service.batch_insert_configs(parsed_data)
        logger.info(f"Parsed {len(config_ids)} configurations")
        return config_ids
        
    def _execute_analysis_phase(
        self, 
        config_ids: list[str], 
        analysis_types: list[str]
    ) -> dict:
        """Execute analysis with balanced read/write optimization."""
        findings = {}
        
        # Process devices in batches to balance memory and I/O
        batch_size = 50  # Smaller batches for mixed operations
        
        for i in range(0, len(config_ids), batch_size):
            batch_ids = config_ids[i:i + batch_size]
            
            # Read configurations for this batch
            configs = self._read_configs_batch(batch_ids)
            
            # Analyze each configuration
            batch_findings = []
            for config in configs:
                for analysis_type in analysis_types:
                    findings_data = self.analysis.analyze_single_config(
                        config, analysis_type
                    )
                    batch_findings.extend(findings_data)
            
            # Write findings for this batch
            if batch_findings:
                finding_ids = self._write_findings_batch(batch_findings)
                findings[f"batch_{i//batch_size}"] = finding_ids
                
        logger.info(f"Analysis completed: {sum(len(f) for f in findings.values())} findings")
        return findings
        
    def _execute_reporting_phase(
        self, 
        findings: dict, 
        report_formats: list[str]
    ) -> list[str]:
        """Execute reporting with read-optimized database."""
        # Large read operations benefit from optimized cache
        report_paths = []
        
        for format_type in report_formats:
            # Single large read operation for all data
            report_data = self._read_complete_analysis_data()
            
            # Generate report (CPU-bound, no database I/O)
            report_path = self.reporting.generate_report(
                report_data, format_type
            )
            report_paths.append(report_path)
            
            # Minimal write: Log report generation
            self._log_report_generation(report_path, format_type)
            
        logger.info(f"Generated {len(report_paths)} reports")
        return report_paths
```

### Additional Considerations for Shifting Workloads

**1. Connection Pool Management:**
```python
class PhaseAwareConnectionManager(DatabaseConnectionManager):
    """Connection manager that adjusts pool size based on workload."""
    
    def optimize_pool_for_phase(self, phase: WorkflowPhase) -> None:
        if phase == WorkflowPhase.PARSING:
            # Fewer connections, focus on write throughput
            self.pool_size = 2
        elif phase == WorkflowPhase.ANALYSIS:
            # More connections for mixed workload
            self.pool_size = 5
        elif phase == WorkflowPhase.REPORTING:
            # Many read connections
            self.pool_size = 8
```

**2. Index Management:**
```python
class PhaseAwareIndexManager:
    """Manages indexes based on workload patterns."""
    
    def prepare_for_analysis_phase(self) -> None:
        """Create temporary indexes for analysis queries."""
        with self.connection_manager.get_session() as session:
            # Temporary indexes for analysis joins
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS tmp_config_device_vendor 
                ON normalized_configs(device_id, vendor)
            """))
            
    def cleanup_after_phase(self, phase: WorkflowPhase) -> None:
        """Remove temporary indexes after phase completion."""
        if phase == WorkflowPhase.ANALYSIS:
            with self.connection_manager.get_session() as session:
                session.execute(text("DROP INDEX IF EXISTS tmp_config_device_vendor"))
```

**3. Memory Management:**
```python
class PhaseAwareMemoryManager:
    """Manages memory allocation based on phase requirements."""
    
    def configure_for_phase(self, phase: WorkflowPhase) -> None:
        with self.connection_manager.get_session() as session:
            if phase == WorkflowPhase.PARSING:
                # Large page cache for write buffering
                session.execute(text("PRAGMA cache_size=25000"))
                session.execute(text("PRAGMA temp_store=MEMORY"))
                
            elif phase == WorkflowPhase.REPORTING:
                # Maximum cache for large analytical queries
                session.execute(text("PRAGMA cache_size=50000"))
                session.execute(text("PRAGMA mmap_size=1073741824"))  # 1GB mmap
```

**4. Monitoring Phase Transitions:**
```python
class PhaseTransitionMonitor:
    """Monitors performance across phase transitions."""
    
    def log_phase_metrics(self, phase: WorkflowPhase, duration: float) -> None:
        """Log performance metrics for each phase."""
        wal_info = self.wal_manager.get_wal_info()
        db_stats = self.monitor.get_database_stats()
        
        metrics = {
            "phase": phase.value,
            "duration_seconds": duration,
            "wal_pages": wal_info.get("wal_pages", 0),
            "database_size": db_stats.get("database_size_bytes", 0),
            "records_processed": db_stats.get("total_records", 0)
        }
        
        logger.info(f"Phase {phase.value} completed", extra=metrics)
```

### Performance Implications

**Parsing Phase Optimizations:**
- Disabled auto-checkpoints during bulk writes
- Larger write cache allocation
- Batch processing to minimize transaction overhead
- WAL file allowed to grow for write performance

**Analysis Phase Optimizations:**
- Balanced cache allocation for read/write mix
- Moderate checkpoint frequency
- Connection pooling optimized for concurrent operations
- Index creation for complex joins

**Reporting Phase Optimizations:**
- Maximum read cache allocation
- Aggressive checkpointing for read performance
- Memory-mapped I/O for large data scans
- Query optimization and statistics updates

This approach ensures optimal database performance as your application transitions through its natural workflow phases.

## Summary

This database design provides:

1. **Process Safety** - Proper understanding of SQLite's locking mechanisms and WAL mode constraints
2. **Accurate Concurrency Model** - Based on SQLite's actual behavior:
   - WAL mode: Multiple readers + single writer, readers don't block writers
   - Rollback mode: Multiple readers OR single writer (exclusive)
3. **Performance Optimization** - WAL checkpointing, indexing, and batch operations
4. **Scalability** - Parallel processing support within SQLite's **single-writer limitation across all processes**
5. **Maintainability** - Clear separation of read/write operations with WAL monitoring
6. **Reliability** - Built-in checkpoint management and WAL health monitoring
7. **Workflow-Aware Optimization** - Database tuning that adapts to shifting workload patterns across application phases

### Key Architectural Decisions:

- **WAL Mode Recommended** for KP-Dagger's read-heavy analytical workload
- **Return-Based Worker Pattern** to respect SQLite's single-writer limitation
- **Main Process Writes** to avoid cross-process write contention
- **Background Writer Thread** to serialize writes while maintaining application responsiveness  
- **Checkpoint Management** to prevent WAL file growth and maintain read performance
- **Process Coordination** understanding that all processes must be on same host for WAL mode
- **Monitoring and Health Checks** for database and WAL file maintenance
- **Phase-Specific Optimization** to handle shifting read/write patterns across workflow phases

The architecture accurately reflects SQLite's capabilities and limitations, particularly the **critical understanding that only one write transaction can be active across all processes**, while providing optimal performance for KP-Dagger's database-centric, potentially parallel processing requirements with **workflow-aware optimization** for shifting workload patterns.
