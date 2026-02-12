# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

from collections import OrderedDict


def order_endpoints():
    """
    Order postgres server instance `dict` sections to the same order the server API handed us.
    NOTE: This is redundant in Python 3.7 however needed for earlier versions.

    :return: A well defined `OrderedDict` of the given SQL instance endpoints.
    """

    def get_endpoints(endpoints):
        """
        Creates ordered dictionaries for the given endpoints to be used in the BoxLayout.
        :param endpoints:
        :return:
        """

        def new_endpoint(e):
            return OrderedDict(
                [
                    ("description", e["description"]),
                    ("endpoint", e["endpoint"]),
                    ("options", []),
                ]
            )

        return [new_endpoint(endpoint) for endpoint in endpoints]

    def get_instances(obj):
        """
        Returns all instances and their endpoints.
        :param obj:
        :return:
        """
        obj = obj if obj else []
        return [
            OrderedDict(
                [
                    ("instanceName", instance["name"]),
                    ("engine", instance["engine"]),
                    ("endpoints", get_endpoints(instance.get("endpoints"))),
                ]
            )
            for instance in obj
        ]

    def get_arc_postgres_endpoints(obj):
        """
        Retrieves all postgres server endpoints in an ordered dictionary to be used in the BoxLayout.
        :param obj:
        :return:
        """
        return (
            None
            if "namespace" not in obj
            else OrderedDict(
                [
                    ("clusterName", obj["namespace"]),
                    ("instance", get_instances(obj["instances"])),
                ]
            )
        )

    return get_arc_postgres_endpoints


def hierarchical_output(command_result):
    """
    Callback for formatting complex custom-output.
    :parm_am command_result: The command's high-level result object.
    :return: Complex BoxLayout otherwise flat json.
    """
    from azext_arcdata.core.layout import BoxLayout

    raw_result = command_result.result
    result = order_endpoints()(raw_result)

    return BoxLayout(
        result,
        config={
            "headers": {
                "left": {"label": "", "id": None},
                "right": {"label": "", "id": None},
            },
            "identifiers": [],
        },
        bdc_config=True,
    )
