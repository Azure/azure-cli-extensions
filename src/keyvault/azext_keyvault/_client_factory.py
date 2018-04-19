# pylint: disable-all

# ---------------------------------------------------------------------------------
# The code for this extension file is pulled from the azure-cli repo
# and modified to run inside a cli extension.  Changes may cause incorrect behavior
# and will be lost if the code is regenerated. Please see the readme.md at the base
# of the keyvault extension for details.
# ---------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def keyvault_client_factory(cli_ctx, **_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_keyvault.mgmt.keyvault import KeyVaultManagementClient
    return get_mgmt_service_client(cli_ctx, KeyVaultManagementClient)


def keyvault_client_vaults_factory(cli_ctx, _):
    return keyvault_client_factory(cli_ctx).vaults


def keyvault_data_plane_factory(cli_ctx, _):
    from azext_keyvault.keyvault import KeyVaultClient, KeyVaultAuthentication

    def get_token(server, resource, scope):  # pylint: disable=unused-argument
        import adal
        from azure.cli.core._profile import Profile
        try:
            return Profile(cli_ctx=cli_ctx).get_login_credentials(resource)[0]._token_retriever()  # pylint: disable=protected-access
        except adal.AdalError as err:
            from knack.util import CLIError
            # pylint: disable=no-member
            if (hasattr(err, 'error_response') and
                    ('error_description' in err.error_response) and
                    ('AADSTS70008:' in err.error_response['error_description'])):
                raise CLIError(
                    "Credentials have expired due to inactivity. Please run 'az login'")
            raise CLIError(err)

    return KeyVaultClient(KeyVaultAuthentication(get_token))
