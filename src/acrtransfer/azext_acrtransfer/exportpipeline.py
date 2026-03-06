# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.azclierror import ResourceNotFoundError
from knack.log import get_logger
from .vendored_sdks.containerregistry.v2025_06_01_preview.models._models_py3 import ExportPipeline, ExportPipelineTargetProperties
from .vendored_sdks.containerregistry.v2025_06_01_preview.models._container_registry_management_client_enums import PipelineSourceType
from .utility_functions import create_identity_properties

logger = get_logger(__name__)


def _extract_storage_account_resource_id(subscription_id, resource_group_name, container_uri):
    """Extract storage account resource ID from container URI.
    Expected format: https://<storage-account-name>.blob.core.windows.net/<container-name>
    """
    try:
        # Parse the URI to get storage account name
        from urllib.parse import urlparse
        parsed = urlparse(container_uri)
        storage_account_name = parsed.hostname.split('.')[0]
        return f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Storage/storageAccounts/{storage_account_name}"
    except Exception:
        return "<storage-account-resource-id>"


def _extract_keyvault_resource_id(subscription_id, resource_group_name, keyvault_secret_uri):
    """Extract key vault resource ID from secret URI.
    Expected format: https://<keyvault-name>.vault.azure.net/secrets/<secret-name>
    """
    try:
        from urllib.parse import urlparse
        parsed = urlparse(keyvault_secret_uri)
        keyvault_name = parsed.hostname.split('.')[0]
        return f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.KeyVault/vaults/{keyvault_name}"
    except Exception:
        return "<key-vault-resource-id>"


def _display_permission_guidance(pipeline_type, storage_access_mode, principal_id, subscription_id, resource_group_name, container_uri, keyvault_secret_uri=None):
    """Display permission guidance for the managed identity."""
    storage_resource_id = _extract_storage_account_resource_id(subscription_id, resource_group_name, container_uri)
    
    if storage_access_mode == 'ManagedIdentity':
        # For export pipeline, need write access (Contributor)
        # For import pipeline, need read access (Reader)
        role = "Storage Blob Data Contributor" if pipeline_type == "export" else "Storage Blob Data Reader"
        
        logger.warning("")
        logger.warning("Please ensure that the Managed Identity of the pipeline (Object ID: %s) has the necessary permissions to access the Storage Account Blob Container.", principal_id)
        logger.warning("Please run:")
        logger.warning("  az role assignment create --assignee \"%s\" --role \"%s\" --scope \"%s\"", principal_id, role, storage_resource_id)
        logger.warning("Note: If the Storage Account is in a different resource group, update the --scope parameter accordingly.")
        logger.warning("")
    elif storage_access_mode == 'SasToken' and keyvault_secret_uri:
        keyvault_resource_id = _extract_keyvault_resource_id(subscription_id, resource_group_name, keyvault_secret_uri)
        
        logger.warning("")
        logger.warning("Please ensure that the Managed Identity of the pipeline (Object ID: %s) has the necessary permissions to access the Key Vault Secret containing the Storage Account SAS Key.", principal_id)
        logger.warning("Please run:")
        logger.warning("  az role assignment create --assignee \"%s\" --role \"Key Vault Secrets User\" --scope \"%s\"", principal_id, keyvault_resource_id)
        logger.warning("Note: If the Key Vault is in a different resource group, update the --scope parameter accordingly.")
        logger.warning("")


def create_exportpipeline(client, resource_group_name, registry_name, export_pipeline_name, storage_account_container_uri, storage_access_mode, keyvault_secret_uri=None, options=None, user_assigned_identity_resource_id=None):
    '''Create an export pipeline.'''

    storage_account_container_uri = storage_account_container_uri.lower()
    if keyvault_secret_uri:
        keyvault_secret_uri = keyvault_secret_uri.lower()

    export_pipeline_target_type = PipelineSourceType.AZURE_STORAGE_BLOB_CONTAINER
    export_pipeline_target_properties = ExportPipelineTargetProperties(storage_access_mode=storage_access_mode,
                                                                       key_vault_uri=keyvault_secret_uri,
                                                                       uri=storage_account_container_uri,
                                                                       type=export_pipeline_target_type)

    identity_properties = create_identity_properties(user_assigned_identity_resource_id)
    export_pipeline = ExportPipeline(identity=identity_properties,
                                     target=export_pipeline_target_properties,
                                     options=options)

    client.export_pipelines.begin_create(resource_group_name=resource_group_name,
                                         registry_name=registry_name,
                                         export_pipeline_name=export_pipeline_name,
                                         export_pipeline_create_parameters=export_pipeline)

    result = client.export_pipelines.get(resource_group_name=resource_group_name,
                                        registry_name=registry_name,
                                        export_pipeline_name=export_pipeline_name)
    
    # Display permission guidance
    if result.identity:
        principal_id = None
        # For system-assigned identity, principal_id is at the top level
        if result.identity.principal_id:
            principal_id = result.identity.principal_id
        # For user-assigned identity, extract principal_id from userAssignedIdentities
        elif result.identity.user_assigned_identities:
            # Get the first (and typically only) user-assigned identity
            for identity_resource_id, identity_info in result.identity.user_assigned_identities.items():
                if identity_info and identity_info.principal_id:
                    principal_id = identity_info.principal_id
                    break
        
        if principal_id:
            from azure.cli.core.commands.client_factory import get_subscription_id
            from azure.cli.core import get_default_cli
            subscription_id = get_subscription_id(get_default_cli())
            _display_permission_guidance(
                pipeline_type="export",
                storage_access_mode=storage_access_mode,
                principal_id=principal_id,
                subscription_id=subscription_id,
                resource_group_name=resource_group_name,
                container_uri=storage_account_container_uri,
                keyvault_secret_uri=keyvault_secret_uri
            )
    
    return result


def get_exportpipeline(client, resource_group_name, registry_name, export_pipeline_name):
    '''Get an export pipeline.'''

    return client.export_pipelines.get(resource_group_name=resource_group_name,
                                       registry_name=registry_name,
                                       export_pipeline_name=export_pipeline_name)


def delete_exportpipeline(client, resource_group_name, registry_name, export_pipeline_name):
    '''Delete an export pipeline.'''

    try:
        client.export_pipelines.get(resource_group_name=resource_group_name,
                                    registry_name=registry_name,
                                    export_pipeline_name=export_pipeline_name)

    except Exception as e:
        raise ResourceNotFoundError(f'Export pipeline {export_pipeline_name} not found on registry {registry_name} in the {resource_group_name} resource group.') from e

    return client.export_pipelines.begin_delete(resource_group_name=resource_group_name,
                                                registry_name=registry_name,
                                                export_pipeline_name=export_pipeline_name)


def list_exportpipeline(client, resource_group_name, registry_name):
    '''List export pipelines on a registry.'''

    return client.export_pipelines.list(resource_group_name=resource_group_name, registry_name=registry_name)
