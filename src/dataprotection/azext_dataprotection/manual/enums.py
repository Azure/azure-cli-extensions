# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def get_protection_status_values():
    return ['ProtectionConfigured', 'ProtectionError']


def get_backup_frequency_values():
    return ['Daily', 'Weekly', 'Hourly']


def get_datastore_type_values():
    return ['ArchiveStore', 'OperationalStore', 'VaultStore']


def get_duration_type_values():
    return ['Days', 'Weeks', 'Months', 'Years']


def get_copy_option_values():
    return ['CustomCopyOption', 'ImmediateCopyOption']


def get_retention_rule_name_values():
    return ['Default', 'Daily', 'Weekly', 'Monthly', 'Yearly']


def get_tag_name_values():
    return ['Daily', 'Weekly', 'Monthly', 'Yearly']


def get_absolute_criteria_values():
    return ['AllBackup', 'FirstOfDay', 'FirstOfMonth', 'FirstOfWeek', 'FirstOfYear']


def get_days_of_week_values():
    return ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']


def get_weeks_of_month_values():
    return ['First', 'Second', 'Third', 'Fourth', 'Last']


def get_months_of_year_values():
    return ['January', 'February', 'March', 'April', 'May', 'June', 'July',
            'August', 'September', 'October', 'November', 'December']


def get_job_status_values():
    return ['InProgress', 'Completed', 'Failed']


def get_job_operation_values():
    return ['OnDemandBackup', 'ScheduledBackup', 'Restore']


def get_datasource_types():
    import azext_dataprotection.manual.helpers as helpers
    return helpers.get_supported_datasource_types()
