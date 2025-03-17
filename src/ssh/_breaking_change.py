from azure.cli.core.breaking_change import register_required_flag_breaking_change, register_default_value_breaking_change, register_other_breaking_change

register_required_flag_breaking_change('bar foo', '--name')
register_default_value_breaking_change('bar foo baz', '--foobar', 'A', 'B')
register_other_breaking_change('bar foo baz', 'During May 2024, another Breaking Change would happen in Build Event.')