# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Map ARM error responses to typed azclierror exceptions."""

from azure.cli.core.azclierror import (
    AzureResponseError,
    ClientRequestError,
    CLIInternalError,
    ForbiddenError,
    InvalidArgumentValueError,
    ResourceNotFoundError,
)


def raise_for_arm_error(response):
    """Raise a typed CLI error for an ARM response with status >= 400."""
    status = response.status_code
    code, message = _extract_error(response)
    detail = f"{code}: {message}" if code else message
    if status == 404:
        raise ResourceNotFoundError(detail)
    if status == 400:
        raise InvalidArgumentValueError(detail)
    if status == 403:
        raise ForbiddenError(detail)
    if status == 409:
        raise ClientRequestError(detail)
    if status >= 500:
        raise CLIInternalError(detail)
    raise ClientRequestError(detail)


def raise_for_async_operation(status_body):
    """Raise a typed CLI error for a failed async operation status body."""
    status = status_body.get('status', 'Failed')
    error = status_body.get('error')
    if isinstance(error, dict):
        code = error.get('code')
        message = error.get('message', '')
        detail = f"{code}: {message}" if code else message
    else:
        detail = ''
    if not detail:
        detail = f"The operation completed with status '{status}'."
    raise AzureResponseError(detail)


def _extract_error(response):
    """Extract (code, message) from an ARM error body when present."""
    try:
        body = response.json()
    except ValueError:
        return None, response.text
    error = body.get('error') if isinstance(body, dict) else None
    if isinstance(error, dict):
        return error.get('code'), error.get('message', response.text)
    return None, response.text
