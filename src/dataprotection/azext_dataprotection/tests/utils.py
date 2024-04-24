# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

import time


def wait_for_job_exclusivity_on_datasource(test, data_source_id=None):
    """ Checks if any job is in progress for pre-set datasource type and
        waits for its completion. Requires dataSourceType and dataSourceId kwargs.
    """
    if data_source_id:
        test.kwargs.update({'dataSourceId': data_source_id})
    if not test.kwargs.get('dataSourceId'):
        return
    jobs_in_progress = test.cmd('az dataprotection job list-from-resourcegraph --datasource-type "{dataSourceType}" --datasource-id "{dataSourceId}" --status "InProgress"').get_output_in_json()
    while jobs_in_progress:
        time.sleep(10)
        jobs_in_progress = test.cmd('az dataprotection job list-from-resourcegraph --datasource-type "{dataSourceType}" --datasource-id "{dataSourceId}" --status "InProgress"').get_output_in_json()


def track_job_to_completion(test, job_id=None):
    """ Takes jobId as input and tracks it to till it is completed.
    """
    if job_id:
        test.kwargs.update({'jobId': job_id})
    if not test.kwargs.get('jobId'):
        raise Exception("'jobId' not provided.")
    job_status = None
    while job_status != "Completed":
        time.sleep(10)
        job_response = test.cmd('az dataprotection job show --ids "{jobId}"').get_output_in_json()
        job_status = job_response["properties"]["status"]
        if job_status not in ["Completed", "InProgress"]:
            raise Exception("Undefined job status received")


def get_midpoint_of_time_range(start_time_str, end_time_str):
    """ Takes start time and end time strings as input and returns mid point as string
        in ISO format.
    """
    import dateutil.parser as dparser
    try:
        start_time = dparser.parse(start_time_str)
        end_time = dparser.parse(end_time_str)
        point_in_time = start_time + (end_time - start_time) / 2
        return point_in_time.strftime("%Y-%m-%dT%H:%M:%S")
    except:
        raise Exception('One or more input dates are invalid.')
