# AKS Agent Evals

## Environment Setup

Create and activate a virtual environment (example shown for bash-compatible shells):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Optional tooling used by the eval harness (Braintrust uploads and semantic classifier helpers):

```bash
python -m pip install braintrust openai autoevals
```

## Running Live Scenarios

```bash
RUN_LIVE=true \
MODEL=azure/gpt-4.1 \
CLASSIFIER_MODEL=azure/gpt-4o \
AKS_AGENT_RESOURCE_GROUP=<rg> \
AKS_AGENT_CLUSTER=<cluster> \
KUBECONFIG=<path-to-kubeconfig> \
AZURE_API_KEY=<key> \
AZURE_API_BASE=<endpoint> \
AZURE_API_VERSION=<version> \
python -m pytest azext_aks_agent/tests/evals/test_ask_agent.py -k 01_list_all_nodes -m aks_eval
```

Per-scenario overrides (`resource_group`, `cluster_name`, `kubeconfig`, `test_env_vars`) still apply. Use `--skip-setup` or `--skip-cleanup` to bypass hooks. Expect the test to log iteration progress, classifier scores, and (on the final iteration) a Braintrust link when uploads are enabled.

**Example output (live run with classifier)**

```
[iteration 1/3] running setup commands for 01_list_all_nodes
[iteration 1/3] invoking AKS Agent CLI for 01_list_all_nodes
[iteration 1/3] classifier score for 01_list_all_nodes: 1
[iteration 2/3] invoking AKS Agent CLI for 01_list_all_nodes
[iteration 2/3] classifier score for 01_list_all_nodes: 1
[iteration 3/3] invoking AKS Agent CLI for 01_list_all_nodes
[iteration 3/3] classifier score for 01_list_all_nodes: 1
...
🔍 Braintrust: https://www.braintrust.dev/app/<org>/p/aks-agent/experiments/aks-agent/... 
```

## Mock Workflow

```bash
# Generate fresh mocks from a live run
RUN_LIVE=true GENERATE_MOCKS=true \
MODEL=azure/gpt-4.1 \
AKS_AGENT_RESOURCE_GROUP=<rg> \
AKS_AGENT_CLUSTER=<cluster> \
KUBECONFIG=<path-to-kubeconfig> \
AZURE_API_KEY=<key> \
AZURE_API_BASE=<endpoint> \
AZURE_API_VERSION=<version> \
python -m pytest azext_aks_agent/tests/evals/test_ask_agent.py -k 02_list_clusters -m aks_eval

# Re-run offline using the recorded response
python -m pytest azext_aks_agent/tests/evals/test_ask_agent.py -k 02_list_clusters -m aks_eval
```

If a mock is missing, pytest skips the scenario with instructions to regenerate it.

**Regression guardrails**

- Mocked answers make iterations deterministic, so you can update parsing or prompts without waiting on live infrastructure.
- If you check in a new mock after behavior changes, reviewers see the exact diff in `mocks/response.txt`, making regressions obvious.
- CI can run `RUN_LIVE` off by default, catching logical regressions early without needing cluster credentials.


**Example skip (no mock present)**

```
azext_aks_agent/tests/evals/test_ask_agent.py::test_ask_agent_live[02_list_clusters]
  SKIPPED: Mock response missing for scenario 02_list_clusters; rerun with RUN_LIVE=true GENERATE_MOCKS=true
```

## Braintrust Uploads

Set the following environment variables to push results:

- `BRAINTRUST_API_KEY` and `BRAINTRUST_ORG` (required)
- Optional overrides: `BRAINTRUST_PROJECT` (default `aks-agent`), `BRAINTRUST_DATASET` (default `aks-agent/ask`), `EXPERIMENT_ID`

Each iteration logs to Braintrust; the console prints a clickable link (for aware terminals) when uploads succeed.

**Tips**

- Leave `EXPERIMENT_ID` unset to generate a fresh experiment name each run (`aks-agent/<model>/<run-id>`).
- Use `BRAINTRUST_RUN_ID=<custom>` if you want deterministic experiment names across retries.
- The upload payload includes classifier score, rationale, raw CLI output, cluster, and resource group metadata for later filtering.

## Semantic Classifier

- Enabled by default; set `ENABLE_CLASSIFIER=false` to opt out.
- Requires Azure OpenAI credentials: `AZURE_API_BASE`, `AZURE_API_KEY`, `AZURE_API_VERSION`, and a classifier deployment specified via `CLASSIFIER_MODEL` (e.g. `azure/<deployment>`). Defaults to the same deployment as `MODEL` when not provided.
- Install classifier dependencies when online (see Environment Setup above if not already installed).

- Scenarios can override the grading style by adding:

  ```yaml
  evaluation:
    correctness:
      type: loose  # or strict (default)
  ```

Classifier scores and rationales are attached to Braintrust uploads and printed in the pytest output metadata.

**Debugging classifiers**

```
python -m pytest ... -o log_cli=true -o log_cli_level=DEBUG -s
```

Look for `classifier score ...` lines to confirm the semantic judge executed.

## Iterations & Tags

- `ITERATIONS=<n>` repeats every scenario, useful for non-deterministic models.
- Filter suites with pytest markers: `-m aks_eval`, `-m easy`, `-m medium`, etc.

## Troubleshooting

- Missing mocks: rerun with `RUN_LIVE=true GENERATE_MOCKS=true`.
- Cleanup always executes unless `--skip-cleanup` is provided; check the `[cleanup]` log line.
- Braintrust disabled messages mean credentials or the SDK are missing.
- Classifier disabled messages usually indicate missing Azure settings (`AZURE_API_BASE`, `AZURE_API_KEY`, `AZURE_API_VERSION`).

## Quick Checklist

- Install dependencies inside a virtual environment (`python -m pip install -e .`) and, if needed, the optional tooling (`python -m pip install braintrust openai autoevals`).
- `RUN_LIVE=true`: set Azure creds (`AZURE_API_KEY`, `AZURE_API_BASE`, `AZURE_API_VERSION`), `MODEL`, kubeconfig, and optional Braintrust vars.
- `RUN_LIVE` unset/false: ensure each scenario directory has `mocks/response.txt`.
- Classifier overrides: `CLASSIFIER_MODEL` (defaults to `MODEL`) and per-scenario `evaluation.correctness.type`.
- Optional: `BRAINTRUST_RUN_ID=<identifier>` to reuse experiment names across retries.
