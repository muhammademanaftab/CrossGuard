"""
Custom Exceptions for Cross Guard.

This module defines custom exception classes for better error handling
and more informative error messages throughout the application.
"""

from typing import Optional, List, Dict, Any


class CrossGuardError(Exception):
    """Base exception for all Cross Guard errors.

    All custom exceptions in Cross Guard should inherit from this class
    to allow catching all Cross Guard-specific errors with a single except clause.

    Attributes:
        message: Human-readable error message
        details: Optional dictionary with additional error context
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON serialization."""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'details': self.details
        }


# =============================================================================
# Parser Exceptions
# =============================================================================

class ParserError(CrossGuardError):
    """Raised when parsing fails.

    This exception is raised when a parser encounters an error while
    processing HTML, CSS, or JavaScript files.
    """

    def __init__(self, message: str, file_path: Optional[str] = None,
                 line_number: Optional[int] = None,
                 parser_type: Optional[str] = None):
        details = {}
        if file_path:
            details['file_path'] = file_path
        if line_number:
            details['line_number'] = line_number
        if parser_type:
            details['parser_type'] = parser_type
        super().__init__(message, details)
        self.file_path = file_path
        self.line_number = line_number
        self.parser_type = parser_type


class HTMLParserError(ParserError):
    """Raised when HTML parsing fails."""

    def __init__(self, message: str, file_path: Optional[str] = None,
                 line_number: Optional[int] = None):
        super().__init__(message, file_path, line_number, parser_type='HTML')


class CSSParserError(ParserError):
    """Raised when CSS parsing fails."""

    def __init__(self, message: str, file_path: Optional[str] = None,
                 line_number: Optional[int] = None):
        super().__init__(message, file_path, line_number, parser_type='CSS')


class JavaScriptParserError(ParserError):
    """Raised when JavaScript parsing fails."""

    def __init__(self, message: str, file_path: Optional[str] = None,
                 line_number: Optional[int] = None):
        super().__init__(message, file_path, line_number, parser_type='JavaScript')


# =============================================================================
# Database Exceptions
# =============================================================================

class DatabaseError(CrossGuardError):
    """Raised when database operations fail.

    This exception is raised when there are issues with loading,
    querying, or updating the Can I Use database.
    """

    def __init__(self, message: str, operation: Optional[str] = None,
                 feature_id: Optional[str] = None):
        details = {}
        if operation:
            details['operation'] = operation
        if feature_id:
            details['feature_id'] = feature_id
        super().__init__(message, details)
        self.operation = operation
        self.feature_id = feature_id


class DatabaseLoadError(DatabaseError):
    """Raised when database fails to load."""

    def __init__(self, message: str, database_path: Optional[str] = None):
        super().__init__(message, operation='load')
        if database_path:
            self.details['database_path'] = database_path
        self.database_path = database_path


class FeatureNotFoundError(DatabaseError):
    """Raised when a requested feature is not found in the database."""

    def __init__(self, feature_id: str):
        message = f"Feature '{feature_id}' not found in database"
        super().__init__(message, operation='lookup', feature_id=feature_id)


class DatabaseUpdateError(DatabaseError):
    """Raised when database update fails."""

    def __init__(self, message: str, update_url: Optional[str] = None):
        super().__init__(message, operation='update')
        if update_url:
            self.details['update_url'] = update_url
        self.update_url = update_url


# =============================================================================
# Analysis Exceptions
# =============================================================================

class AnalysisError(CrossGuardError):
    """Raised when analysis operations fail.

    This exception is raised when there are issues during the
    compatibility analysis process.
    """

    def __init__(self, message: str, phase: Optional[str] = None,
                 features_analyzed: Optional[int] = None):
        details = {}
        if phase:
            details['phase'] = phase
        if features_analyzed is not None:
            details['features_analyzed'] = features_analyzed
        super().__init__(message, details)
        self.phase = phase
        self.features_analyzed = features_analyzed


class ValidationError(AnalysisError):
    """Raised when input validation fails."""

    def __init__(self, message: str, invalid_files: Optional[List[str]] = None):
        super().__init__(message, phase='validation')
        if invalid_files:
            self.details['invalid_files'] = invalid_files
        self.invalid_files = invalid_files or []


class CompatibilityCheckError(AnalysisError):
    """Raised when compatibility checking fails."""

    def __init__(self, message: str, browser: Optional[str] = None,
                 version: Optional[str] = None):
        super().__init__(message, phase='compatibility_check')
        if browser:
            self.details['browser'] = browser
        if version:
            self.details['version'] = version
        self.browser = browser
        self.version = version


class ScoringError(AnalysisError):
    """Raised when score calculation fails."""

    def __init__(self, message: str, scoring_method: Optional[str] = None):
        super().__init__(message, phase='scoring')
        if scoring_method:
            self.details['scoring_method'] = scoring_method
        self.scoring_method = scoring_method


# =============================================================================
# Export Exceptions
# =============================================================================

class ExportError(CrossGuardError):
    """Raised when export operations fail."""

    def __init__(self, message: str, export_format: Optional[str] = None,
                 output_path: Optional[str] = None):
        details = {}
        if export_format:
            details['export_format'] = export_format
        if output_path:
            details['output_path'] = output_path
        super().__init__(message, details)
        self.export_format = export_format
        self.output_path = output_path


class JSONExportError(ExportError):
    """Raised when JSON export fails."""

    def __init__(self, message: str, output_path: Optional[str] = None):
        super().__init__(message, export_format='JSON', output_path=output_path)


class PDFExportError(ExportError):
    """Raised when PDF export fails."""

    def __init__(self, message: str, output_path: Optional[str] = None):
        super().__init__(message, export_format='PDF', output_path=output_path)


class HTMLExportError(ExportError):
    """Raised when HTML export fails."""

    def __init__(self, message: str, output_path: Optional[str] = None):
        super().__init__(message, export_format='HTML', output_path=output_path)


# =============================================================================
# File Exceptions
# =============================================================================

class FileError(CrossGuardError):
    """Raised when file operations fail."""

    def __init__(self, message: str, file_path: Optional[str] = None,
                 operation: Optional[str] = None):
        details = {}
        if file_path:
            details['file_path'] = file_path
        if operation:
            details['operation'] = operation
        super().__init__(message, details)
        self.file_path = file_path
        self.operation = operation


class FileNotFoundError(FileError):
    """Raised when a required file is not found."""

    def __init__(self, file_path: str):
        message = f"File not found: {file_path}"
        super().__init__(message, file_path=file_path, operation='read')


class FileReadError(FileError):
    """Raised when reading a file fails."""

    def __init__(self, file_path: str, reason: Optional[str] = None):
        message = f"Failed to read file: {file_path}"
        if reason:
            message += f" ({reason})"
        super().__init__(message, file_path=file_path, operation='read')
        self.reason = reason


class FileWriteError(FileError):
    """Raised when writing to a file fails."""

    def __init__(self, file_path: str, reason: Optional[str] = None):
        message = f"Failed to write file: {file_path}"
        if reason:
            message += f" ({reason})"
        super().__init__(message, file_path=file_path, operation='write')
        self.reason = reason


# =============================================================================
# Configuration Exceptions
# =============================================================================

class ConfigurationError(CrossGuardError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str, config_key: Optional[str] = None,
                 expected_type: Optional[str] = None):
        details = {}
        if config_key:
            details['config_key'] = config_key
        if expected_type:
            details['expected_type'] = expected_type
        super().__init__(message, details)
        self.config_key = config_key
        self.expected_type = expected_type


class InvalidBrowserError(ConfigurationError):
    """Raised when an invalid browser is specified."""

    def __init__(self, browser: str, valid_browsers: Optional[List[str]] = None):
        message = f"Invalid browser: {browser}"
        super().__init__(message, config_key='browser')
        self.details['invalid_browser'] = browser
        if valid_browsers:
            self.details['valid_browsers'] = valid_browsers
        self.browser = browser
        self.valid_browsers = valid_browsers


class InvalidVersionError(ConfigurationError):
    """Raised when an invalid browser version is specified."""

    def __init__(self, browser: str, version: str):
        message = f"Invalid version '{version}' for browser '{browser}'"
        super().__init__(message, config_key='version')
        self.details['browser'] = browser
        self.details['version'] = version
        self.browser = browser
        self.version = version
