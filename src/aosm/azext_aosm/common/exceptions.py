# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.azclierror import UserFault


class InvalidFileTypeError(Exception):
    """Raised when the file type is not supported by the parser"""


class MissingDependency(UserFault):
    """Raised when the required dependency is missing"""


class MissingChartDependencyError(Exception):
    """Raised when the chart dependency is missing"""


class SchemaGetOrGenerateError(Exception):
    """Raised when the schema cannot be generated or retrieved"""


class DefaultValuesNotFoundError(UserFault):
    """Raised when the default values file cannot be found"""


class TemplateValidationError(Exception):
    """Raised when template validation fails"""
