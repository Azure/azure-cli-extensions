# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access
# pylint: disable=line-too-long
from azext_dataprotection.aaz.latest.dataprotection.backup_vault import Update as _Update
from ..helpers import clean_nulls_from_session_http_response


class Update(_Update):

    class BackupVaultsCreateOrUpdate(_Update.BackupVaultsCreateOrUpdate):

        def __call__(self, *args, **kwargs):    # Remove after error handling fixed.
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
            # This is a temporary fix for AAZ failing to handle null values in error response.
            clean_nulls_from_session_http_response(session)
            return self.on_error(session.http_response)
