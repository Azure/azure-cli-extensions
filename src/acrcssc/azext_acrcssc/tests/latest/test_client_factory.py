# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest import mock

from azext_acrcssc import _client_factory
from azext_acrcssc.helper._constants import ACR_API_VERSION_2019_06_01_PREVIEW


class TestAcrTasksClientFactory(unittest.TestCase):

    def test_task_clients_use_split_resource_type_when_available(self):
        resource_types = SimpleNamespace(
            MGMT_CONTAINERREGISTRY=mock.sentinel.legacy_resource_type,
            MGMT_CONTAINERREGISTRYTASKS=mock.sentinel.tasks_resource_type)
        service_client = SimpleNamespace(
            tasks=mock.sentinel.tasks,
            registries=mock.sentinel.registries,
            task_runs=mock.sentinel.task_runs,
            runs=mock.sentinel.runs)

        with mock.patch.object(_client_factory, "ResourceType", resource_types), \
                mock.patch.object(
                    _client_factory,
                    "get_mgmt_service_client",
                    return_value=service_client) as get_client:
            clients = {
                "tasks": _client_factory.cf_acr_tasks(mock.sentinel.cli_ctx),
                "registries": _client_factory.cf_acr_registries_tasks(mock.sentinel.cli_ctx),
                "task_runs": _client_factory.cf_acr_taskruns(mock.sentinel.cli_ctx),
                "runs": _client_factory.cf_acr_runs(mock.sentinel.cli_ctx),
            }

        self.assertEqual(
            clients,
            {
                "tasks": mock.sentinel.tasks,
                "registries": mock.sentinel.registries,
                "task_runs": mock.sentinel.task_runs,
                "runs": mock.sentinel.runs,
            })
        self.assertEqual(
            get_client.call_args_list,
            [mock.call(mock.sentinel.cli_ctx, mock.sentinel.tasks_resource_type)] * 4)

    def test_task_clients_fall_back_to_legacy_resource_type_and_api_version(self):
        resource_types = SimpleNamespace(
            MGMT_CONTAINERREGISTRY=mock.sentinel.legacy_resource_type)
        service_client = SimpleNamespace(
            tasks=mock.sentinel.tasks,
            registries=mock.sentinel.registries,
            task_runs=mock.sentinel.task_runs,
            runs=mock.sentinel.runs)

        with mock.patch.object(_client_factory, "ResourceType", resource_types), \
                mock.patch.object(
                    _client_factory,
                    "get_mgmt_service_client",
                    return_value=service_client) as get_client:
            clients = {
                "tasks": _client_factory.cf_acr_tasks(mock.sentinel.cli_ctx),
                "registries": _client_factory.cf_acr_registries_tasks(mock.sentinel.cli_ctx),
                "task_runs": _client_factory.cf_acr_taskruns(mock.sentinel.cli_ctx),
                "runs": _client_factory.cf_acr_runs(mock.sentinel.cli_ctx),
            }

        self.assertEqual(
            clients,
            {
                "tasks": mock.sentinel.tasks,
                "registries": mock.sentinel.registries,
                "task_runs": mock.sentinel.task_runs,
                "runs": mock.sentinel.runs,
            })
        self.assertEqual(
            get_client.call_args_list,
            [
                mock.call(
                    mock.sentinel.cli_ctx,
                    mock.sentinel.legacy_resource_type,
                    api_version=ACR_API_VERSION_2019_06_01_PREVIEW)
            ] * 4)

    def test_task_models_use_split_resource_type_when_available(self):
        resource_types = SimpleNamespace(
            MGMT_CONTAINERREGISTRY=mock.sentinel.legacy_resource_type,
            MGMT_CONTAINERREGISTRYTASKS=mock.sentinel.tasks_resource_type)

        with mock.patch.object(_client_factory, "ResourceType", resource_types), \
                mock.patch.object(
                    _client_factory,
                    "get_sdk",
                    create=True,
                    return_value=mock.sentinel.models) as get_sdk:
            models = _client_factory.get_acr_tasks_models(mock.sentinel.cli_ctx)

        self.assertIs(models, mock.sentinel.models)
        get_sdk.assert_called_once_with(
            mock.sentinel.cli_ctx,
            mock.sentinel.tasks_resource_type,
            "models")

    def test_task_models_fall_back_to_legacy_resource_type(self):
        resource_types = SimpleNamespace(
            MGMT_CONTAINERREGISTRY=mock.sentinel.legacy_resource_type)

        with mock.patch.object(_client_factory, "ResourceType", resource_types), \
                mock.patch.object(
                    _client_factory,
                    "get_sdk",
                    create=True,
                    return_value=mock.sentinel.models) as get_sdk:
            models = _client_factory.get_acr_tasks_models(mock.sentinel.cli_ctx)

        self.assertIs(models, mock.sentinel.models)
        get_sdk.assert_called_once_with(
            mock.sentinel.cli_ctx,
            mock.sentinel.legacy_resource_type,
            "models")

