# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

import re
from azure.cli.core.util import user_confirmation
from knack.util import CLIError
from azure.core.serialization import NULL as AzureCoreNull
from azure.cli.command_modules.acr._utils import get_resource_group_name_by_registry_name, get_registry_by_name
from .vendored_sdks.containerregistry.v2025_09_01_preview.generated.container_registry_management_client.models._models import (
    CacheRule, CacheRuleProperties,
    CacheRuleUpdateParameters, CacheRuleUpdateProperties, ImportSource, ImportImageParameters,
    PlatformFilter, ArtifactTypeFilter, TagFilter, ArtifactSyncFilterProperties,
    IdentityProperties, UserIdentityProperties
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

def process_assign_identity_parameter(assign_identity: str) -> IdentityProperties:
    """   
    Process assign identity parameter and return IdentityProperties object.

    :param assign_identity: User-assigned managed identity resource ID
    :return: IdentityProperties object or None
    """

    if not assign_identity:
        return None
  
    if not is_valid_user_assigned_managed_identity_resource_id(assign_identity):
        raise CLIError(f"Invalid user-assigned managed identity resource ID: {assign_identity}")


    identity_properties = IdentityProperties(
        type="UserAssigned",
        user_assigned_identities={
            assign_identity: UserIdentityProperties()
        }
    )
    return identity_properties
    
def is_valid_user_assigned_managed_identity_resource_id(resource_id):
    # format Validation logic for user-assigned managed identity resource ID
    # include the full pattern of Microsoft.ManagedIdentity.
    # check GUID format for subscription ID
    # https://docs.microsoft.com/azure/azure-resource-manager/management/resource-name-rules#microsoftmanagedidentity
   pattern = (
        r"^/subscriptions/[0-9a-zA-Z\-]{36}"
        r"/resourceGroups/[^/]+"
        r"/providers/Microsoft\.ManagedIdentity/userAssignedIdentities/[^/]+$"
    ) 
   return bool(re.match(pattern, resource_id, re.IGNORECASE))

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
                     assign_identity=None,
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

    sync_str = sync if sync else None
    sync_referrers_str = "Enabled" if sync_referrers and sync_referrers.lower() == 'enabled' else "Disabled"

    # Validate sync_referrers requires activesync - check both when sync is provided and when it's not
    if sync_referrers and sync_referrers.lower() == 'enabled':
        if not sync or sync.lower() != 'activesync':
            raise CLIError("Syncing referrers requires sync to be set to 'activesync'. Please update your cache rule configuration.")

    if include_artifact_types and exclude_artifact_types:
        raise CLIError("You cannot specify both include_artifact_types and exclude_artifact_types. Please choose one.")

    if include_image_types and exclude_image_types:
        raise CLIError("You cannot specify both include_image_types and exclude_image_types. Please choose one.")

    #validate that filter parameters require sync to be enabled
    if sync and sync.lower() != 'activesync' and (include_artifact_types or exclude_artifact_types or 
                              include_image_types or exclude_image_types or 
                              platforms or starts_with or ends_with or contains):
        raise CLIError("Artifact sync filters (--include-artifact-types, --exclude-artifact-types, "
                        "--include-image-types, --exclude-image-types, --platforms, "
                        "--starts-with, --ends-with, --contains) require --sync activesync.")

    cred_set_id = AzureCoreNull if not cred_set else f'{registry.id}/credentialSets/{cred_set}'

    identity_properties = process_assign_identity_parameter(assign_identity)

    tag = None

    if ':' in source_repo:
        source_repo, tag = source_repo.rsplit(':', 1)

    #create artifact sync filters object
    artifact_sync_filters = None

    if sync and sync.lower() == 'activesync':
        artifact_sync_filters = {}

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
        sync_mode=sync_str,
        sync_referrers=sync_referrers_str,
    )

    if artifact_sync_filters:
        properties.artifact_sync_filters = artifact_sync_filters

    # Create cache rule with properties
    cache_rule = CacheRule(
        name=name,
        properties=properties,
        identity=identity_properties
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
                            assign_identity=None,
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

    #fetch existing cacheRule
    cache_rule = client.get(resource_group_name=rg,
                            registry_name=registry_name,
                            cache_rule_name=name)

    #extract existing properties
    properties = cache_rule.properties
    sync_mode = properties.sync_mode
    sync_referrers_status = properties.sync_referrers

    #check if activesync is enabled 
    #check both existing sync mode (when not changing sync) AND new sync value (when updating sync)
    isActiveSync = (sync is None and sync_mode and sync_mode.lower() == 'activesync') or (sync and sync.lower() == 'activesync')

    # Validate sync_referrers requires activesync
    if sync_referrers and sync_referrers.lower() == 'enabled' and not isActiveSync:
        raise CLIError("Syncing referrers requires sync to be set to 'activesync'. Please update your cache rule configuration.")

    # Warn if mutually exclusive parameters are provided
    if include_artifact_types and exclude_artifact_types:
        raise CLIError("You cannot specify both include_artifact_types and exclude_artifact_types. Please choose one.")
    if include_image_types and exclude_image_types:
        raise CLIError("You cannot specify both include_image_types and exclude_image_types. Please choose one.")
 
    # Initialize filter objects
    updated_tags = None
    updated_platforms = None
    updated_artifact_types = None
    updated_image_types = None

    #preserve old artifact sync filters
    preserve_filters = (properties.artifact_sync_filters is not None and isActiveSync)

    if preserve_filters:
        # Copy tag filters If no new filters are provided
        if properties.artifact_sync_filters.tags and not starts_with and not ends_with and not contains:
            updated_tags = properties.artifact_sync_filters.tags

        # Copy platform filters If no new platform filters are provided
        if properties.artifact_sync_filters.platforms and not platforms:
            updated_platforms = properties.artifact_sync_filters.platforms

        # Copy artifact types filters if no new artifact types filters are provided
        if properties.artifact_sync_filters.artifact_types and not include_artifact_types and not exclude_artifact_types:
            updated_artifact_types = properties.artifact_sync_filters.artifact_types

        # Copy image types filters if no new image types filters are provided
        if properties.artifact_sync_filters.image_types and not include_image_types and not exclude_image_types:
            updated_image_types = properties.artifact_sync_filters.image_types

    #Handle credential sets update
    cred_set_id = properties.credential_set_resource_id
    if remove_cred_set:
        cred_set_id = AzureCoreNull
    elif cred_set:
        cred_set_id = f'{registry.id}/credentialSets/{cred_set}'

    if cred_set is None and not remove_cred_set:
        cred_set_id = AzureCoreNull

    # Process identity parameter
    identity_properties = process_assign_identity_parameter(assign_identity)

    # Handle artifact sync status - only change if explicitly provided
    if sync is not None:
        sync_mode = "ActiveSync" if sync.lower() == 'activesync' else "PassiveSync"

    if sync_referrers is not None:
        sync_referrers_status = "Enabled" if sync_referrers and sync_referrers.lower() == 'enabled' else "Disabled"

    #update artifact sync filters object
    updated_artifact_sync_filters = None
    if isActiveSync:
        if starts_with or ends_with or contains:
            updated_tags = TagFilter(
                type="KQL",
                query=_create_kql(starts_with, ends_with, contains)
            )

        if platforms:
            platform_list = platforms if isinstance(platforms, list) else platforms.split(',')
            updated_platforms = PlatformFilter(
                type="array",
                values=platform_list
            )

        if include_artifact_types:
            include_artifact_list = include_artifact_types if isinstance(include_artifact_types, list) else include_artifact_types.split(',')
            updated_artifact_types = ArtifactTypeFilter(
                type="include",
                values=include_artifact_list
            )
        elif exclude_artifact_types:
            exclude_artifact_list = exclude_artifact_types if isinstance(exclude_artifact_types, list) else exclude_artifact_types.split(',')
            updated_artifact_types = ArtifactTypeFilter(
                type="exclude",
                values=exclude_artifact_list
            )

        if include_image_types:
            include_image_list = include_image_types if isinstance(include_image_types, list) else include_image_types.split(',')
            updated_image_types = ArtifactTypeFilter(
                type="include",
                values=include_image_list
            )
        elif exclude_image_types:
            exclude_image_list = exclude_image_types if isinstance(exclude_image_types, list) else exclude_image_types.split(',')
            updated_image_types = ArtifactTypeFilter(
                type="exclude",
                values=exclude_image_list
            )

    #create artifactSyncFilterProperties object if any filter is set
    updated_artifact_sync_filters = ArtifactSyncFilterProperties(
        tags=updated_tags,
        platforms=updated_platforms,
        artifact_types=updated_artifact_types,
        image_types=updated_image_types
    )

    #create updated cache rule properties
    updated_properties = CacheRuleUpdateProperties(
        credential_set_resource_id= cred_set_id,
        sync_mode= sync_mode,
        sync_referrers=sync_referrers_status,
        artifact_sync_filters=updated_artifact_sync_filters
    )

    if isActiveSync:
        user_confirmation("Your cache rule has Artifact Sync enabled and will automatically import tags into your registry. This may incur additional storage charges. Continue?", yes)

    if remove_cred_set:
        return client.begin_create(resource_group_name=rg,
                                   registry_name=registry_name,
                                   cache_rule_name=name,
                                   cache_rule_create_parameters=CacheRuleUpdateParameters(
                                        properties=updated_properties,
                                        identity=identity_properties))

    return client.begin_update(resource_group_name=rg,
                               registry_name=registry_name,
                               cache_rule_name=name,
                               cache_rule_update_parameters=CacheRuleUpdateParameters(
                                    properties=updated_properties,
                                    identity=identity_properties))


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
                         
