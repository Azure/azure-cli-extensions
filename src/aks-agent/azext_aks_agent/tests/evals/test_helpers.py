# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from . import helpers
from .braintrust_uploader import BraintrustUploader


def test_extract_ai_answer_uses_last_marker() -> None:
    output = dedent(
        """
        AI: previous answer
        some other text
        AI: final answer line
        """
    )
    assert helpers.extract_ai_answer(output) == "final answer line"


def test_extract_ai_answer_missing_marker() -> None:
    with pytest.raises(ValueError):
        helpers.extract_ai_answer("No AI marker present")


def test_ensure_expected_output_success() -> None:
    error = helpers.ensure_expected_output(["alpha", "beta"], "beta -- alpha -- gamma")
    assert error is None


def test_ensure_expected_output_failure() -> None:
    message = helpers.ensure_expected_output(["alpha", "beta"], "alpha only")
    assert message is not None
    assert "beta" in message


def test_find_missing_env_vars_detects_empty_values() -> None:
    env = {name: "value" for name in helpers.REQUIRED_ENV_VARS}
    env[helpers.REQUIRED_ENV_VARS[0]] = ""
    missing = helpers.find_missing_env_vars(env)
    assert helpers.REQUIRED_ENV_VARS[0] in missing


def test_load_scenarios_reads_prompt(tmp_path: Path) -> None:
    root = tmp_path / "fixtures"
    root.mkdir()
    scenario_dir = root / "01_test"
    scenario_dir.mkdir()
    yaml_path = scenario_dir / "test_case.yaml"
    yaml_path.write_text(
        """
        user_prompt: say hello
        expected_output:
          - hello
        tags:
          - easy
        before_test: echo setup
        after_test:
          - echo cleanup
        resource_group: custom-rg
        cluster_name: custom-cluster
        kubeconfig: /fake/kubeconfig
        test_env_vars:
          EXTRA: '1'
        evaluation:
          correctness:
            type: loose
        """,
        encoding="utf-8",
    )

    scenarios = helpers.load_scenarios(root)
    assert len(scenarios) == 1
    scenario = scenarios[0]
    assert scenario.prompt == "say hello"
    assert scenario.expected_output == ["hello"]
    assert scenario.tags == ["easy"]
    assert scenario.before_commands == ["echo setup"]
    assert scenario.after_commands == ["echo cleanup"]
    assert scenario.resource_group == "custom-rg"
    assert scenario.cluster_name == "custom-cluster"
    assert scenario.kubeconfig == "/fake/kubeconfig"
    assert scenario.env_overrides == {"EXTRA": "1"}
    assert scenario.mock_path == scenario_dir
    assert scenario.evaluation_type == "loose"


def test_load_scenarios_requires_easy_or_medium(tmp_path: Path) -> None:
    root = tmp_path / "fixtures-bad"
    root.mkdir()
    scenario_dir = root / "01_bad"
    scenario_dir.mkdir()
    yaml_path = scenario_dir / "test_case.yaml"
    yaml_path.write_text(
        """
        user_prompt: say hello
        expected_output:
          - hello
        tags:
          - experimental
        """,
        encoding="utf-8",
    )

    with pytest.raises(ValueError) as exc:
        helpers.load_scenarios(root)
    assert "easy" in str(exc.value)


def test_load_scenarios_invalid_evaluation_type(tmp_path: Path) -> None:
    root = tmp_path / "fixtures-eval"
    root.mkdir()
    scenario_dir = root / "01_bad_eval"
    scenario_dir.mkdir()
    yaml_path = scenario_dir / "test_case.yaml"
    yaml_path.write_text(
        """
        user_prompt: say hello
        expected_output:
          - hello
        tags:
          - easy
        evaluation:
          correctness:
            type: fuzzy
        """,
        encoding="utf-8",
    )

    with pytest.raises(ValueError) as exc:
        helpers.load_scenarios(root)
    assert "evaluation.correctness.type" in str(exc.value)


def test_load_mock_answer(tmp_path: Path) -> None:
    scenario_dir = tmp_path / "scenario"
    mock_file = scenario_dir / helpers.MOCK_FILE
    mock_file.parent.mkdir(parents=True, exist_ok=True)
    mock_file.write_text("mocked answer", encoding="utf-8")

    assert helpers.load_mock_answer(scenario_dir) == "mocked answer"


def test_load_mock_answer_missing(tmp_path: Path) -> None:
    scenario_dir = tmp_path / "scenario"
    scenario_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        helpers.load_mock_answer(scenario_dir)


def test_save_mock_answer(tmp_path: Path) -> None:
    scenario_dir = tmp_path / "scenario"
    path = helpers.save_mock_answer(scenario_dir, "saved answer")
    assert path.exists()
    assert path.read_text(encoding="utf-8") == "saved answer"



class _StubSpan:
    def __init__(self) -> None:
        self.logged = []
        self.ended = False
    def log(self, **kwargs):
        self.logged.append(kwargs)
    def end(self):
        self.ended = True


class _StubExperiment:
    def __init__(self) -> None:
        self.spans: list[tuple[str, _StubSpan]] = []
        self.flush_called = False
    def start_span(self, name: str):
        span = _StubSpan()
        self.spans.append((name, span))
        return span
    def flush(self):
        self.flush_called = True


class _StubBraintrustModule:
    def __init__(self) -> None:
        self.datasets = []
        self.experiments = []
    def init_dataset(self, project: str, name: str):
        self.datasets.append((project, name))
        return object()
    def init(self, project: str, experiment: str, dataset, open: bool, update: bool, metadata):
        self.experiments.append((project, experiment, metadata))
        return _StubExperiment()


def test_braintrust_uploader_disabled_without_keys(monkeypatch):
    uploader = BraintrustUploader({})
    assert not uploader.enabled
    uploader.record(
        scenario_name='demo',
        iteration=0,
        total_iterations=1,
        prompt='hi',
        answer='hello',
        expected_output=['hello'],
        model='model',
        tags=[],
        passed=True,
        run_live=True,
        raw_output='hello',
        resource_group='',
        cluster_name='',
    )


def test_braintrust_uploader_records(monkeypatch):
    import sys
    stub = _StubBraintrustModule()
    monkeypatch.setitem(sys.modules, 'braintrust', stub)
    env = {
        'BRAINTRUST_API_KEY': 'key',
        'BRAINTRUST_ORG': 'org',
        'BRAINTRUST_PROJECT': 'proj',
        'BRAINTRUST_DATASET': 'dataset',
        'EXPERIMENT_ID': 'experiment',
    }
    uploader = BraintrustUploader(env)
    assert uploader.enabled
    info = uploader.record(
        scenario_name='demo',
        iteration=1,
        total_iterations=3,
        prompt='hi',
        answer='hello',
        expected_output=['hello'],
        model='model',
        tags=['easy'],
        passed=True,
        run_live=True,
        raw_output='hello',
        resource_group='rg',
        cluster_name='cluster',
    )
    monkeypatch.delitem(sys.modules, 'braintrust', raising=False)
    assert stub.datasets == [('proj', 'dataset')]
    assert stub.experiments[-1][0] == 'proj'
    assert info is not None
    assert 'url' in info
    assert 'classifier_score' in info
