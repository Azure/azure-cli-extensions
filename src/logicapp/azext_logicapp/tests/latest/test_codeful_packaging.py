# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock
import zipfile

from azure.cli.core.azclierror import ValidationError

from azext_logicapp import _workflow, custom


class CodefulPackagingTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "App"
        self.root.mkdir()
        (self.root / "host.json").write_text('{"version":"2.0"}\n', encoding="utf-8")
        self.project = self.root / "App.csproj"
        self.archive = self.root / "package.zip"
        self.manifest = self.root / "package.manifest.json"

    def write_project(self, references=None, project_references=None, sdk="Microsoft.NET.Sdk"):
        references = references or []
        project_references = project_references or []
        items = [
            '<PackageReference Include="{}" Version="1.0.0" />'.format(reference)
            for reference in references
        ]
        items.extend(
            '<ProjectReference Include="{}" />'.format(reference)
            for reference in project_references
        )
        self.project.write_text(
            '<Project Sdk="{}"><ItemGroup>{}</ItemGroup></Project>'.format(sdk, "".join(items)),
            encoding="utf-8")

    def write_codeful_project(self):
        self.write_project([
            "Microsoft.Azure.Workflows.Sdk",
            "Microsoft.Azure.Functions.Worker.Sdk"
        ])

    @staticmethod
    def successful_publish(worker_path="App.dll", language="dotnet-isolated"):
        def publish(command, **_kwargs):
            output = Path(command[command.index("--output") + 1])
            output.mkdir(parents=True, exist_ok=True)
            (output / worker_path).parent.mkdir(parents=True, exist_ok=True)
            (output / worker_path).write_bytes(b"synthetic assembly")
            (output / "worker.config.json").write_text(json.dumps({
                "description": {
                    "language": language,
                    "defaultExecutablePath": "dotnet",
                    "defaultWorkerPath": worker_path
                }
            }), encoding="utf-8")
            return subprocess.CompletedProcess(command, 0, "", "")
        return publish

    def test_detects_package_and_project_references_without_misclassifying_legacy(self):
        self.write_codeful_project()
        self.assertEqual(str(self.project), _workflow._resolve_codeful_project(str(self.root), None))

        self.write_project(project_references=[
            r"..\Microsoft.Azure.Workflows.Sdk\Microsoft.Azure.Workflows.Sdk.csproj",
            r"..\Microsoft.Azure.Functions.Worker.Sdk\Microsoft.Azure.Functions.Worker.Sdk.csproj"
        ])
        self.assertEqual(str(self.project), _workflow._resolve_codeful_project(str(self.root), None))

        self.write_project(["Microsoft.Azure.Workflows.WebJobs.Extension"],
                           sdk="Microsoft.NET.Sdk.Functions")
        self.assertIsNone(_workflow._resolve_codeful_project(str(self.root), None))
        with self.assertRaisesRegex(ValidationError, "traditional"):
            _workflow._resolve_codeful_project(str(self.root), str(self.project))

        self.write_project([
            "Microsoft.Azure.Workflows.Sdk",
            "Microsoft.Azure.Functions.Worker.Sdk",
            "Microsoft.Azure.Workflows.WebJobs.Extension"
        ])
        with self.assertRaisesRegex(ValidationError, "mixes"):
            _workflow._resolve_codeful_project(str(self.root), None)

    def test_multiple_codeful_projects_require_explicit_selection(self):
        self.write_codeful_project()
        second = self.root / "Worker" / "Worker.csproj"
        second.parent.mkdir()
        second.write_text(self.project.read_text(encoding="utf-8"), encoding="utf-8")

        with self.assertRaisesRegex(ValidationError, "Multiple SDK-based projects"):
            _workflow._resolve_codeful_project(str(self.root), None)
        self.assertEqual(str(second), _workflow._resolve_codeful_project(
            str(self.root), str(Path("Worker") / "Worker.csproj")))

    def test_packages_published_worker_and_safe_runtime_assets_deterministically(self):
        self.write_codeful_project()
        (self.root / "Program.cs").write_text("class Program {}\n", encoding="utf-8")
        (self.root / "stale-root.dll").write_bytes(b"old")
        (self.root / "bin").mkdir()
        (self.root / "bin" / "old.dll").write_bytes(b"old")
        stale = self.root / "lib" / "codeful"
        stale.mkdir(parents=True)
        (stale / "stale.dll").write_bytes(b"stale")
        maps = self.root / "Artifacts" / "Maps"
        schemas = self.root / "Artifacts" / "Schemas"
        maps.mkdir(parents=True)
        schemas.mkdir(parents=True)
        (maps / "transform.xslt").write_text("<xsl:stylesheet version=\"1.0\" />", encoding="utf-8")
        (schemas / "order.xsd").write_text("<schema />", encoding="utf-8")
        (self.root / "drop.tmp").write_text("drop", encoding="utf-8")
        (self.root / "keep.tmp").write_text("keep", encoding="utf-8")
        (self.root / ".funcignore").write_text("*.tmp\n!keep.tmp\n/package*.zip\n", encoding="utf-8")

        with mock.patch("azext_logicapp._workflow.subprocess.run",
                        side_effect=self.successful_publish()) as run:
            first = custom.deployment_package(
                None, path=str(self.root), output_path=str(self.archive),
                manifest=str(self.manifest), dotnet="dotnet-custom")
            first_bytes = self.archive.read_bytes()
            second = custom.deployment_package(
                None, path=str(self.root), output_path=str(self.archive),
                manifest=str(self.manifest), dotnet="dotnet-custom", force=True)

        self.assertEqual(first_bytes, self.archive.read_bytes())
        self.assertEqual(first["contentHash"], second["contentHash"])
        command = run.call_args_list[0].args[0]
        self.assertEqual("dotnet-custom", command[0])
        self.assertEqual([
            "publish", str(self.project), "--configuration", "Release",
            "--framework", "net8.0"
        ], command[1:7])
        self.assertEqual("-p:LogicAppFolderToPublish=", command[-1])
        self.assertEqual(str(self.root), run.call_args_list[0].kwargs["cwd"])
        self.assertTrue(run.call_args_list[0].kwargs["check"] is False)

        with zipfile.ZipFile(self.archive) as package:
            names = set(package.namelist())
            self.assertIn("host.json", names)
            self.assertIn("keep.tmp", names)
            self.assertIn("Artifacts/Maps/transform.xslt", names)
            self.assertIn("Artifacts/Schemas/order.xsd", names)
            self.assertIn("lib/codeful/App.dll", names)
            self.assertIn("lib/codeful/worker.config.json", names)
            self.assertNotIn("Program.cs", names)
            self.assertNotIn("App.csproj", names)
            self.assertNotIn("stale-root.dll", names)
            self.assertNotIn("drop.tmp", names)
            self.assertNotIn("lib/codeful/stale.dll", names)
            worker = json.loads(package.read("lib/codeful/worker.config.json"))
            self.assertEqual("dotnet", worker["description"]["language"])

        reasons = {item["path"]: item["reason"] for item in second["excluded"]}
        self.assertEqual("codeful-source", reasons["Program.cs"])
        self.assertEqual("codeful-source", reasons["App.csproj"])
        self.assertEqual("build-output", reasons["stale-root.dll"])
        self.assertEqual("build-output", reasons["bin"])
        self.assertEqual("stale-codeful-output", reasons["lib/codeful"])
        self.assertEqual("ignoreFile", reasons["drop.tmp"])
        self.assertEqual("package-output", reasons["package.zip"])
        self.assertEqual("package-output", reasons["package.manifest.json"])

    def test_source_ignore_rules_filter_publish_output_but_preserve_required_worker_files(self):
        self.write_codeful_project()
        (self.root / ".funcignore").write_text(
            "private.json\nworker.config.json\nApp.dll\n", encoding="utf-8")

        def publish_with_private_content(command, **_kwargs):
            output = Path(command[command.index("--output") + 1])
            output.mkdir(parents=True, exist_ok=True)
            (output / "App.dll").write_bytes(b"synthetic assembly")
            (output / "private.json").write_text('{"secret":"synthetic"}', encoding="utf-8")
            (output / "worker.config.json").write_text(json.dumps({
                "description": {
                    "language": "dotnet-isolated",
                    "defaultExecutablePath": "dotnet",
                    "defaultWorkerPath": "App.dll"
                }
            }), encoding="utf-8")
            return subprocess.CompletedProcess(command, 0, "", "")

        with mock.patch("azext_logicapp._workflow.subprocess.run",
                        side_effect=publish_with_private_content):
            result = custom.deployment_package(
                None, path=str(self.root), output_path=str(self.archive),
                manifest=str(self.manifest))

        with zipfile.ZipFile(self.archive) as package:
            names = set(package.namelist())
            self.assertNotIn("lib/codeful/private.json", names)
            self.assertIn("lib/codeful/worker.config.json", names)
            self.assertIn("lib/codeful/App.dll", names)
        self.assertIn(
            {"path": "lib/codeful/private.json", "reason": "ignoreFile"},
            result["excluded"])

    def test_escaped_bang_is_a_literal_exclusion_after_an_earlier_json_rule(self):
        (self.root / ".funcignore").write_text(
            "*.json\n\\!private.json\n!host.json\n", encoding="utf-8")
        (self.root / "private.json").write_text("{}", encoding="utf-8")
        (self.root / "!private.json").write_text("{}", encoding="utf-8")

        result = custom.deployment_package(
            None, path=str(self.root), output_path=str(self.archive),
            manifest=str(self.manifest))

        included = {item["path"] for item in result["included"]}
        self.assertNotIn("private.json", included)
        self.assertNotIn("!private.json", included)
        self.assertIn("host.json", included)

    def test_directory_only_wildcards_match_root_and_nested_ancestors_in_order(self):
        (self.root / ".funcignore").write_text(
            "private*/\n!private-keep/allowed.json\n", encoding="utf-8")
        files = {
            "private-data/token.txt": "excluded root",
            "nested/private-cache/token.txt": "excluded nested",
            "private-keep/blocked.txt": "excluded by directory rule",
            "private-keep/allowed.json": "included by later negation"
        }
        for relative, content in files.items():
            path = self.root / Path(relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

        result = custom.deployment_package(
            None, path=str(self.root), output_path=str(self.archive),
            manifest=str(self.manifest))

        included = {item["path"] for item in result["included"]}
        self.assertNotIn("private-data/token.txt", included)
        self.assertNotIn("nested/private-cache/token.txt", included)
        self.assertNotIn("private-keep/blocked.txt", included)
        self.assertIn("private-keep/allowed.json", included)

    def test_rejects_missing_or_escaping_worker_assembly_without_outputs(self):
        self.write_codeful_project()

        def invalid_publish(command, **_kwargs):
            output = Path(command[command.index("--output") + 1])
            output.mkdir(parents=True, exist_ok=True)
            (output / "worker.config.json").write_text(json.dumps({
                "description": {
                    "language": "dotnet-isolated",
                    "defaultWorkerPath": "../outside.dll"
                }
            }), encoding="utf-8")
            return subprocess.CompletedProcess(command, 0, "", "")

        with mock.patch("azext_logicapp._workflow.subprocess.run", side_effect=invalid_publish):
            with self.assertRaisesRegex(ValidationError, "outside lib/codeful"):
                custom.deployment_package(
                    None, path=str(self.root), output_path=str(self.archive),
                    manifest=str(self.manifest))
        self.assertFalse(self.archive.exists())
        self.assertFalse(self.manifest.exists())

    def test_rejects_publish_without_worker_config_and_invalid_host(self):
        self.write_codeful_project()

        def no_worker_config(command, **_kwargs):
            Path(command[command.index("--output") + 1]).mkdir(parents=True, exist_ok=True)
            return subprocess.CompletedProcess(command, 0, "", "")

        with mock.patch("azext_logicapp._workflow.subprocess.run", side_effect=no_worker_config):
            with self.assertRaisesRegex(ValidationError, "worker.config.json"):
                custom.deployment_package(
                    None, path=str(self.root), output_path=str(self.archive),
                    manifest=str(self.manifest))

        (self.root / "host.json").write_text("[]", encoding="utf-8")
        with mock.patch("azext_logicapp._workflow.subprocess.run",
                        side_effect=self.successful_publish()):
            with self.assertRaisesRegex(ValidationError, "JSON objects"):
                custom.deployment_package(
                    None, path=str(self.root), output_path=str(self.archive),
                    manifest=str(self.manifest))

    def test_codeless_and_legacy_projects_keep_existing_packaging_path(self):
        self.write_project(["Microsoft.Azure.Workflows.WebJobs.Extension"],
                           sdk="Microsoft.NET.Sdk.Functions")
        workflow = self.root / "Orders"
        workflow.mkdir()
        (workflow / "workflow.json").write_text('{"definition":{}}\n', encoding="utf-8")

        with mock.patch("azext_logicapp._workflow.subprocess.run") as run:
            result = custom.deployment_package(
                None, path=str(self.root), output_path=str(self.archive),
                manifest=str(self.manifest))

        run.assert_not_called()
        with zipfile.ZipFile(self.archive) as package:
            self.assertIn("App.csproj", package.namelist())
            self.assertIn("Orders/workflow.json", package.namelist())
        self.assertEqual("sha256:", result["contentHash"][:7])

    def test_refuses_symbolic_links_in_codeless_package_input(self):
        target = self.root / "target.json"
        link = self.root / "linked.json"
        target.write_text("{}", encoding="utf-8")
        try:
            link.symlink_to(target)
        except OSError as error:
            self.skipTest("Host does not permit symlink creation: {}".format(error))

        with self.assertRaisesRegex(ValidationError, "Symbolic links"):
            custom.deployment_package(
                None, path=str(self.root), output_path=str(self.archive),
                manifest=str(self.manifest))


if __name__ == "__main__":
    unittest.main()
