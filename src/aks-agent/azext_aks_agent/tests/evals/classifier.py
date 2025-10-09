# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Iterable, List, Optional, Sequence

try:
    import openai
except ImportError:  # pragma: no cover - optional dependency
    openai = None  # type: ignore

try:
    from autoevals import LLMClassifier, init as autoevals_init
    _AUTOEVALS_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    LLMClassifier = None  # type: ignore
    autoevals_init = None  # type: ignore
    _AUTOEVALS_AVAILABLE = False

try:
    from braintrust.oai import wrap_openai
except ImportError:  # pragma: no cover - optional dependency
    wrap_openai = lambda client: client  # type: ignore

from braintrust import Span, SpanTypeAttribute  # type: ignore

LOGGER = logging.getLogger(__name__)

ENABLE_CLASSIFIER = os.environ.get("ENABLE_CLASSIFIER", "true").lower() != "false"
CLASSIFIER_ENABLED = ENABLE_CLASSIFIER
DEFAULT_EVALUATION_TYPE = (
    os.environ.get("CLASSIFIER_EVALUATION", "strict").strip().lower() or "strict"
)
CLASSIFIER_MODEL = os.environ.get("CLASSIFIER_MODEL", os.environ.get("MODEL", ""))
AZURE_API_KEY = os.environ.get("AZURE_API_KEY")
AZURE_API_BASE = os.environ.get("AZURE_API_BASE")
AZURE_API_VERSION = os.environ.get("AZURE_API_VERSION")

_STRICT_PROMPT = """
You are evaluating the correctness of an OUTPUT given by a LLM. You must return a score that
represents the correctness of that OUTPUT.

The correctness is defined by the presence of EXPECTED ELEMENTS in the OUTPUT.
Make a judgement call whether each ELEMENT sufficiently matches the OUTPUT. ELEMENTS do
not need to appear verbatim or be a perfect match but their essence should be
present in the whole OUTPUT, even if it spans multiple sentences.

# EXPECTED ELEMENTS

- {{expected}}

# OUTPUT

{{output}}


Return a choice based on the number of EXPECTED ELEMENTS present in the OUTPUT.
Possible choices:
- A: All elements are presents
- B: Either no element is present or only some but not all elements are present
"""

_LOOSE_PROMPT = """
You are evaluating the correctness of an OUTPUT given by a LLM. You must return a score that
represents the correctness of that OUTPUT.

The correctness is defined by the presence of EXPECTED content in the OUTPUT.
Make a judgement call whether the EXPECTED content sufficiently matches the OUTPUT. EXPECTED
content does not need to appear verbatim or be a perfect match but its essence should be
present in the whole OUTPUT, even if it spans multiple sentences.

# EXPECTED

{{expected}}

# OUTPUT

{{output}}


Return a choice based on whether the OUTPUT matches the EXPECTED content.
Possible choices:
- A: The OUTPUT reasonably matches the EXPECTED content
- B: The OUTPUT does not match the EXPECTED content
"""


_client_initialised = False
_client_available = False
_model_for_api: Optional[str] = None


def _ensure_client() -> bool:
    global _client_initialised, _client_available, _model_for_api
    if _client_initialised:
        return _client_available

    _client_initialised = True

    if not ENABLE_CLASSIFIER:
        LOGGER.debug("Classifier disabled via ENABLE_CLASSIFIER")
        return False
    if not _AUTOEVALS_AVAILABLE:
        LOGGER.warning("autoevals package not installed; skipping classifier")
        return False
    if openai is None:
        LOGGER.warning("openai package not installed; skipping classifier")
        return False
    if not AZURE_API_BASE or not AZURE_API_KEY or not AZURE_API_VERSION:
        LOGGER.warning(
            "Azure classifier requires AZURE_API_BASE, AZURE_API_KEY, AZURE_API_VERSION"
        )
        return False

    try:
        client, model_for_api = create_llm_client()
    except Exception as exc:  # pragma: no cover - setup failure
        LOGGER.warning("Unable to initialise classifier client: %s", exc)
        return False

    if AZURE_API_BASE:
        wrapped_client = wrap_openai(client)
        autoevals_init(wrapped_client)  # type: ignore[arg-type]
    else:
        autoevals_init(client)  # type: ignore[arg-type]

    _model_for_api = model_for_api
    _client_available = True
    return True


@lru_cache(maxsize=4)
def _prompt_for(evaluation_type: str) -> str:
    if evaluation_type == "loose":
        return _LOOSE_PROMPT
    return _STRICT_PROMPT


@lru_cache(maxsize=4)
def _classifier_for(evaluation_type: str) -> Optional[LLMClassifier]:
    if not _ensure_client():
        return None
    prompt = _prompt_for(evaluation_type)
    return LLMClassifier(  # type: ignore[call-arg]
        name="Correctness",
        prompt_template=prompt,
        choice_scores={"A": 1, "B": 0},
        use_cot=True,
        model=CLASSIFIER_MODEL,
        api_key=AZURE_API_KEY,
        base_url=AZURE_API_BASE,
        api_version=AZURE_API_VERSION,
    )


def _normalise_expected(expected: Sequence[str] | str) -> List[str]:
    if isinstance(expected, str):
        return [expected]
    return [str(item) for item in expected]


def evaluate_correctness(
    *,
    expected_elements: Sequence[str] | str,
    output: Optional[str],
    parent_span: Optional[Span] = None,
    evaluation_type: Optional[str] = None,
    caplog=None,
):
    evaluation_type = (evaluation_type or DEFAULT_EVALUATION_TYPE or "strict").strip().lower()
    if evaluation_type not in {"strict", "loose"}:
        evaluation_type = "strict"

    if caplog is not None:
        caplog.set_level("INFO", logger="classifier")
    logger = logging.getLogger("classifier")

    classifier = _classifier_for(evaluation_type)
    if classifier is None:
        logger.info("Classifier unavailable; skipping semantic evaluation")
        return None

    expected_list = _normalise_expected(expected_elements)
    expected_str = "\n- ".join(expected_list)
    prompt_template = _prompt_for(evaluation_type)

    logger.info(
        "Evaluating correctness with Azure OpenAI; base_url=%s, api_version=%s, model=%s",
        AZURE_API_BASE,
        AZURE_API_VERSION,
        CLASSIFIER_MODEL,
    )

    def _run():
        return classifier(  # type: ignore[operator]
            input=prompt_template,
            output=output,
            expected=expected_str,
        )

    if parent_span:
        with parent_span.start_span(
            name="Correctness", type=SpanTypeAttribute.SCORE
        ) as span:
            result = _run()
            span.log(
                input=prompt_template,
                output=result.metadata.get("rationale", ""),
                expected=expected_str,
                scores={"correctness": result.score},
                metadata=result.metadata,
            )
            return result
    return _run()


def create_llm_client():
    if openai is None:
        raise RuntimeError("openai package not available")
    if not AZURE_API_BASE or not AZURE_API_KEY or not AZURE_API_VERSION:
        raise ValueError("Azure OpenAI classifier requires AZURE_API_BASE, AZURE_API_KEY, AZURE_API_VERSION")

    model_name = CLASSIFIER_MODEL or "azure/deployment"
    if model_name.startswith("azure/"):
        parts = model_name.split("/", 1)
        if len(parts) != 2:
            raise ValueError(
                "CLASSIFIER_MODEL must follow 'azure/<deployment>' when using Azure OpenAI"
            )
        deployment = parts[1]
    else:
        deployment = model_name

    client = openai.AzureOpenAI(  # type: ignore[attr-defined]
        azure_endpoint=AZURE_API_BASE,
        azure_deployment=deployment,
        api_version=AZURE_API_VERSION,
        api_key=AZURE_API_KEY,
    )
    return client, deployment
