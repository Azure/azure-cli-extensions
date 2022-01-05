from datetime import datetime
from azure.cli.core.util import CLIError

def validate_datetime_format(namespace):
    format = '%Y-%m-%d %H:%M:%S' #'%m/%d/%Y'
    if namespace.schedule_start_datetime:
        datetime.strptime(namespace.schedule_start_datetime, format)
    if namespace.schedule_end_datetime:
        datetime.strptime(namespace.schedule_end_datetime, format)
        if namespace.schedule_start_datetime:
            if namespace.schedule_end_datetime < namespace.schedule_start_datetime:
                raise CLIError('Argument Error: end-date is before start-date')

def validate_time_format(namespace):
    format = '%H:%M:%S'
    if namespace.schedule_recurrence_start_time:
        datetime.strptime(namespace.schedule_recurrence_start_time, format)
    if namespace.schedule_recurrence_end_time:
        datetime.strptime(namespace.schedule_recurrence_end_time, format)

def validate_severity(namespace):
    if namespace.filter_severity:
        for x in namespace.filter_severity:
            if x not in ['Equals', 'NotEquals', 'Sev0', 'Sev1', 'Sev2', 'Sev3', 'Sev4']:
                raise CLIError('Argument Error: filter-severity values have to be one of [Equals, NotEquals, Sev0, Sev1, Sev2, Sev3, Sev4]')

def validate_monitor_condition(namespace):
    if namespace.filter_monitor_condition:
        for x in namespace.filter_monitor_condition:
            if x not in ['Equals', 'NotEquals', 'Fired', 'Resolved']:
                raise CLIError('Argument Error: filter-monitor-condition values have to be one of [Equals, NotEquals, Fired, Resolved]')

def validate_signal_type(namespace):
    if namespace.filter_signal_type:
        for x in namespace.filter_signal_type:
            if x not in ['Equals', 'NotEquals', 'Metric', 'Log', 'Unknown']:
                raise CLIError('Argument Error: filter-signal-type values have to be one of [Equals, NotEquals, Metric, Log, Unknown]')
