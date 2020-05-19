# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

def costmanagement_query(cmd,
                         client,
                         scope,
                         type_,
                         timeframe,
                         time_period=None,
                         dataset_configuration=None,
                         dataset_aggregation=None,
                         dataset_grouping=None,
                         dataset_filter=None):
    from azext_costmanagement.generated.custom import costmanagement_query_usage

    # for now, query is for Azure cloud only, not for external cloud
    return costmanagement_query_usage(cmd,
                                      client,
                                      scope,
                                      type_,
                                      timeframe,
                                      time_period,
                                      dataset_configuration,
                                      dataset_aggregation,
                                      dataset_grouping,
                                      dataset_filter)
