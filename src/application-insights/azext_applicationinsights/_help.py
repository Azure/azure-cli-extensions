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
          az monitor app-insights component connect-webapp -g myRG -n myApp --enable-profiler --enable-snapshot-debugger
      - name: Connect AI to a web app using resource id and enable profiler and disable snapshot debugger for the web app.
        text: |
          az monitor app-insights component connect-webapp --ids /subscriptions/mySub/resourceGroups/myRG/providers/Microsoft.Web/sites/myApp --enable-profiler --enable-snapshot-debugger false
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

helps['monitor app-insights component billing'] = """
    type: group
    short-summary: Manage an Application Insights component billing features.
"""

helps['monitor app-insights component billing show'] = """
    type: command
    short-summary: Show the billing features of an Application Insights resource.
    examples:
      - name: Show the billing features of an application insights component
        text: |
          az monitor app-insights component billing show --app demoApp -g demoRg
"""

helps['monitor app-insights component billing update'] = """
    type: command
    short-summary: Update the billing features of an Application Insights resource.
    examples:
      - name: Update the daily cap of the billing features
        text: |
          az monitor app-insights component billing update --app demoApp -g demoRg --cap 200 --stop
"""

helps['monitor app-insights api-key'] = """
    type: group
    short-summary: Operations on API keys associated with an Application Insights component.
"""

helps['monitor app-insights api-key show'] = """
    type: command
    short-summary: Get all keys or a specific API key associated with an Application Insights resource.
    parameters:
      - name: --api-key
        type: string
        short-summary: name of the API key to fetch. Can be found using `api-key show`.
    examples:
      - name: Fetch API Key.
        text: |
          az monitor app-insights api-key show --app demoApp -g demoRg --api-key demo-key
      - name: Fetch API Keys.
        text: |
          az monitor app-insights api-key show --app demoApp -g demoRg
"""

helps['monitor app-insights api-key delete'] = """
    type: command
    short-summary: Delete an API key from an Application Insights resource.
    parameters:
      - name: --api-key
        type: string
        short-summary: Name of the API key to delete. Can be found using `api-key show`.
    examples:
      - name: Delete API Key.
        text: |
          az monitor app-insights api-key delete --app demoApp -g demoRg --api-key demo-key
"""

helps['monitor app-insights api-key create'] = """
    type: command
    short-summary: Create a new API key for use with an Application Insights resource.
    parameters:
      - name: --api-key
        type: string
        short-summary: Name of the API key to create.
      - name: --read-properties
        type: list
        short-summary: A space seperated list of names of read Roles for this API key to inherit. Possible values include ReadTelemetry, AuthenticateSDKControlChannel and "".
      - name: --write-properties
        type: list
        short-summary: A space seperated list of names of write Roles for this API key to inherit. Possible values include WriteAnnotations and "".
    examples:
      - name: Create a component with kind web and location.
        text: |
          az monitor app-insights api-key create --api-key cli-demo --read-properties ReadTelemetry --write-properties WriteAnnotations -g demoRg --app testApp
      - name: Create a component with kind web and location without any permission
        text: |
          az monitor app-insights api-key create --api-key cli-demo --read-properties '""' --write-properties '""' -g demoRg --app testApp
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

helps['monitor app-insights component linked-storage'] = """
    type: group
    short-summary: Manage linked storage account for an Application Insights component.
"""

helps['monitor app-insights component linked-storage show'] = """
    type: command
    short-summary: Show the details of linked storage account for an Application Insights component.
"""

helps['monitor app-insights component linked-storage link'] = """
    type: command
    short-summary: Link a storage account with an Application Insights component.
"""

helps['monitor app-insights component linked-storage update'] = """
    type: command
    short-summary: Update the linked storage account for an Application Insights component.
"""

helps['monitor app-insights component linked-storage unlink'] = """
    type: command
    short-summary: Unlink a storage account with an Application Insights component.
"""

helps['monitor app-insights component continues-export'] = """
    type: group
    short-summary: Manage Continuous Export configurations for an Application Insights component.
"""

helps['monitor app-insights component continues-export list'] = """
    type: command
    short-summary: List Continuous Export configurations for an Application Insights component.
    examples:
      - name: ExportConfigurationsList
        text: |
            az monitor app-insights component continues-export list -g rg \\
            --app 578f0e27-12e9-4631-bc02-50b965da2633
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

helps['monitor app-insights component continues-export show'] = """
    type: command
    short-summary: Get a specific Continuous Export configuration of an Application Insights component.
    examples:
      - name: Get a Continuous Export configuration by ID.
        text: |
            az monitor app-insights component continues-export show -g rg \\
            --app 578f0e27-12e9-4631-bc02-50b965da2633 \\
            --id exportid
"""

helps['monitor app-insights component continues-export delete'] = """
    type: command
    short-summary: Delete a specific Continuous Export configuration of an Application Insights component.
    examples:
      - name: Delete a Continuous Export configuration by ID.
        text: |
            az monitor app-insights component continues-export delete -g rg \\
            --app 578f0e27-12e9-4631-bc02-50b965da2633 \\
            --id exportid
"""
