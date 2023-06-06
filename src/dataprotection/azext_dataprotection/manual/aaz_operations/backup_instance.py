# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access
# pylint: disable=line-too-long
from azext_dataprotection.aaz.latest.dataprotection.backup_instance import (
    AdhocBackup as _AdhocBackup,
    Update as _Update
)
from ..helpers import clean_nulls_from_session_http_response


class AdhocBackup(_AdhocBackup):

    class BackupInstancesAdhocBackup(_AdhocBackup.BackupInstancesAdhocBackup):

        def __call__(self, *args, **kwargs):
            request = self.make_request()
            session = self.client.send_request(request=request, stream=False, **kwargs)
            if session.http_response.status_code in [200]:
                return self.on_200(session)
            # Removing null valued items from json to fix 'Bad Request' error.
            clean_nulls_from_session_http_response(session)
            return self.on_error(session.http_response)

        def on_200(self, session):
            data = self.deserialize_http_content(session)
            data = data.get('properties')
            self.ctx.set_var(
                "instance",
                data,
                schema_builder=self._build_schema_on_200
            )


class Update(_Update):

    class BackupInstancesCreateOrUpdate(_Update.BackupInstancesCreateOrUpdate):

        def __call__(self, *args, **kwargs):
            request = self.make_request()
            session = self.client.send_request(request=request, stream=False, **kwargs)
            if session.http_response.status_code in [202]:
                return self.client.build_lro_polling(
                    self.ctx.args.no_wait,
                    session,
                    self.on_200_201,
                    self.on_error,
                    lro_options={"final-state-via": "azure-async-operation"},
                    path_format_arguments=self.url_parameters,
                )
            if session.http_response.status_code in [200, 201]:
                return self.client.build_lro_polling(
                    self.ctx.args.no_wait,
                    session,
                    self.on_200_201,
                    self.on_error,
                    lro_options={"final-state-via": "azure-async-operation"},
                    path_format_arguments=self.url_parameters,
                )
            # Removing null valued items from json to fix 'Bad Request' error.
            clean_nulls_from_session_http_response(session)
            return self.on_error(session.http_response)
