# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from __future__ import print_function
from json.decoder import JSONDecodeError
from kubernetes.client.models.v1_status import V1Status
from kubernetes.client.models.v1_status_details import V1StatusDetails
from kubernetes.client.models.v1_list_meta import V1ListMeta
from azext_arcdata.vendored_sdks.kubernetes_sdk.HttpCodes import http_status_codes
from humanfriendly.tables import (
    format_pretty_table,
    format_robust_table,
    format_smart_table,
)

import json
import sys


class K8sAdmissionReviewError(Exception):
    def __init__(self, e: Exception) -> "K8sAdmissionReviewError":
        if not K8sAdmissionReviewError.is_admission_review_error(e):
            raise ValueError(
                "Error does not come from admission review response"
            )

        body = json.loads(e.body) if type(e.body) is str else e.body
        self._status: V1Status = V1Status(
            api_version=body["apiVersion"] if "apiVersion" in body else None,
            code=body["code"] if "code" in body else None,
            details=(
                V1StatusDetails(**body["details"])
                if "details" in body
                else None
            ),
            kind=body["kind"] if "kind" in body else None,
            message=body["message"] if "message" in body else None,
            metadata=body["metadata"] if "metadata" in body else None,
            reason=body["reason"] if "reason" in body else None,
            status=body["status"] if "status" in body else None,
        )

        self._error: Exception = e

    @property
    def api_version(self) -> str:
        return self._status.api_version

    @property
    def code(self) -> int:
        return self._status.code

    @property
    def details(self) -> V1StatusDetails:
        return self._status.details

    @property
    def kind(self) -> str:
        return self._status.kind

    @property
    def message(self) -> str:
        return self._status.message

    @property
    def metadata(self) -> V1ListMeta:
        return self._status.metadata

    @property
    def reason(self) -> str:
        return self._status.reason

    @property
    def status(self) -> str:
        return self._status.status

    def pretty_print_errors(self):
        """
        Prints admission respsonse errors in a nice format
        depending on the number of errors. If only one it will
        just print the message associated with it, otherwise will
        create a table to format all the errors.
        """
        causes = getattr(self.details, "causes", [])
        if len(causes) > 1:
            print(
                "Admission webhook denied the request with the following errors: \n\n",
                file=sys.stderr,
            )

        print(self._to_string(), file=sys.stderr)

    def _to_string(self) -> str:
        """
        Returns a string representation of this error
        """
        message = "Invalid configuration: \n\n"
        causes = getattr(self.details, "causes", [])
        column_names = ["Field", "Message"]
        data = [
            [
                c.get("field", "Custom resource"),
                c.get("message", "Custom resource validation error"),
            ]
            for c in causes
        ]
        if len(causes) > 1:
            return message + format_smart_table(data, column_names)
        else:
            return message + format_robust_table(data, column_names)

    def __str__(self) -> str:
        """
        @override
        """
        return self._to_string()

    @staticmethod
    def is_admission_review_error(e: Exception) -> bool:
        """
        Determines if the exception body has a response that looks like an admission review error.
        """
        try:
            response = getattr(e, "body", None)
            if response is None:
                return False
            response = (
                json.loads(response) if type(response) is str else response
            )

            is403: bool = (
                "code" in response
                and response["code"] == http_status_codes.forbidden
            )
            isStatus: bool = "kind" in response and response["kind"] == "Status"
            isFailure: bool = (
                "status" in response and response["status"] == "Failure"
            )
            containsAdmissionWebhook: bool = (
                "message" in response
                and "admission webhook" in response["message"]
            )
            return is403 and isStatus and isFailure and containsAdmissionWebhook
        except JSONDecodeError:
            return False
