# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
import base64
import json
import os
import re
import shutil
import sys
import time
from datetime import datetime

import azext_arcdata.core.kubernetes as kubernetes_util
import yaml
from azext_arcdata.core.constants import (
    ARC_GROUP,
    AZDATA_PASSWORD,
    AZDATA_USERNAME,
    DATA_CONTROLLER_CRD_VERSION,
    DATA_CONTROLLER_PLURAL,
    USE_K8S_EXCEPTION_TEXT,
)
from azext_arcdata.core.labels import parse_labels
from azext_arcdata.core.prompt import prompt, prompt_pass
from azext_arcdata.core.util import (
    FileUtil,
    check_and_set_kubectl_context,
    get_config_from_template,
    is_windows,
    retry,
)
from azext_arcdata.kubernetes_sdk.client import (
    K8sApiException,
    KubernetesError,
    http_status_codes,
)
from azext_arcdata.kubernetes_sdk.errors.K8sAdmissionReviewError import (
    K8sAdmissionReviewError,
)
from azext_arcdata.kubernetes_sdk.models.custom_resource import CustomResource
from azext_arcdata.kubernetes_sdk.models.data_controller_custom_resource import (
    DataControllerCustomResource,
)
from azext_arcdata.sqlmidb.constants import (
    RESTORE_TASK_RESOURCE_KIND,
    RESTORE_TASK_RESOURCE_KIND_PLURAL,
    TASK_API_GROUP,
    TASK_API_VERSION,
)
from azext_arcdata.sqlmidb.exceptions import SqlmidbError
from azext_arcdata.sqlmidb.models.restore_cr_model import (
    SqlmiRestoreTaskCustomResource,
)
from azext_arcdata.sqlmidb.util import parse_restore_time
from humanfriendly.terminal.spinners import AutomaticSpinner
from knack.cli import CLIError
from knack.log import get_logger
from urllib3.exceptions import MaxRetryError, NewConnectionError

logger = get_logger(__name__)


def arc_sql_midb_restore(
    client,
    namespace=None,
    managed_instance=None,
    name=None,
    dest_name=None,
    time=None,
    use_k8s=None,
    nowait=None,
    dry_run=None,
):
    """
    Restores SQL MI to a PITR
    :param client:
    :param namespace:
    :param managed_instance : The name of the source sql managed instance.
    :param name: The source db from where the backups should be restored.
    :param dest_name: The name of the database at the destination server
                      where backup is to be restored to.
    :param time: "The Point in time, within the retention time to
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

        if time is None:
            time = parse_restore_time(str(datetime.now()))

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
                },
                "restorePoint": time,
                "dryRun": dry_run,
                "destination": {
                    "name": managed_instance,
                    "database": dest_name,
                },
            },
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
            elif state == "Failed":
                raise Exception(
                    "Failed to restore the backup. {}".format(
                        status.get("message")
                    )
                )
            time.sleep(delay)
            delay = min(60, delay * 2)


def _get_json_output(cr: CustomResource):
    output_dict = {
        "sourceDatabase": cr.get("spec", {})
        .get("source", {})
        .get("database", {}),
        "destDatabase": cr.get("spec", {})
        .get("destination", {})
        .get("database", {}),
        "restorePoint": cr.get("spec", {}).get("restorePoint", {}),
    }
    output_dict.update(cr.get("status", {}))
    return json.dumps(output_dict, indent=4)
