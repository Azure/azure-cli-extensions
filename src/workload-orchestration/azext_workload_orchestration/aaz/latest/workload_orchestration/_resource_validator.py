# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

from azure.cli.core.aaz import *
from azure.cli.core.azclierror import ValidationError


class ValidateResourceExists(AAZHttpOperation):
    """Validates that an ARM resource exists by making a GET request to its resource ID."""
    CLIENT_TYPE = "MgmtClient"

    def __init__(self, ctx, resource_id, resource_label="Resource"):
        super().__init__(ctx)
        self._resource_id = str(resource_id)
        self._resource_label = resource_label

    def __call__(self, *args, **kwargs):
        request = self.make_request()
        session = self.client.send_request(request=request, stream=False, **kwargs)
        if session.http_response.status_code == 404:
            raise ValidationError(
                f"{self._resource_label} not found. The resource with ID '{self._resource_id}' does not exist. "
                f"Please provide a valid {self._resource_label.lower()} resource ID."
            )
        if session.http_response.status_code != 200:
            raise ValidationError(
                f"Failed to validate {self._resource_label.lower()} existence for ID '{self._resource_id}'. "
                f"Received status code: {session.http_response.status_code}"
            )

    @property
    def url(self):
        return self.client.format_url(
            "{resourceId}",
            **self.url_parameters
        )

    @property
    def method(self):
        return "GET"

    @property
    def error_format(self):
        return "MgmtErrorFormat"

    @property
    def url_parameters(self):
        parameters = {
            **self.serialize_url_param(
                "resourceId", self._resource_id,
                required=True,
                skip_quote=True,
            ),
        }
        return parameters

    @property
    def query_parameters(self):
        parameters = {
            **self.serialize_query_param(
                "api-version", "2025-06-01",
                required=True,
            ),
        }
        return parameters

    @property
    def header_parameters(self):
        parameters = {
            **self.serialize_header_param(
                "Accept", "application/json",
            ),
        }
        return parameters
