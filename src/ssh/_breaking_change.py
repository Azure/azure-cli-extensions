from azure.cli.core.breaking_change import register_required_flag_breaking_change, register_default_value_breaking_change, register_other_breaking_change

register_other_breaking_change('ssh arc', 'On May 21st 2025, any ssh arc commands on versions <2.0.4 will no longer work. Please upgrade to az ssh version >=2.0.4', taget_version='2.0.4')