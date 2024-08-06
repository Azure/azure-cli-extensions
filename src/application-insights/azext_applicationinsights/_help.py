# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

# pylint: disable=line-too-long

helps['monitor app-insights'] = """
    type: group
    short-summary: Commands for querying data in Application Insights applications.
    parameters:
      - name: --offset
        short-summary: >
          Time offset of the query range, in ##d##h format.
        long-summary: >
          Can be used with either --start-time or --end-time. If used with --start-time, then
          the end time will be calculated by adding the offset. If used with --end-time (default), then
          the start time will be calculated by subtracting the offset. If --start-time and --end-time are
          provided, then --offset will be ignored.
"""

helps['monitor app-insights component'] = """
    type: group
    short-summary: Manage an Application Insights component or its subcomponents.
"""

helps['monitor app-insights component create'] = """
    type: command
    short-summary: Create a new Application Insights resource.
    parameters:
      - name: --application-type
        type: string
        short-summary: Type of application being monitored. Possible values include 'web', 'other'. Default value is'web' .
      - name: --kind -k
        type: string
        short-summary: The kind of application that this component refers to, used to customize UI. This value is a freeform string, values should typically be one of web, ios, other, store, java, phone.
    examples:
      - name: Create a component with kind web and location.
        text: |
          az monitor app-insights component create --app demoApp --location westus2 --kind web -g demoRg --application-type web --retention-time 120
"""

helps['monitor app-insights component update'] = """
    type: command
    short-summary: Update properties on an existing Application Insights resource. The primary value which can be updated is kind, which customizes the UI experience.
    parameters:
      - name: --kind -k
        type: string
        short-summary: The kind of application that this component refers to, used to customize UI. This value is a freeform string, values should typically be one of web, ios, other, store, java, phone.
    examples:
      - name: Update a component with kind web.
        text: |
          az monitor app-insights component update --app demoApp -k web -g demoRg --retention-time 120
"""

helps['monitor app-insights component update-tags'] = """
    type: command
    short-summary: Update tags on an existing Application Insights resource.
    examples:
      - name: Update the tag 'name' to equal 'value'.
        text: |
          az monitor app-insights component update-tags --app demoApp --tags name=value -g demoRg
"""

helps['monitor app-insights component connect-webapp'] = """
    type: command
    short-summary: Connect AI to a web app.
    examples:
      - name: Connect AI to a web app and enable both profiler and snapshot debugger for the web app.
        text: |
          az monitor app-insights component connect-webapp -g myRG -a myAI --web-app myApp --enable-profiler --enable-snapshot-debugger
      - name: Connect AI to a web app using resource id and enable profiler and disable snapshot debugger for the web app.
        text: |
          az monitor app-insights component connect-webapp -g myRG -a myAI --web-app /subscriptions/mySub/resourceGroups/myRG/providers/Microsoft.Web/sites/myApp --enable-profiler --enable-snapshot-debugger false
"""

helps['monitor app-insights component connect-function'] = """
    type: command
    short-summary: Connect AI to an Azure function.
    examples:
      - name: Connect AI to an Azure function.
        text: |
          az monitor app-insights component connect-function -g myRG -a myAI --function myFunction
      - name: Connect AI to an Azure function using resource id.
        text: |
          az monitor app-insights component connect-function -g myRG -a myAI --function /subscriptions/mySub/resourceGroups/myRG/providers/Microsoft.Web/sites/myFunction
"""

helps['monitor app-insights component show'] = """
    type: command
    short-summary: Get an Application Insights resource.
    examples:
      - name: Get a component by name.
        text: |
          az monitor app-insights component show --app demoApp -g demoRg
      - name: List components in a resource group.
        text: |
          az monitor app-insights component show -g demoRg
      - name: List components in the currently selected subscription.
        text: |
          az monitor app-insights component show
"""

helps['monitor app-insights component delete'] = """
    type: command
    short-summary: Delete a new Application Insights resource.
    examples:
      - name: Delete a component with kind web and location.
        text: |
          az monitor app-insights component delete --app demoApp -g demoRg
"""

helps['monitor app-insights metrics'] = """
    type: group
    short-summary: Retrieve metrics from an application.
"""

helps['monitor app-insights events'] = """
    type: group
    short-summary: Retrieve events from an application.
"""

helps['monitor app-insights query'] = """
    type: command
    short-summary: Execute a query over data in your application.
    parameters:
      - name: --offset
        short-summary: >
          Time offset of the query range, in ##d##h format.
        long-summary: >
          Can be used with either --start-time or --end-time. If used with --start-time, then
          the end time will be calculated by adding the offset. If used with --end-time (default), then
          the start time will be calculated by subtracting the offset. If --start-time and --end-time are
          provided, then --offset will be ignored.
    examples:
      - name: Execute a simple query over past 1 hour and 30 minutes.
        text: |
          az monitor app-insights query --app e292531c-eb03-4079-9bb0-fe6b56b99f8b --analytics-query 'requests | summarize count() by bin(timestamp, 1h)' --offset 1h30m
"""

helps['monitor app-insights metrics show'] = """
    type: command
    short-summary: View the value of a single metric.
    parameters:
      - name: --interval
        short-summary: >
          The interval over which to aggregate metrics, in ##h##m format.
      - name: --offset
        short-summary: >
          Time offset of the query range, in ##d##h format.
        long-summary: >
          Can be used with either --start-time or --end-time. If used with --start-time, then
          the end time will be calculated by adding the offset. If used with --end-time (default), then
          the start time will be calculated by subtracting the offset. If --start-time and --end-time are
          provided, then --offset will be ignored.
    examples:
      - name: View the count of availabilityResults events.
        text: |
          az monitor app-insights metrics show --app e292531c-eb03-4079-9bb0-fe6b56b99f8b --metric availabilityResults/count
"""

helps['monitor app-insights metrics get-metadata'] = """
    type: command
    short-summary: Get the metadata for metrics on a particular application.
    examples:
      - name: Views the metadata for the provided app.
        text: |
          az monitor app-insights metrics get-metadata --app e292531c-eb03-4079-9bb0-fe6b56b99f8b
"""

helps['monitor app-insights events show'] = """
    type: command
    short-summary: List events by type or view a single event from an application, specified by type and ID.
    parameters:
      - name: --offset
        short-summary: >
          Time offset of the query range, in ##d##h format.
        long-summary: >
          Can be used with either --start-time or --end-time. If used with --start-time, then
          the end time will be calculated by adding the offset. If used with --end-time (default), then
          the start time will be calculated by subtracting the offset. If --start-time and --end-time are
          provided, then --offset will be ignored.
    examples:
      - name: Get an availability result by ID.
        text: |
          az monitor app-insights events show --app 578f0e27-12e9-4631-bc02-50b965da2633 --type availabilityResults --event b2cf08df-bf42-4278-8d2c-5b55f85901fe
      - name: List availability results from the last 24 hours.
        text: |
          az monitor app-insights events show --app 578f0e27-12e9-4631-bc02-50b965da2633 --type availabilityResults --offset 24h
"""

helps['monitor app-insights component continues-export'] = """
    type: group
    short-summary: Manage Continuous Export configurations for an Application Insights component.
"""

helps['monitor app-insights component continues-export create'] = """
    type: command
    short-summary: Create a Continuous Export configuration for an Application Insights component.
    examples:
      - name: Create a Continuous Export configuration.
        text: |
            az monitor app-insights component continues-export create -g rg \\
            --app 578f0e27-12e9-4631-bc02-50b965da2633 \\
            --record-types Requests Event Exceptions Metrics PageViews \\
            --dest-account account --dest-container container --dest-sub-id sub-id \\
            --dest-sas se=2020-10-27&sp=w&sv=2018-11-09&sr=c
"""

helps['monitor app-insights component continues-export update'] = """
    type: command
    short-summary: Update a Continuous Export configuration for an Application Insights component.
    examples:
      - name: Update a Continuous Export configuration record-types.
        text: |
            az monitor app-insights component continues-export update -g rg \\
            --app 578f0e27-12e9-4631-bc02-50b965da2633 \\
            --id exportid \\
            --record-types Requests Event Exceptions Metrics PageViews
      - name: Update a Continuous Export configuration storage destination.
        text: |
            az monitor app-insights component continues-export update -g rg \\
            --app 578f0e27-12e9-4631-bc02-50b965da2633 \\
            --id exportid \\
            --dest-account account --dest-container container --dest-sub-id sub-id \\
            --dest-sas se=2020-10-27&sp=w&sv=2018-11-09&sr=c
"""

helps['monitor app-insights web-test'] = """
    type: group
    short-summary: Manage web test with application insights
"""

helps['monitor app-insights web-test list'] = """
    type: command
    short-summary: "Get all Application Insights web tests defined for the specified component. And Get all \
Application Insights web tests defined within a specified resource group. And Get all Application Insights web test \
alerts definitions within a subscription."
    examples:
      - name: webTestListByComponent
        text: |-
               az monitor app-insights web-test list --component-name "my-component" --resource-group \
"my-resource-group"
      - name: webTestListByResourceGroup
        text: |-
               az monitor app-insights web-test list --resource-group "my-resource-group"
      - name: webTestList
        text: |-
               az monitor app-insights web-test list
"""

helps['monitor app-insights web-test show'] = """
    type: command
    short-summary: "Get a specific Application Insights web test definition."
    examples:
      - name: webTestGet
        text: |-
               az monitor app-insights web-test show --resource-group "my-resource-group" --name \
"my-webtest-01-mywebservice"
"""

helps['monitor app-insights web-test create'] = """
    type: command
    short-summary: "Create an Application Insights web test definition."
    parameters:
      - name: --locations
        short-summary: "A list of where to physically run the tests from to give global coverage for accessibility of \
your application."
        long-summary: |
            Usage: --locations Id=XX

            Id: Location ID for the WebTest to run from.

            Multiple actions can be specified by using more than one --locations argument.
      - name: --content-validation
        short-summary: "The collection of content validation properties"
        long-summary: |
            Usage: --content-validation content-match=XX ignore-case=XX pass-if-text-found=XX

            content-match: Content to look for in the return of the WebTest.  Must not be null or empty.
            ignore-case: When set, this value makes the ContentMatch validation case insensitive.
            pass-if-text-found: When true, validation will pass if there is a match for the ContentMatch string.  If \
false, validation will fail if there is a match
      - name: --headers
        short-summary: "List of headers and their values to add to the WebTest call."
        long-summary: |
            Usage: --headers key=XX value=XX

            key: The name of the header.
            value: The value of the header.

            Multiple actions can be specified by using more than one --headers argument.
    examples:
      - name: webTestCreate
        text: |-
               az monitor app-insights web-test create --kind "ping" --location "South Central US" --web-test \
"<WebTest Name=\\"my-webtest\\" Id=\\"678ddf96-1ab8-44c8-9274-123456789abc\\" Enabled=\\"True\\" \
CssProjectStructure=\\"\\" CssIteration=\\"\\" Timeout=\\"120\\" WorkItemIds=\\"\\" xmlns=\\"http://microsoft.com/schem\
as/VisualStudio/TeamTest/2010\\" Description=\\"\\" CredentialUserName=\\"\\" CredentialPassword=\\"\\" \
PreAuthenticate=\\"True\\" Proxy=\\"default\\" StopOnError=\\"False\\" RecordedResultFile=\\"\\" ResultsLocale=\\"\\" \
><Items><Request Method=\\"GET\\" Guid=\\"a4162485-9114-fcfc-e086-123456789abc\\" Version=\\"1.1\\" \
Url=\\"http://my-component.azurewebsites.net\\" ThinkTime=\\"0\\" Timeout=\\"120\\" ParseDependentRequests=\\"True\\" \
FollowRedirects=\\"True\\" RecordResult=\\"True\\" Cache=\\"False\\" ResponseTimeGoal=\\"0\\" Encoding=\\"utf-8\\" \
ExpectedHttpStatusCode=\\"200\\" ExpectedResponseUrl=\\"\\" ReportingName=\\"\\" IgnoreHttpStatusCode=\\"False\\" \
/></Items></WebTest>" --description "Ping web test alert for mytestwebapp" --enabled true --frequency 900 \
--web-test-kind "ping" --locations Id="us-fl-mia-edge" --defined-web-test-name \
"my-webtest-my-component" --retry-enabled true --synthetic-monitor-id "my-webtest-my-component" --timeout 120 \
--resource-group "my-resource-group" --name "my-webtest-my-component" --tags hidden-link:XX=XX
      - name: webTestCreateStandard
        text: |-
               az monitor app-insights web-test create --location "South Central US" --description "Ping web test \
alert for mytestwebapp" --enabled true --frequency 900 --web-test-kind "standard" --locations Id="us-fl-mia-edge" \
--defined-web-test-name "my-webtest-my-component" --http-verb "POST" --request-body "SGVsbG8gd29ybGQ=" --request-url \
"https://bing.com" --retry-enabled true --synthetic-monitor-id "my-webtest-my-component" --timeout 120 \
--ssl-lifetime-check 100 --ssl-check true --resource-group "my-resource-group" --name \
"my-webtest-my-component" --tags hidden-link:XX=XX
"""

helps['monitor app-insights web-test update'] = """
    type: command
    short-summary: "Update an Application Insights web test definition."
    parameters:
      - name: --locations
        short-summary: "A list of where to physically run the tests from to give global coverage for accessibility of \
your application."
        long-summary: |
            Usage: --locations Id=XX

            Id: Location ID for the WebTest to run from.

            Multiple actions can be specified by using more than one --locations argument.
      - name: --content-validation
        short-summary: "The collection of content validation properties"
        long-summary: |
            Usage: --content-validation content-match=XX ignore-case=XX pass-if-text-found=XX

            content-match: Content to look for in the return of the WebTest.  Must not be null or empty.
            ignore-case: When set, this value makes the ContentMatch validation case insensitive.
            pass-if-text-found: When true, validation will pass if there is a match for the ContentMatch string.  If \
false, validation will fail if there is a match
      - name: --headers
        short-summary: "List of headers and their values to add to the WebTest call."
        long-summary: |
            Usage: --headers key=XX value=XX

            key: The name of the header.
            value: The value of the header.

            Multiple actions can be specified by using more than one --headers argument.
    examples:
      - name: webTestUpdate
        text: |-
               az monitor app-insights web-test update --kind "ping" --location "South Central US" --web-test \
"<WebTest Name=\\"my-webtest\\" Id=\\"678ddf96-1ab8-44c8-9274-123456789abc\\" Enabled=\\"True\\" \
CssProjectStructure=\\"\\" CssIteration=\\"\\" Timeout=\\"30\\" WorkItemIds=\\"\\" xmlns=\\"http://microsoft.com/schema\
s/VisualStudio/TeamTest/2010\\" Description=\\"\\" CredentialUserName=\\"\\" CredentialPassword=\\"\\" \
PreAuthenticate=\\"True\\" Proxy=\\"default\\" StopOnError=\\"False\\" RecordedResultFile=\\"\\" ResultsLocale=\\"\\" \
><Items><Request Method=\\"GET\\" Guid=\\"a4162485-9114-fcfc-e086-123456789abc\\" Version=\\"1.1\\" \
Url=\\"http://my-component.azurewebsites.net\\" ThinkTime=\\"0\\" Timeout=\\"30\\" ParseDependentRequests=\\"True\\" \
FollowRedirects=\\"True\\" RecordResult=\\"True\\" Cache=\\"False\\" ResponseTimeGoal=\\"0\\" Encoding=\\"utf-8\\" \
ExpectedHttpStatusCode=\\"200\\" ExpectedResponseUrl=\\"\\" ReportingName=\\"\\" IgnoreHttpStatusCode=\\"False\\" \
/></Items></WebTest>" --frequency 600 --web-test-kind "ping" --locations Id="us-fl-mia-edge" --locations \
Id="apac-hk-hkn-azr" --defined-web-test-name "my-webtest-my-component" --synthetic-monitor-id \
"my-webtest-my-component" --timeout 30 --resource-group "my-resource-group" --name "my-webtest-my-component"
"""

helps['monitor app-insights web-test delete'] = """
    type: command
    short-summary: "Delete an Application Insights web test."
    examples:
      - name: webTestDelete
        text: |-
               az monitor app-insights web-test delete --resource-group "my-resource-group" --name \
"my-webtest-01-mywebservice"
"""
