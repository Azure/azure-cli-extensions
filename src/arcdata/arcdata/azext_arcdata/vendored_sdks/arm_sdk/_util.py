# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from types import SimpleNamespace
from typing import Callable
from json import JSONEncoder, dumps, loads

import time
import pydash as _


def dict_to_dot_notation(d: dict):
    class _Namespace(SimpleNamespace):
        @property
        def to_dict(self):
            class _Encoder(JSONEncoder):
                def default(self, o):
                    return o.__dict__

            return loads(dumps(self, indent=4, cls=_Encoder))

    return loads(dumps(d), object_hook=lambda item: _Namespace(**item))


def wait_for_error(
    func: Callable, *func_args, retry_tol=1800, retry_delay=5, e=Exception
):
    for _ in range(0, retry_tol, retry_delay):
        try:
            func(*func_args)
            time.sleep(retry_delay)
        except e:
            break


def wait(func: Callable, *func_args, retry_tol=1800, retry_delay=5):
    try:
        current_status = None
        for _ in range(0, retry_tol, retry_delay):
            status = func(*func_args)
            if status == "Ready" or status == "Succeeded":
                break
            elif status and "Error" in status:
                raise Exception(
                    f"An error happened while waiting. The "
                    f"deployment state is: {status}"
                )
            else:
                if current_status != status:
                    if current_status:
                        print(
                            f"Deployment state '{current_status}' "
                            f"has completed."
                        )

                    current_status = status
                    print(f"Current deployment state is '{current_status}'")

                time.sleep(retry_delay)
        # Return last observed status from our polling
        return status
    except Exception as e:
        raise e


def wait_for_upgrade(
    target, func: Callable, *func_args, retry_tol=10000, retry_delay=5
):
    try:
        for _ in range(0, retry_tol, retry_delay):
            status = func(*func_args)
            if status and status["runningVersion"] == target:
                break
            time.sleep(retry_delay)
    except Exception as e:
        raise e


def retry(func: Callable, *func_args, max_tries=10, retry_delay=5, e=Exception):
    result = None
    for i in range(max_tries):
        try:
            time.sleep(retry_delay)
            result = func(*func_args)
            break
        except e:
            continue
    return result


def conditional_retry(
    func: Callable,
    condition_func: Callable,
    max_tries=5,
    exception_type=Exception,
    **kwargs,
):
    """
    Apply func until condition_func returns True or until max_tries attempts have been made.
    """
    result = None
    tries = 0
    while not condition_func() and tries < max_tries:
        try:
            result = func(**kwargs)
        except exception_type:
            pass
        tries += 1

    return result


def poll_provisioning_state(func: Callable, *func_args, wait_time=300):
    cnt = 0
    while True:
        status = func(*func_args)
        if status == "Succeeded":
            break
        elif status == "Failed":
            raise Exception("This operation has failed.")
        elif status == "Accepted":
            if cnt < wait_time:  # total wait time in seconds
                time.sleep(5)
                cnt += 5
            else:
                raise Exception("This operation has timed out.")
        else:
            break

    return status
