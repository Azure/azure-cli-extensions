# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def mysql_up(client, resource_group_name, server_name, sku_name,
             location=None, administrator_login=None, administrator_login_password=None, backup_retention=None,
             geo_redundant_backup=None, ssl_enforcement=None, storage_mb=None, tags=None, version=None):
    from azext_rdbms_up.vendored_sdks.azure_mgmt_rdbms import mysql
    parameters = mysql.models.ServerForCreate(
        sku=mysql.models.Sku(name=sku_name),
        properties=mysql.models.ServerPropertiesForDefaultCreate(
            administrator_login=administrator_login,
            administrator_login_password=administrator_login_password,
            version=version,
            ssl_enforcement=ssl_enforcement,
            storage_profile=mysql.models.StorageProfile(
                backup_retention_days=backup_retention,
                geo_redundant_backup=geo_redundant_backup,
                storage_mb=storage_mb)),
        location=location,
        tags=tags)

    return client.create(resource_group_name, server_name, parameters)
