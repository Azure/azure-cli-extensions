# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path
from typing import Iterable


import pytest

from .classifier import (
    CLASSIFIER_ENABLED,
    DEFAULT_EVALUATION_TYPE,
    evaluate_correctness,
)
from .helpers import (
    MANDATORY_TAGS,
    Scenario,
    ensure_expected_output,
    extract_ai_answer,
    find_missing_env_vars,
    load_mock_answer,
    load_scenarios,
    save_mock_answer,
)
from .braintrust_uploader import BraintrustUploader


SCENARIO_ROOT = Path(__file__).parent / "fixtures" / "ask_agent"
DIFFICULTY_MARKS = {tag.lower() for tag in MANDATORY_TAGS}
MARKED_TAGS = DIFFICULTY_MARKS | {"kubernetes"}
RUN_LIVE = os.environ.get("RUN_LIVE", "").lower() == "true"
GENERATE_MOCKS = os.environ.get("GENERATE_MOCKS", "").lower() == "true"
ITERATIONS = int(os.environ.get("ITERATIONS", "1"))
BRAINTRUST_UPLOADER = BraintrustUploader(os.environ)

pytestmark = [
    pytest.mark.skipif(
        not RUN_LIVE,
        reason="LIVE evals require RUN_LIVE=true; run manually when exercising AKS Agent evals",
    ),
    pytest.mark.aks_eval,
]


def _set_user_property(request: pytest.FixtureRequest, key: str, value: str) -> None:
    for idx, (existing_key, _) in enumerate(request.node.user_properties):
        if existing_key == key:
            request.node.user_properties[idx] = (key, value)
            return
    request.node.user_properties.append((key, value))

def _resolve_evaluation_type(scenario: Scenario) -> str:
    env_default = os.environ.get("CLASSIFIER_EVALUATION", DEFAULT_EVALUATION_TYPE)
    evaluation_type = scenario.evaluation_type or env_default or "strict"
    evaluation_type = evaluation_type.strip().lower()
    return evaluation_type if evaluation_type in {"strict", "loose"} else "strict"


def _load_env() -> dict[str, str]:
    env = os.environ.copy()
    missing = find_missing_env_vars(env)
    if missing:
        joined = ", ".join(missing)
        pytest.fail(f"Missing required environment variables for live eval run: {joined}")
    return env


def _build_command(prompt: str, model: str, resource_group: str, cluster_name: str) -> list[str]:
    # The prompt is a positional argument; spaces are preserved when sent as a single list item.
    return [
        "az",
        "aks",
        "agent",
        prompt,
        "--model",
        model,
        "-g",
        resource_group,
        "-n",
        cluster_name,
        "--no-interactive",
    ]


def _run_cli(command: Iterable[str], env: dict[str, str]) -> str:
    try:
        result = subprocess.run(  # noqa: S603
            list(command),
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
    except subprocess.CalledProcessError as exc:  # pragma: no cover - live failure path
        output = exc.stdout or ""
        stderr = exc.stderr or ""
        cmd_display = " ".join(shlex.quote(item) for item in exc.cmd)
        pytest.fail(
            "AKS Agent CLI call failed\n"
            f"Command: {cmd_display}\n"
            f"Return code: {exc.returncode}\n"
            f"Stdout: {output}\n"
            f"Stderr: {stderr}"
        )
    return result.stdout


def _run_commands(
    commands: list[str], env: dict[str, str], label: str, scenario: Scenario
) -> None:
    for cmd in commands:
        try:
            completed = subprocess.run(  # noqa: S603
                cmd,
                check=True,
                capture_output=True,
                text=True,
                env=env,
                shell=True,
                cwd=scenario.mock_path,
            )
        except subprocess.CalledProcessError as exc:  # pragma: no cover - live failure path
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            pytest.fail(
                f"{label} command failed for scenario {scenario.name}\n"
                f"Command: {cmd}\n"
                f"Return code: {exc.returncode}\n"
                f"Stdout: {stdout}\n"
                f"Stderr: {stderr}"
            )
        else:
            # Provide quick visibility into command results when debugging failures.
            if completed.stdout:
                print(f"[{label}] {scenario.name}: {completed.stdout.strip()}")


def _scenario_params() -> list:
    # Mirror scenario difficulty tags as pytest markers so ``-m <tag>`` selects cases.
    params: list = []
    for scenario in load_scenarios(SCENARIO_ROOT):
        marks = []
        for tag in scenario.tags:
            normalized = tag.strip().lower()
            if normalized in MARKED_TAGS:
                marks.append(getattr(pytest.mark, normalized))
        params.append(pytest.param(scenario, id=scenario.name, marks=marks))
    return params


@pytest.mark.parametrize("scenario", _scenario_params())
@pytest.mark.parametrize("iteration", range(ITERATIONS))
def test_ask_agent_live(
    scenario: Scenario,
    iteration: int,
    aks_skip_setup: bool,
    aks_skip_cleanup: bool,
    request: pytest.FixtureRequest,
) -> None:
    iteration_label = f"[iteration {iteration + 1}/{ITERATIONS}]"
    if RUN_LIVE:
        env = _load_env()

        model = env["MODEL"]
        resource_group = scenario.resource_group or env["AKS_AGENT_RESOURCE_GROUP"]
        cluster_name = scenario.cluster_name or env["AKS_AGENT_CLUSTER"]
        if scenario.kubeconfig:
            env["KUBECONFIG"] = scenario.kubeconfig

        if scenario.env_overrides:
            env.update(scenario.env_overrides)

        if iteration == 0 and scenario.before_commands and not aks_skip_setup:
            print(f"{iteration_label} running setup commands for {scenario.name}")
            _run_commands(scenario.before_commands, env, "setup", scenario)

        command = _build_command(
            prompt=scenario.prompt,
            model=model,
            resource_group=resource_group,
            cluster_name=cluster_name,
        )

        print(f"{iteration_label} invoking AKS Agent CLI for {scenario.name}")
        try:
            raw_output = _run_cli(command, env)
            answer = ""
            passed = True
            error_message = None
            try:
                answer = extract_ai_answer(raw_output)
            except ValueError as exc:
                answer = raw_output
                passed = False
                error_message = str(exc)

            classifier_score = None
            classifier_rationale = None
            need_substring_validation = True
            if CLASSIFIER_ENABLED:
                evaluation_type = _resolve_evaluation_type(scenario)
                classifier_result = evaluate_correctness(
                    expected_elements=scenario.expected_output,
                    output=answer,
                    evaluation_type=evaluation_type,
                )
                if classifier_result is not None:
                    classifier_score = getattr(classifier_result, "score", None)
                    classifier_rationale = classifier_result.metadata.get(
                        "rationale", ""
                    )
                    print(
                        f"{iteration_label} classifier score for {scenario.name}: {classifier_score}"
                    )
                    if classifier_score is None:
                        print(
                            f"{iteration_label} classifier returned no score for {scenario.name}; falling back to substring checks"
                        )
                    else:
                        need_substring_validation = False
                        if classifier_score < 1:
                            passed = False
                            if not error_message:
                                error_message = "Classifier judged answer incorrect"
                else:
                    print(
                        f"{iteration_label} classifier unavailable for {scenario.name}; falling back to substring checks"
                    )

            if need_substring_validation and passed:
                check_error = ensure_expected_output(scenario.expected_output, answer)
                if check_error:
                    passed = False
                    error_message = check_error
            if classifier_score is not None:
                _set_user_property(request, "classifier_score", str(classifier_score))
            if classifier_rationale:
                _set_user_property(request, "classifier_rationale", classifier_rationale)

            record_info = BRAINTRUST_UPLOADER.record(
                scenario_name=scenario.name,
                iteration=iteration,
                total_iterations=ITERATIONS,
                prompt=scenario.prompt,
                answer=answer,
                expected_output=scenario.expected_output,
                model=model,
                tags=scenario.tags,
                passed=passed,
                run_live=True,
                raw_output=raw_output,
                resource_group=resource_group,
                cluster_name=cluster_name,
                error_message=error_message,
                classifier_score=classifier_score,
                classifier_rationale=classifier_rationale,
            )
            if record_info:
                span_id = record_info.get('span_id')
                root_span_id = record_info.get('root_span_id')
                url = record_info.get('url')
                if span_id:
                    _set_user_property(request, 'braintrust_span_id', str(span_id))
                if root_span_id:
                    _set_user_property(request, 'braintrust_root_span_id', str(root_span_id))
                if url and iteration == ITERATIONS - 1:
                    _set_user_property(request, 'braintrust_experiment_url', str(url))

            if not passed:
                pytest.fail(
                    f"Scenario {scenario.name}: {error_message or 'evaluation failed'}\nAI answer:\n{answer}"
                )

            if GENERATE_MOCKS:
                mock_path = save_mock_answer(scenario.mock_path, answer)
                print(f"{iteration_label} [mock] wrote response to {mock_path}")
        finally:
            if (
                iteration == ITERATIONS - 1
                and scenario.after_commands
                and not aks_skip_cleanup
            ):
                print(f"{iteration_label} running cleanup commands for {scenario.name}")
                _run_commands(scenario.after_commands, env, "cleanup", scenario)
    else:
        if GENERATE_MOCKS:
            pytest.fail("GENERATE_MOCKS requires RUN_LIVE=true")
        try:
            answer = load_mock_answer(scenario.mock_path)
            print(f"{iteration_label} replayed mock response for {scenario.name}")
        except FileNotFoundError:
            pytest.skip(f"Mock response missing for scenario {scenario.name}; rerun with RUN_LIVE=true GENERATE_MOCKS=true")

        error = ensure_expected_output(scenario.expected_output, answer)
        passed = error is None
        record_info = BRAINTRUST_UPLOADER.record(
            scenario_name=scenario.name,
            iteration=iteration,
            total_iterations=ITERATIONS,
            prompt=scenario.prompt,
            answer=answer,
            expected_output=scenario.expected_output,
            model=os.environ.get('MODEL', 'unknown'),
            tags=scenario.tags,
            passed=passed,
            run_live=False,
            raw_output=answer,
            resource_group=os.environ.get('AKS_AGENT_RESOURCE_GROUP', ''),
            cluster_name=os.environ.get('AKS_AGENT_CLUSTER', ''),
            error_message=error,
            classifier_score=None,
            classifier_rationale=None,
        )
        if record_info:
            span_id = record_info.get('span_id')
            root_span_id = record_info.get('root_span_id')
            url = record_info.get('url')
            if span_id:
                _set_user_property(request, 'braintrust_span_id', str(span_id))
            if root_span_id:
                _set_user_property(request, 'braintrust_root_span_id', str(root_span_id))
            if url:
                _set_user_property(request, 'braintrust_experiment_url', str(url))
        if not passed:
            pytest.fail(f"Scenario {scenario.name}: {error}\nAI answer:\n{answer}")
