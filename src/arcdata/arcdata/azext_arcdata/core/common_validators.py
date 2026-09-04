# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azure.cli.core.azclierror import ArgumentUsageError


def validate_mutually_exclusive_arm_kubernetes(
    namespace, kubernetes_only, arm_only
):
    # -- ARM path  --
    if not namespace.use_k8s:
        required_for_arm = []  # assert [Required]

        if not namespace.resource_group:
            required_for_arm.append("--resource-group/-g")

        if not namespace.custom_location:
            required_for_arm.append("--custom-location")

        # -- backwards compatibility (w/o --cluster-name) --
        if not namespace.cluster_name and not namespace.location:
            raise ArgumentUsageError(
                "The following arguments are required: '--location' when "
                "'--cluster-name' is not provided."
            )

        if required_for_arm:
            msg = (
                "The following arguments are required: {missing} when "
                "'--use-k8s' is not provided."
            )
            raise ArgumentUsageError(
                msg.format(missing=", ".join(required_for_arm))
            )

        # -- assert only non arm args are provided --
        for arg in namespace.__dict__:
            value = namespace.__dict__[arg]
            if arg in kubernetes_only and value:
                arg = "--{}".format(arg.replace("_", "-"))
                msg = (
                    f"The following arguments are not permitted without "
                    f"the '--use-k8s' argument: {arg}"
                )
                raise ArgumentUsageError(msg)

    # -- kubernetes path --
    if namespace.use_k8s:
        required_for_kubernetes = []  # assert [Required]
        if not namespace.namespace:
            required_for_kubernetes.append("--k8s-namespace/-k")

        if not namespace.location:
            required_for_kubernetes.append("--location/l")

        if required_for_kubernetes:
            msg = (
                "The following arguments are required with '--use-k8s': "
                "{missing}"
            )
            raise ArgumentUsageError(
                msg.format(missing=", ".join(required_for_kubernetes))
            )
        not_permitted = []
        for arg in namespace.__dict__:
            value = namespace.__dict__[arg]
            if arg in arm_only and value:
                not_permitted.append("--{}".format(arg.replace("_", "-")))

        if not_permitted:
            msg = (
                f"The following arguments are not permitted with the "
                f"'--use-k8s' argument: {', '.join(not_permitted)}"
            )
            raise ArgumentUsageError(msg)


def validate_mutually_exclusive_direct_indirect(
    namespace, required_direct=None, direct_only=None, ignore_direct=None
):
    """
    Common direct/indirect argument validations that can be applied across
    different command groups.

    :param namespace: The argument namespace map.
    :param required_direct: Optional required arguments for direct mode.
    :param direct_only: Optional direct mode only arguments.
    :raises ValueError
    """

    # -- mutually exclusive --
    _validate_indirect_mode_args(namespace, direct_only, ignore_direct)

    if not namespace.use_k8s and namespace.namespace:
        raise ValueError(
            "Cannot specify' --k8s-namespace/-k ' without '--use-k8s'. "
            "The '--k8s-namespace/-k' is only available for commands using the Kubernetes API."
        )

    # -- direct --
    _validate_direct_mode_args(namespace, required_direct)

    # Check the forbidden flags
    #
    forbidden_list = {}
    if hasattr(namespace, "noexternal_endpoint"):
        forbidden_list["--no-external-endpoint"] = namespace.noexternal_endpoint
    if hasattr(namespace, "certificate_public_key_file"):
        forbidden_list["--cert-public-key-file"] = (
            namespace.certificate_public_key_file
        )
    if hasattr(namespace, "certificate_private_key_file"):
        forbidden_list["--cert-private-key-file"] = (
            namespace.certificate_private_key_file
        )
    if hasattr(namespace, "service_certificate_secret"):
        forbidden_list["--service-cert-secret"] = (
            namespace.service_certificate_secret
        )
    if hasattr(namespace, "admin_login_secret"):
        forbidden_list["--admin-login-secret"] = namespace.admin_login_secret
    if hasattr(namespace, "labels"):
        forbidden_list["--labels"] = namespace.labels
    if hasattr(namespace, "annotation"):
        forbidden_list["--annotations"] = namespace.annotations
    if hasattr(namespace, "service_labels"):
        forbidden_list["--service-labels"] = namespace.service_labels
    if hasattr(namespace, "service_annotations"):
        forbidden_list["--service-annotations"] = namespace.service_annotations
    if hasattr(namespace, "collation"):
        forbidden_list["--collation"] = namespace.collation
    if hasattr(namespace, "language"):
        forbidden_list["--language"] = namespace.language
    if hasattr(namespace, "agent_enabled"):
        forbidden_list["--agent-enabled"] = namespace.agent_enabled

    direct_mode_forbid_list = []
    for flag in forbidden_list:
        if forbidden_list[flag]:
            direct_mode_forbid_list.append(flag)

    if not namespace.use_k8s and direct_mode_forbid_list:
        raise ValueError(
            "Cannot specify {0} without '--use-k8s'. "
            "The {0} is only available for commands using the Kubernetes API.".format(
                direct_mode_forbid_list
            )
        )


def _validate_indirect_mode_args(namespace, direct_only, ignore_direct):
    if namespace.use_k8s:
        ignore_direct = ignore_direct or []
        msg = "Cannot specify '--use-k8s' with the following ARM-targeted arguments: {args}."
        included = direct_only or []

        if (
            namespace.resource_group
            and "--resource-group/-g" not in ignore_direct
        ):
            included.append("--resource-group/-g")

        if included:
            raise ValueError(msg.format(args=", ".join(included)))


def _validate_direct_mode_args(namespace, required_direct):
    if not namespace.use_k8s:
        msg = "The following ARM-targeted arguments are required: {missing}."
        missing = required_direct or []

        if not namespace.resource_group:
            missing.append("--resource-group/-g")

        # [--subscription] is handled differently, so omit check as required

        if missing:
            raise ValueError(msg.format(missing=", ".join(missing)))
