|Scenario|Result|ErrorMessage|ErrorStack|ErrorNormalized|StartDt|EndDt|
|step_data_collection_rule_create|successed||||2020-12-04 09:52:16.150100|2020-12-04 09:52:26.128187|
|step_data_collection_rule_show|successed||||2020-12-04 09:52:26.128187|2020-12-04 09:52:28.271091|
|step_data_collection_rule_list_by_resource_group|successed||||2020-12-04 09:52:28.271091|2020-12-04 09:52:30.414010|
|step_data_collection_rule_list_by_subscription|failed|Query 'length(@)' doesn't yield expected value '1', instead the actual value is '3'. Data:  [   {     "dataFlows": [       {         "destinations": [           "clitesthldx5k3njrpoa"         ],         "streams": [           "Microsoft-Perf",           "Microsoft-Syslog",           "Microsoft-WindowsEvent"         ]       }     ],     "dataSources": {       "extensions": null,       "performanceCounters": [         {           "counterSpecifiers": [             "\\Processor(_Total)\\% Processor|Traceback (most recent call last):   File "C:\Users\kairu\projects\azure-cli-extensions\src\monitor-control-service\azext_amcs\tests\__init__.py", line 66, in wrapper     ret = func_to_call(*args, **kwargs)   File "C:\Users\kairu\projects\azure-cli-extensions\src\monitor-control-service\azext_amcs\tests\latest\example_steps.py", line 70, in step_data_collection_rule_list_by_subscription     test.cmd('az monitor data-collection rule list ',   File "c:\users\kairu\projects\azure-cli\src\azure-cli-||2020-12-04 09:52:30.414010|2020-12-04 09:52:31.275060|
|step_data_collection_rule_update_tags|successed||||2020-12-04 09:52:31.352996|2020-12-04 09:52:40.405962|
|step_data_collection_rule_association_create|successed||||2020-12-04 09:52:40.405962|2020-12-04 09:52:43.087835|
|step_data_collection_rule_association_show|successed||||2020-12-04 09:52:43.087835|2020-12-04 09:52:44.828049|
|step_data_collection_rule_association_list_by_rule|successed||||2020-12-04 09:52:44.828049|2020-12-04 09:52:45.719036|
|step_data_collection_rule_association_list_by_resource|successed||||2020-12-04 09:52:45.719036|2020-12-04 09:52:47.627076|
|step_data_collection_rule_association_delete|successed||||2020-12-04 09:52:47.627076|2020-12-04 09:52:49.879294|
|step_data_collection_rule_delete|successed||||2020-12-04 09:52:49.879294|2020-12-04 09:52:57.082759|
Coverage: 10/11
