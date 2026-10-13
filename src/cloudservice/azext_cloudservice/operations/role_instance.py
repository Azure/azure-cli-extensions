# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access

from azext_cloudservice.aaz.latest.cloud_service.role_instance._show_remote_desktop_file import \
    ShowRemoteDesktopFile as _ShowRemoteDesktopFile


class RoleInstanceShowRemoteDesktopFile(_ShowRemoteDesktopFile):
    """The service returns the RDP file as application/x-rdp, not JSON."""

    class CloudServiceRoleInstancesGetRemoteDesktopFile(
            _ShowRemoteDesktopFile.CloudServiceRoleInstancesGetRemoteDesktopFile):

        def __call__(self, *args, **kwargs):
            request = self.make_request()
            # stream=True keeps the content-decode policy from rejecting application/x-rdp
            session = self.client.send_request(request=request, stream=True, **kwargs)
            if session.http_response.status_code in [200]:
                return self.on_200(session)
            return self.on_error(session.http_response)

        @property
        def header_parameters(self):
            return {
                **self.serialize_header_param("Accept", "application/x-rdp"),
            }

        def on_200(self, session):
            data = session.http_response.body().decode('utf-8')
            self.ctx.set_var(
                "instance",
                data,
                schema_builder=self._build_schema_on_200
            )
