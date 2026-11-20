# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------------


class HTTPCodes(object):
    """
    Defines the HTTP status codes.
    """

    # -- Success --
    @property
    def ok(self):
        return 200

    @property
    def created(self):
        return 201

    @property
    def no_content(self):
        return 204

    # -- Client Errors --
    @property
    def bad_request(self):
        return 400

    @property
    def unauthorized(self):
        return 401

    @property
    def forbidden(self):
        return 403

    @property
    def not_found(self):
        return 404

    @property
    def method_not_allowed(self):
        return 405

    @property
    def request_timeout(self):
        return 408

    @property
    def conflict(self):
        return 409

    # -- Server Errors --
    @property
    def bad_gateway(self):
        return 502

    @property
    def service_unavailable(self):
        return 503

    @property
    def gateway_timeout(self):
        return 504


http_status_codes = HTTPCodes()
