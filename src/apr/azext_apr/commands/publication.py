# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from azure.cli.core.commands.parameters import resource_group_name_type
from knack.help_files import helps

from azext_apr.server import DataPlaneClient, list_all, resolve_id_or_name, wait_for_task

helps["apr publication"] = """
type: group
short-summary: View and delete publications.
"""

helps["apr publication list"] = """
type: command
short-summary: List publications.
examples:
  - name: List all publications in a registry.
    text: az apr publication list -g myrg -r myregistry
  - name: List publications for a given repository.
    text: az apr publication list -g myrg -r myregistry --repository myrepo
"""

helps["apr publication show"] = """
type: command
short-summary: Show details for a publication.
examples:
  - name: Show a publication by id.
    text: az apr publication show -g myrg -r myregistry --id mypublicationid
"""

helps["apr publication delete"] = """
type: command
short-summary: Delete a publication.
examples:
  - name: Delete a publication by id.
    text: az apr publication delete -g myrg -r myregistry --id mypublicationid
"""


def register_commands(loader):
    publication_type = CliCommandType(operations_tmpl="azext_apr.commands.publication#{}")
    with loader.command_group(
        "apr publication", custom_command_type=publication_type, is_preview=True
    ) as g:
        g.custom_command("list", "list_publications")
        g.custom_show_command("show", "show_publication")
        g.custom_command("delete", "delete_publication", confirmation=True, supports_no_wait=True)


def load_arguments(loader, _command):
    with loader.argument_context("apr publication") as c:
        c.argument("resource_group_name", resource_group_name_type)
        c.argument(
            "registry_name",
            options_list=["--registry", "-r"],
            help="Name of the parent APR registry.",
        )
        # Publications have no name; they're referenced by id.
        c.argument("publication_id", options_list=["--id"], help="Publication id.")

    with loader.argument_context("apr publication list") as c:
        c.ignore("publication_id")
        c.argument(
            "repository",
            options_list=["--repository"],
            help="Filter publications by repository (Name or ID).",
        )
        c.argument(
            "limit",
            type=int,
            help="Max number of publications to return. Omit to return all.",
        )


def _client(cmd, registry_name, resource_group_name):
    return DataPlaneClient.for_registry(cmd, registry_name, resource_group_name)


def list_publications(cmd, registry_name, repository=None, resource_group_name=None, limit=None):
    client = _client(cmd, registry_name, resource_group_name)
    params = None
    if repository:
        params = {"repository": resolve_id_or_name(client, "repositories", repository)}
    return list_all(client, "/publications/", max_items=limit, params=params)


def show_publication(cmd, registry_name, publication_id, resource_group_name=None):
    client = _client(cmd, registry_name, resource_group_name)
    return client.get(f"/publications/{publication_id}/").json()


def delete_publication(cmd, registry_name, publication_id, resource_group_name=None, no_wait=False):
    client = _client(cmd, registry_name, resource_group_name)
    resp = client.delete(f"/publications/{publication_id}/")
    return wait_for_task(client, resp, no_wait)
