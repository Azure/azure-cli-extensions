# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import random
import time
import unittest
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import pytest
from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
    RequiredArgumentMissingError,
    ResourceNotFoundError,
)
from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse, live_only


# from .utils import get_test_resource_group, get_test_workspace, get_test_workspace_location, get_test_workspace_storage, get_test_workspace_storage_grs, get_test_workspace_random_name, get_test_workspace_random_long_name, get_test_capabilities, get_test_workspace_provider_sku_list, all_providers_are_in_capabilities, issue_cmd_with_param_missing
# from ..._version_check_helper import check_version
# from datetime import datetime
# from ...__init__ import CLI_REPORTED_VERSION
# from ...operations.workspace import _validate_storage_account, _autoadd_providers, SUPPORTED_STORAGE_SKU_TIERS, SUPPORTED_STORAGE_KINDS, DEPLOYMENT_NAME_PREFIX

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))


class QuantumCliTest(ScenarioTest):
    @AllowLargeResponse()
    def test_cli(self):

        # self.test_submit()
        self.test_submit_with_disabled_then_enabled_storage_key_access()

        test_workspace_v1 = "qw-v1-e2e-tests-eus"
        test_location_v1 = "eastus"
        test_resource_group_v1 = "e2e-scenarios"
        test_storage_v1 = "e2etestswus2"
        test_provider_v1 = "quantinuum"
        test_target_v1 = "quantinuum.sim.h2-1sc"

        test_location_v1 = "westus"
        test_storage_v1 = "clitestsawestus"
        # test_storage_v1 = "clitestsaeastus"
        # test_storage_v1 = "newsaclitest2westus"
        # test_location_v1 = "eastus2euap"
        # test_workspace_v1 = "qw-v1-e2e-tests-" + test_location_v1 + "-" + str(random.randint(1000000, 9999999))
        # results = self.cmd(
        #     f"az quantum workspace create --auto-accept -g {test_resource_group_v1} -w {test_workspace_v1} -l {test_location_v1} -a {test_storage_v1} -o json",
        #     checks=[  # -r {test_provider_sku_list}
        #         self.check("name", "Microsoft.AzureQuantum-" + test_workspace_v1),
        #     ],
        # ).get_output_in_json()
        # print(f"workspace create results: {results}\n")
        
        # test_workspace_v1 = "qw-v1-e2e-tests-westus-9136098"
        # test_workspace_v1 = "qw-v1-e2e-tests-westus-1208187"
        # test_workspace_v1 = "qw-v1-e2e-tests-westus-7972346"
        # test_workspace_v1 = "qw-v1-e2e-tests-eastus-4457997"
        # test_workspace_v1 = "qw-v1-e2e-tests-westus-8928449"
        # test_workspace_v1 = "qw-v1-e2e-tests-westus-5783974"

        # self.test_cli_scenarios(
        #     resource_group=test_resource_group_v1,
        #     ws_name=test_workspace_v1,
        #     location=test_location_v1,
        #     storage=test_storage_v1,
        #     provider=test_provider_v1,
        #     target=test_target_v1,
        #     is_v2=False,
        # )

        # self.test_cli_scenarios_using_operations(
        #     resource_group=test_resource_group_v1,
        #     ws_name=test_workspace_v1,
        #     location=test_location_v1,
        #     storage=test_storage_v1,
        #     provider=test_provider_v1,
        #     target=test_target_v1,
        #     is_v2=False,
        # )

        # test_workspace_v2 = "qw-v2-e2e-tests-eastus2euap"
        # test_location_v2 = "eastus2euap"
        # test_resource_group_v2 = "e2e-scenarios"
        # test_storage_v2 = "e2etestswus2"
        # test_provider_v2 = "provider1"  # "provider4"
        # test_target_v2 = "microsoft.sim.cesarlucatero-001"  # "provider4.target1"

        # test_workspace_v2 = "ws-v2-storage-tests-eastus2euap"
        # test_storage_v2 = "clitestsaeastus"

        # self.test_cli_scenarios(
        #     resource_group=test_resource_group_v2,
        #     ws_name=test_workspace_v2,
        #     location=test_location_v2,
        #     storage=test_storage_v2,
        #     provider=test_provider_v2,
        #     target=test_target_v2,
        #     is_v2=True,
        # )

        # self.test_cli_scenarios_using_operations(
        #     resource_group=test_resource_group_v2,
        #     ws_name=test_workspace_v2,
        #     location=test_location_v2,
        #     storage=test_storage_v2,
        #     provider=test_provider_v2,
        #     target=test_target_v2,
        #     is_v2=True,
        # )

        self.cmd("az quantum target clear")
        self.cmd("az quantum workspace clear")

    def test_cli_scenarios(
        self,
        resource_group: str,
        ws_name: str,
        location: str,
        storage: str,
        provider: str,
        target: str,
        is_v2: bool = False,
    ):

        ws_kind = "V2" if is_v2 else "V1"
        print(
            f"\n\nCLI TESTS FOR workspace {ws_kind}: '{ws_name}' in resource group '{resource_group}' at location '{location}' with storage account '{storage}'\n"
        )

        self.cmd("az quantum target clear")
        self.cmd("az quantum workspace clear")
        
        print("TARGET list...")
        targets = self.cmd(
            f"az quantum target list -g {resource_group} -w {ws_name} -o json"
        ).get_output_in_json()  # new way without location
        targets = self.cmd(
            f"az quantum target list -g {resource_group} -w {ws_name} -l {location} -o json"
        ).get_output_in_json()  # old way with location for backwards compatibility
        print(f"target list results: {targets}\n")
        assert len(targets) > 0

        print(f"\n{ws_kind} QUANTUM COMMANDS ===>")

        print("QUANTUM execute...")
        job_name = (
            "cli-job-exec-" + datetime.now().isoformat()
        )  # new way without location
        execute_results = self.cmd(
            f"az quantum execute -g {resource_group} -w {ws_name} -t {target} --job-name {job_name} --job-input-format qir.v1 --job-input-file c:/repos/azure-cli-extensions/src/quantum/azext_quantum/tests/latest/input_data/ccnot.bc --job-params priority=High tags=cli,test --entry-point ENTRYPOINT__main -o json"
        ).get_output_in_json()
        print(f"quantum execute results: {execute_results}\n")

        print("QUANTUM run...")
        job_name = (
            "cli-job-run-" + datetime.now().isoformat()
        )  # old way with location for backwards compatibility
        run_results = self.cmd(
            f"az quantum run -g {resource_group} -w {ws_name} -t {target} -l {location} --job-name {job_name} --job-input-format qir.v1 --job-input-file c:/repos/azure-cli-extensions/src/quantum/azext_quantum/tests/latest/input_data/ccnot.bc --job-params priority=Standard tags=cli,test --entry-point ENTRYPOINT__main -o json"
        ).get_output_in_json()
        print(f"quantum run results: {run_results}\n")

        # JOB COMMANDS
        print(f"\n{ws_kind} JOB COMMANDS ===>")

        print("JOB submit without location...")
        job_name = (
            "cli-job-ccnot1-" + datetime.now().isoformat()
        )  # new way without location
        job_submit_results = self.cmd(
            f"az quantum job submit -g {resource_group} -w {ws_name} -t {target} --job-name {job_name} --job-input-format qir.v1 --job-input-file c:/repos/azure-cli-extensions/src/quantum/azext_quantum/tests/latest/input_data/ccnot.bc --entry-point ENTRYPOINT__main --job-params priority=High tags=cli,test -o json"
        ).get_output_in_json()
        print(f"job submit results: {job_submit_results}\n")
        print("JOB cancel without location...")
        results = self.cmd(
            f"az quantum job cancel -g {resource_group} -w {ws_name} -j {job_submit_results['id']} -o json"
        )
        if results is not None:
            results = results.get_output_in_json()
        print(f"job cancel results: {results}\n")

        print("JOB submit with location...")
        job_name = (
            "cli-job-ccnot1-" + datetime.now().isoformat()
        )  # old way with location for backwards compatibility
        job_submit_results = self.cmd(
            f"az quantum job submit -g {resource_group} -w {ws_name} -l {location} -t {target} --job-name {job_name} --job-input-format qir.v1 --job-input-file c:/repos/azure-cli-extensions/src/quantum/azext_quantum/tests/latest/input_data/ccnot.bc --entry-point ENTRYPOINT__main -o json"
        ).get_output_in_json()
        print("JOB cancel with location...")
        results = self.cmd(
            f"az quantum job cancel -g {resource_group} -w {ws_name} -l {location} -j {job_submit_results['id']} -o json"
        )
        if results is not None:
            results = results.get_output_in_json()
        print(f"job cancel results: {results}\n")

        print("JOB submit...")
        job_name = "cli-job-ccnot1-" + datetime.now().isoformat()
        job_submit_results = self.cmd(
            f"az quantum job submit -g {resource_group} -w {ws_name} -t {target} --job-name {job_name} --job-input-format qir.v1 --job-input-file c:/repos/azure-cli-extensions/src/quantum/azext_quantum/tests/latest/input_data/ccnot.bc --entry-point ENTRYPOINT__main --job-params priority=Standard tags=cli,test -o json"
        ).get_output_in_json()
        print(f"job submit results: {job_submit_results}\n")

        print("JOB wait...")
        results = self.cmd(
            f"az quantum job wait -g {resource_group} -w {ws_name} -j {job_submit_results['id']} -o json"
        ).get_output_in_json()  # new way without location
        results = self.cmd(
            f"az quantum job wait -g {resource_group} -w {ws_name} -l {location} -j {job_submit_results['id']} -o json"
        ).get_output_in_json()  # old way with location for backwards compatibility
        print(f"job wait results: {results}\n")

        print("JOB show...")
        results = self.cmd(
            f"az quantum job show -g {resource_group} -w {ws_name} -j {job_submit_results['id']} -o json"
        ).get_output_in_json()  # new way without location
        results = self.cmd(
            f"az quantum job show -g {resource_group} -w {ws_name} -l {location} -j {job_submit_results['id']} -o json"
        ).get_output_in_json()  # old way with location for backwards compatibility
        print(f"job show results: {results}\n")

        print("JOB output...")
        results = self.cmd(
            f"az quantum job output -g {resource_group} -w {ws_name} -j {job_submit_results['id']} -o json"
        ).get_output_in_json()  # new way without location
        results = self.cmd(
            f"az quantum job output -g {resource_group} -w {ws_name} -l {location} -j {job_submit_results['id']} -o json"
        ).get_output_in_json()  # old way with location for backwards compatibility
        print(f"job output results: {results}\n")

        print("JOB list by provider-id...")
        results = self.cmd(
            f"az quantum job list -g {resource_group} -w {ws_name} --provider-id {provider} -o json"
        ).get_output_in_json()
        results = self.cmd(
            f"az quantum job list -g {resource_group} -w {ws_name} -l {location} --provider-id {provider} -o json"
        ).get_output_in_json()
        results = [(job["name"], job["status"], job["id"]) for job in results]
        print(f"job list --provider-id {provider} results: {results}\n")

        print("JOB list by target-id...")
        results = self.cmd(
            f"az quantum job list -g {resource_group} -w {ws_name} --target-id {target} -o json"
        ).get_output_in_json()
        results = self.cmd(
            f"az quantum job list -g {resource_group} -w {ws_name} -l {location} --target-id {target} -o json"
        ).get_output_in_json()
        results = [(job["name"], job["status"], job["id"]) for job in results]
        print(f"job list --target-id {target} results: {results}\n")

        print("JOB list with orderby target and top 1...")
        jobs_list = self.cmd(
            f"az quantum job list -g {resource_group} -w {ws_name} --orderby Target --top 1 -o json"
        ).get_output_in_json()
        jobs_list = self.cmd(
            f"az quantum job list -g {resource_group} -w {ws_name} -l {location} --orderby Target --top 1 -o json"
        ).get_output_in_json()
        print(f"job list --orderby Target --top 1 results: {str(jobs_list)}\n")

        print(f"\n{ws_kind} WORKSPACE COMMANDS ===>")

        print("WORKSPACE clear...")
        self.cmd("az quantum workspace clear")
        """
        print("WORKSPACE create...")
        new_ws_name = ws_name + "-" + str(random.randint(1000000, 9999999))
        results = self.cmd(
            f"az quantum workspace create --auto-accept -g {resource_group} -w {new_ws_name} -l eastus -a {storage} -o json",
            checks=[  # -r {test_provider_sku_list}
                self.check("name", "Microsoft.AzureQuantum-" + new_ws_name),
            ],
        ).get_output_in_json()
        print(f"workspace create results: {results}\n")

        print("WORKSPACE update...")
        results = self.cmd(
            f"az quantum workspace update --enable-api-key False -g {resource_group} -w {new_ws_name} -o json"
        ).get_output_in_json()
        print(f"workspace update --enable-api-key False -g -w results: {results}\n")

        print("WORKSPACE delete...")
        results = self.cmd(
            f"az quantum workspace delete -g {resource_group} -w {new_ws_name} -o json",
            checks=[
                self.check("name", new_ws_name),
                self.check("properties.provisioningState", "Deleting"),
            ],
        ).get_output_in_json()
        print(f"workspace delete results: {results}\n")
        """
        print("WORKSPACE list...")
        workspaces = self.cmd(
            f"az quantum workspace list -l {location} -o json"
        ).get_output_in_json()
        workspaces_names = [ws["name"] for ws in workspaces]
        print(f"workspace list -l {location} results: {workspaces_names}\n")
        assert len(workspaces) > 0
        workspaces = self.cmd(
            "az quantum workspace list -o json",
            checks=[
                self.check(f"[?name=='{ws_name}'].resourceGroup | [0]", resource_group)
            ],
        ).get_output_in_json()
        workspaces_names = [ws["name"] for ws in workspaces]
        print(f"workspace list -o results: {workspaces_names}\n")
        assert len(workspaces) > 0

        if not is_v2:
            print("WORKSPACE quotas...")
            results = self.cmd(
                f"az quantum workspace quotas -g {resource_group} -w {ws_name} -o json"
            ).get_output_in_json()  # new way without location
            results = self.cmd(
                f"az quantum workspace quotas -l {location} -g {resource_group} -w {ws_name} -o json"
            ).get_output_in_json()  # old way with location for backwards compatibility
            print(f"workspace quotas -l -g -w results: {results}\n")

        print("WORKSPACE show...")
        results = self.cmd(
            f"az quantum workspace show -g {resource_group} -w {ws_name} -o json",
            checks=[self.check("name", ws_name)],
        ).get_output_in_json()
        print(f"workspace show -g -w results: {results}\n")

        print("WORKSPACE keys list...")
        results = self.cmd(
            f"az quantum workspace keys list -g {resource_group} -w {ws_name} -o json"
        ).get_output_in_json()
        print(f"workspace keys list -g -w results: {results}\n")

        print("WORKSPACE keys regenerate...")
        results = self.cmd(
            f"az quantum workspace keys regenerate --key-type Primary,Secondary -g {resource_group} -w {ws_name} -o json"
        )
        print(f"workspace keys regenerate Primary,Secondary -g -w results: {results}\n")

        # WORKSPACE UPDATE does not work for workspaces with managed storage account enabled: it returns (WrongApiVersion) Workspace has managed storage account enabled, which is supported by api versions starting from 2025-01-01-preview
        # print("WORKSPACE update...")
        # results = self.cmd(f'az quantum workspace update --enable-api-key False -g {resource_group} -w {ws_name} -o json').get_output_in_json()
        # print(f"workspace update --enable-api-key False -g -w results: {results}\n")

        print("WORKSPACE set...")
        results = self.cmd(
            f"az quantum workspace set -g {resource_group} -w {ws_name} -o json",
            checks=[self.check("name", ws_name)],
        ).get_output_in_json()
        results = self.cmd(
            f"az quantum workspace set -g {resource_group} -w {ws_name} -l {location} -o json",
            checks=[self.check("name", ws_name)],
        ).get_output_in_json()
        print(f"workspace set results: {results}\n")

        print("WORKSPACE show...")
        results = self.cmd(
            "az quantum workspace show -o json", checks=[self.check("name", ws_name)]
        ).get_output_in_json()
        print(f"workspace show results: {results}\n")

        if not is_v2:
            print("WORKSPACE quotas...")
            results = self.cmd(
                "az quantum workspace quotas -o json"
            ).get_output_in_json()
            print(f"workspace quotas results: {results}\n")

        print("WORKSPACE keys list...")
        results = self.cmd(
            f"az quantum workspace keys list -o json"
        ).get_output_in_json()
        print(f"workspace keys list results: {results}\n")

        print("WORKSPACE keys regenerate...")
        results = self.cmd(
            f"az quantum workspace keys regenerate --key-type Primary,Secondary -o json"
        )
        print(f"workspace keys regenerate Primary,Secondary results: {results}\n")

        print("WORKSPACE list...")
        workspaces = self.cmd(f"az quantum workspace list -o json").get_output_in_json()
        workspaces_names = [ws["name"] for ws in workspaces]
        print(f"workspace list results: {workspaces_names}\n")

        print(f"\n{ws_kind} TARGET COMMANDS ===>")
        print("TARGET clear...")
        results = self.cmd("az quantum target clear")
        print(f"target clear results: {results}\n")

        # TARGET commands without target set

        print("TARGET list...")
        targets = self.cmd("az quantum target list -o json").get_output_in_json()
        print(f"target list results: {targets}\n")
        assert len(targets) > 0

        print("TARGET show...")
        results = self.cmd(
            f"az quantum target show -t {target} -o json",
            checks=[self.check("targetId", target)],
        ).get_output_in_json()
        print(f"target show results: {results}\n")

        print("TARGET clear...")
        results = self.cmd("az quantum target clear")
        print(f"target clear results: {results}\n")

        print("TARGET set...")
        results = self.cmd(
            f"az quantum target set -t {target} -o json",
            checks=[self.check("targetId", target)],
        ).get_output_in_json()
        print(f"target set results: {results}\n")

        # TARGET commands within target set

        print("TARGET show...")
        results = self.cmd(
            f"az quantum target show -o json", checks=[self.check("targetId", target)]
        ).get_output_in_json()
        print(f"target show results: {results}\n")

        print("TARGET list...")
        targets = self.cmd("az quantum target list -o json").get_output_in_json()
        print(f"target list results: {targets}\n")
        assert len(targets) > 0

        # JOB COMMANDS
        print(f"\n{ws_kind} JOB COMMANDS with workspace & target set ===>")

        print("JOB submit...")
        job_name = "cli-job-ccnot1-" + datetime.now().isoformat()
        job_submit_results = self.cmd(
            f"az quantum job submit --job-name {job_name} --job-input-format qir.v1 --job-input-file c:/repos/azure-cli-extensions/src/quantum/azext_quantum/tests/latest/input_data/ccnot.bc --entry-point ENTRYPOINT__main -o json"
        ).get_output_in_json()
        print(f"job submit results: {job_submit_results}\n")

        print("JOB cancel...")
        results = self.cmd(
            f"az quantum job cancel -j {job_submit_results['id']} -o json"
        )
        if results is not None:
            results = results.get_output_in_json()
        print(f"job cancel results: {results}\n")

        print("JOB submit...")
        job_name = "cli-job-ccnot1-" + datetime.now().isoformat()
        job_submit_results = self.cmd(
            f"az quantum job submit --job-name {job_name} --job-input-format qir.v1 --job-input-file c:/repos/azure-cli-extensions/src/quantum/azext_quantum/tests/latest/input_data/ccnot.bc --entry-point ENTRYPOINT__main --job-params priority=High tags=cli,test -o json"
        ).get_output_in_json()
        print(f"job submit results: {job_submit_results}\n")

        print("JOB wait...")
        results = self.cmd(
            f"az quantum job wait -j {job_submit_results['id']} -o json"
        ).get_output_in_json()
        print(f"job wait results: {results}\n")

        print("JOB show...")
        results = self.cmd(
            f"az quantum job show -j {job_submit_results['id']} -o json"
        ).get_output_in_json()
        print(f"job show results: {results}\n")

        print("JOB output...")
        results = self.cmd(
            f"az quantum job output -j {job_submit_results['id']} -o json"
        ).get_output_in_json()
        print(f"job output results: {results}\n")

        print("JOB list by provider-id...")
        results = self.cmd(
            f"az quantum job list --provider-id {provider} -o json"
        ).get_output_in_json()
        results = [(job["name"], job["status"], job["id"]) for job in results]
        print(f"job list --provider-id {provider} results: {results}\n")

        print("JOB list by target-id...")
        results = self.cmd(
            f"az quantum job list --target-id {target} -o json"
        ).get_output_in_json()
        results = [(job["name"], job["status"], job["id"]) for job in results]
        print(f"job list --target-id {target} results: {results}\n")

        print("JOB list with orderby target and top 1...")
        jobs_list = self.cmd(
            "az quantum job list --orderby Target --top 1 -o json"
        ).get_output_in_json()
        print(f"job list --orderby Target --top 1 results: {str(jobs_list)}\n")

        print(f"\n{ws_kind} OFFERINGS COMMANDS ===>")
        print("OFFERINGS list...")
        results = self.cmd(
            f"az quantum offerings list -l {location} -o json"
        ).get_output_in_json()
        print(f"offerings list results: {results}\n")

        print("OFFERINGS show terms...")
        results = self.cmd(
            f"az quantum offerings show-terms -l {location} -p {provider} -k default -o json"
        )
        print(f"offerings show-terms results: {str(results)}\n")

        print("OFFERINGS accept terms...")
        results = self.cmd(
            f"az quantum offerings accept-terms -l {location} -p {provider} -k default -o json"
        )
        print(f"offerings accept-terms results: {str(results)}\n")

    def test_cli_scenarios_using_operations(
        self,
        resource_group: str,
        ws_name: str,
        location: str,
        storage: str,
        provider: str,
        target: str,
        is_v2: bool = False,
    ):
        """
        Same scenarios as test_cli_scenarios but calling operations directly
        instead of going through the Azure CLI command dispatcher.
        """
        from azext_quantum.operations import job as job_ops
        from azext_quantum.operations import offerings as offerings_ops
        from azext_quantum.operations import target as target_ops
        from azext_quantum.operations import workspace as workspace_ops

        # Wrap cli_ctx in a minimal object that operations expect as 'cmd'
        class MockCmd:
            def __init__(self, cli_ctx):
                self.cli_ctx = cli_ctx

        cmd = MockCmd(self.cli_ctx)

        job_input_file = "c:/repos/azure-cli-extensions/src/quantum/azext_quantum/tests/latest/input_data/ccnot.bc"

        ws_kind = "V2" if is_v2 else "V1"
        print(
            f"\n\nOPERATION TESTS FOR workspace {ws_kind}: '{ws_name}' in resource group '{resource_group}' at location '{location}' with storage account '{storage}'\n"
        )

        target_ops.clear(cmd)
        workspace_ops.clear(cmd)

        print("TARGET list...")
        targets = target_ops.list(
            cmd, resource_group, ws_name
        )  # new way without location
        targets = target_ops.list(
            cmd, resource_group, ws_name, location=location
        )  # old way with location for backwards compatibility
        print(f"target list results: {targets}\n")
        assert len(targets) > 0

        print(f"\n{ws_kind} QUANTUM COMMANDS ===>")

        print("QUANTUM execute...")
        job_name = (
            "cli-job-exec-" + datetime.now().isoformat()
        )  # new way without location
        execute_results = job_ops.run(
            cmd,
            resource_group,
            ws_name,
            target,
            job_input_file,
            "qir.v1",
            job_name=job_name,
            storage=None, # storage,
            job_params={"priority": "High", "tags": "cli,test"},
            entry_point="ENTRYPOINT__main",
        )
        print(f"quantum execute results: {execute_results}\n")

        print("QUANTUM run...")
        job_name = (
            "cli-job-run-" + datetime.now().isoformat()
        )  # old way with location for backwards compatibility
        run_results = job_ops.run(
            cmd,
            resource_group,
            ws_name,
            target,
            job_input_file,
            "qir.v1",
            location=location,
            job_name=job_name,
            storage=None, # storage,
            job_params={"priority": "Standard", "tags": "cli,test"},
            entry_point="ENTRYPOINT__main",
        )
        print(f"quantum run results: {run_results}\n")

        # JOB COMMANDS
        print(f"\n{ws_kind} JOB COMMANDS ===>")

        print("JOB submit without location...")
        job_name = (
            "cli-job-ccnot1-" + datetime.now().isoformat()
        )  # new way without location
        job_submit_results = job_ops.submit(
            cmd,
            resource_group,
            ws_name,
            target,
            job_input_file,
            "qir.v1",
            job_name=job_name,
            storage=None, # storage,
            job_params={"priority": "High", "tags": "cli,test"},
            entry_point="ENTRYPOINT__main",
        )
        print(f"job submit results: {job_submit_results}\n")
        print("JOB cancel without location...")
        results = job_ops.cancel(cmd, job_submit_results["id"], resource_group, ws_name)
        print(f"job cancel results: {results}\n")

        print("JOB submit with location...")
        job_name = (
            "cli-job-ccnot1-" + datetime.now().isoformat()
        )  # old way with location for backwards compatibility
        job_submit_results = job_ops.submit(
            cmd,
            resource_group,
            ws_name,
            target,
            job_input_file,
            "qir.v1",
            location=location,
            job_name=job_name,
            storage=None, # storage,
            entry_point="ENTRYPOINT__main",
        )
        print("JOB cancel with location...")
        results = job_ops.cancel(
            cmd, job_submit_results["id"], resource_group, ws_name, location=location
        )
        print(f"job cancel results: {results}\n")

        print("JOB submit...")
        job_name = "cli-job-ccnot1-" + datetime.now().isoformat()
        job_submit_results = job_ops.submit(
            cmd,
            resource_group,
            ws_name,
            target,
            job_input_file,
            "qir.v1",
            job_name=job_name,
            storage=None, # storage,
            job_params={"priority": "Standard", "tags": "cli,test"},
            entry_point="ENTRYPOINT__main",
        )
        print(f"job submit results: {job_submit_results}\n")

        print("JOB wait...")
        results = job_ops.wait(
            cmd, job_submit_results["id"], resource_group, ws_name
        )  # new way without location
        results = job_ops.wait(
            cmd, job_submit_results["id"], resource_group, ws_name, location=location
        )  # old way with location for backwards compatibility
        print(f"job wait results: {results}\n")

        print("JOB show...")
        results = job_ops.job_show(
            cmd, job_submit_results["id"], resource_group, ws_name
        )  # new way without location
        results = job_ops.job_show(
            cmd, job_submit_results["id"], resource_group, ws_name, location=location
        )  # old way with location for backwards compatibility
        print(f"job show results: {results}\n")

        print("JOB output...")
        results = job_ops.output(
            cmd, job_submit_results["id"], resource_group, ws_name
        )  # new way without location
        results = job_ops.output(
            cmd, job_submit_results["id"], resource_group, ws_name, location=location
        )  # old way with location for backwards compatibility
        print(f"job output results: {results}\n")

        print("JOB list by provider-id...")
        results = job_ops.list(cmd, resource_group, ws_name, provider_id=provider)
        results = job_ops.list(
            cmd, resource_group, ws_name, location=location, provider_id=provider
        )
        results = [(job["name"], job["status"], job["id"]) for job in results]
        print(f"job list --provider-id {provider} results: {results}\n")

        print("JOB list by target-id...")
        results = job_ops.list(cmd, resource_group, ws_name, target_id=target)
        results = job_ops.list(
            cmd, resource_group, ws_name, location=location, target_id=target
        )
        results = [(job["name"], job["status"], job["id"]) for job in results]
        print(f"job list --target-id {target} results: {results}\n")

        print("JOB list with orderby target and top 1...")
        jobs_list = job_ops.list(cmd, resource_group, ws_name, orderby="Target", top=1)
        jobs_list = job_ops.list(
            cmd, resource_group, ws_name, location=location, orderby="Target", top=1
        )
        print(f"job list --orderby Target --top 1 results: {str(jobs_list)}\n")

        print(f"\n{ws_kind} WORKSPACE COMMANDS ===>")

        print("WORKSPACE clear...")
        workspace_ops.clear(cmd)
        """
        print("WORKSPACE create...")
        new_ws_name = ws_name + "-" + str(random.randint(1000000, 9999999))
        results = workspace_ops.create(
            cmd, resource_group, new_ws_name, "eastus", storage, auto_accept=True
        )
        assert results.name == "Microsoft.AzureQuantum-" + new_ws_name
        print(f"workspace create results: {results}\n")

        print("WORKSPACE update...")
        results = workspace_ops.enable_keys(cmd, resource_group, new_ws_name, enable_key="False")
        print(f"workspace update --enable-api-key False -g -w results: {results}\n")

        print("WORKSPACE delete...")
        results = workspace_ops.delete(cmd, resource_group, new_ws_name)
        assert results.name == new_ws_name
        assert results.properties.provisioning_state == "Deleting"
        print(f"workspace delete results: {results}\n")
        """
        print("WORKSPACE list...")
        workspaces = workspace_ops.list(cmd, location=location)
        workspaces_names = [ws.name for ws in workspaces]
        print(f"workspace list -l {location} results: {workspaces_names}\n")
        assert len(workspaces) > 0
        workspaces = workspace_ops.list(cmd)
        workspaces_names = [ws.name for ws in workspaces]
        assert any(
            ws.name == ws_name and ws.resource_group == resource_group
            for ws in workspaces
        )
        print(f"workspace list results: {workspaces_names}\n")
        assert len(workspaces) > 0

        if not is_v2:
            print("WORKSPACE quotas...")
            results = workspace_ops.quotas(
                cmd, resource_group, ws_name
            )  # new way without location
            results = workspace_ops.quotas(
                cmd, resource_group, ws_name, location=location
            )  # old way with location for backwards compatibility
            print(f"workspace quotas -l -g -w results: {results}\n")

        print("WORKSPACE show...")
        results = workspace_ops.get(cmd, resource_group, ws_name)
        assert results.name == ws_name
        print(f"workspace show -g -w results: {results}\n")

        print("WORKSPACE keys list...")
        results = workspace_ops.list_keys(cmd, resource_group, ws_name)
        print(f"workspace keys list -g -w results: {results}\n")

        print("WORKSPACE keys regenerate...")
        results = workspace_ops.regenerate_keys(
            cmd, resource_group, ws_name, key_type="Primary,Secondary"
        )
        print(f"workspace keys regenerate Primary,Secondary -g -w results: {results}\n")

        print("WORKSPACE set...")
        results = workspace_ops.set(cmd, ws_name, resource_group)
        assert results.name == ws_name
        results = workspace_ops.set(cmd, ws_name, resource_group, location=location)
        assert results.name == ws_name
        print(f"workspace set results: {results}\n")

        print("WORKSPACE show...")
        results = workspace_ops.get(cmd)
        assert results.name == ws_name
        print(f"workspace show results: {results}\n")

        if not is_v2:
            print("WORKSPACE quotas...")
            results = workspace_ops.quotas(cmd, None, None)
            print(f"workspace quotas results: {results}\n")

        print("WORKSPACE keys list...")
        results = workspace_ops.list_keys(cmd)
        print(f"workspace keys list results: {results}\n")

        print("WORKSPACE keys regenerate...")
        results = workspace_ops.regenerate_keys(cmd, key_type="Primary,Secondary")
        print(f"workspace keys regenerate Primary,Secondary results: {results}\n")

        print("WORKSPACE list...")
        workspaces = workspace_ops.list(cmd)
        workspaces_names = [ws.name for ws in workspaces]
        print(f"workspace list results: {workspaces_names}\n")

        print(f"\n{ws_kind} TARGET COMMANDS ===>")
        print("TARGET clear...")
        target_ops.clear(cmd)

        # TARGET commands without target set

        print("TARGET list...")
        targets = target_ops.list(cmd, None, None)
        print(f"target list results: {targets}\n")
        assert len(targets) > 0

        print("TARGET show...")
        results = target_ops.target_show(cmd, target)
        assert results.target_id == target
        print(f"target show results: {results}\n")

        print("TARGET clear...")
        target_ops.clear(cmd)

        print("TARGET set...")
        results = target_ops.set(cmd, target)
        assert results.target_id == target
        print(f"target set results: {results}\n")

        # TARGET commands with target set

        print("TARGET show...")
        results = target_ops.target_show(cmd, None)
        assert results.target_id == target
        print(f"target show results: {results}\n")

        print("TARGET list...")
        targets = target_ops.list(cmd, None, None)
        print(f"target list results: {targets}\n")
        assert len(targets) > 0

        # JOB COMMANDS
        print(f"\n{ws_kind} JOB COMMANDS with workspace & target set ===>")

        print("JOB submit...")
        job_name = "cli-job-ccnot1-" + datetime.now().isoformat()
        job_submit_results = job_ops.submit(
            cmd,
            None,
            None,
            None,
            job_input_file,
            "qir.v1",
            job_name=job_name,
            storage=None, # storage,
            entry_point="ENTRYPOINT__main",
        )
        print(f"job submit results: {job_submit_results}\n")

        print("JOB cancel...")
        results = job_ops.cancel(cmd, job_submit_results["id"], None, None)
        print(f"job cancel results: {results}\n")

        print("JOB submit...")
        job_name = "cli-job-ccnot1-" + datetime.now().isoformat()
        job_submit_results = job_ops.submit(
            cmd,
            None,
            None,
            None,
            job_input_file,
            "qir.v1",
            job_name=job_name,
            storage=None, # storage,
            job_params={"priority": "High", "tags": "cli,test"},
            entry_point="ENTRYPOINT__main",
        )
        print(f"job submit results: {job_submit_results}\n")

        print("JOB wait...")
        results = job_ops.wait(cmd, job_submit_results["id"], None, None)
        print(f"job wait results: {results}\n")

        print("JOB show...")
        results = job_ops.job_show(cmd, job_submit_results["id"], None, None)
        print(f"job show results: {results}\n")

        print("JOB output...")
        results = job_ops.output(cmd, job_submit_results["id"], None, None)
        print(f"job output results: {results}\n")

        print("JOB list by provider-id...")
        results = job_ops.list(cmd, None, None, provider_id=provider)
        results = [(job["name"], job["status"], job["id"]) for job in results]
        print(f"job list --provider-id {provider} results: {results}\n")

        print("JOB list by target-id...")
        results = job_ops.list(cmd, None, None, target_id=target)
        results = [(job["name"], job["status"], job["id"]) for job in results]
        print(f"job list --target-id {target} results: {results}\n")

        print("JOB list with orderby target and top 1...")
        jobs_list = job_ops.list(cmd, None, None, orderby="Target", top=1)
        print(f"job list --orderby Target --top 1 results: {str(jobs_list)}\n")

        print(f"\n{ws_kind} OFFERINGS COMMANDS ===>")
        print("OFFERINGS list...")
        results = offerings_ops.list_offerings(cmd, location)
        print(f"offerings list results: {results}\n")

        print("OFFERINGS show terms...")
        results = offerings_ops.show_terms(cmd, provider, "default", location)
        print(f"offerings show-terms results: {str(results)}\n")

        print("OFFERINGS accept terms...")
        results = offerings_ops.accept_terms(cmd, provider, "default", location)
        print(f"offerings accept-terms results: {str(results)}\n")


    def test_submit_with_disabled_then_enabled_storage_key_access(self):
        test_location = "eastus"
        test_resource_group = "e2e-scenarios"
        test_workspace_temp = "ws-v1-e2e-tests-eastus-4605175" # "ws-v1-e2e-tests-" + test_location + "-" + str(random.randint(1000000, 9999999))
        test_provider_sku_list = "rigetti/azure-basic-qvm-only-unlimited"
        # Storage account names must be 3-24 lowercase alphanumeric characters only
        test_storage_temp = "e2etests47140761" # "e2etests" + str(random.randint(10000000, 99999999))

        # Test that create workspace with not existing storage will create storage
        # self.cmd(f"az quantum workspace create --auto-accept -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_temp} -r {test_provider_sku_list} --skip-autoadd")

        # Verify that access keys are disabled on the newly created storage account
        # storage_info = self.cmd(f"az storage account show -g {test_resource_group} -n {test_storage_temp} -o json").get_output_in_json()
        # self.assertFalse(storage_info["allowSharedKeyAccess"], "Access keys should be disabled on the newly created storage account for new workspace")

        self.cmd(f"az quantum workspace set -g {test_resource_group} -w {test_workspace_temp} -l {test_location}")
        # time.sleep(60) # wait for role assignments to propagate so the new workspace can access the storage account

        # Test that job submission works with disabled access keys on linked storage (/sasUri returns user delegation SAS)
        results = self.cmd("az quantum job submit -t rigetti.sim.qvm --job-input-format rigetti.quil.v1 --job-input-file input_data/bell-state.quil --job-output-format rigetti.quil-results.v1 -o json").get_output_in_json()
        self.assertIn("id", results)

        job = self.cmd(f"az quantum job show -j {results['id']} -o json").get_output_in_json()
        self.assert_contains_user_delegation_sas_params(job["containerUri"])
        self.assert_contains_standard_sas_params(job["containerUri"])
        self.assert_contains_user_delegation_sas_params(job["inputDataUri"])
        self.assert_contains_standard_sas_params(job["inputDataUri"])
        self.assert_contains_user_delegation_sas_params(job["outputDataUri"])
        self.assert_contains_standard_sas_params(job["outputDataUri"])
        
        # Enable access keys on the storage account
        updated = self.cmd(f"az storage account update -g {test_resource_group} -n {test_storage_temp} --allow-shared-key-access true -o json").get_output_in_json()
        self.assertTrue(updated["allowSharedKeyAccess"], "Access keys should be enabled after update")

        time.sleep(300) # wait for the cache to update

        # Test that job submission works with enabled access keys on linked storage (/sasUri returns container-scoped Service SAS)
        results = self.cmd("az quantum job submit -t rigetti.sim.qvm --job-input-format rigetti.quil.v1 --job-input-file input_data/bell-state.quil --job-output-format rigetti.quil-results.v1 -o json").get_output_in_json()
        self.assertIn("id", results)

        job = self.cmd(f"az quantum job show -j {results['id']} -o json").get_output_in_json()
        self.assert_not_contains_user_delegation_sas_params(job["containerUri"])
        self.assert_contains_standard_sas_params(job["containerUri"])
        self.assert_not_contains_user_delegation_sas_params(job["inputDataUri"])
        self.assert_contains_standard_sas_params(job["inputDataUri"])
        self.assert_not_contains_user_delegation_sas_params(job["outputDataUri"])
        self.assert_contains_standard_sas_params(job["outputDataUri"])

        # Clean up
        # self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp}')
        # self.cmd(f'az storage account delete -g {test_resource_group} -n {test_storage_temp} --yes')

    def test_submit(self):
        test_location = "eastus"
        test_resource_group = "e2e-scenarios"
        test_workspace_temp = "ws-v1-e2e-tests-eastus-8808959" # "ws-v1-e2e-tests-" + test_location + "-" + str(random.randint(1000000, 9999999))
        test_provider_sku_list = "rigetti/azure-basic-qvm-only-unlimited"
        test_storage = "clitestsaeastus"

        # self.cmd(f"az quantum workspace create --auto-accept -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage} -r {test_provider_sku_list} --skip-autoadd")
        
        # Wait for role assignments to propagate so the new workspace can access the storage account
        # time.sleep(60)
        
        self.cmd(f"az quantum workspace set -g {test_resource_group} -w {test_workspace_temp} -l {test_location}")

        # Submit a job to Rigetti and look for SAS tokens in URIs in the output
        results = self.cmd("az quantum job submit -t rigetti.sim.qvm --job-input-format rigetti.quil.v1 -t rigetti.sim.qvm --job-input-file input_data/bell-state.quil --job-output-format rigetti.quil-results.v1 -o json").get_output_in_json()
        print(f"job submit results: {results}\n")
        self.assert_not_contains_standard_sas_params(results["containerUri"])
        self.assert_not_contains_user_delegation_sas_params(results["containerUri"])

        self.assert_not_contains_standard_sas_params(results["inputDataUri"])
        self.assert_not_contains_user_delegation_sas_params(results["inputDataUri"])

        self.assert_not_contains_standard_sas_params(results["outputDataUri"])
        self.assert_not_contains_user_delegation_sas_params(results["outputDataUri"])

        job = self.cmd(f"az quantum job show -j {results['id']} -o json").get_output_in_json()
        print(f"job show results: {job}\n")

        self.assert_contains_user_delegation_sas_params(job["containerUri"])
        self.assert_contains_standard_sas_params(job["containerUri"])

        self.assert_contains_user_delegation_sas_params(job["inputDataUri"])
        self.assert_contains_standard_sas_params(job["inputDataUri"])
        
        self.assert_contains_user_delegation_sas_params(job["outputDataUri"])
        self.assert_contains_standard_sas_params(job["outputDataUri"])

        # # Run a Quil pass-through job on Rigetti
        # results = self.cmd("az quantum run -t rigetti.sim.qvm --job-input-format rigetti.quil.v1 -t rigetti.sim.qvm --job-input-file input_data/bell-state.quil --job-output-format rigetti.quil-results.v1 -o json").get_output_in_json()
        # self.assertIn("ro", results)

        # # Run an IonQ Circuit pass-through job on IonQ
        # results = self.cmd("az quantum run -t ionq.simulator --shots 100 --job-input-format ionq.circuit.v1 --job-input-file input_data/Qiskit-3-qubit-GHZ-circuit.json --job-output-format ionq.quantum-results.v1 --job-params shots=100 content-type=application/json -o json").get_output_in_json()
        # self.assertIn("histogram", results)

        # # Test "az quantum job list" output, for filter-params, --skip, --top, and --orderby
        # results = self.cmd("az quantum job list --provider-id rigetti -o json").get_output_in_json()
        # self.assertIn("rigetti", str(results))

        # results = self.cmd("az quantum job list --target-id ionq.simulator -o json").get_output_in_json()
        # self.assertIn("ionq.simulator", str(results))

        # jobs_list = self.cmd("az quantum job list --top 1 -o json").get_output_in_json()
        # self.assertEqual(len(jobs_list), 1)
    
        # jobs_list = self.cmd("az quantum job list --skip 1 -o json").get_output_in_json()
        # self.assertEqual(len(jobs_list), 2)

        # jobs_list = self.cmd("az quantum job list --orderby Target --top 1 -o json").get_output_in_json()
        # self.assertEqual(len(jobs_list), 1)
        # results = str(jobs_list)
        # self.assertIn("ionq", results)
        # self.assertTrue("rigetti" not in results)

        # jobs_list = self.cmd("az quantum job list --orderby Target --skip 1 -o json").get_output_in_json()
        # self.assertEqual(len(jobs_list), 2)
        # results = str(jobs_list)
        # self.assertIn("rigetti", results)
        # self.assertTrue("ionq" not in results)

        # self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp}')
    
    def assert_contains_user_delegation_sas_params(self, uri: str):
        """Assert that the given URI contains user delegation SAS parameters."""
        params = parse_qs(urlparse(uri).query)
        self.assertIn("skoid", params)   # signed key object ID (service principal OID)
        self.assertIn("sktid", params)   # signed key tenant ID
        self.assertIn("skt", params)     # signed key start time
        self.assertIn("ske", params)     # signed key expiry time
        self.assertIn("sks", params)     # signed key service (b = Blob)
        self.assertIn("skv", params)     # signed key version

    def assert_not_contains_user_delegation_sas_params(self, uri: str):
        """Assert that the given URI does not contain user delegation SAS parameters."""
        params = parse_qs(urlparse(uri).query)
        self.assertNotIn("skoid", params)
        self.assertNotIn("sktid", params)
        self.assertNotIn("skt", params)
        self.assertNotIn("ske", params)
        self.assertNotIn("sks", params)
        self.assertNotIn("skv", params)

    def assert_contains_standard_sas_params(self, uri: str):
        """Assert that the given URI contains standard SAS parameters."""
        params = parse_qs(urlparse(uri).query)
        self.assertIn("sv", params)    # SAS version
        self.assertIn("st", params)    # start time
        self.assertIn("se", params)    # expiry time
        self.assertIn("sr", params)    # signed resource (e.g. c = container)
        self.assertIn("sp", params)    # permissions
        self.assertIn("sig", params)   # signature

    def assert_not_contains_standard_sas_params(self, uri: str):
        """Assert that the given URI does not contain standard SAS parameters."""
        params = parse_qs(urlparse(uri).query)
        self.assertNotIn("sv", params)
        self.assertNotIn("st", params)
        self.assertNotIn("se", params)
        self.assertNotIn("sr", params)
        self.assertNotIn("sp", params)
        self.assertNotIn("sig", params)

if __name__ == "__main__":
    QuantumCliTest("test_cli").test_cli()
