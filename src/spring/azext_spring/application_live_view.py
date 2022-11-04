# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument, logging-format-interpolation, protected-access, wrong-import-order, too-many-lines
from knack.log import get_logger

from .vendored_sdks.appplatform.v2022_11_01_preview import models

DEFAULT_NAME = "default"

logger = get_logger(__name__)


def show(cmd, client, service, resource_group):
    return client.application_live_views.get(resource_group, service, DEFAULT_NAME)


def create(cmd, client, service, resource_group):
    return client.application_live_views.begin_create_or_update(resource_group, service, DEFAULT_NAME, models.ApplicationLiveViewResource())


def delete(cmd, client, service, resource_group):
    return client.application_live_views.begin_delete(resource_group, service, DEFAULT_NAME)
