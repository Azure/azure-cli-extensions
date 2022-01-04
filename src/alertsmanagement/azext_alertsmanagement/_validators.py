from datetime import datetime
from azure.cli.core.util import CLIError

def validate_date_format(namespace):
    format = '%m/%d/%Y'
    if namespace.schedule_start_date:
        datetime.strptime(namespace.schedule_start_date, format)
    if namespace.schedule_end_date:
        datetime.strptime(namespace.schedule_end_date, format)

def validate_time_format(namespace):
    format = '%H:%M:%S'
    if namespace.schedule_start_time:
        datetime.strptime(namespace.schedule_start_time, format)
    if namespace.schedule_end_time:
        datetime.strptime(namespace.schedule_end_time, format)

def validate_severity(namespace):
    if namespace.filter_severity:
        for x in namespace.filter_severity:
            if x not in ['Equals', 'NotEquals', 'Sev0', 'Sev1', 'Sev2', 'Sev3', 'Sev4']:
                raise CLIError('filter-severity values have to be one of [Equals, NotEquals, Sev0, Sev1, Sev2, Sev3, Sev4]')

def validate_monitor_condition(namespace):
    if namespace.filter_monitor_condition:
        for x in namespace.filter_monitor_condition:
            if x not in ['Equals', 'NotEquals', 'Fired', 'Resolved']:
                raise CLIError('filter-monitor-condition values have to be one of [Equals, NotEquals, Fired, Resolved]')

def validate_signal_type(namespace):
    if namespace.filter_signal_type:
        for x in namespace.filter_signal_type:
            if x not in ['Equals', 'NotEquals', 'Metric', 'Log', 'Unknown']:
                raise CLIError('filter-signal-type values have to be one of [Equals, NotEquals, Metric, Log, Unknown]')
