# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access
# pylint: disable=line-too-long

from azext_dataprotection.aaz.latest.dataprotection.restorable_time_range import Find as _Find
from ..helpers import clean_nulls_from_session_http_response, validate_recovery_point_datetime_format


class Find(_Find):

    # Can be used to make start_time and end_time input more user friendly
    # def pre_operations(self):
    #     self.ctx.args.start_time = validate_recovery_point_datetime_format(self.ctx.args.start_time)
    #     self.ctx.args.end_time = validate_recovery_point_datetime_format(self.ctx.args.end_time)

    class RestorableTimeRangesFind(_Find.RestorableTimeRangesFind):

        def __call__(self, *args, **kwargs):    # Remove after error handling fixed.
            request = self.make_request()
            session = self.client.send_request(request=request, stream=False, **kwargs)
            if session.http_response.status_code in [200]:
                return self.on_200(session)
            # Removing null valued items from json to fix 'Bad Request' error.
            # This is a temporary fix for AAZ failing to handle null values in error response.
            clean_nulls_from_session_http_response(session)
            return self.on_error(session.http_response)
