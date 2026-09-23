# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from http import HTTPStatus

from azure.cli.core.aaz import AAZFreeFormDictType
from azure.cli.core.util import get_error_type_by_status_code

from azext_maintenance.aaz.latest.maintenance.scheduledevents import (
    Acknowledge as _Acknowledge,
    ListAcknowledge as _ListAcknowledge,
)


class _ResponseContentOperation:
    _schema_on_response = None

    def __call__(self, *args, **kwargs):
        request = self.make_request()
        session = self.client.send_request(request=request, stream=False, **kwargs)
        status_code = session.http_response.status_code
        if status_code == 200:
            return self.on_200(session)
        body = session.http_response.body()
        if 200 <= status_code < 300:
            if body:
                return self.on_response(session)
            return None
        if body:
            try:
                data = json.loads(body)
            except (ValueError, TypeError):
                return self.on_error(session.http_response)
            error_type = get_error_type_by_status_code(str(status_code))
            try:
                status_name = HTTPStatus(status_code).name.title().replace('_', '')
            except ValueError:
                status_name = f'HTTP{status_code}'
            raise error_type(f'{status_name}\n{json.dumps(data, indent=2)}')
        return self.on_error(session.http_response)

    def on_response(self, session):
        data = self.deserialize_http_content(session)
        self.ctx.set_var(
            "instance",
            data,
            schema_builder=self._build_schema_on_response,
        )

    @classmethod
    def _build_schema_on_response(cls):
        if cls._schema_on_response is None:
            cls._schema_on_response = AAZFreeFormDictType()
        return cls._schema_on_response


class _AcknowledgeOperation(
        _ResponseContentOperation,
        _Acknowledge.ScheduledEventOperationGroupAcknowledge):
    """Return successful acknowledgements and raise failures with their JSON body."""


class _ListAcknowledgeOperation(
        _ResponseContentOperation,
        _ListAcknowledge.ScheduledEventOperationGroupAcknowledgeList):
    """Return multi-status results as output and raise failures with their JSON body."""


class Acknowledge(_Acknowledge):
    ScheduledEventOperationGroupAcknowledge = _AcknowledgeOperation


class ListAcknowledge(_ListAcknowledge):
    ScheduledEventOperationGroupAcknowledgeList = _ListAcknowledgeOperation


__all__ = ["Acknowledge", "ListAcknowledge"]
