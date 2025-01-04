"""
Base parser class for resume parsing.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseParser(ABC):
    """Base class for resume parsers."""

    def __init__(self, file_path: str):
        """Initialize the parser with a file path.

        Args:
            file_path: Path to the resume file
        """
        self.file_path = file_path

    @abstractmethod
    def parse(self) -> Any:
        """Parse the resume file and return structured data.

        Returns:
            Parsed resume data in the appropriate format
        """
        pass
