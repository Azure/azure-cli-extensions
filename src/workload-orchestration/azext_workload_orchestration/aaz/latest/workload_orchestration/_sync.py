# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

from azure.cli.core.aaz import *
import logging
from azext_workload_orchestration.aaz.latest.workload_orchestration._resync_target_helper import process_targets_in_parallel
from azext_workload_orchestration.aaz.latest.workload_orchestration._resource_validator import ValidateResourceExists

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


@register_command(
    "workload-orchestration sync",
)
class Sync(AAZCommand):
    """Sync workload orchestration resources for a custom location

    :example: Sync resources for a custom location
        az workload-orchestration sync --custom-location /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.ExtendedLocation/customLocations/myCustomLocation
    """

    _aaz_info = {
        "version": "2025-06-01",
    }

    def _handler(self, command_args):
        super()._handler(command_args)
        self._execute_operations()
        return self._output()

    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)

        _args_schema = cls._args_schema
        _args_schema.custom_location = AAZStrArg(
            options=["--custom-location"],
            help="The resource ID of the custom location.",
            required=True,
        )
        _args_schema.local_connected_registry_ip = AAZStrArg(
            options=["--local-connected-registry-ip"],
            help=(
                "IP address of the local connected registry on the new cluster. "
                "Not required if staging is not enabled for any solutions. "
                "If staging is enabled and this value is not provided, syncing those solutions will fail. "
                "When provided, the value is set in the configuration and a new revision for the solutions with staging enabled is installed."
            ),
            required=False,
        )
        return cls._args_schema

    def _execute_operations(self):
        self.pre_operations()

        # Step 0: Validate the custom location argument and confirm the resource exists
        _log_step("[Step 0] Validating custom location...")
        custom_location_id = str(self.ctx.args.custom_location)
        import re
        from azure.cli.core.azclierror import InvalidArgumentValueError as _InvalidArgError
        _CUSTOM_LOCATION_RE = re.compile(
            r"^/subscriptions/[^/]+/resourceGroups/[^/]+/providers/"
            r"Microsoft\.ExtendedLocation/customLocations/[^/]+$",
            re.IGNORECASE,
        )
        if not _CUSTOM_LOCATION_RE.match(custom_location_id):
            raise _InvalidArgError(
                f"'{custom_location_id}' is not a valid custom location resource ID. "
                "Expected format: /subscriptions/<sub>/resourceGroups/<rg>/providers/"
                "Microsoft.ExtendedLocation/customLocations/<name>"
            )
        ValidateResourceExists(
            ctx=self.ctx,
            resource_id=custom_location_id,
            resource_label="Custom Location",
            api_version="2021-08-31-preview",
        )()
        _log_step("[Step 0] Custom location validated.")

        # Step 1: Get all succeeded targets associated with the custom location via ARG
        _log_step("[Step 1/3] Querying targets for the given custom location...")
        query_op = self.TargetsArgQuery(ctx=self.ctx)
        try:
            query_op()
            self._targets = query_op._result
            _log_step("[Step 1/3] Query succeeded: found %d target(s).", len(self._targets))
        except Exception as exc:
            _log_step("[Step 1/3] Query failed: %s", exc)
            raise

        if not self._targets:
            logger.warning("No targets found for the given custom location.")
            self.post_operations()
            return

        # Display targets to the user
        print(f"\nFound {len(self._targets)} target(s) for the custom location:")
        print(f"  {'#':<4} {'Subscription':<38} {'Resource Group':<30} {'Target Name'}")
        print(f"  {'-'*4} {'-'*38} {'-'*30} {'-'*30}")
        for i, target in enumerate(self._targets):
            print(f"  [{i + 1}]  {target.get('subscriptionId', ''):<38} {target.get('resourceGroup', ''):<30} {target.get('name', '')}")

        # Step 2: Determine which targets to sync
        _log_step("[Step 2/3] Determining which targets to sync...")
        selected_targets = self._targets
        from knack.prompting import prompt
        user_input = prompt(
            "\nEnter the numbers of the targets to sync (e.g. 1,3) or press Enter to sync all: "
        )
        if user_input.strip():
            from azure.cli.core.azclierror import InvalidArgumentValueError
            try:
                indices = [int(x.strip()) - 1 for x in user_input.split(",")]
                selected_targets = [self._targets[i] for i in indices if 0 <= i < len(self._targets)]
                if not selected_targets:
                    raise InvalidArgumentValueError("No valid targets selected.")
            except ValueError:
                raise InvalidArgumentValueError(
                    "Invalid input. Please enter comma-separated numbers from the list."
                )
        _log_step("[Step 2/3] %d target(s) selected for sync.", len(selected_targets))

        # Step 3: Re-sync selected targets in parallel (10 at a time)
        _log_step("[Step 3/3] Starting sync for %d selected target(s)...", len(selected_targets))
        local_connected_registry_ip = str(self.ctx.args.local_connected_registry_ip) if self.ctx.args.local_connected_registry_ip else None
        results = process_targets_in_parallel(self.ctx, selected_targets, local_connected_registry_ip=local_connected_registry_ip)
        _log_step("[Step 3/3] Sync completed.")

        # Final summary
        print("\nSync Summary:")
        print(f"  {'Target':<35} {'Solution':<45} {'Status'}")
        print(f"  {'-'*35} {'-'*45} {'-'*20}")
        for r in results:
            target_name = r["target"]
            if r["put_error"]:
                print(f"  {target_name:<35} {'-':<45} FAILED (sync): {r['put_error']}")
                continue
            failed_map = {name: msg for name, msg in r["install_errors"]}
            staged_map = {name: new_id for name, new_id in r.get("staged_installs", [])}
            skipped_staged = set(r.get("skipped_staged", []))
            all_solutions = (
                r["installed"]
                + [name for name, _ in r.get("staged_installs", [])]
                + [name for name, _ in r["install_errors"]]
                + r.get("skipped_staged", [])
            )
            if not all_solutions:
                print(f"  {target_name:<35} {'(no deployed solutions)':<45} OK")
                continue
            for i, sol in enumerate(all_solutions):
                label = target_name if i == 0 else ""
                if sol in skipped_staged:
                    status = "SKIPPED (staging enabled, --local-connected-registry-ip not provided)"
                elif sol in staged_map:
                    new_id = staged_map[sol]
                    new_ver = new_id.rstrip("/").split("/")[-1] if new_id else "?"
                    status = f"OK (staged, new version: {new_ver})"
                elif sol in failed_map:
                    status = f"FAILED: {failed_map[sol]}"
                else:
                    status = "OK"
                print(f"  {label:<35} {sol:<45} {status}")

        self._synced_targets = selected_targets
        self.post_operations()

    class TargetsArgQuery(AAZHttpOperation):
        CLIENT_TYPE = "MgmtClient"

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
            custom_location = self.ctx.args.custom_location.to_serialized_data()
            body = {
                "query": (
                    "Resources"
                    " | where type =~ 'Microsoft.Edge/targets'"
                    f" | where extendedLocation.name =~ '{custom_location}'"
                    " | where properties.provisioningState =~ 'Succeeded'"
                    " | project id, name, location, resourceGroup, subscriptionId,"
                    "           extendedLocation, properties, tags"
                ),
                "options": {
                    "resultFormat": "objectArray"
                }
            }
            return self.serialize_content(body)

        def on_200(self, session):
            data = self.deserialize_http_content(session)
            self._result = data.get("data", [])

    @register_callback
    def pre_operations(self):
        pass

    @register_callback
    def post_operations(self):
        pass

    def _output(self, *args, **kwargs):
        return None


__all__ = ["Sync"]
