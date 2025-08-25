# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
import yaml
from azext_mlv2.tests.scenario_test_helper import MLBaseScenarioTest
from azext_mlv2.tests.util import assert_same


class EnvironmentScenarioTest(MLBaseScenarioTest):
    @pytest.mark.skip(reason="Unable to get authority configuration for login")
    def test_environment_no_workspace_no_registry(self) -> None:
        for base_command in ["az ml environment list", "az ml environment show -n abc", "az ml environment create -n abc"]:
            with pytest.raises(Exception) as exp:
                dep_obj = self.cmd(f'{base_command} --workspace-name="" --registry-name=""')
            assert "one the following arguments are required: [--workspace-name/-w, --registry-name]" in str(exp.value)

    def test_environment(self) -> None:
        env_obj = self.cmd(
            "az ml environment create --file ./src/machinelearningservices/azext_mlv2/tests/test_configs/environment/environment_conda.yml --name {environmentName} --set version=1 --tags test=test -g testrg -w testworkspace"
        )
        env_obj = yaml.safe_load(env_obj.output)
        assert env_obj["name"] == self.kwargs.get("environmentName", None)
        assert env_obj["version"] == "1"
        assert "image" in env_obj
        assert "conda_file" in env_obj
        assert env_obj["tags"]["test"] == "test"
        env_show_obj = self.cmd("az ml environment show -g testrg -w testworkspace --name {environmentName} --version 1")
        env_show_obj = yaml.safe_load(env_show_obj.output)
        assert_same(env_obj, env_show_obj, filter=["creation_context"])
        # list environments
        environments = self.cmd("az ml environment list -g testrg -w testworkspace --max-results 1")
        assert len(yaml.safe_load(environments.output)) == 1
        """
        Bug in line 249 environment.py
        """
        # env_update_obj = self.cmd("az ml environment update -n {environmentName} -v 1 --set tags.name=test_tag")
        # env_update_obj = yaml.safe_load(env_update_obj.output)
        # assert env_update_obj["name"] == self.kwargs.get("environmentName", None)
        # assert env_update_obj["tags"]["name"] == "test_tag"

        # archive environment version
        env_archive_obj = self.cmd("az ml environment archive -g testrg -w testworkspace -n {environmentName} -v 1")
        assert env_archive_obj.output == ""

        # restore environment version
        env_restore_obj = self.cmd("az ml environment restore -g testrg -w testworkspace -n {environmentName} -v 1")
        assert env_restore_obj.output == ""

        # archive environment
        env_archive_obj = self.cmd("az ml environment archive -g testrg -w testworkspace -n {environmentName}")
        assert env_archive_obj.output == ""

        # restore environment
        env_restore_obj = self.cmd("az ml environment restore -g testrg -w testworkspace -n {environmentName}")
        assert env_restore_obj.output == ""

    def test_environment_list(self) -> None:
        env_list_obj = self.cmd("az ml environment list -g testrg -w testworkspace")
        env_list_obj = yaml.safe_load(env_list_obj.output)
        for env in env_list_obj:
            assert env["name"]
            assert env["latest version"]
            assert "id" not in env
            assert "version" not in env

        if len(env_list_obj) > 0:
            env_name = env_list_obj[0]["name"]
            env_name_obj = self.cmd(f"az ml environment list -g testrg -w testworkspace --name {env_name}")
            env_name_obj = yaml.safe_load(env_name_obj.output)
            assert "name" in env_name_obj[0]
            assert "version" in env_name_obj[0]
            assert "latest version" not in env_name_obj[0]
            assert "id" not in env_name_obj[0]

    # This test is not working. TODO: https://dev.azure.com/msdata/Vienna/_workitems/edit/3372868
    @pytest.mark.skip(reason="Recording and replay not working.")
    def test_environment_with_docker_context(self) -> None:
        env_obj = self.cmd(
            "az ml environment create --file ./src/machinelearningservices/azext_mlv2/tests/test_configs/environment/environment_docker_context.yml --name {environmentName} --set version=1 -g testrg -w testworkspace"
        )
        env_obj = yaml.safe_load(env_obj.output)
        assert env_obj["name"] == self.kwargs.get("environmentName", None)
        assert env_obj["build"]["path"]
        assert env_obj["build"]["dockerfile_path"] == "DockerfileNonDefault"
        assert env_obj["version"] == "1"

        env_show_obj = self.cmd("az ml environment show --name {environmentName} --version 1")
        env_show_obj = yaml.safe_load(env_show_obj.output)
        assert env_obj["name"] == self.kwargs.get("environmentName", None)
        assert env_obj["build"]
        assert env_obj["build"]["path"]
        assert env_obj["build"]["dockerfile_path"] == "DockerfileNonDefault"
        assert env_obj["version"] == "1"
        assert_same(env_obj, env_show_obj, filter=["creation_context"])

    # This test is not working. TODO: https://dev.azure.com/msdata/Vienna/_workitems/edit/3372868
    @pytest.mark.skip(reason="Recording and replay not working.")
    def test_environment_build_context(self) -> None:
        env_obj = self.cmd(
            "az ml environment create --build-context ./src/machinelearningservices/azext_mlv2/tests/test_configs/environment/environment_docker_context.yml --name {environmentName} --set version=5 -g testrg -w testworkspace"
        )
        env_obj = yaml.safe_load(env_obj.output)
        assert env_obj["name"] == self.kwargs.get("environmentName", None)
        assert env_obj["build"]
        assert env_obj["build"]["path"]
        assert env_obj["build"]["dockerfile_path"]

        env_show_obj = self.cmd("az ml environment show --name {environmentName} --version 5")
        env_show_obj = yaml.safe_load(env_show_obj.output)

        assert_same(env_obj, env_show_obj, filter=["creation_context"])

    def test_environment_with_image(self) -> None:
        env_obj = self.cmd(
            "az ml environment create --file ./src/machinelearningservices/azext_mlv2/tests/test_configs/environment/environment_docker_image.yml --name {environmentName} --version 1 --image pytorch.pytorch --conda-file endpoint_conda.yml -g testrg -w testworkspace"
        )
        env_obj = yaml.safe_load(env_obj.output)
        assert env_obj["image"] == "pytorch.pytorch"
        assert "conda_file" in env_obj

    def test_environment_params_override(self) -> None:
        env_obj = self.cmd(
            "az ml environment create --file ./src/machinelearningservices/azext_mlv2/tests/test_configs/environment/environment_conda_name_version.yml --name {environmentName} --description bla --os-type windows --version 2 -g testrg -w testworkspace"
        )
        env_obj = yaml.safe_load(env_obj.output)
        assert env_obj["description"] == "bla"
        assert env_obj["os_type"] == "windows"
        assert env_obj["version"] == "2"

    def test_environment_with_no_file(self) -> None:
        env_obj = self.cmd(
            "az ml environment create --name {environmentName} --version 1 --image pytorch.pytorch --conda-file ./src/machinelearningservices/azext_mlv2/tests/test_configs/environment/endpoint_conda.yml -g testrg -w testworkspace"
        )
        env_obj = yaml.safe_load(env_obj.output)
        assert env_obj["image"] == "pytorch.pytorch"
        assert "conda_file" in env_obj

    @pytest.mark.skip(reason="Test depends on batch endpoint that is never defined in the test configs")
    def test_environment_anonymous_env_with_image(self) -> None:
        env_obj = self.cmd(
            "az ml batch-deployment create -n batch-dep1 -e batendp1 --file ./src/machinelearningservices/azext_mlv2/tests/test_configs/deployments/batch/batch_deployment_anon_env_with_image.yaml"
        )
        env_obj = yaml.safe_load(env_obj.output)
        anon_environment = env_obj.get("environment").split("/")
        assert anon_environment[-1] == "e6b10c1cf68e59c9ebd6f84184973c4b"
        assert anon_environment[-3] == "CliV2AnonymousEnvironment"

    @pytest.mark.skip(reason="Test depends on batch endpoint that is never defined in the test configs")
    def test_environment_anonymous_env_with_docker(self) -> None:
        env_obj = self.cmd(
            "az ml batch-deployment create -n batch-dep1 -e batendp1 --file ./src/machinelearningservices/azext_mlv2/tests/test_configs/deployments/batch/batch_deployment_anon_env_with_docker.yaml"
        )
        env_obj = yaml.safe_load(env_obj.output)
        anon_environment = env_obj.get("environment").split("/")
        assert anon_environment[-1] == "6bf4c7a654530fb4dbcf929db3e66600"
        assert anon_environment[-3] == "CliV2AnonymousEnvironment"

    @pytest.mark.skip(reason="Test depends on batch endpoint that is never defined in the test configs")
    def test_environment_anonymous_env_with_conda(self) -> None:
        env_obj = self.cmd(
            "az ml batch-deployment create -n batch-dep1 -e batendp1 --file ./src/machinelearningservices/azext_mlv2/tests/test_configs/deployments/batch/batch_deployment_anon_env_with_conda.yaml"
        )
        env_obj = yaml.safe_load(env_obj.output)
        anon_environment = env_obj.get("environment").split("/")
        assert anon_environment[-1] == "10e20cf4ec11a618e87f0dd965ef70b2"
        assert anon_environment[-3] == "CliV2AnonymousEnvironment"

    def test_environment_show_registry(self) -> None:
        env_obj = self.cmd(
            "az ml environment show -n 4c99f460-20cd-4821-8745-202aa7555604 -v 93435847-704b-4280-83f3-f735d8b5eff7 --registry-name testfeed"
        )
        env_obj = yaml.safe_load(env_obj.output)
        assert (
            env_obj["id"]
            == "azureml://registries/testFeed/environments/4c99f460-20cd-4821-8745-202aa7555604/versions/93435847-704b-4280-83f3-f735d8b5eff7"
        )
        assert env_obj["name"] == "4c99f460-20cd-4821-8745-202aa7555604"

    def test_environment_list_registry(self) -> None:
        env_obj = self.cmd("az ml environment list --registry-name test-registry-ux-1")
        env_obj = yaml.safe_load(env_obj.output)

        assert len(env_obj) > 1

    def test_environment_create_in_registry(self) -> None:

        env_obj = self.cmd(
            "az ml environment create -n conda_name_version_e2e  -v 2 -f ./src/machinelearningservices/azext_mlv2/tests/test_configs/environment/environment_conda_name_version.yml --registry-name testFeed"
        )
        env_obj = yaml.safe_load(env_obj.output)
        assert len(env_obj) > 1
        env_obj_1 = self.cmd(
            "az ml environment create -n docker_image_e2e  -v 2 -f ./src/machinelearningservices/azext_mlv2/tests/test_configs/environment/environment_docker_image.yml --registry-name testFeed"
        )
        env_obj_1 = yaml.safe_load(env_obj_1.output)
        assert len(env_obj_1) > 1

    def test_environment_archive_in_registry(self) -> None:

        env_archive_obj = self.cmd(
            "az ml environment archive -n bani_env -v 1 --registry-name dsvm-test"
        )
        assert env_archive_obj.output == ""

    @pytest.mark.skip(reason="(2860895): LRO sends live requests even in recording mode.")
    def test_environment_restore_in_registry(self) -> None:

        env_restore_obj = self.cmd(
            "az ml environment restore -n taji-registry-env -v 1 --registry-name taji-registry2"
        )
        assert env_restore_obj.output == ""

    def test_environment_update(self) -> None:
        env_obj = self.cmd(
            "az ml environment update -n online-endpoint-mir-test -v 3 --set tags.nn=kkk -g testrg -w testworkspace"
        )
        env_obj = yaml.safe_load(env_obj.output)
        assert env_obj["tags"]["nn"] == "kkk"


