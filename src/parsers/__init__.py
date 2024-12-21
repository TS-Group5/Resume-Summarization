"""
Parser module for extracting structured data from various resume formats.
"""

from .ats_parser import ATSParser
from .industry_manager_parser import IndustryManagerParser

__all__ = [
    'ATSParser',
    'IndustryManagerParser'
]
