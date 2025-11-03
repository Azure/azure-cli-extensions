# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from knack.help_files import helps


def get_deployment_template_help():
    """Load deployment template help content."""


helps['ml deployment-template'] = """
type: group
short-summary: Manage Azure ML deployment templates.
long-summary: |
    Deployment templates are reusable templates that define deployment configurations for Azure ML.
    They support registry-based operations only (not workspace-based) and provide a way to
    standardize and share deployment configurations across teams and projects.
"""

helps['ml deployment-template list'] = """
type: command
short-summary: List deployment templates in a registry.
long-summary: |
    List all deployment templates available in the specified registry. This command
    returns all templates along with their metadata including name, version, description, and tags.
examples:
  - name: List all deployment templates in a registry
    text: az ml deployment-template list --registry-name myregistry
  - name: List deployment templates with specific output format
    text: az ml deployment-template list --registry-name myregistry --output table
"""

helps['ml deployment-template get'] = """
type: command
short-summary: Get a specific deployment template by name and version.
long-summary: |
    Retrieve detailed information about a specific deployment template. If version is not
    specified, the latest version will be returned.
examples:
  - name: Get a specific version of a deployment template
    text: az ml deployment-template get --name my-template --version 1 --registry-name myregistry
"""

helps['ml deployment-template create'] = """
type: command
short-summary: Create a new deployment template from a YAML file.
long-summary: |
    Create a new deployment template using a YAML configuration file. The YAML file should
    contain the complete deployment template definition including endpoints, parameters, and metadata.
    You can override specific values using command-line parameters.
examples:
  - name: Create a deployment template from a YAML file
    text: az ml deployment-template create --file template.yml --registry-name myregistry
  - name: Create with name and version overrides
    text: az ml deployment-template create --file template.yml --name custom-template --version 2 --registry-name myregistry
  - name: Create without waiting for completion
    text: az ml deployment-template create --file template.yml --registry-name myregistry --no-wait
"""

helps['ml deployment-template update'] = """
type: command
short-summary: Update specific fields of an existing deployment template.
long-summary: |
    Update metadata fields (description and tags) of an existing deployment template without
    requiring a YAML file. This command follows Azure CLI conventions and only accepts specific
    field updates. Tags are merged with existing tags rather than replaced.

    For structural changes to the deployment template (endpoints, deployment configuration, etc.),
    use the 'create' command with a YAML file.
examples:
  - name: Update deployment template description
    text: az ml deployment-template update --name my-template --version 1 --registry-name myregistry --set "description=Updated description"
  - name: Update deployment template tags
    text: az ml deployment-template update --name my-template --version 1 --registry-name myregistry --set "tags=environment=production owner=ml-team"
  - name: Update both description and tags
    text: az ml deployment-template update --name my-template --version 1 --registry-name myregistry --set "description=Production template" --set "tags=status=active"
"""

helps['ml deployment-template archive'] = """
type: command
short-summary: Archive a deployment template.
long-summary: |
    Archive a deployment template to mark it as inactive. Archived templates are not
    returned in list operations by default. You can archive a specific version or all
    versions of a template.
examples:
  - name: Archive a specific version
    text: az ml deployment-template archive --name my-template --version 1 --registry-name myregistry
  - name: Archive without waiting for completion
    text: az ml deployment-template archive --name my-template --version 1 --registry-name myregistry --no-wait
"""

helps['ml deployment-template restore'] = """
type: command
short-summary: Restore an archived deployment template.
long-summary: |
    Restore a previously archived deployment template to make it active again. Restored
    templates will appear in list operations. You can restore a specific version or all
    versions of a template.
examples:
  - name: Restore a specific version
    text: az ml deployment-template restore --name my-template --version 1 --registry-name myregistry
  - name: Restore without waiting for completion
    text: az ml deployment-template restore --name my-template --version 1 --registry-name myregistry --no-wait
"""
