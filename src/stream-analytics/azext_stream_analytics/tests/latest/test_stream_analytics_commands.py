# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

import json

from azure.cli.testsdk import (
    ResourceGroupPreparer,
    ScenarioTest,
    StorageAccountPreparer
)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


class StreamAnalyticsClientTest(ScenarioTest):
    @ResourceGroupPreparer(name_prefix="cli_test_stream_analytics_", location="westus")
    def test_job_crud(self):
        self.kwargs.update({
            "job_name": "job",
            "locale": "en-US"
        })
        # create a streaming job
        self.cmd(
            "stream-analytics job create -n {job_name} -g {rg} \
            --data-locale {locale} \
            --output-error-policy Drop --out-of-order-policy Drop \
            --order-max-delay 0 --arrival-max-delay 5",
            checks=[
                self.check("name", "{job_name}"),
                self.check("type", "Microsoft.StreamAnalytics/streamingjobs")
            ]
        )
        # retrieve/update a streaming job
        self.cmd(
            "stream-analytics job list -g {rg}",
            checks=[
                self.check("length(@)", 1),
                self.check("@[0].name", "{job_name}")
            ]
        )
        self.cmd(
            "stream-analytics job update -n {job_name} -g {rg} \
            --order-max-delay 10 --arrival-max-delay 29"
        )
        self.cmd(
            "stream-analytics job show -n {job_name} -g {rg}",
            checks=[
                self.check("eventsOutOfOrderMaxDelayInSeconds", 10),
                self.check("eventsLateArrivalMaxDelayInSeconds", 29)
            ]
        )
        # delete a streaming job
        self.cmd("stream-analytics job delete -n {job_name} -g {rg} --yes")

    @ResourceGroupPreparer(name_prefix="cli_test_stream_analytics_", location="westus")
    def test_transformation_crud(self):
        self.kwargs.update({
            "job_name": "job",
            "transformation_name": "transformation",
            "input_name": "input",
            "output_name": "output",
            "locale": "en-US"
        })
        # create a streaming job
        self.cmd(
            "stream-analytics job create -n {job_name} -g {rg} \
            --data-locale {locale} \
            --output-error-policy Drop --out-of-order-policy Drop \
            --order-max-delay 0 --arrival-max-delay 5"
        )
        # create a transformation
        self.kwargs["saql"] = f"SELECT * INTO {self.kwargs['output_name']} FROM {self.kwargs['input_name']}"
        self.cmd(
            "stream-analytics transformation create -n {transformation_name} -g {rg} \
            --job-name {job_name} \
            --saql '{saql}' --streaming-units 6",
            checks=[
                self.check("name", "{transformation_name}"),
                self.check("type", "Microsoft.StreamAnalytics/streamingjobs/transformations")
            ]
        )
        # retrieve/update a transformation
        self.cmd(
            "stream-analytics transformation update -n {transformation_name} -g {rg} \
            --job-name {job_name} --saql '{saql}' --streaming-units 3"
        )
        self.cmd(
            "stream-analytics transformation show -n {transformation_name} -g {rg} --job-name {job_name}",
            checks=[
                self.check("name", "{transformation_name}"),
                self.check("streamingUnits", 3)
            ]
        )

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix="cli_test_stream_analytics_", location="westus")
    @StorageAccountPreparer(parameter_name="storage_account")
    def test_input_crud(self, storage_account):
        self.kwargs.update({
            "job_name": "job",
            "input_name": "input",
            "locale": "en-US",
            "account": storage_account,
            "container": "container"
        })
        # create a streaming job
        self.cmd(
            "stream-analytics job create -n {job_name} -g {rg} \
            --data-locale {locale} \
            --output-error-policy Drop --out-of-order-policy Drop \
            --order-max-delay 0 --arrival-max-delay 5"
        )
        # prepare storage account
        self.kwargs["key"] = self.cmd(
            "storage account keys list --account-name {account}"
        ).get_output_in_json()[0]["value"]
        self.cmd(
            "storage container create -n {container} \
            --account-name {account} --account-key {key}"
        )
        # create/test an input
        props = {
            "type": "Reference",
            "datasource": {
                "type": "Microsoft.Storage/Blob",
                "properties": {
                    "container": self.kwargs["container"],
                    "dateFormat": "yyyy/MM/dd",
                    "pathPattern": "{date}/{time}",
                    "storageAccounts": [{
                        "accountName": self.kwargs["account"],
                        "accountKey": self.kwargs["key"]
                    }],
                    "timeFormat": "HH"
                }
            },
            "serialization": {
                "type": "Csv",
                "properties": {
                    "encoding": "UTF8",
                    "fieldDelimiter": ","
                }
            }
        }
        self.kwargs["properties"] = json.dumps(props)
        self.cmd(
            "stream-analytics input create -n {input_name} -g {rg} \
            --job-name {job_name} \
            --properties '{properties}'",
            checks=[
                self.check("name", "{input_name}"),
                self.check("type", "Microsoft.StreamAnalytics/streamingjobs/inputs")
            ]
        )
        self.cmd(
            "stream-analytics input test -n {input_name} -g {rg} \
            --job-name {job_name} \
            --properties '{properties}'",
            checks=[
                self.check("status", "TestSucceeded")
            ]
        )
        # retrieve/update an input
        self.cmd(
            "stream-analytics input list -g {rg} --job-name {job_name}",
            checks=[
                self.check("length(@)", 1),
                self.check("@[0].name", "{input_name}")
            ]
        )
        props["datasource"]["properties"]["dateFormat"] = "MM/dd/yyyy"
        self.kwargs["properties"] = json.dumps(props)
        self.cmd(
            "stream-analytics input update -n {input_name} -g {rg} \
            --job-name {job_name} --properties '{properties}'"
        )
        self.cmd(
            "stream-analytics input show -n {input_name} -g {rg} --job-name {job_name}",
            checks=[
                self.check("name", "{input_name}"),
                self.check("properties.datasource.dateFormat", "MM/dd/yyyy")
            ]
        )
        # delete an input
        self.cmd("stream-analytics input delete -n {input_name} -g {rg} --job-name {job_name} --yes")

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix="cli_test_stream_analytics_", location="westus")
    @StorageAccountPreparer(parameter_name="storage_account")
    def test_output_crud(self, storage_account):
        self.kwargs.update({
            "job_name": "job",
            "output_name": "output",
            "locale": "en-US",
            "account": storage_account,
            "container": "container"
        })
        # create a streaming job
        self.cmd(
            "stream-analytics job create -n {job_name} -g {rg} \
            --data-locale {locale} \
            --output-error-policy Drop --out-of-order-policy Drop \
            --order-max-delay 0 --arrival-max-delay 5"
        )
        # prepare storage account
        self.kwargs["key"] = self.cmd(
            "storage account keys list --account-name {account}"
        ).get_output_in_json()[0]["value"]
        self.cmd(
            "storage container create -n {container} \
            --account-name {account} --account-key {key}"
        )
        # create/test an output
        datasource_props = {
            "type": "Microsoft.Storage/Blob",
            "properties": {
                "storageAccounts": [{
                    "accountName": self.kwargs["account"],
                    "accountKey": self.kwargs["key"]
                }],
                "container": self.kwargs["container"],
                "pathPattern": "{date}/{time}",
                "dateFormat": "yyyy/MM/dd",
                "timeFormat": "HH"
            }
        }
        serialization_props = {
            "type": "Csv",
            "properties": {
                "fieldDelimiter": ",",
                "encoding": "UTF8"
            }
        }
        self.kwargs["datasource"] = json.dumps(datasource_props)
        self.kwargs["serialization"] = json.dumps(serialization_props)
        self.cmd(
            "stream-analytics output create -n {output_name} -g {rg} \
            --job-name {job_name} \
            --datasource '{datasource}' --serialization '{serialization}'",
            checks=[
                self.check("name", "{output_name}"),
                self.check("type", "Microsoft.StreamAnalytics/streamingjobs/outputs")
            ]
        )
        self.cmd(
            "stream-analytics output test -n {output_name} -g {rg} \
            --job-name {job_name} \
            --datasource '{datasource}' --serialization '{serialization}'",
            checks=[
                self.check("status", "TestSucceeded")
            ]
        )
        # retrieve/update an output
        self.cmd(
            "stream-analytics output list -g {rg} --job-name {job_name}",
            checks=[
                self.check("length(@)", 1),
                self.check("@[0].name", "{output_name}")
            ]
        )
        datasource_props["properties"]["dateFormat"] = "MM/dd/yyyy"
        self.kwargs["datasource"] = json.dumps(datasource_props)
        self.cmd(
            "stream-analytics output update -n {output_name} -g {rg} \
            --job-name {job_name} \
            --datasource '{datasource}' --serialization '{serialization}'"
        )
        self.cmd(
            "stream-analytics output show -n {output_name} -g {rg} --job-name {job_name}",
            checks=[
                self.check("name", "{output_name}"),
                self.check("datasource.dateFormat", "MM/dd/yyyy")
            ]
        )
        # delete an output
        self.cmd("stream-analytics output delete -n {output_name} -g {rg} --job-name {job_name} --yes")

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix="cli_test_stream_analytics_", location="westus")
    @StorageAccountPreparer(parameter_name="storage_account")
    def test_job_scale(self, storage_account):
        self.kwargs.update({
            "job_name": "job",
            "transformation_name": "transformation",
            "input_name": "input",
            "output_name": "output",
            "locale": "en-US",
            "account": storage_account,
            "container": "container"
        })
        # create a streaming job
        self.cmd(
            "stream-analytics job create -n {job_name} -g {rg} \
            --data-locale {locale} \
            --output-error-policy Drop --out-of-order-policy Drop \
            --order-max-delay 0 --arrival-max-delay 5"
        )
        # create a transformation
        self.kwargs["saql"] = f"SELECT * INTO {self.kwargs['output_name']} FROM {self.kwargs['input_name']}"
        self.cmd(
            "stream-analytics transformation create -n {transformation_name} -g {rg} \
            --job-name {job_name} \
            --saql '{saql}' --streaming-units 6"
        )
        # prepare storage account
        self.kwargs["key"] = self.cmd(
            "storage account keys list --account-name {account}"
        ).get_output_in_json()[0]["value"]
        self.cmd(
            "storage container create -n {container} \
            --account-name {account} --account-key {key}"
        )
        # create an input
        self.kwargs["properties"] = json.dumps({
            "type": "Stream",
            "datasource": {
                "type": "Microsoft.Storage/Blob",
                "properties": {
                    "storageAccounts": [{
                        "accountName": self.kwargs["account"],
                        "accountKey": self.kwargs["key"]
                    }],
                    "container": self.kwargs["container"],
                    "pathPattern": "{date}/{time}",
                    "dateFormat": "MM/dd/yyyy",
                    "timeFormat": "HH",
                    "sourcePartitionCount": 16
                }
            },
            "serialization": {
                "type": "Csv",
                "properties": {
                    "fieldDelimiter": ",",
                    "encoding": "UTF8"
                }
            }
        })
        self.cmd(
            "stream-analytics input create -n {input_name} -g {rg} \
            --job-name {job_name} --properties '{properties}'"
        )
        # create an output
        self.kwargs["datasource"] = json.dumps({
            "type": "Microsoft.Storage/Blob",
            "properties": {
                "storageAccounts": [{
                    "accountName": self.kwargs["account"],
                    "accountKey": self.kwargs["key"]
                }],
                "container": self.kwargs["container"],
                "pathPattern": "{date}/{time}",
                "dateFormat": "yyyy/MM/dd",
                "timeFormat": "HH"
            }
        })
        self.kwargs["serialization"] = json.dumps({
            "type": "Csv",
            "properties": {
                "fieldDelimiter": ",",
                "encoding": "UTF8"
            }
        })
        self.cmd(
            "stream-analytics output create -n {output_name} -g {rg} \
            --job-name {job_name} \
            --datasource '{datasource}' --serialization '{serialization}'"
        )
        # start/stop a running job
        self.cmd("stream-analytics job start -n {job_name} -g {rg} --output-start-mode JobStartTime")
        self.cmd("stream-analytics job stop -n {job_name} -g {rg}")

    @ResourceGroupPreparer(name_prefix="cli_test_stream_analytics_", location="westus")
    def test_function_crud(self):
        self.kwargs.update({
            "job_name": "job",
            "function_name": "function",
            "workspace_name": "workspace",
            "locale": "en-US"
        })
        # create a streaming job
        self.cmd(
            "stream-analytics job create -n {job_name} -g {rg} \
            --data-locale {locale} \
            --output-error-policy Drop --out-of-order-policy Drop \
            --order-max-delay 0 --arrival-max-delay 5"
        )
        # create/test a function
        props = {
            "type": "Scalar",
            "properties": {
                "inputs": [{
                    "dataType": "Any"
                }],
                "output": {
                    "dataType": "Any"
                },
                "binding": {
                    "type": "Microsoft.StreamAnalytics/JavascriptUdf",
                    "properties": {
                        "script": "function (a, b) { return a + b; }"
                    }
                }
            }
        }
        self.kwargs["props"] = json.dumps(props)
        self.cmd(
            "stream-analytics function create -n {function_name} -g {rg} \
            --job-name {job_name} --properties '{props}'",
            checks=[
                self.check("name", "{function_name}"),
                self.check("type", "Microsoft.StreamAnalytics/streamingjobs/functions")
            ]
        )
        self.cmd(
            "stream-analytics function test -n {function_name} -g {rg} \
            --job-name {job_name} --properties '{props}'",
            checks=[
                self.check("status", "TestFailed")
            ]
        )
        # retrieve/update a function
        self.cmd(
            "stream-analytics function list -g {rg} --job-name {job_name}",
            checks=[
                self.check("length(@)", 1),
                self.check("@[0].name", "{function_name}")
            ]
        )
        props["properties"]["binding"]["properties"]["script"] = "function (a, b) { return a * b; }"
        self.kwargs["props"] = json.dumps(props)
        self.cmd(
            "stream-analytics function update -n {function_name} -g {rg} \
            --job-name {job_name} --properties '{props}'"
        )
        self.cmd(
            "stream-analytics function show -n {function_name} -g {rg} --job-name {job_name}",
            checks=[
                self.check("name", "{function_name}"),
                self.check("properties.binding.script", "function (a, b) {{ return a * b; }}")
            ]
        )
        # delete a function
        self.cmd("stream-analytics job delete -n {function_name} -g {rg} --job-name {job_name} --yes")

    @ResourceGroupPreparer(name_prefix="cli_test_stream_analytics_")
    def test_subscription_inspect(self):
        self.kwargs.update({
            "location": "westus"
        })
        self.cmd(
            "stream-analytics subscription inspect -l {location}",
            checks=[
                self.check("length(value)", 2),
                self.check("value[0].type", "Microsoft.StreamAnalytics/quotas")
            ]
        )

    @ResourceGroupPreparer(name_prefix="cli_test_stream_analytics_")
    def test_cluster_crud(self):
        self.kwargs.update({
            "cluster": "cli-cluster",
            "capacity1": 36,
            "capacity2": 72,
        })
        # create a cluster
        self.cmd(
            "stream-analytics cluster create -n {cluster} -g {rg} --sku name=Default capacity={capacity1}",
            checks=[
                self.check("sku.capacity", 36),
                self.check("type", "Microsoft.StreamAnalytics/clusters"),
            ]
        )
        # retrieve/update a cluster
        self.cmd(
            "stream-analytics cluster list -g {rg}",
            checks=[
                self.check("length(@)", 1),
                self.check("@[0].name", "{cluster}"),
            ]
        )
        self.cmd("stream-analytics cluster update -n {cluster} -g {rg} --sku capacity={capacity2}")
        self.cmd(
            "stream-analytics cluster show -n {cluster} -g {rg}",
            checks=[
                self.check("sku.capacity", 72),
                self.check("name", "{cluster}"),
            ]
        )
        # delete a cluster
        self.cmd("stream-analytics cluster delete -n {cluster} -g {rg} --yes")

    @ResourceGroupPreparer(name_prefix="cli_test_stream_analytics_")
    @StorageAccountPreparer(name_prefix="pl", kind="StorageV2")
    def test_private_endpoint_crud(self, storage_account):
        self.kwargs.update({
            "sa": storage_account,
            "pe": "cli-pe",
            "cluster": "cli-cluster",
        })

        self.cmd("stream-analytics cluster create -n {cluster} -g {rg} --sku name=Default capacity=36")
        # prepare connections
        self.kwargs["sa_id"] = self.cmd('storage account show -n {sa} -g {rg}').get_output_in_json()["id"]
        self.kwargs["group_id"] = self.cmd("storage account private-link-resource list -g {rg} \
                                           --account-name {sa}").get_output_in_json()[0]["groupId"]
        self.kwargs["connections"] = json.dumps([{
            "privateLinkServiceId": self.kwargs["sa_id"],
            "groupIds": [self.kwargs["group_id"]]
        }])
        self.cmd(
            "stream-analytics private-endpoint create -n {pe} -g {rg} \
            --cluster-name {cluster} --connections '{connections}'",
            checks=[
                self.check("name", "{pe}"),
                self.check("type", "Microsoft.StreamAnalytics/clusters/privateEndpoints"),
            ]
        )

        self.cmd(
            "stream-analytics private-endpoint list -g {rg} --cluster-name {cluster}",
            checks=[
                self.check("length(@)", 1),
                self.check("@[0].name", "{pe}"),
            ]
        )
        self.cmd(
            "stream-analytics private-endpoint show -n {pe} -g {rg} --cluster-name {cluster}",
            checks=[
                self.check("name", "{pe}"),
                self.check("type", "Microsoft.StreamAnalytics/clusters/privateEndpoints"),
            ]
        )
        self.cmd("stream-analytics private-endpoint delete -n {pe} -g {rg} --cluster-name {cluster} --yes")
