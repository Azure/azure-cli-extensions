# CDN and AFD Extension Testing

## Environment configuration

The committed [config.json](config.json) defines the shared test subscription,
cloud, ARM endpoint, fixtures, and recording/playback timeout budgets.
Recording selects the configured subscription in memory without changing the
user's default Azure CLI subscription. The configured cloud and subscription
must already be available in the Azure CLI account cache. Playback uses the
test SDK's mock subscription and does not require live credentials.

Put personal overrides in `config.local.json` in this directory (Git ignored),
or pass `--config <path>` to the runner. Overrides are merged into `config.json`.
`AZURE_CDN_TEST_SUBSCRIPTION_ID`, `AZURE_CDN_TEST_CLOUD`, and
`AZURE_CDN_TEST_ARM_ENDPOINT` override the corresponding settings.
Do not put credentials in configuration files.

Classic CDN tests reuse the configured existing `Standard_Microsoft` profile,
matching the Azure PowerShell fixture pattern. `AZURE_CDN_TEST_PROFILE_ID` can
override this fixture. Tests never delete the shared profile or overwrite its
existing endpoints; they clean up their own endpoints and restore profile tags.
New Classic profile creation and domain onboarding are tested as expected
service rejections.

The two Classic custom-domain HTTPS scenarios instead reuse the existing
endpoints and domains identified by `classic_byoc_latest_endpoint_id` and
`classic_https_endpoint_id`. Only those scenarios select the subscription from
their endpoint fixture ID. They verify the deployed certificate configuration
and repeat HTTPS enablement with the same parameters; they do not create or
delete domains/endpoints, disable HTTPS, or change DNS records.
State checks accept either a deployed certificate or the observed asynchronous
enablement substate for the configured certificate source.

## Running scenarios

In the activated azdev environment with CDN registered, run from `src\cdn`:

```powershell
python -m azext_cdn.tests.latest.run_tests replay --list
python -m azext_cdn.tests.latest.run_tests replay
python -m azext_cdn.tests.latest.run_tests replay test_afd_log_analytic test_afd_waf_log_analytic
python -m azext_cdn.tests.latest.run_tests record
```

Use the runner, rather than a direct pytest/azdev test invocation, to enforce
the timeout budgets in `config.json`. Each scenario runs in a separate process.
A deadline terminates that process, reports a timeout, and allows other cases
to run within the remaining batch budget. The worker emits thread diagnostics
before its deadline. Playback blocks network access and refuses missing recordings.

## Results and cleanup

Logs, per-case JUnit XML, and `results.json` are written under `src\cdn\.test-results\`
(Git ignored), or `--output-dir <path>`. Failed/timed-out recording captures are
preserved there and the previous cassette is restored.

Forced termination cannot run unittest cleanup. Inspect the log and shared
resources before retrying; never delete the shared Classic profile or its
preexisting endpoints.
