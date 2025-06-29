"""Parser output to database normalization."""


class Normalizer:
    """Converts device-specific models to normalized database models."""

    def __init__(self) -> None:
        """Initialize normalizer."""
        self.device_normalizers = {}

    def normalize_configuration(self, device_config: dict, device_type: str) -> dict:
        """
        Normalize device configuration to common database format.

        Args:
            device_config: Device-specific configuration data
            device_type: Type of device (cisco-ios, cisco-asa, etc.)

        Returns:
            Normalized configuration dictionary

        """
        msg = "Configuration normalization not yet implemented"
        raise NotImplementedError(msg)

    def register_normalizer(self, device_type: str, normalizer_class: type) -> None:
        """
        Register a device-specific normalizer.

        Args:
            device_type: Device type identifier
            normalizer_class: Normalizer class for this device type

        """
        self.device_normalizers[device_type] = normalizer_class
