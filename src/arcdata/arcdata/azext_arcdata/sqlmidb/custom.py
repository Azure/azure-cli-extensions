from datetime import datetime
import json
import time
from knack.log import get_logger
from knack.cli import CLIError
from humanfriendly.terminal.spinners import AutomaticSpinner

# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.core.constants import USE_K8S_EXCEPTION_TEXT
from azext_arcdata.core.util import check_and_set_kubectl_context, is_windows
from azext_arcdata.vendored_sdks.kubernetes_sdk.models.custom_resource import CustomResource
from azext_arcdata.sqlmidb.constants import (
    RESTORE_TASK_RESOURCE_KIND,
    RESTORE_TASK_RESOURCE_KIND_PLURAL,
    TASK_API_GROUP,
    TASK_API_VERSION,
)
from azext_arcdata.vendored_sdks.kubernetes_sdk.models.restore_cr_model import SqlmiRestoreTaskCustomResource

logger = get_logger(__name__)


def arc_sql_midb_restore(
    client,
    namespace=None,
    managed_instance=None,
    name=None,
    dest_name=None,  # pylint: disable=unused-argument
    restore_time=None,
    use_k8s=None,
    nowait=None,
    dry_run=None,  # pylint: disable=unused-argument
):
    """
    Restores SQL MI to a PITR
    :param client:
    :param namespace:
    :param managed_instance : The name of the source sql managed instance.
    :param name: The source db from where the backups should be restored.
    :param dest_name: The name of the database at the destination server
                      where backup is to be restored to.
    :param restore_time: "The Point in time, within the retention time to
                  restore to, specified as a timestamp in UTC format.
                  If not provided current
                  timestamp will be used and thus last available
                  backup will be restored."
    :param use_k8s:
    :return:
    """

    try:
        if not use_k8s:
            raise ValueError(USE_K8S_EXCEPTION_TEXT)

        check_and_set_kubectl_context()
        namespace = namespace or client.namespace

        # if dest_mi is None:
        #     dest_mi = managed_instance

        if restore_time is None:
            restore_time = str(datetime.now())

        task_name = "sql-restore-" + str(datetime.timestamp(datetime.now()))
        spec_object = {
            "apiVersion": TASK_API_GROUP + "/" + TASK_API_VERSION,
            "kind": RESTORE_TASK_RESOURCE_KIND,
            "metadata": {
                "name": task_name,
            },
            "spec": {
                "source": {
                    "name": managed_instance,
                    "database": name,
                }
            }
        }

        cr = CustomResource.decode(SqlmiRestoreTaskCustomResource, spec_object)
        cr.metadata.namespace = namespace
        cr.validate(client.apis.kubernetes)
        res = client.apis.kubernetes.create_namespaced_custom_object(
            cr=cr,
            plural=RESTORE_TASK_RESOURCE_KIND_PLURAL,
            ignore_conflict=True,
        )
        if nowait is None:
            if not is_windows():
                with AutomaticSpinner(
                    "Running",
                    show_time=True,
                ):
                    res = _check_restore_status(
                        client, task_name, namespace=namespace
                    )
            else:
                res = _check_restore_status(
                    client,
                    task_name,
                    namespace=namespace,
                )
            client.stdout(_get_json_output(res))
    except Exception as e:
        raise CLIError(e)


def _check_restore_status(client, task_name: str, namespace=None):
    delay = 1
    last_message = None

    while True:
        task = client.apis.kubernetes.get_namespaced_custom_object(
            namespace=namespace,
            name=task_name,
            group=TASK_API_GROUP,
            version=TASK_API_VERSION,
            plural=RESTORE_TASK_RESOURCE_KIND_PLURAL,
        )

        status = task.get("status", {})
        message = status.get("message")
        if message != last_message:
            last_message = message
            state = status.get("state")
            if state == "Completed":
                return task
            if state == "Failed":
                raise RuntimeError(
                    "Failed to restore the backup. {}".format(
                        status.get("message")
                    )
                )
            time.sleep(delay)
            delay = min(60, delay * 2)


def _get_json_output(cr: CustomResource):
    output_dict = {
        "sourceDatabase": cr.get("spec", {}).get("source", {}).get("database", {}),
        "restorePoint": cr.get("spec", {}).get("restorePoint", {}),
    }
    output_dict.update(cr.get("status", {}))
    return json.dumps(output_dict, indent=4)
