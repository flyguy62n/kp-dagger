"""File processing service for encoding detection, validation, and hashing."""

from kp_dagger.core.services.file_processing.discovery import (
    FileDiscoveryService,
)
from kp_dagger.core.services.file_processing.encoding import (
    CharsetNormalizerEncodingDetector,
)
from kp_dagger.core.services.file_processing.hashing import (
    ConfigurableFileHashGenerator,
    SHA384FileHashGenerator,
)
from kp_dagger.core.services.file_processing.mime_detection import MimeDetector
from kp_dagger.core.services.file_processing.path_utilities import (
    PathUtilitiesService,
)
from kp_dagger.core.services.file_processing.protocols import (
    ContentStreamer,
    EncodingDetector,
    FileDiscoverer,
    FileValidator,
    HashGenerator,
    MimeTypeDetector,
    PathUtilities,
)
from kp_dagger.core.services.file_processing.service import (
    FileProcessingService,
)
from kp_dagger.core.services.file_processing.streaming import (
    FileContentStreamer,
)
from kp_dagger.core.services.file_processing.validation import (
    BasicFileValidator,
)

__all__: list[str] = [
    "BasicFileValidator",
    "CharsetNormalizerEncodingDetector",
    "ConfigurableFileHashGenerator",
    "ContentStreamer",
    "EncodingDetector",
    "FileContentStreamer",
    "FileDiscoverer",
    "FileDiscoveryService",
    "FileProcessingService",
    "FileValidator",
    "HashGenerator",
    "MimeDetector",
    "MimeTypeDetector",
    "PathUtilities",
    "PathUtilitiesService",
    "SHA384FileHashGenerator",
]
