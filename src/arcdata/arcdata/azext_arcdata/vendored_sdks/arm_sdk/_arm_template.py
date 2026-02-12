# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from datetime import datetime
from ._util import dict_to_dot_notation
from jinja2 import Environment, FileSystemLoader
from knack.log import get_logger
import azure.core.exceptions as exceptions

import os
import json
import uuid

__all__ = ["ARMTemplate"]

logger = get_logger(__name__)


class ARMTemplate(object):
    def __init__(self, dc_client=None):
        self._dc_client = dc_client

        env = Environment(
            loader=FileSystemLoader(
                searchpath=os.path.join(os.path.dirname(__file__), "templates")
            )
        )
        env.filters["jsonify"] = json.dumps
        self._template = env.get_template("arm-template.tmpl")

    def render_dc_upgrade(self, cluster_name, extension_name, dc):
        env_var_overrides = self._environment_variable_overrides()
        resource_matrix = self.resource_matrix_factory(
            include_extension=True, include_resource_hydration=True
        )
        k8s = dict_to_dot_notation(dc.properties.k8_s_raw)
        _, custom_location = os.path.split(dc.extended_location.name)

        arm = json.loads(
            self._template.render(
                resources=self.resources(resource_matrix),
                control=dc.properties.k8_s_raw,
                credentials={},
                log_analytics={},
                extensions=env_var_overrides.extensions,
                docker_username=env_var_overrides.docker_username,
                docker_password=env_var_overrides.docker_password,
                cluster=cluster_name,
                namespace=k8s.metadata.namespace,
                custom_location=custom_location,
                resource_name=extension_name,
            )
        )

        # -- log --
        d = dict_to_dot_notation(arm.copy())
        d.properties.parameters.metricsAndLogsDashboardPassword_4 = "*"
        d.properties.parameters.logAnalyticsPrimaryKey_4 = "*"
        d.properties.parameters.imagePassword = "*"
        logger.debug(json.dumps(d.to_dict, indent=4))

        return arm

    def render_dc(self, control, properties):
        env_var_overrides = self._environment_variable_overrides()
        cluster_name = properties.get("cluster_name")
        custom_location = properties.get("custom_location")
        namespace = properties.get("namespace")
        resource_group = properties.get("resource_group")
        resource_matrix = self._build_included_resource_matrix(
            namespace, custom_location, cluster_name, resource_group
        )
        dc_name = properties.get("dc_name")

        arm = json.loads(
            self._template.render(
                resources=self.resources(resource_matrix),
                control=control,
                credentials=properties.get("metrics_credentials"),
                log_analytics=properties.get("log_analytics"),
                docker_username=env_var_overrides.docker_username,
                docker_password=env_var_overrides.docker_password,
                cluster=cluster_name,
                namespace=namespace,
                resource_name=properties.get("extension_name"),
                extension_train=properties.get("extension_train"),
                extension_version=properties.get("extension_version"),
                # Role assignment resource names are generated from DC name + timestamp + random UUID
                # To avoid collisions with other role assignments in the past + future
                resource_name_1=uuid.uuid5(
                    uuid.uuid4(), name=str(dc_name + str(datetime.now()))
                ),  # role1 name
                resource_name_2=uuid.uuid5(
                    uuid.uuid4(), name=str(dc_name + str(datetime.now()))
                ),  # role2 name
                custom_location=custom_location,
                is_least_privilege=properties.get("is_least_privilege"),
                arcdata_api_version=properties.get("api_version"),
            )
        )

        # -- log --
        d = dict_to_dot_notation(arm.copy())
        d.properties.parameters.metricsAndLogsDashboardPassword_4 = "*"
        d.properties.parameters.logAnalyticsPrimaryKey_4 = "*"
        d.properties.parameters.imagePassword = "*"
        logger.debug(json.dumps(d.to_dict, indent=4))

        return arm

    @staticmethod
    def resource_matrix_factory(
        include_extension=False,
        include_roles_1=False,
        include_roles_2=False,
        include_custom_location=False,
        include_resource_hydration=False,
    ):
        """
        Assume all resources exist hence do not include
        """
        return dict_to_dot_notation(
            {
                "include_extension": include_extension,
                "include_roles_1": include_roles_1,
                "include_roles_2": include_roles_2,
                "include_custom_location": include_custom_location,
                "include_resource_hydration": include_resource_hydration,
            }
        )

    @staticmethod
    def resources(resource_matrix):
        """
        :return: Dynamic list of ordered arm template resources.
        """

        # -- Build needed resources --
        resources = []  # Note: insert order matters
        depends_on = None

        if resource_matrix.include_extension:
            resources.append(
                {"dependsOn": depends_on, "tmpl": "extensions.tmpl"}
            )
            depends_on = "resourceName"

        if resource_matrix.include_roles_1:
            resources.append(
                {"dependsOn": depends_on, "tmpl": "roles-assignments-1.tmpl"}
            )
            depends_on = "resourceName_1"

        if resource_matrix.include_roles_2:
            resources.append(
                {"dependsOn": depends_on, "tmpl": "roles-assignments-2.tmpl"}
            )
            depends_on = "resourceName_2"

        if resource_matrix.include_custom_location:
            resources.append(
                {"dependsOn": depends_on, "tmpl": "custom-locations.tmpl"}
            )
            depends_on = "resourceName_3"

        if resource_matrix.include_resource_hydration:
            resources.append(
                {"dependsOn": depends_on, "tmpl": "resource-hydration.tmpl"}
            )
            depends_on = "resourceSyncRuleName"

        # -- data-controller always created --
        resources.append(
            {"dependsOn": depends_on, "tmpl": "datacontroller.tmpl"}
        )

        return resources

    def _environment_variable_overrides(self):
        # -- docker env overrides --
        docker_username = os.getenv("DOCKER_USERNAME", "")
        docker_password = os.getenv("DOCKER_PASSWORD", "")
        docker_username = docker_username or os.getenv("REGISTRY_USERNAME", "")
        docker_password = docker_password or os.getenv("REGISTRY_PASSWORD", "")

        return dict_to_dot_notation(
            {
                "docker_username": docker_username,
                "docker_password": docker_password,
            }
        )

    def _build_included_resource_matrix(
        self, namespace, custom_location, cluster_name, resource_group
    ):
        try:
            # Assume all resources exist hence do not include
            resource_matrix = self.resource_matrix_factory()

            # -- verify extension and role info --
            if not self._dc_client.get_extension(cluster_name, resource_group):
                resource_matrix.include_extension = True
                resource_matrix.include_roles_1 = True
                resource_matrix.include_roles_2 = True
            else:
                # contributor role and monitoring publisher role
                roles = self._dc_client.get_role_assignments(
                    cluster_name, resource_group
                )
                if len(roles["value"]) == 0:
                    resource_matrix.include_roles_1 = True
                    resource_matrix.include_roles_2 = True

            resource_graph = self._dc_client.get_resource_graph(
                cluster_name, resource_group, namespace
            )
            count = resource_graph["count"]

            if count == 0:  # Include CL
                resource_matrix.include_custom_location = True
            elif count == 1:
                # check if provided CL match existing CL, if not error
                cl_name = resource_graph["data"][0]["customLocationName"]
                if custom_location != cl_name:
                    raise Exception(
                        f"An existing custom location name "
                        f"{cl_name} has been found in the cluster "
                        f"{cluster_name}. A cluster can only "
                        f"have one custom location."
                    )
            else:
                raise Exception(
                    f"Multiple custom location or namespace have been found "
                    f"under cluster {cluster_name}. A "
                    f"cluster can only have one custom location with one "
                    f"namespace."
                )

            # -- default to False
            if not self._dc_client.has_hydration(
                resource_group, custom_location
            ):
                resource_matrix.include_resource_hydration = True

            logger.debug(resource_matrix)

            return resource_matrix
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e
