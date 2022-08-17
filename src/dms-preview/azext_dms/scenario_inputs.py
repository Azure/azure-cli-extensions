# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_dms.vendored_sdks.datamigration.models import (MongoDbMigrationSettings)


def get_mongo_to_mongo_input(database_options_json,
                             source_connection_info,
                             target_connection_info):
    if 'databases' not in database_options_json or database_options_json.get('databases') is None:
        raise ValueError("'databases' must be present in 'database_options_json'.")

    if 'replication' not in database_options_json or database_options_json.get('replication') is None:
        raise ValueError("'replication' must be present and not null in 'database_options_json'.")

    return MongoDbMigrationSettings(databases=database_options_json['databases'],
                                    source=source_connection_info,
                                    target=target_connection_info,
                                    boost_rus=database_options_json.get('boostRUs', 0),
                                    replication=database_options_json['replication'],
                                    throttling=database_options_json.get('throttling', None))
