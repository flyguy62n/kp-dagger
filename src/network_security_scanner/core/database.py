"""Database management for the network security scanner."""

import uuid
from pathlib import Path
from typing import Any

import duckdb
from sqlmodel import SQLModel, create_engine

from network_security_scanner.core.exceptions import DatabaseError
from network_security_scanner.models.base.enums import DeviceType


class DatabaseManager:
    """Manages database operations for the network security scanner."""

    def __init__(self, database_path: str | Path | None = None) -> None:
        """Initialize the database manager.

        Args:
            database_path: Path to database file or ":memory:" for in-memory
        """
        if database_path is None:
            database_path = ":memory:"
        elif isinstance(database_path, Path):
            database_path = str(database_path)

        self.database_path = database_path
        self.connection: duckdb.DuckDBPyConnection | None = None
        self.engine = None
        self._is_initialized = False

    def initialize(self) -> None:
        """Initialize the database and create tables."""
        try:
            # Create DuckDB connection
            if self.database_path == ":memory:":
                self.connection = duckdb.connect(":memory:")
            else:
                # Ensure directory exists
                db_path = Path(self.database_path)
                db_path.parent.mkdir(parents=True, exist_ok=True)
                self.connection = duckdb.connect(str(db_path))

            # Create SQLModel engine using DuckDB
            connection_string = f"duckdb:///{self.database_path}"
            self.engine = create_engine(connection_string)

            # Create all tables
            SQLModel.metadata.create_all(self.engine)

            self._is_initialized = True

        except Exception as e:
            msg = f"Failed to initialize database: {e}"
            raise DatabaseError(msg) from e

    def store_device_config(
        self,
        device_type: DeviceType,
        config_file: Path,
        parsed_config: dict[str, Any],
    ) -> str:
        """Store device configuration in the database.

        Args:
            device_type: Type of device
            config_file: Path to configuration file
            parsed_config: Parsed configuration data

        Returns:
            Device ID

        Raises:
            DatabaseError: If storage fails
        """
        if not self._is_initialized:
            self.initialize()

        try:
            device_id = str(uuid.uuid4())

            # Extract basic device info from parsed config
            hostname = parsed_config.get("hostname", config_file.stem)

            # Store device metadata
            device_data = {
                "id": device_id,
                "hostname": hostname,
                "device_type": device_type.value,
                "config_file_path": str(config_file),
                "parsed_config": parsed_config,
            }

            # Use raw SQL for now since we're using DuckDB
            if self.connection:
                self.connection.execute("""
                    CREATE TABLE IF NOT EXISTS devices (
                        id VARCHAR PRIMARY KEY,
                        hostname VARCHAR,
                        device_type VARCHAR,
                        config_file_path VARCHAR,
                        parsed_config JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                self.connection.execute(
                    """
                    INSERT INTO devices (id, hostname, device_type, config_file_path, parsed_config)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    [
                        device_id,
                        hostname,
                        device_type.value,
                        str(config_file),
                        str(parsed_config),  # Convert to string for now
                    ],
                )

                self.connection.commit()

            return device_id

        except Exception as e:
            msg = f"Failed to store device configuration: {e}"
            raise DatabaseError(msg) from e

    def get_device_config(self, device_id: str) -> dict[str, Any] | None:
        """Retrieve device configuration from database.

        Args:
            device_id: Device identifier

        Returns:
            Device configuration data or None if not found
        """
        if not self._is_initialized:
            self.initialize()

        try:
            if self.connection:
                result = self.connection.execute(
                    "SELECT * FROM devices WHERE id = ?", [device_id]
                ).fetchone()

                if result:
                    return {
                        "id": result[0],
                        "hostname": result[1],
                        "device_type": result[2],
                        "config_file_path": result[3],
                        "parsed_config": result[4],
                        "created_at": result[5] if len(result) > 5 else None,
                    }

            return None

        except Exception as e:
            msg = f"Failed to retrieve device configuration: {e}"
            raise DatabaseError(msg) from e

    def list_devices(self) -> list[dict[str, Any]]:
        """List all devices in the database.

        Returns:
            List of device metadata
        """
        if not self._is_initialized:
            self.initialize()

        try:
            devices = []

            if self.connection:
                results = self.connection.execute(
                    "SELECT id, hostname, device_type, config_file_path, created_at FROM devices"
                ).fetchall()

                for result in results:
                    devices.append(
                        {
                            "id": result[0],
                            "hostname": result[1],
                            "device_type": result[2],
                            "config_file_path": result[3],
                            "created_at": result[4] if len(result) > 4 else None,
                        }
                    )

            return devices

        except Exception as e:
            msg = f"Failed to list devices: {e}"
            raise DatabaseError(msg) from e

    def close(self) -> None:
        """Close database connections."""
        if self.connection:
            self.connection.close()
            self.connection = None

        self._is_initialized = False

    def __enter__(self) -> "DatabaseManager":
        """Context manager entry."""
        if not self._is_initialized:
            self.initialize()
        return self

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()


# Keep backward compatibility
Database = DatabaseManager
