# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_dataprotection.aaz.latest.dataprotection.restorable_time_range import Find as _Find
import json
from ..helpers import clean_nulls_from_json


class Find(_Find):

    class RestorableTimeRangesFind(_Find.RestorableTimeRangesFind):

        def __call__(self, *args, **kwargs):
            request = self.make_request()
            session = self.client.send_request(request=request, stream=False, **kwargs)
            if session.http_response.status_code in [200]:
                return self.on_200(session)
            # Removing null valued items from json to fix 'Bad Request' error.
            clean_reponse = clean_nulls_from_json(json.loads(session.http_response.text()))
            encoding = session.http_response.internal_response.encoding
            session.http_response.internal_response._content = bytes(json.dumps(clean_reponse), encoding)
            return self.on_error(session.http_response)

