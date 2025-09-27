# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional
from urllib.parse import quote

LOGGER = logging.getLogger(__name__)


@dataclass
class BraintrustMetadata:
    project: str
    dataset: str
    experiment: Optional[str]
    api_key: str
    org: str


class BraintrustUploader:
    """Uploads eval results to Braintrust when credentials and SDK are available."""

    def __init__(self, env: Mapping[str, str | None]) -> None:
        self._env = env
        self._metadata = self._load_metadata(env)
        self._enabled = self._metadata is not None
        self._braintrust = None
        self._dataset = None
        self._experiments: Dict[str, Any] = {}
        self._warning_emitted = False

    @staticmethod
    def _load_metadata(env: Mapping[str, str | None]) -> Optional[BraintrustMetadata]:
        api_key = env.get("BRAINTRUST_API_KEY") or ""
        org = env.get("BRAINTRUST_ORG") or ""
        if not api_key or not org:
            return None
        project = env.get("BRAINTRUST_PROJECT") or "aks-agent"
        dataset = env.get("BRAINTRUST_DATASET") or "aks-agent/ask"
        experiment = env.get("EXPERIMENT_ID")
        return BraintrustMetadata(
            project=project,
            dataset=dataset,
            experiment=experiment,
            api_key=api_key,
            org=org,
        )

    @property
    def enabled(self) -> bool:
        return self._enabled

    def _warn_once(self, message: str) -> None:
        if not self._warning_emitted:
            LOGGER.warning("[braintrust] %s", message)
            self._warning_emitted = True

    def _ensure_braintrust(self) -> bool:
        if self._braintrust is not None:
            return True
        if not self._enabled or not self._metadata:
            return False
        try:
            import braintrust  # type: ignore
        except ImportError:
            self._warn_once(
                "braintrust package not installed; skipping Braintrust uploads"
            )
            self._enabled = False
            return False

        # Configure environment for braintrust SDK
        os.environ.setdefault("BRAINTRUST_API_KEY", self._metadata.api_key)
        os.environ.setdefault("BRAINTRUST_ORG", self._metadata.org)
        self._braintrust = braintrust
        return True

    def _ensure_dataset(self) -> Optional[Any]:
        if not self._ensure_braintrust():
            return None
        if self._dataset is None and self._metadata:
            try:
                self._dataset = self._braintrust.init_dataset(  # type: ignore[attr-defined]
                    project=self._metadata.project,
                    name=self._metadata.dataset,
                )
            except Exception as exc:  # pragma: no cover - SDK specific failure
                self._warn_once(f"Unable to initialise Braintrust dataset: {exc}")
                self._enabled = False
                return None
        return self._dataset

    def _get_experiment(self, experiment_name: str) -> Optional[Any]:
        if experiment_name in self._experiments:
            return self._experiments[experiment_name]
        dataset = self._ensure_dataset()
        if dataset is None or not self._metadata:
            return None
        try:
            experiment = self._braintrust.init(  # type: ignore[attr-defined]
                project=self._metadata.project,
                experiment=experiment_name,
                dataset=dataset,
                open=False,
                update=True,
                metadata={"aks_agent": True},
            )
        except Exception as exc:  # pragma: no cover - SDK specific failure
            self._warn_once(f"Unable to initialise Braintrust experiment: {exc}")
            self._enabled = False
            return None
        self._experiments[experiment_name] = experiment
        return experiment

    def _build_url(
        self,
        experiment_name: str,
        span_id: Optional[str],
        root_span_id: Optional[str],
    ) -> Optional[str]:
        if not self._metadata:
            return None
        encoded_exp = quote(experiment_name, safe="")
        base = (
            f"https://www.braintrust.dev/app/{self._metadata.org}/p/"
            f"{self._metadata.project}/experiments/{encoded_exp}"
        )
        if span_id and root_span_id:
            return f"{base}?r={span_id}&s={root_span_id}"
        return base

    def record(
        self,
        *,
        scenario_name: str,
        iteration: int,
        total_iterations: int,
        prompt: str,
        answer: str,
        expected_output: list[str],
        model: str,
        tags: list[str],
        passed: bool,
        run_live: bool,
        raw_output: str,
        resource_group: str,
        cluster_name: str,
        error_message: Optional[str] = None,
        classifier_score: Optional[float] = None,
        classifier_rationale: Optional[str] = None,
    ) -> Optional[Dict[str, Optional[str]]]:
        if not self._enabled:
            return None
        metadata = self._metadata
        if not metadata:
            return None

        if metadata.experiment:
            experiment_name = metadata.experiment
        else:
            iteration_token = os.environ.get("BRAINTRUST_RUN_ID") or os.environ.get("GITHUB_RUN_ID") or os.environ.get("CI_PIPELINE_ID")
            if not iteration_token:
                iteration_token = f"{model}-{os.getpid()}"
            experiment_name = f"aks-agent/{model}/{iteration_token}"
        experiment = self._get_experiment(experiment_name)
        if experiment is None:
            return None

        span = experiment.start_span(
            name=f"{scenario_name} [iter {iteration + 1}/{total_iterations}]"
        )
        metadata: Dict[str, Any] = {
            "raw_output": raw_output,
            "resource_group": resource_group,
            "cluster_name": cluster_name,
            "error": error_message,
        }
        if classifier_score is not None:
            metadata["classifier_score"] = classifier_score
        if classifier_rationale:
            metadata["classifier_rationale"] = classifier_rationale

        span.log(
            input=prompt,
            output=answer,
            expected="\n".join(expected_output),
            dataset_record_id=scenario_name,
            scores={
                "correctness": 1 if passed else 0,
                "classifier": classifier_score,
            },
            tags=list(tags) + [f"model:{model}", f"run_live:{run_live}"],
            metadata=metadata,
        )
        span_id = getattr(span, "id", None)
        root_span_id = getattr(span, "root_span_id", None)
        span.end()
        try:
            experiment.flush()
        except Exception as exc:  # pragma: no cover - SDK specific failure
            self._warn_once(f"Failed flushing Braintrust experiment: {exc}")
            self._enabled = False
            return None
        return {
            "span_id": span_id,
            "root_span_id": root_span_id,
            "url": self._build_url(experiment_name, span_id, root_span_id),
            "classifier_score": classifier_score,
            "classifier_rationale": classifier_rationale,
        }
