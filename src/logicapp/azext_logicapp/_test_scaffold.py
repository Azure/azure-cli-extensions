# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Source-only scaffolding for the native Logic Apps test SDK."""

import json
import os
import re
from xml.sax.saxutils import escape

from azure.cli.core.azclierror import FileOperationError, ValidationError

from . import _testing
from ._constants import NATIVE_TEST_PROJECT_FILE as PROJECT_FILE, NATIVE_TEST_STATE_DIRECTORY as STATE_DIRECTORY
from ._workflow import validate_workflow_document

SDK_VERSION = "1.0.3"
ENGINE_VERSION = "1.165.50"
MSTEST_VERSION = "4.0.2"


def default_project(root, workflow):
    return os.path.join(root, "Tests", workflow, PROJECT_FILE)


def selected_workflow(root, workflow):
    if not isinstance(workflow, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", workflow):
        raise _testing.InputError("input.options")
    root = _testing._path(root)  # pylint: disable=protected-access
    host = _testing._json(_testing._read(os.path.join(root, "host.json")))  # pylint: disable=protected-access
    if (not isinstance(host, dict) or host.get("version") != "2.0" or
            not isinstance(host.get("extensionBundle"), dict) or
            host["extensionBundle"].get("id") != "Microsoft.Azure.Functions.ExtensionBundle.Workflows"):
        raise _testing.InputError("host.invalid")
    path = os.path.join(root, workflow, "workflow.json")
    data = _testing._read(path)  # pylint: disable=protected-access
    document = _testing._json(data)  # pylint: disable=protected-access
    findings = []
    validate_workflow_document(document, workflow, "workflow.json", findings)
    if (any(row["severity"] == "error" for row in findings) or
            not isinstance(document, dict) or document.get("kind") not in ("Stateful", "Stateless") or
            not isinstance(document.get("definition"), dict) or
            not isinstance(document["definition"].get("actions"), dict) or
            document["definition"].get("$schema") != _testing.protocol.WORKFLOW_SCHEMA):
        raise _testing.InputError("workflow.root")
    return path, data, document


def _msbuild_path(value):
    # XML escaping alone does not protect an MSBuild path from property/item expansion.
    return escape(re.sub(r"[%$@();'?*]", lambda match: "%{:02X}".format(ord(match.group())), value),
                  {'"': "&quot;"})


def _sources(workflow_path, project_directory, trigger):
    same_drive = os.path.normcase(os.path.splitdrive(workflow_path)[0]) == os.path.normcase(
        os.path.splitdrive(project_directory)[0])
    include = _msbuild_path(os.path.relpath(workflow_path, project_directory) if same_drive else workflow_path)
    project = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <IsPackable>false</IsPackable>
    <IsTestProject>true</IsTestProject>
    <RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>
    <UseSharedCompilation>false</UseSharedCompilation>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="MSTest" Version="[{mstest}]" />
    <PackageReference Include="Microsoft.Azure.Workflows.WebJobs.Tests.Extension" Version="[{sdk}]" />
    <PackageReference Include="Microsoft.Azure.Workflows.WebJobs.Extension" Version="[{engine}]" />
    <None Include="{workflow}" Link="workflow.json" CopyToOutputDirectory="Always" />
    <None Update="trigger.json" CopyToOutputDirectory="Always" />
  </ItemGroup>
</Project>
""".format(mstest=MSTEST_VERSION, sdk=SDK_VERSION, engine=ENGINE_VERSION, workflow=include)
    code = """using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using Microsoft.Azure.Workflows.UnitTesting;
using Microsoft.Azure.Workflows.UnitTesting.Definitions;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

[assembly: DoNotParallelize]

public class JsonMockOutput : MockOutput
{
    [JsonProperty("body")]
    public JToken Body { get; set; }
}

[TestClass]
public class WorkflowTests
{
    [TestMethod]
    [Ignore("Review fixtures and mock all external operations; replace the guard with business assertions.")]
    public async Task AuthoredScenario()
    {
        Assert.Inconclusive("Author synthetic fixtures, action mocks and business assertions before enabling this test.");
        var executor = new UnitTestExecutor(Path.Combine(AppContext.BaseDirectory, "workflow.json"));
        var trigger = new TriggerMock(TestWorkflowStatus.Succeeded, TRIGGER_LITERAL,
            new JsonMockOutput { Body = JToken.Parse(File.ReadAllText(Path.Combine(AppContext.BaseDirectory, "trigger.json"))) });
        var actions = new Dictionary<string, ActionMock>();
        var result = await executor.RunWorkflowAsync(new TestMockDefinition(trigger, actions), timeoutInSeconds: 30);
        Assert.IsNotNull(result);
        Assert.AreEqual(TestWorkflowStatus.Succeeded, result.Status);
        // Add assertions against result.Actions or result.Outputs; status alone is not business coverage.
    }
}
""".replace("TRIGGER_LITERAL", json.dumps(trigger, ensure_ascii=True))
    config = """<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <clear />
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" protocolVersion="3" />
  </packageSources>
</configuration>
"""
    return {
        PROJECT_FILE: project,
        "WorkflowTests.cs": code,
        "trigger.json": "{}\n",
        "global.json": json.dumps({"sdk": {"version": "8.0.426", "rollForward": "latestPatch",
                                           "allowPrerelease": False}}, indent=2) + "\n",
        "NuGet.Config": config,
        ".gitignore": "bin/\nobj/\n" + STATE_DIRECTORY + "/\n*.csproj.lock\n",
    }


def create_project(root, workflow, output_path=None, trigger=None):
    try:
        workflow_path, original, document = selected_workflow(root, workflow)
        triggers = document["definition"]["triggers"]
        if trigger is None:
            if len(triggers) != 1:
                raise ValidationError("Select --trigger explicitly when the workflow has multiple triggers.")
            trigger = next(iter(triggers))
        if not isinstance(trigger, str) or trigger not in triggers:
            raise ValidationError("--trigger must select an existing trigger in this workflow.")
        destination = _testing._path(output_path or os.path.dirname(default_project(root, workflow)))  # pylint: disable=protected-access
        if os.path.lexists(destination):
            raise ValidationError("Test output directory already exists; select a new --output-path. No files were overwritten.")
        sources = _sources(workflow_path, destination, trigger)
        if _testing._read(workflow_path) != original:  # pylint: disable=protected-access
            raise _testing.InputError("input.changed")
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        _testing._path(destination)  # pylint: disable=protected-access
        os.mkdir(destination)
        for name, content in sources.items():
            target = _testing._path(os.path.join(destination, name))  # pylint: disable=protected-access
            handle = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
        if _testing._read(workflow_path) != original:  # pylint: disable=protected-access
            raise _testing.InputError("input.changed")
    except _testing.InputError as ex:
        raise ValidationError(
            "Test scaffolding refused an unsafe, invalid or changed local input. "
            "Use test plan for bounded authoring diagnostics; inspect any partially created output.") from ex
    except OSError as ex:
        raise FileOperationError(
            "Test scaffolding could not finish. Inspect the selected output directory before retrying; "
            "existing files were not overwritten.") from ex
    return {"testProject": os.path.join(destination, PROJECT_FILE), "workflow": workflow,
            "sdkVersion": SDK_VERSION, "engineVersion": ENGINE_VERSION, "targetFramework": "net8.0",
            "files": list(sources), "executionState": "notExecuted", "restorePerformed": False,
            "scaffoldState": "requiresAuthoring",
            "nextAction": "Review trigger.json, mock external operations and author business assertions in WorkflowTests.cs. "
                          "The ignored/inconclusive starter is deliberately not a passing test."}
