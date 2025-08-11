# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.util import user_confirmation
from knack.util import CLIError
from azure.core.serialization import NULL as AzureCoreNull
from azure.cli.command_modules.acr._utils import get_resource_group_name_by_registry_name, get_registry_by_name
from .vendored_sdks.containerregistry.v2025_07_01_preview.generated.container_registry_management_client.models._models import (
    CacheRule, CacheRuleProperties,
    CacheRuleUpdateParameters, CacheRuleUpdateProperties, ImportSource, ImportImageParameters,
    PlatformFilter, ArtifactTypeFilter, TagFilter
)

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
                     yes=False,
                     platforms=None,
                     sync_referrers=False,
                     include_artifact_types=None,
                     exclude_artifact_types=None,
                     include_image_types=None,
                     exclude_image_types=None
                     ):

    registry, _ = get_registry_by_name(cmd.cli_ctx, registry_name, resource_group_name)

    #extract resource group from registry id
    if resource_group_name:
        rg = resource_group_name
    else:
        #extract resource group from registry id
        import re
        match = re.search(r'/resourceGroups/([^/]+)/', registry.id)
        rg = match.group(1) if match else None

    if not rg:
        raise CLIError("Resource group could not be determined. Please provide a valid resource group name.")

    sync_str = "Enable" if sync == 'enable' else "Disable"
    sync_referrers_str = "Enable" if sync_referrers == 'enable' else "Disable"

    if sync_referrers and not sync:
        raise CLIError("The --sync-referrers parameter requires the --sync parameter to be enabled. Please enable sync to use this feature.")

    if include_artifact_types and exclude_artifact_types:
        raise CLIError("You cannot specify both include_artifact_types and exclude_artifact_types. Please choose one.")

    if include_image_types and exclude_image_types:
        raise CLIError("You cannot specify both include_image_types and exclude_image_types. Please choose one.")

    cred_set_id = AzureCoreNull if not cred_set else f'{registry.id}/credentialSets/{cred_set}'
    tag = None

    if ':' in source_repo:
        source_repo, tag = source_repo.rsplit(':', 1)

    #create artifact sync filters object
    artifact_sync_filters = {}

    if sync == 'enable':
        if platforms:
            platform_list = platforms if isinstance(platforms, list) else platforms.split(',')
            artifact_sync_filters['platforms'] = PlatformFilter(
                type="array",
                values=platform_list
            )

        if include_artifact_types:
            include_artifact_list = include_artifact_types if isinstance(include_artifact_types, list) else include_artifact_types.split(',')
            artifact_sync_filters["artifactTypes"] = ArtifactTypeFilter(
                type="include",
                values=include_artifact_list
            )
        elif exclude_artifact_types:
            exclude_artifact_list = exclude_artifact_types if isinstance(exclude_artifact_types, list) else exclude_artifact_types.split(',')
            artifact_sync_filters["artifactTypes"] = ArtifactTypeFilter(
                type="exclude",
                values=exclude_artifact_list
            )

        if include_image_types:
            include_image_list = include_image_types if isinstance(include_image_types, list) else include_image_types.split(',')
            artifact_sync_filters["imageTypes"] = ArtifactTypeFilter(
                type="include",
                values=include_image_list
            )
        elif exclude_image_types:
            exclude_image_list = exclude_image_types if isinstance(exclude_image_types, list) else exclude_image_types.split(',')
            artifact_sync_filters["imageTypes"] = ArtifactTypeFilter(
                type="exclude",
                values=exclude_image_list
            )

        kql_str = f"Tags | where Name == '{tag}'" if tag is not None else _create_kql(starts_with, ends_with, contains)
        if sync and not kql_str:
            kql_str = "Tags"

        artifact_sync_filters["tags"] = TagFilter(
            type="KQL",
            query=kql_str
        )

    #create cacheRuleProperties object
    properties = CacheRuleProperties(
        credential_set_resource_id=cred_set_id,
        source_repository=source_repo,
        target_repository=target_repo,
        artifact_sync_status=sync_str,
        sync_referrers=sync_referrers_str,
    )

    if artifact_sync_filters:
        properties.artifact_sync_filters = artifact_sync_filters

    # Create cache rule with properties
    cache_rule = CacheRule(
        name=name,
        properties=properties
    )

    if tag is None and sync and not dry_run:
        user_confirmation("Your cache rule has Artifact Sync enabled and will automatically import tags into your registry. This may incur additional storage charges. Run with the dry-run flag for details. Continue?", yes)

    return client.begin_create(
        resource_group_name=rg,
        registry_name=registry_name,
        cache_rule_name=name,
        cache_rule_create_parameters=cache_rule,
    )


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
                            yes=False,
                            platforms=None,
                            sync_referrers=None,
                            include_artifact_types=None,
                            exclude_artifact_types=None,
                            include_image_types=None,
                            exclude_image_types=None
                            ):

    registry, rg = get_registry_by_name(cmd.cli_ctx, registry_name, resource_group_name)

    # Warn if mutually exclusive parameters are provided
    if sync_referrers and not sync:
        raise CLIError("The --sync-referrers parameter requires the --sync parameter to be enabled. Please enable sync to use this feature.")
    if include_artifact_types and exclude_artifact_types:
        raise CLIError("You cannot specify both include_artifact_types and exclude_artifact_types. Please choose one.")
    if include_image_types and exclude_image_types:
        raise CLIError("You cannot specify both include_image_types and exclude_image_types. Please choose one.")

    #fetch existing cacheRule
    cache_rule = client.get(resource_group_name=rg,
                            registry_name=registry_name,
                            cache_rule_name=name)

    #extract existing properties
    properties = cache_rule.properties
    artifact_sync_status = properties.artifact_sync_status
    sync_referrers_status = properties.sync_referrers

    #create updated artifact sync filters object
    updated_artifact_sync_filters = {}

    #preserve old artifact sync filters
    preserve_filters = (properties.artifact_sync_filters is not None and
                        (sync == 'enable' or sync is None))

    if preserve_filters:
        # Copy tag filters If no new filters are provided
        if properties.artifact_sync_filters.tags and not starts_with and not ends_with and not contains:
            updated_artifact_sync_filters["tags"] = properties.artifact_sync_filters.tags

        # Copy platform filters If no new platform filters are provided
        if properties.artifact_sync_filters.platforms and not platforms:
            updated_artifact_sync_filters["platforms"] = properties.artifact_sync_filters.platforms

        # Copy artifact types filters if no new artifact types filters are provided
        if properties.artifact_sync_filters.artifact_types and not include_artifact_types and not exclude_artifact_types:
            updated_artifact_sync_filters["artifact_types"] = properties.artifact_sync_filters.artifact_types

        # Copy image types filters if no new image types filters are provided
        if properties.artifact_sync_filters.image_types and not include_image_types and not exclude_image_types:
            updated_artifact_sync_filters["image_types"] = properties.artifact_sync_filters.image_types

    #Handle credential sets update
    cred_set_id = properties.credential_set_resource_id
    if remove_cred_set:
        cred_set_id = AzureCoreNull
    elif cred_set:
        cred_set_id = f'{registry.id}/credentialSets/{cred_set}'

    if cred_set is None and not remove_cred_set:
        cred_set_id = AzureCoreNull

    # Handle artifact sync status
    if sync is not None:
        artifact_sync_status = "Enable" if sync == 'enable' else "Disable"
        # clear filters if sync is disabled
        if sync == 'disable':
            updated_artifact_sync_filters = {}

    if sync_referrers is not None:
        sync_referrers_status = "Enable" if sync_referrers == 'enable' else "Disable"

    #update artifact sync filters object
    if sync == 'enable':
        if starts_with or ends_with or contains:
            updated_artifact_sync_filters["tags"] = TagFilter(
                type="KQL",
                query=_create_kql(starts_with, ends_with, contains)
            )

        if platforms:
            platform_list = platforms if isinstance(platforms, list) else platforms.split(',')
            updated_artifact_sync_filters["platforms"] = PlatformFilter(
                type="array",
                values=platform_list
            )

        if include_artifact_types:
            include_artifact_list = include_artifact_types if isinstance(include_artifact_types, list) else include_artifact_types.split(',')
            updated_artifact_sync_filters["artifact_types"] = ArtifactTypeFilter(
                type="include",
                values=include_artifact_list
            )
        elif exclude_artifact_types:
            exclude_artifact_list = exclude_artifact_types if isinstance(exclude_artifact_types, list) else exclude_artifact_types.split(',')
            updated_artifact_sync_filters["artifact_types"] = ArtifactTypeFilter(
                type="exclude",
                values=exclude_artifact_list
            )

        if include_image_types:
            include_image_list = include_image_types if isinstance(include_image_types, list) else include_image_types.split(',')
            updated_artifact_sync_filters["image_types"] = ArtifactTypeFilter(
                type="include",
                values=include_image_list
            )
        elif exclude_image_types:
            exclude_image_list = exclude_image_types if isinstance(exclude_image_types, list) else exclude_image_types.split(',')
            updated_artifact_sync_filters["image_types"] = ArtifactTypeFilter(
                type="exclude",
                values=exclude_image_list
            )

    #create updated cache rule properties
    updated_properties = CacheRuleUpdateProperties(
        credential_set_resource_id= cred_set_id,
        artifact_sync_status= artifact_sync_status,
        sync_referrers=sync_referrers_status,
        artifact_sync_filters=updated_artifact_sync_filters
    )

    if sync == 'enable':
        user_confirmation("Your cache rule has Artifact Sync enabled and will automatically import tags into your registry. This may incur additional storage charges. Continue?", yes)


    if remove_cred_set:
        return client.begin_create(resource_group_name=rg,
                                   registry_name=registry_name,
                                   cache_rule_name=name,
                                   cache_rule_create_parameters=CacheRuleUpdateParameters(properties=updated_properties))

    return client.begin_update(resource_group_name=rg,
                               registry_name=registry_name,
                               cache_rule_name=name,
                               cache_rule_update_parameters=CacheRuleUpdateParameters(properties=updated_properties))


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
                                   # import tag with force to override existing tags
                                   mode="Force",
                                   target_tags=[target_repo + ":" + tag])

    return client.registries.begin_import_image(resource_group_name=rg,
                                                registry_name=registry_name,
                                                parameters=params)
                         
