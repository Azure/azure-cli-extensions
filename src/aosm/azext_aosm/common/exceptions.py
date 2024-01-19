class InvalidFileTypeError(Exception):
    """Raised when the file type is not supported by the parser"""


class MissingChartDependencyError(Exception):
    """Raised when the chart dependency is missing"""


class SchemaGetOrGenerateError(Exception):
    """Raised when the schema cannot be generated or retrieved"""


class DefaultValuesNotFoundError(Exception):
    """Raised when the default values file cannot be found"""
