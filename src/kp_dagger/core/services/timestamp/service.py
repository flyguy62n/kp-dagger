"""Timestamp service implementation providing datetime operations."""

from datetime import UTC, datetime, timedelta, timezone


class TimestampService:
    """Timestamp service implementation providing datetime operations."""

    def __init__(self, default_timezone: timezone = UTC) -> None:
        """
        Initialize timestamp service.

        Args:
            default_timezone: Default timezone for operations (defaults to UTC)

        """
        self.default_timezone = default_timezone
        self._cached_filename_timestamp: str | None = None

    def now(self) -> datetime:
        """Get current local datetime."""
        return datetime.now().astimezone()

    def utc_now(self) -> datetime:
        """Get current UTC datetime."""
        return datetime.now(UTC)

    def format_iso(self, dt: datetime) -> str:
        """
        Format datetime as ISO 8601 string.

        Args:
            dt: Datetime to format

        Returns:
            ISO 8601 formatted string

        """
        return dt.isoformat()

    def format_rfc3339(self, dt: datetime) -> str:
        """
        Format datetime as RFC 3339 string.

        Args:
            dt: Datetime to format

        Returns:
            RFC 3339 formatted string

        """
        # Add timezone info if not present
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=self.default_timezone)

        return dt.strftime("%Y-%m-%dT%H:%M:%S%z")

    def format_filename(self, dt: datetime) -> str:
        """
        Format datetime for use in filenames (YYYYMMDD-HHMMSS).

        Args:
            dt: Datetime to format

        Returns:
            Filename-safe formatted string (YYYYMMDD-HHMMSS)

        """
        return dt.strftime("%Y%m%d-%H%M%S")

    def format_filename_now(self) -> str:
        """
        Format current local time for use in filenames (YYYYMMDD-HHMMSS).

        The timestamp is cached on first call and reused for subsequent calls
        during the same application run to ensure consistent timestamps across
        all files in a batch processing operation.

        Returns:
            Filename-safe formatted string for current local time (cached)

        """
        if self._cached_filename_timestamp is None:
            self._cached_filename_timestamp = self.format_filename(self.now())
        return self._cached_filename_timestamp

    def reset_filename_cache(self) -> None:
        """
        Reset the cached filename timestamp to force regeneration on next call.

        This is useful for testing or if you want to force a new timestamp
        during the same application run.
        """
        self._cached_filename_timestamp = None

    def parse_iso(self, iso_string: str) -> datetime:
        """
        Parse ISO 8601 string to datetime.

        Args:
            iso_string: ISO 8601 formatted string

        Returns:
            Parsed datetime object

        Raises:
            ValueError: If string cannot be parsed

        """
        try:
            return datetime.fromisoformat(iso_string)
        except ValueError as e:
            msg = f"Invalid ISO format: {iso_string}"
            raise ValueError(msg) from e

    def to_utc(self, dt: datetime) -> datetime:
        """
        Convert datetime to UTC.

        Args:
            dt: Datetime to convert

        Returns:
            UTC datetime

        """
        if dt.tzinfo is None:
            # Assume local timezone if none specified
            dt = dt.replace(tzinfo=self.default_timezone)

        return dt.astimezone(UTC)

    def from_timestamp(self, timestamp: float) -> datetime:
        """
        Create datetime from Unix timestamp.

        Args:
            timestamp: Unix timestamp (seconds since epoch)

        Returns:
            Datetime object in UTC

        """
        return datetime.fromtimestamp(timestamp, tz=UTC)

    def to_timestamp(self, dt: datetime) -> float:
        """
        Convert datetime to Unix timestamp.

        Args:
            dt: Datetime to convert

        Returns:
            Unix timestamp (seconds since epoch)

        """
        return dt.timestamp()

    def elapsed_seconds(
        self,
        start_time: datetime,
        end_time: datetime | None = None,
    ) -> float:
        """
        Calculate elapsed seconds between two datetimes.

        Args:
            start_time: Start datetime
            end_time: End datetime (defaults to current UTC time)

        Returns:
            Elapsed seconds as float

        """
        if end_time is None:
            end_time = self.utc_now()

        return (end_time - start_time).total_seconds()

    def add_seconds(self, dt: datetime, seconds: float) -> datetime:
        """
        Add seconds to a datetime.

        Args:
            dt: Base datetime
            seconds: Seconds to add (can be negative)

        Returns:
            Modified datetime

        """
        return dt + timedelta(seconds=seconds)
