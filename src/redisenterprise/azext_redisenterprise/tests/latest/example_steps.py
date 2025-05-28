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
                 '--location "centraluseuap" '
                 '--sku "Balanced_B10" '
                 '--tags tag1="value1" '
                 '--no-database '
                 '--resource-group "{rg}"',
                 checks=checks)
    elif test.kwargs.get('geo-replication'):
        if cache_num == 1:
            test.cmd('az redisenterprise create '
                        '--cluster-name "{cluster31}" '
                        '--sku "Balanced_B10" '
                        '--location "centraluseuap" '
                        '--tags tag1="value1" '
                        '--no-database '
                        '--resource-group "{rg31}"',
                        checks=checks)
        elif cache_num == 2:
                test.cmd('az redisenterprise create '
                     '--location "centraluseuap" '
                     '--cluster-name "{cluster32}" '
                     '--sku "Balanced_B10" '
                     '--client-protocol "Encrypted" '
                     '--clustering-policy "EnterpriseCluster" '
                     '--eviction-policy "NoEviction" '
                     '--group-nickname "groupName" '
                     '--linked-databases id="/subscriptions/{subscription}/resourceGroups/{rg31}/providers/Microsoft.Cache/redisEnterprise/{cluster31}/databases/{database}" '
                     '--linked-databases id="/subscriptions/{subscription}/resourceGroups/{rg32}/providers/Microsoft.Cache/redisEnterprise/{cluster32}/databases/{database}" '
                     '--port 10000 '
                     '--resource-group "{rg32}"',
                checks=checks)
    elif test.kwargs.get('access-policy-assignment'):
        test.cmd('az redisenterprise create '
                 '--cluster-name "{cluster}" '
                 '--sku "Balanced_B10" '
                 '--location "centraluseuap" '
                 '--tags tag1="value1" '
                 '--resource-group "{rg}" '
                 '--high-availability "Disabled" '
                 '--minimum-tls-version "1.2" '
                 '--client-protocol "Encrypted" '
                 '--clustering-policy "EnterpriseCluster" '
                 '--eviction-policy "NoEviction"',
                 checks=checks)
    elif test.kwargs.get('access-key-authentication'):
        test.cmd('az redisenterprise create '
                 '--cluster-name "{cluster}" '
                 '--sku "Balanced_B10" '
                 '--location "centraluseuap" '
                 '--tags tag1="value1" '
                 '--access-keys-auth Disabled '
                 '--resource-group "{rg}" '
                 '--minimum-tls-version "1.2" '
                 '--client-protocol "Encrypted" '
                 '--clustering-policy "EnterpriseCluster" '
                 '--eviction-policy "NoEviction"',
                 checks=checks)
    elif test.kwargs.get('no-cluster-policy'):
        test.cmd('az redisenterprise create '
                 '--cluster-name "{cluster}" '
                 '--sku "Balanced_B10" '
                 '--location "centraluseuap" '
                 '--tags tag1="value1" '
                 '--minimum-tls-version "1.2" '
                 '--client-protocol "Encrypted" '
                 '--clustering-policy "NoCluster" '
                 '--eviction-policy "NoEviction" '
                 '--modules name="RedisBloom" '
                 '--modules name="RedisTimeSeries" '
                 '--modules name="RediSearch" '
                 '--port 10000 '
                 '--resource-group "{rg}"',
                 checks=checks)
    else:
        test.cmd('az redisenterprise create '
                 '--cluster-name "{cluster}" '
                 '--sku "Balanced_B10" '
                 '--location "centraluseuap" '
                 '--tags tag1="value1" '
                 #'--zones "1" "2" "3" '
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

def step_database_update(test, checks=None):
    if checks is None:
        checks = []
    if test.kwargs.get('access-key-authentication'):
        test.cmd('az redisenterprise database update '
                 '--cluster-name "{cluster}" '
                 '--access-keys-auth Enabled '
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
    elif test.kwargs.get('access-key-authentication'):
        test.cmd('az redisenterprise database create '
                 '--cluster-name "{cluster}" '
                 '--client-protocol "Plaintext" '
                 '--clustering-policy "OSSCluster" '
                 '--eviction-policy "AllKeysLRU" '
                 '--port 10000 '
                 '--access-keys-auth Disabled '
                 '--resource-group "{rg}"',
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
                 
def step_database_access_policy_assignment_create(test, checks=None):
    if checks is None:
        checks = []
    if test.kwargs.get('access-policy-assignment'):
        test.cmd('az redisenterprise database access-policy-assignment create '
                 '--cluster-name "{cluster}" '
                 '--access-policy-assignment-name defaultTestEntraApp1 '
                 '--access-policy-name default '
                 '--object-id 6497c918-11ad-41e7-1b0f-7c518a87d0b0 '
                 '--database-name "default" '
                 '--resource-group "{rg}"',
                 checks=checks)

def step_database_access_policy_assignment_list(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise database access-policy-assignment list '
             '--cluster-name "{cluster}" '
             '--database-name "default" '
             '--resource-group "{rg}"',
             checks=checks)

def step_database_access_policy_assignment_delete(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise database access-policy-assignment delete -y '
             '--cluster-name "{cluster}" '
             '--database-name "default" '
             '--resource-group "{rg}" '
             '--access-policy-assignment-name defaultTestEntraApp1',
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

def step_list_skus_for_scaling(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise list-skus-for-scaling '
             '--cluster-name "{cluster}" '
             '--resource-group "{rg}"',
             checks=checks)