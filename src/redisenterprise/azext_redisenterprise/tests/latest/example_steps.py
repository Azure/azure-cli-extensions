# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=unused-argument


# EXAMPLE: /RedisEnterprise/put/RedisEnterpriseCreate

# NOTE: Functions will always first be looked up in manual/custom.py followed by generated/custom.py

def step_create(test, checks=None, cache_num=1):
    if checks is None:
        checks = []
    if test.kwargs.get('no_database'):
        test.cmd('az redisenterprise create '
                 '--cluster-name "{cluster}" '
                 '--location "East US" '
                 '--sku "EnterpriseFlash_F300" '
                 '--tags tag1="value1" '
                 '--no-database '
                 '--resource-group "{rg}"',
                 checks=checks)
    elif test.kwargs.get('geo-replication'):
        if cache_num == 1:
            test.cmd('az redisenterprise create '
                        '--cluster-name "{cluster31}" '
                        '--sku "EnterpriseFlash_F300" '
                        '--location "East US" '
                        '--tags tag1="value1" '
                        '--no-database '
                        '--resource-group "{rg31}"',
                        checks=checks)
        elif cache_num == 2:
                test.cmd('az redisenterprise create '
                     '--location "West US" '
                     '--cluster-name "{cluster32}" '
                     '--sku "EnterpriseFlash_F300" '
                     '--client-protocol "Encrypted" '
                     '--clustering-policy "EnterpriseCluster" '
                     '--eviction-policy "NoEviction" '
                     '--group-nickname "groupName" '
                     '--linked-databases id="/subscriptions/{subscription}/resourceGroups/{rg31}/providers/Microsoft.Cache/redisEnterprise/{cluster31}/databases/{database}" '
                     '--linked-databases id="/subscriptions/{subscription}/resourceGroups/{rg32}/providers/Microsoft.Cache/redisEnterprise/{cluster32}/databases/{database}" '
                     '--port 10000 '
                     '--resource-group "{rg32}"',
                checks=checks)
    else:
        test.cmd('az redisenterprise create '
                 '--cluster-name "{cluster}" '
                 '--sku "Enterprise_E20" '
                 '--capacity 4 '
                 '--location "East US" '
                 '--tags tag1="value1" '
                 '--zones "1" "2" "3" '
                 '--minimum-tls-version "1.2" '
                 '--client-protocol "Encrypted" '
                 '--clustering-policy "EnterpriseCluster" '
                 '--eviction-policy "NoEviction" '
                 '--modules name="RedisBloom" '
                 '--modules name="RedisTimeSeries" '
                 '--modules name="RediSearch" '
                 '--port 10000 '
                 '--resource-group "{rg}"',
                 checks=checks)


# EXAMPLE: /Databases/post/RedisEnterpriseDatabasesForceUnlink - unlinking a database during a regional outage
def step_database_force_unlink(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise database force-unlink '
             '--cluster-name "{cluster32}" '
             '--unlink-ids "/subscriptions/{subscription}/resourceGroups/{rg31}/providers/Microsoft.Cache/redisEnterprise/{'
             'myRedisEnterprise2}/databases/{database}" '
             '--resource-group "{rg32}"',
             checks=checks)


# EXAMPLE: /RedisEnterprise/get/RedisEnterpriseGet
def step_show(test, checks=None):
    if checks is None:
        checks = []
    if test.kwargs.get('geo-replication'):
        test.cmd('az redisenterprise show '
                 '--cluster-name "{cluster32}" '
                 '--resource-group "{rg32}"',
                checks=checks)
    else:
        test.cmd('az redisenterprise show '
                 '--cluster-name "{cluster}" '
                 '--resource-group "{rg}"',
                 checks=checks)


# EXAMPLE: /RedisEnterprise/delete/RedisEnterpriseDelete
def step_delete(test, checks=None):
    if checks is None:
        checks = []
    if test.kwargs.get('geo-replication'):
        test.cmd('az redisenterprise delete -y '
                 '--cluster-name "{cluster31}" '
                 '--resource-group "{rg31}"',
                 checks=checks)
        test.cmd('az redisenterprise delete -y '
                 '--cluster-name "{cluster32}" '
                 '--resource-group "{rg32}"',
                 checks=checks)
    else:
        test.cmd('az redisenterprise delete -y '
                 '--cluster-name "{cluster}" '
                 '--resource-group "{rg}"',
                 checks=checks)


# EXAMPLE: /Databases/put/RedisEnterpriseDatabasesCreate
def step_database_create(test, checks=None):
    if checks is None:
        checks = []
    if test.kwargs.get('geo-replication'):
        test.cmd('az redisenterprise database create '
                '--cluster-name "{cluster31}" '
                '--client-protocol "Encrypted" '
                '--clustering-policy "EnterpriseCluster" '
                '--eviction-policy "NoEviction" '
                '--group-nickname "groupName" '
                '--linked-databases id="/subscriptions/{subscription}/resourceGroups/{rg31}/providers/Microsoft.Cache/redisEnterprise/{cluster31}/databases/{database}" '
                '--port 10000 '
                '--resource-group "{rg31}"',
        checks=checks)
    else:
        test.cmd('az redisenterprise database create '
                 '--cluster-name "{cluster}" '
                 '--client-protocol "Plaintext" '
                 '--clustering-policy "OSSCluster" '
                 '--eviction-policy "AllKeysLRU" '
                 '--port 10000 '
                 '--resource-group "{rg}"',
                 checks=checks)

def step_database_force_unlink(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise database force-unlink '
             '--cluster-name "{cluster32}" '
             '--unlink-ids "/subscriptions/{subscription}/resourceGroups/{rg31}/providers/Microsoft.Cache/redisEnterprise/{'
             'cluster31}/databases/{database}" '
             '--resource-group "{rg32}"',
             checks=checks)

# EXAMPLE: /Databases/get/RedisEnterpriseDatabasesGet
def step_database_show(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise database show '
            '--cluster-name "{cluster}" '
            '--resource-group "{rg}"',
            checks=checks)


# EXAMPLE: /Databases/get/RedisEnterpriseDatabasesListByCluster
def step_database_list(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise database list '
             '--cluster-name "{cluster}" '
             '--resource-group "{rg}"',
             checks=checks)


# EXAMPLE: /Databases/post/RedisEnterpriseDatabasesListKeys
def step_database_list_keys(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise database list-keys '
             '--cluster-name "{cluster}" '
             '--resource-group "{rg}"',
             checks=checks)


# EXAMPLE: /Databases/post/RedisEnterpriseDatabasesRegenerateKey
def step_database_regenerate_key(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise database regenerate-key '
             '--cluster-name "{cluster}" '
             '--key-type "Primary" '
             '--resource-group "{rg}"',
             checks=checks)


# EXAMPLE: /Databases/delete/RedisEnterpriseDatabasesDelete
def step_database_delete(test, checks=None):
    if checks is None:
        checks = []
    if test.kwargs.get('geo-replication'):
        test.cmd('az redisenterprise database delete -y '
                 '--cluster-name "{cluster31}" '
                 '--resource-group "{rg31}"',
                 checks=checks)
        test.cmd('az redisenterprise database delete -y '
                 '--cluster-name "{cluster32}" '
                 '--resource-group "{rg32}"',
                 checks=checks)
    else:
        test.cmd('az redisenterprise database delete -y '
                 '--cluster-name "{cluster}" '
                 '--resource-group "{rg}"',
                 checks=checks)
