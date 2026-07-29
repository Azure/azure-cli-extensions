# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

from azure.cli.core.aaz import *
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


def _log_step(msg, *args):
    """Print a step message only when --verbose is active.

    Azure CLI sets the level of the 'azure-cli' logger to INFO when --verbose
    is passed.  Extension loggers live under 'azext_*', a completely separate
    hierarchy, so logger.info() here is silently dropped even with --verbose.
    We check the 'azure-cli' logger as a reliable proxy for verbose mode and
    write directly to stdout so the message is always visible to the user.
    """
    if logging.getLogger('azure-cli').isEnabledFor(logging.INFO):
        print(msg % args if args else msg)



class TargetPut(AAZHttpOperation):
    """PUT a target to re-sync it to the new cluster."""
    CLIENT_TYPE = "MgmtClient"

    def __init__(self, ctx, target):
        super().__init__(ctx)
        self._target = target

    def __call__(self, *args, **kwargs):
        request = self.make_request()
        session = self.client.send_request(request=request, stream=False, **kwargs)
        if session.http_response.status_code == 200:
            return self.on_200_201(session)
        if session.http_response.status_code in [201, 202]:
            poller = self.client.build_lro_polling(
                False,
                session,
                self.on_200_201,
                self.on_error,
                lro_options={"final-state-via": "azure-async-operation"},
                path_format_arguments=self.url_parameters,
            )
            return poller.run()
        return self.on_error(session.http_response)

    @property
    def url(self):
        return self.client.format_url(
            "{targetId}",
            **self.url_parameters
        )

    @property
    def url_parameters(self):
        return {
            **self.serialize_url_param(
                "targetId", self._target["id"],
                required=True,
                skip_quote=True,
            ),
        }

    @property
    def method(self):
        return "PUT"

    @property
    def error_format(self):
        return "MgmtErrorFormat"

    @property
    def query_parameters(self):
        return {
            **self.serialize_query_param("api-version", "2025-08-01", required=True),
        }

    @property
    def header_parameters(self):
        return {
            **self.serialize_header_param("Content-Type", "application/json"),
            **self.serialize_header_param("Accept", "application/json"),
        }

    @property
    def content(self):
        body = {
            "location": self._target.get("location"),
            "extendedLocation": self._target.get("extendedLocation"),
            "properties": self._target.get("properties"),
            "tags": self._target.get("tags"),
        }
        return self.serialize_content(body)

    def on_200_201(self, session):
        pass


class TargetGet(AAZHttpOperation):
    """GET a target to check its provisioning state."""
    CLIENT_TYPE = "MgmtClient"

    def __init__(self, ctx, target):
        super().__init__(ctx)
        self._target = target

    def __call__(self, *args, **kwargs):
        request = self.make_request()
        session = self.client.send_request(request=request, stream=False, **kwargs)
        if session.http_response.status_code == 200:
            return self.on_200(session)
        return self.on_error(session.http_response)

    @property
    def url(self):
        return self.client.format_url("{targetId}", **self.url_parameters)

    @property
    def url_parameters(self):
        return {
            **self.serialize_url_param(
                "targetId", self._target["id"],
                required=True,
                skip_quote=True,
            ),
        }

    @property
    def method(self):
        return "GET"

    @property
    def error_format(self):
        return "MgmtErrorFormat"

    @property
    def query_parameters(self):
        return {**self.serialize_query_param("api-version", "2025-08-01", required=True)}

    @property
    def header_parameters(self):
        return {**self.serialize_header_param("Accept", "application/json")}

    def on_200(self, session):
        data = self.deserialize_http_content(session)
        self._result = data


class TargetSolutionVersionsArgQuery(AAZHttpOperation):
    """Fetch all solution versions installed on a target via ARG."""
    CLIENT_TYPE = "MgmtClient"

    def __init__(self, ctx, target_id):
        super().__init__(ctx)
        self._target_id = target_id

    def __call__(self, *args, **kwargs):
        request = self.make_request()
        session = self.client.send_request(request=request, stream=False, **kwargs)
        if session.http_response.status_code == 200:
            return self.on_200(session)
        return self.on_error(session.http_response)

    @property
    def url(self):
        return self.client.format_url("/providers/Microsoft.ResourceGraph/resources")

    @property
    def method(self):
        return "POST"

    @property
    def error_format(self):
        return "MgmtErrorFormat"

    @property
    def query_parameters(self):
        return {
            **self.serialize_query_param("api-version", "2022-10-01", required=True),
        }

    @property
    def header_parameters(self):
        return {
            **self.serialize_header_param("Content-Type", "application/json"),
            **self.serialize_header_param("Accept", "application/json"),
        }

    @property
    def content(self):
        body = {
            "query": (
                "ExtensibilityResources"
                " | where type =~ 'microsoft.edge/targets/solutions/versions'"
                f" | where tolower(id) startswith tolower('{self._target_id}')"
                " | project id, name, location, resourceGroup, subscriptionId,"
                "           provisioningState = tostring(properties.provisioningState),"
                "           state = tostring(properties.state),"
                "           specification = properties.specification"
            ),
            "options": {
                "resultFormat": "objectArray"
            }
        }
        return self.serialize_content(body)

    def on_200(self, session):
        data = self.deserialize_http_content(session)
        self._result = data.get("data", [])


class TargetInstallSolution(AAZHttpOperation):
    """POST installSolution for a specific solution version on a target."""
    CLIENT_TYPE = "MgmtClient"

    def __init__(self, ctx, target, solution_version_id):
        super().__init__(ctx)
        self._target = target
        self._solution_version_id = solution_version_id

    def __call__(self, *args, **kwargs):
        request = self.make_request()
        session = self.client.send_request(request=request, stream=False, **kwargs)
        if session.http_response.status_code == 202:
            poller = self.client.build_lro_polling(
                False,
                session,
                self.on_200,
                self.on_error,
                lro_options={"final-state-via": "location"},
                path_format_arguments=self.url_parameters,
            )
            return poller.run()
        return self.on_error(session.http_response)

    @property
    def url(self):
        return self.client.format_url(
            "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}"
            "/providers/Microsoft.Edge/targets/{targetName}/installSolution",
            **self.url_parameters
        )

    @property
    def url_parameters(self):
        target_id = self._target["id"]
        parts = target_id.split("/")
        return {
            **self.serialize_url_param("subscriptionId", parts[2], required=True),
            **self.serialize_url_param("resourceGroupName", parts[4], required=True),
            **self.serialize_url_param("targetName", parts[8], required=True),
        }

    @property
    def method(self):
        return "POST"

    @property
    def error_format(self):
        return "MgmtErrorFormat"

    @property
    def query_parameters(self):
        return {
            **self.serialize_query_param("api-version", "2025-08-01", required=True),
        }

    @property
    def header_parameters(self):
        return {
            **self.serialize_header_param("Content-Type", "application/json"),
            **self.serialize_header_param("Accept", "application/json"),
        }

    @property
    def content(self):
        body = {"solutionVersionId": self._solution_version_id}
        return self.serialize_content(body)

    def on_200(self, session):
        pass


class UpdateConfigWithRegistryIp(AAZHttpOperation):
    """Fetch the DynamicConfigurationVersion for a staged solution and update LocalConnectedRegistryIP.

    Steps performed in __call__:
      1. GET the target solution version to resolve ``solutionTemplateVersionId``.
      2. Derive the config URL from the target's configurationReference.
      3. GET the existing DynamicConfigurationVersion (or prepare a new one if absent).
      4. Set LocalConnectedRegistryIP in the YAML values.
      5. PUT the updated object back.
    """
    CLIENT_TYPE = "MgmtClient"

    def __init__(self, ctx, target_id, solution_version_id, local_ip):
        super().__init__(ctx)
        self._target_id = target_id
        self._solution_version_id = solution_version_id
        self._local_ip = local_ip
        self.solution_template_version_id = None  # populated during __call__

    def __call__(self, *args, **kwargs):
        import json
        import yaml
        from azext_workload_orchestration.aaz.latest.workload_orchestration.configuration._config_helper import ConfigurationHelper

        # Step 1: GET the target solution version to find solutionTemplateVersionId
        sv_url = self.client.format_url("{svId}", svId=self._solution_version_id)
        sv_req = self.client._request(
            "GET", sv_url, {"api-version": "2025-08-01"}, {"Accept": "application/json"}, None, {}, None
        )
        sv_resp = self.client.send_request(request=sv_req, stream=False)
        if sv_resp.http_response.status_code != 200:
            raise Exception(
                f"Failed to GET solution version {self._solution_version_id}: "
                f"HTTP {sv_resp.http_response.status_code}"
            )
        sv_data = json.loads(sv_resp.http_response.text())
        self.solution_template_version_id = sv_data.get("properties", {}).get("solutionTemplateVersionId")
        if not self.solution_template_version_id:
            raise Exception(
                f"solutionTemplateVersionId not found on solution version {self._solution_version_id}"
            )

        # Extract solution template version (last segment of the ARM ID, e.g. "1.0.0")
        template_version = self.solution_template_version_id.rstrip("/").split("/")[-1]

        # Extract solutionUniqueId from solution version path:
        # .../solutions/{uniqueId}/versions/{version}
        sv_parts = self._solution_version_id.split("/")
        solution_unique_id = sv_parts[10]

        # Step 2: Get the configuration ID for this target
        config_id = ConfigurationHelper.getConfigurationId(self._target_id, self.client)

        # Step 3: GET the current DynamicConfigurationVersion
        # URL pattern (mirrors _config_set.py): {configId}/dynamicConfigurations/{uniqueId}/versions/{version}
        dcv_url = f"{config_id}/dynamicConfigurations/{solution_unique_id}/versions/{template_version}"
        dcv_req = self.client._request(
            "GET", dcv_url, {"api-version": "2025-08-01"}, {"Accept": "application/json"}, None, {}, None
        )
        dcv_resp = self.client.send_request(request=dcv_req, stream=False)

        if dcv_resp.http_response.status_code == 200:
            dcv_data = json.loads(dcv_resp.http_response.text())
            raw_values = dcv_data.get("properties", {}).get("values", "")
            try:
                values = yaml.safe_load(raw_values) or {}
            except Exception:
                values = {}
            values["LocalConnectedRegistryIP"] = self._local_ip
            # Only send properties — strip all read-only top-level fields
            body = {
                "properties": {
                    "values": yaml.dump(values, default_flow_style=False)
                }
            }
        elif dcv_resp.http_response.status_code == 404:
            body = {
                "properties": {
                    "values": yaml.dump({"LocalConnectedRegistryIP": self._local_ip}, default_flow_style=False)
                }
            }
        else:
            raise Exception(
                f"Failed to GET DynamicConfigurationVersion: HTTP {dcv_resp.http_response.status_code}"
            )

        # Step 4: PUT the updated DynamicConfigurationVersion
        serialized_body = self.serialize_content(body)
        put_req = self.client._request(
            "PUT", dcv_url,
            {"api-version": "2025-08-01"},
            {"Content-Type": "application/json", "Accept": "application/json"},
            serialized_body, {}, None
        )
        put_resp = self.client.send_request(request=put_req, stream=False)
        if put_resp.http_response.status_code not in [200, 201]:
            raise Exception(
                f"Failed to PUT DynamicConfigurationVersion: HTTP {put_resp.http_response.status_code}"
                f" - {put_resp.http_response.text()}"
            )

    # The following properties are required by the base class but are not used
    # because __call__ is fully overridden.
    @property
    def url(self):
        raise NotImplementedError

    @property
    def method(self):
        raise NotImplementedError

    @property
    def error_format(self):
        return "MgmtErrorFormat"

    @property
    def query_parameters(self):
        return {}

    @property
    def header_parameters(self):
        return {}


class ReviewStagedSolutionVersion(AAZHttpOperation):
    """POST reviewSolutionVersion for a staged solution and wait for completion."""
    CLIENT_TYPE = "MgmtClient"

    def __init__(self, ctx, target, solution_template_version_id):
        super().__init__(ctx)
        self._target = target
        self._solution_template_version_id = solution_template_version_id
        self._result = None

    def __call__(self, *args, **kwargs):
        request = self.make_request()
        session = self.client.send_request(request=request, stream=False, **kwargs)
        if session.http_response.status_code in [200, 202]:
            poller = self.client.build_lro_polling(
                False,
                session,
                self.on_200,
                self.on_error,
                lro_options={"final-state-via": "location"},
                path_format_arguments=self.url_parameters,
            )
            return poller.run()
        return self.on_error(session.http_response)

    @property
    def url(self):
        return self.client.format_url(
            "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}"
            "/providers/Microsoft.Edge/targets/{targetName}/reviewSolutionVersion",
            **self.url_parameters
        )

    @property
    def url_parameters(self):
        parts = self._target["id"].split("/")
        return {
            **self.serialize_url_param("subscriptionId", parts[2], required=True),
            **self.serialize_url_param("resourceGroupName", parts[4], required=True),
            **self.serialize_url_param("targetName", parts[8], required=True),
        }

    @property
    def method(self):
        return "POST"

    @property
    def error_format(self):
        return "MgmtErrorFormat"

    @property
    def query_parameters(self):
        return {**self.serialize_query_param("api-version", "2025-08-01", required=True)}

    @property
    def header_parameters(self):
        return {
            **self.serialize_header_param("Content-Type", "application/json"),
            **self.serialize_header_param("Accept", "application/json"),
        }

    @property
    def content(self):
        return self.serialize_content({"solutionTemplateVersionId": self._solution_template_version_id})

    def on_200(self, session):
        self._result = self.deserialize_http_content(session)


class PublishStagedSolutionVersion(AAZHttpOperation):
    """POST publishSolutionVersion for a staged solution and wait for staging to complete."""
    CLIENT_TYPE = "MgmtClient"

    def __init__(self, ctx, target, solution_version_id):
        super().__init__(ctx)
        self._target = target
        self._solution_version_id = solution_version_id

    def __call__(self, *args, **kwargs):
        request = self.make_request()
        session = self.client.send_request(request=request, stream=False, **kwargs)
        if session.http_response.status_code in [200, 202]:
            poller = self.client.build_lro_polling(
                False,
                session,
                self.on_200,
                self.on_error,
                lro_options={"final-state-via": "location"},
                path_format_arguments=self.url_parameters,
            )
            return poller.run()
        return self.on_error(session.http_response)

    @property
    def url(self):
        return self.client.format_url(
            "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}"
            "/providers/Microsoft.Edge/targets/{targetName}/publishSolutionVersion",
            **self.url_parameters
        )

    @property
    def url_parameters(self):
        parts = self._target["id"].split("/")
        return {
            **self.serialize_url_param("subscriptionId", parts[2], required=True),
            **self.serialize_url_param("resourceGroupName", parts[4], required=True),
            **self.serialize_url_param("targetName", parts[8], required=True),
        }

    @property
    def method(self):
        return "POST"

    @property
    def error_format(self):
        return "MgmtErrorFormat"

    @property
    def query_parameters(self):
        return {**self.serialize_query_param("api-version", "2025-08-01", required=True)}

    @property
    def header_parameters(self):
        return {
            **self.serialize_header_param("Content-Type", "application/json"),
            **self.serialize_header_param("Accept", "application/json"),
        }

    @property
    def content(self):
        return self.serialize_content({"solutionVersionId": self._solution_version_id})

    def on_200(self, session):
        pass


_RETRY_DELAYS = [5, 10, 20]  # seconds between retries (up to 3 retries)

_PROVISIONING_POLL_INTERVAL = 10  # seconds between provisioning state polls
_PROVISIONING_TIMEOUT = 300       # maximum seconds to wait for provisioning to settle
_TRANSITIONAL_STATES = {"accepted", "updating", "creating", "deleting"}


def _wait_for_target_provisioned(ctx, target):
    """Poll target GET until provisioningState leaves transitional states or timeout.

    Raises TimeoutError if the target has not settled within _PROVISIONING_TIMEOUT seconds.
    Returns the final provisioningState string.
    """
    target_name = target.get("name", target.get("id", ""))
    deadline = time.time() + _PROVISIONING_TIMEOUT
    while time.time() < deadline:
        get_op = TargetGet(ctx=ctx, target=target)
        get_op()
        state = (get_op._result.get("properties", {}).get("provisioningState") or "").lower()
        _log_step("[%s] Waiting for provisioning to settle, current state: '%s'.", target_name, state)
        if state not in _TRANSITIONAL_STATES:
            return state
        time.sleep(_PROVISIONING_POLL_INTERVAL)
    raise TimeoutError(
        f"Timed out after {_PROVISIONING_TIMEOUT}s waiting for target '{target_name}' "
        "to leave transitional provisioning state."
    )


def _is_staging_enabled(sv):
    """Return True if the solution version has at least one component with staged images.

    Mirrors the C# IsValidStageProperties logic:
    checks specification.components[*].properties.staged.images
    """
    try:
        specification = sv.get("specification") or {}
        components = specification.get("components", []) or []
        for component in components:
            if not isinstance(component, dict):
                continue
            staged = component.get("properties", {}).get("staged")
            if staged and staged.get("images"):
                return True
        return False
    except Exception:
        return False


def _retry_with_backoff(fn):
    """Call fn(), retrying up to 3 times with delays of 5s, 10s, 20s on failure."""
    last_exc = None
    for delay in _RETRY_DELAYS:
        try:
            return fn()
        except Exception as exc:
            last_exc = exc
            time.sleep(delay)
    # Final attempt after all retries exhausted
    try:
        return fn()
    except Exception as exc:
        raise exc from last_exc


def process_staged_solution(ctx, target, sv, local_connected_registry_ip):
    """Orchestrate a staged solution sync: update config → review → publish → install.

    Args:
        ctx: AAZCommandCtx from the parent Sync command.
        target (dict): Target object.
        sv (dict): Solution version object with staging enabled.
        local_connected_registry_ip (str): IP of the local connected registry on the new cluster.
    """
    sv_id = sv.get("id", "")
    target_id = target.get("id", "")

    target_name = target.get("name", target_id)

    # Step 1: Fetch config and update LocalConnectedRegistryIP
    _log_step("[%s] Staged '%s': Updating configuration with local registry IP...", target_name, sv_id.rstrip('/').split('/')[-1])
    config_op = UpdateConfigWithRegistryIp(
        ctx=ctx, target_id=target_id, solution_version_id=sv_id, local_ip=local_connected_registry_ip
    )
    try:
        _retry_with_backoff(config_op)
        _log_step("[%s] Staged: Configuration update succeeded.", target_name)
    except Exception as exc:
        _log_step("[%s] Staged: Configuration update failed: %s", target_name, exc)
        raise
    solution_template_version_id = config_op.solution_template_version_id

    # Step 2: Review — creates/updates the target solution version on the new cluster
    _log_step("[%s] Staged: Reviewing solution version...", target_name)
    review_op = ReviewStagedSolutionVersion(
        ctx=ctx, target=target, solution_template_version_id=solution_template_version_id
    )
    try:
        _retry_with_backoff(review_op)
        _log_step("[%s] Staged: Review succeeded.", target_name)
    except Exception as exc:
        _log_step("[%s] Staged: Review failed: %s", target_name, exc)
        raise
    # Use the solution version ID returned by review; fall back to the existing one
    new_sv_id = ((review_op._result or {}).get("id")) or sv_id

    # Step 3: Publish — triggers staging on the new cluster (downloads images)
    _log_step("[%s] Staged: Publishing solution version...", target_name)
    publish_op = PublishStagedSolutionVersion(ctx=ctx, target=target, solution_version_id=new_sv_id)
    try:
        _retry_with_backoff(publish_op)
        _log_step("[%s] Staged: Publish succeeded.", target_name)
    except Exception as exc:
        _log_step("[%s] Staged: Publish failed: %s", target_name, exc)
        raise

    # Step 4: Install
    _log_step("[%s] Staged: Installing solution version...", target_name)
    install_op = TargetInstallSolution(ctx=ctx, target=target, solution_version_id=new_sv_id)
    try:
        _retry_with_backoff(install_op)
        _log_step("[%s] Staged: Install succeeded.", target_name)
    except Exception as exc:
        _log_step("[%s] Staged: Install failed: %s", target_name, exc)
        raise
    return new_sv_id


def process_target(ctx, target, local_connected_registry_ip=None):
    """Orchestrate per-target sync: PUT the target, fetch its solution versions,
    and trigger install for each version in 'Deployed' state.

    Args:
        ctx: AAZCommandCtx from the parent Sync command.
        target (dict): A target object from the ARG query.
        local_connected_registry_ip (str|None): IP of the local connected registry on the
            new cluster. When provided, solution versions with staging enabled are detected
            and separated out for special handling.

    Returns:
        dict with keys: target, put_error, installed, install_errors, staged_solutions
    """
    target_id = target.get("id", "")
    target_name = target.get("name", target_id)
    result = {
        "target": target_name,
        "put_error": None,
        "installed": [],
        "staged_installs": [],  # list of (original_name, new_sv_id) for staged solutions
        "install_errors": [],
        "skipped_staged": [],  # list of solution names skipped: staging enabled but no registry IP
    }

    # Step A: Re-sync the target via PUT (with retries)
    _log_step("[%s] Step A: Re-syncing target via PUT...", target_name)
    try:
        _retry_with_backoff(lambda: TargetPut(ctx=ctx, target=target)())
        _log_step("[%s] Step A: Target PUT succeeded.", target_name)
    except Exception as exc:
        _log_step("[%s] Step A: Target PUT failed: %s", target_name, exc)
        result["put_error"] = str(exc)
        return result

    # Wait for the target to leave transitional provisioning states before proceeding.
    # The PUT may return 200/201 immediately while the service still transitions through
    # 'Accepted' -> 'Updating' -> 'Succeeded' asynchronously. Subsequent operations such
    # as reviewSolutionVersion will fail with InvalidResourceOperation if we proceed too
    # early.
    _log_step("[%s] Step A: Waiting for target provisioning to settle...", target_name)
    try:
        final_state = _wait_for_target_provisioned(ctx, target)
        _log_step("[%s] Step A: Target provisioning settled with state '%s'.", target_name, final_state)
    except Exception as exc:
        _log_step("[%s] Step A: Error waiting for target provisioning: %s", target_name, exc)
        result["put_error"] = str(exc)
        return result

    # Step B: Fetch installed solution versions for this target
    _log_step("[%s] Step B: Fetching installed solution versions...", target_name)
    try:
        query_op = TargetSolutionVersionsArgQuery(ctx=ctx, target_id=target_id)
        query_op()
        solution_versions = getattr(query_op, "_result", [])
        _log_step("[%s] Step B: Found %d solution version(s).", target_name, len(solution_versions))
    except Exception as exc:
        _log_step("[%s] Step B: Failed to fetch solution versions: %s", target_name, exc)
        result["put_error"] = f"Failed to fetch solution versions: {exc}"
        return result

    # Step C: Trigger install for each solution version in 'Deployed' state
    deployed = [sv for sv in solution_versions if sv.get("state", "").lower() == "deployed"]
    _log_step("[%s] Step C: Installing %d deployed solution(s)...", target_name, len(deployed))
    for sv in deployed:
        sv_id = sv.get("id", "")
        sv_name = sv.get("name", sv_id)
        if _is_staging_enabled(sv):
            if not local_connected_registry_ip:
                _log_step(
                    "[%s] Skipping solution '%s': staging enabled but --local-connected-registry-ip not provided.",
                    target_name, sv_name
                )
                result["skipped_staged"].append(sv_name)
                continue
            # Staged solution: update config then review → publish → install
            _log_step("[%s] Installing staged solution '%s'...", target_name, sv_name)
            sv_captured = sv
            try:
                new_sv_id = process_staged_solution(ctx, target, sv_captured, local_connected_registry_ip)
                result["staged_installs"].append((sv_name, new_sv_id or sv_id))
                _log_step("[%s] Staged solution '%s' installed successfully.", target_name, sv_name)
            except Exception as exc:
                _log_step("[%s] Staged solution '%s' failed: %s", target_name, sv_name, exc)
                result["install_errors"].append((sv_name, str(exc)))
            time.sleep(5)
            continue
        _log_step("[%s] Installing solution '%s'...", target_name, sv_name)
        try:
            _retry_with_backoff(
                lambda: TargetInstallSolution(ctx=ctx, target=target, solution_version_id=sv_id)()
            )
            result["installed"].append(sv_name)
            _log_step("[%s] Solution '%s' installed successfully.", target_name, sv_name)
        except Exception as exc:
            _log_step("[%s] Solution '%s' failed: %s", target_name, sv_name, exc)
            result["install_errors"].append((sv_name, str(exc)))
        time.sleep(5)

    return result


def process_targets_in_parallel(ctx, targets, batch_size=10, local_connected_registry_ip=None):
    """Process targets in parallel batches and return a summary of any errors.

    Args:
        ctx: AAZCommandCtx from the parent Sync command.
        targets (list): List of target objects to process.
        batch_size (int): Number of targets to process concurrently.
        local_connected_registry_ip (str|None): IP of the local connected registry on the
            new cluster, forwarded to process_target for staging detection.

    Returns:
        list[dict]: Results for all targets.
    """
    all_results = []
    for i in range(0, len(targets), batch_size):
        batch = targets[i:i + batch_size]
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = {
                executor.submit(process_target, ctx, target, local_connected_registry_ip): target
                for target in batch
            }
            for future in as_completed(futures):
                target = futures[future]
                try:
                    all_results.append(future.result())
                except Exception as exc:
                    all_results.append({
                        "target": target.get("name", target.get("id", "")),
                        "put_error": str(exc),
                        "installed": [],
                        "staged_installs": [],
                        "install_errors": [],
                        "skipped_staged": [],
                    })
    return all_results
