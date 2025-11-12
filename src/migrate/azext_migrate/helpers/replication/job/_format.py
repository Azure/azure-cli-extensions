# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Job formatting utilities for Azure Migrate local replication jobs.
"""


def calculate_duration(start_time, end_time):
    """
    Calculate duration between two timestamps.

    Args:
        start_time (str): ISO format start time
        end_time (str, optional): ISO format end time

    Returns:
        str: Formatted duration string or None
    """
    if not start_time:
        return None

    from datetime import datetime
    try:
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        if end_time:
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            duration = end - start
            total_seconds = int(duration.total_seconds())
            minutes, seconds = divmod(total_seconds, 60)
            hours, minutes = divmod(minutes, 60)

            if hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        else:
            # Job still running
            now = datetime.utcnow()
            duration = now - start
            total_seconds = int(duration.total_seconds())
            minutes, seconds = divmod(total_seconds, 60)
            hours, minutes = divmod(minutes, 60)

            if hours > 0:
                return f"{hours}h {minutes}m (in progress)"
            elif minutes > 0:
                return f"{minutes}m {seconds}s (in progress)"
            else:
                return f"{seconds}s (in progress)"
    except Exception:
        return None


def format_job_output(job_details):
    """
    Format job details into a clean, user-friendly output.

    Args:
        job_details (dict): Raw job details from the API

    Returns:
        dict: Formatted job information
    """
    props = job_details.get('properties', {})

    # Extract key information
    formatted = {
        'jobName': job_details.get('name'),
        'displayName': props.get('displayName'),
        'state': props.get('state'),
        'vmName': props.get('objectInternalName'),
        'startTime': props.get('startTime'),
        'endTime': props.get('endTime'),
        'duration': calculate_duration(
            props.get('startTime'),
            props.get('endTime'))}

    # Add error information if present
    errors = props.get('errors', [])
    if errors:
        formatted['errors'] = [
            {
                'message': err.get('message'),
                'code': err.get('code'),
                'recommendation': err.get('recommendation')
            }
            for err in errors
        ]

    # Add task progress
    tasks = props.get('tasks', [])
    if tasks:
        formatted['tasks'] = [
            {
                'name': task.get('taskName'),
                'state': task.get('state'),
                'duration': calculate_duration(task.get('startTime'), task.get('endTime'))
            }
            for task in tasks
        ]

    return formatted


def format_job_summary(job_details):
    """
    Format job details into a summary for list output.

    Args:
        job_details (dict): Raw job details from the API

    Returns:
        dict: Formatted job summary
    """
    props = job_details.get('properties', {})
    errors = props.get('errors') or []

    return {
        'jobName': job_details.get('name'),
        'displayName': props.get('displayName'),
        'state': props.get('state'),
        'vmName': props.get('objectInternalName'),
        'startTime': props.get('startTime'),
        'endTime': props.get('endTime'),
        'duration': calculate_duration(
            props.get('startTime'),
            props.get('endTime')),
        'hasErrors': len(errors) > 0}
