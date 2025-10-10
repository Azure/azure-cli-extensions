# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from knack.help_files import helps
import azext_arcdata.sqlmi.help  # pylint: disable=check-to-ignore
import azext_arcdata.sqlmidb.help  # pylint: disable=check-to-ignore

import azext_arcdata.sqlarc.database.help  # pylint: disable=check-to-ignore #TODO: Add this back for database
import azext_arcdata.sqlarc.server.help  # pylint: disable=check-to-ignore
import azext_arcdata.dc.help  # pylint: disable=check-to-ignore
import azext_arcdata.postgres.help  # pylint: disable=check-to-ignore
import azext_arcdata.ad_connector.help  # pylint: disable=check-to-ignore
import azext_arcdata.failover_group.help  # pylint: disable=check-to-ignore
