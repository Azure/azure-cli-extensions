# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long


from azure.cli.core.util import user_confirmation
from azure.core.serialization import NULL as AzureCoreNull
from azure.cli.command_modules.acr._utils import get_resource_group_name_by_registry_name, get_registry_by_name
from .vendored_sdks.containerregistry.v2023_11_01_preview.models._models_py3 import CacheRule, ArtifactSyncScopeFilterProperties, CacheRuleUpdateParameters, ImportSource, ImportImageParameters


def _create_kql(starts_with=None, ends_with=None, contains=None):
    if not starts_with and not ends_with and not contains:
        return "Tags"

    query = "Tags | where "

    if starts_with:
        query += f"Name startswith '{starts_with}'"
        if ends_with or contains:
            query += " and "
    if ends_with:
        query += f"Name endswith '{ends_with}'"
        if contains:
            query += " and "
    if contains:
        query += f"Name contains '{contains}'"

    return query


def _separate_params(query):
    starts_with = None
    ends_with = None
    contains = None

    if "Name startswith" in query:
        starts_with = query.split("Name startswith")[1].split("'")[1]

    if "Name endswith" in query:
        ends_with = query.split("Name endswith")[1].split("'")[1]

    if "Name contains" in query:
        contains = query.split("Name contains")[1].split("'")[1]

    return starts_with, ends_with, contains


def acr_cache_show(cmd,
                   client,
                   registry_name,
                   name,
                   resource_group_name=None):

    rg = get_resource_group_name_by_registry_name(cmd.cli_ctx, registry_name, resource_group_name)

    return client.get(resource_group_name=rg,
                      registry_name=registry_name,
                      cache_rule_name=name)


def acr_cache_list(cmd,
                   client,
                   registry_name,
                   resource_group_name=None):

    rg = get_resource_group_name_by_registry_name(cmd.cli_ctx, registry_name, resource_group_name)

    return client.list(resource_group_name=rg,
                       registry_name=registry_name)


def acr_cache_delete(cmd,
                     client,
                     registry_name,
                     name,
                     resource_group_name=None):

    rg = get_resource_group_name_by_registry_name(cmd.cli_ctx, registry_name, resource_group_name)

    return client.begin_delete(resource_group_name=rg,
                               registry_name=registry_name,
                               cache_rule_name=name)


def acr_cache_create(cmd,
                     client,
                     registry_name,
                     name,
                     source_repo,
                     target_repo,
                     resource_group_name=None,
                     cred_set=None,
                     sync=False,
                     starts_with=None,
                     ends_with=None,
                     contains=None,
                     dry_run=False,
                     yes=False):

    registry, rg = get_registry_by_name(cmd.cli_ctx, registry_name, resource_group_name)

    sync_str = "Active" if sync else "Inactive"
    cred_set_id = AzureCoreNull if not cred_set else f'{registry.id}/credentialSets/{cred_set}'
    tag = None
    if ':' in source_repo:
        tag = source_repo.split(':')[1]
        source_repo = source_repo.split(':')[0]

    kql_str = f"Tags | Where Name == {tag}" if tag is not None else _create_kql(starts_with, ends_with, contains)

    CacheRuleCreateParameters = CacheRule
    cache_rule_create_params = CacheRuleCreateParameters()
    cache_rule_create_params.name = name
    cache_rule_create_params.source_repository = source_repo
    cache_rule_create_params.target_repository = target_repo
    cache_rule_create_params.credential_set_resource_id = cred_set_id
    cache_rule_create_params.artifact_sync_status = sync_str
    cache_rule_create_params.artifact_sync_scope_filter_properties = ArtifactSyncScopeFilterProperties(type="KQL", query=kql_str)

    if tag is None and sync and not dry_run:
        user_confirmation("Your cache rule has Artifact Sync enabled and will automatically import tags into your registry. This may incur additional storage charges. Run with the dry-run flag for details. Continue?", yes)

    return client.begin_create(resource_group_name=rg,
                               registry_name=registry_name,
                               cache_rule_name=name,
                               cache_rule_create_parameters=cache_rule_create_params,
                               dry_run=dry_run)


def acr_cache_update_custom(cmd,
                            client,
                            registry_name,
                            name,
                            resource_group_name=None,
                            cred_set=None,
                            remove_cred_set=False,
                            sync=None,
                            starts_with=None,
                            ends_with=None,
                            contains=None,
                            yes=False):

    instance = CacheRuleUpdateParameters()
    registry, rg = get_registry_by_name(cmd.cli_ctx, registry_name, resource_group_name)

    if remove_cred_set:
        instance = client.get(resource_group_name=rg,
                              registry_name=registry_name,
                              cache_rule_name=name)

    cred_set_id = AzureCoreNull if remove_cred_set else f'{registry.id}/credentialSets/{cred_set}'

    if remove_cred_set or cred_set:
        instance.credential_set_resource_id = cred_set_id

    if sync is not None:
        instance.artifact_sync_status = "Active" if sync else "Inactive"

    if starts_with or ends_with or contains:
        instance.artifact_sync_scope_filter_properties = ArtifactSyncScopeFilterProperties(type="KQL", query=_create_kql(starts_with, ends_with, contains))

    if sync:
        user_confirmation("Your cache rule has Artifact Sync enabled and will automatically import tags into your registry. This may incur additional storage charges. Continue?", yes)


    if remove_cred_set:
        return client.begin_create(resource_group_name=rg,
                                   registry_name=registry_name,
                                   cache_rule_name=name,
                                   cache_rule_create_parameters=instance)

    return client.begin_update(resource_group_name=rg,
                               registry_name=registry_name,
                               cache_rule_name=name,
                               cache_rule_update_parameters=instance)


def acr_cache_sync(cmd,
                   client,
                   registry_name,
                   name,
                   image,
                   resource_group_name=None):

    rg = get_resource_group_name_by_registry_name(cmd.cli_ctx, registry_name, resource_group_name)

    rule = client.cache_rules.get(resource_group_name=rg,
                                  registry_name=registry_name,
                                  cache_rule_name=name)
    tag = image
    rule_id = rule.id
    source_repo = rule.source_repository
    target_repo = rule.target_repository
    source_image_str = source_repo[source_repo.find('/') + 1:] + ":" + tag

    import_source = ImportSource(source_image=source_image_str,
                                 cache_rule_resource_id=rule_id)

    params = ImportImageParameters(source=import_source,
                                   mode="NoForce",
                                   target_tags=[target_repo + ":" + tag])

    return client.registries.begin_import_image(resource_group_name=rg,
                                                registry_name=registry_name,
                                                parameters=params)
