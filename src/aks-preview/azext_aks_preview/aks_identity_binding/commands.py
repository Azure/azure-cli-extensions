# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def _parse_allowed_subjects_from_file(allowed_subjects_from_file):
    """Load the --allowed-subjects-from-file payload into a list of AllowedSubject models.

    The file is expected to contain a JSON array where each element matches the AllowedSubject
    REST shape, e.g.:
        [
          {
            "namespaceSelector": {"matchLabels": ["kubernetes.io/metadata.name=team-a"]},
            "serviceAccountSelector": {"matchLabels": ["app=payments"]}
          }
        ]
    Note: 'matchLabels' is an array of "key=value" strings, matching the AKS API contract.
    """
    if allowed_subjects_from_file is None:
        return None

    from azure.cli.core.util import get_file_json
    from azure.cli.core.azclierror import InvalidArgumentValueError
    from azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.models import (
        AllowedSubject,
    )

    allowed_subjects = get_file_json(allowed_subjects_from_file)

    if not isinstance(allowed_subjects, list):
        raise InvalidArgumentValueError(
            "--allowed-subjects-from-file must contain a JSON array of subject objects."
        )

    result = []
    for index, subject in enumerate(allowed_subjects):
        if not isinstance(subject, dict):
            raise InvalidArgumentValueError(
                f"allowed subject at index {index} must be a JSON object."
            )
        if not subject.get("namespaceSelector"):
            raise InvalidArgumentValueError(
                f"allowed subject at index {index} is missing the required 'namespaceSelector'."
            )
        # AllowedSubject (a rest _Model) accepts a raw JSON mapping and validates field shapes.
        result.append(AllowedSubject(subject))

    return result


# `az aks identity-binding create` command
def aks_ib_cmd_create(
    cmd, client,  # pylint: disable=unused-argument
    resource_group_name: str,
    cluster_name: str,
    name: str,
    managed_identity_resource_id: str,
    allowed_subjects_from_file=None,
    no_wait: bool = False,
):
    from azure.cli.core.util import sdk_no_wait
    from azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.models import (
        IdentityBinding,
        IdentityBindingProperties,
        IdentityBindingManagedIdentityProfile,
    )

    instance = IdentityBinding(
        name=name,
        properties=IdentityBindingProperties(
            managed_identity=IdentityBindingManagedIdentityProfile(
                resource_id=managed_identity_resource_id,
            ),
            allowed_subjects=_parse_allowed_subjects_from_file(allowed_subjects_from_file),
        )
    )

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        cluster_name,
        name,
        instance,
    )


# `az aks identity-binding update` command
def aks_ib_cmd_update(
    cmd, client,  # pylint: disable=unused-argument
    resource_group_name: str,
    cluster_name: str,
    name: str,
    allowed_subjects_from_file: str,
    no_wait: bool = False,
):
    from azure.cli.core.util import sdk_no_wait

    instance = client.get(
        resource_group_name=resource_group_name,
        resource_name=cluster_name,
        identity_binding_name=name,
    )

    # allowed_subjects_from_file is required for update (enforced at argument
    # registration), so it is always provided here. It is the only mutable
    # field today; requiring it avoids a no-op full-PUT.
    instance.properties.allowed_subjects = _parse_allowed_subjects_from_file(
        allowed_subjects_from_file
    )

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        cluster_name,
        name,
        instance,
    )


# `az aks identity-binding delete` command
def aks_ib_cmd_delete(
    cmd, client,  # pylint: disable=unused-argument
    resource_group_name: str,
    cluster_name: str,
    name: str,
    no_wait: bool = False,
):
    from azure.cli.core.util import sdk_no_wait

    return sdk_no_wait(
        no_wait,
        client.begin_delete,
        resource_group_name=resource_group_name,
        resource_name=cluster_name,
        identity_binding_name=name,
    )


# `az aks identity-binding show` command
def aks_ib_cmd_show(
    cmd, client,  # pylint: disable=unused-argument
    resource_group_name: str,
    cluster_name: str,
    name: str,
):
    return client.get(
        resource_group_name=resource_group_name,
        resource_name=cluster_name,
        identity_binding_name=name,
    )


# `az aks identity-binding list` command
def aks_ib_cmd_list(
    cmd, client,  # pylint: disable=unused-argument
    resource_group_name: str,
    cluster_name: str,
):
    return client.list_by_managed_cluster(
        resource_group_name=resource_group_name,
        resource_name=cluster_name,
    )
