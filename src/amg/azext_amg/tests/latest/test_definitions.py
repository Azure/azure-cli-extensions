# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

test_data_source = {
    "access": "proxy",
    "uid": "da714998-ca29-4adc-851b-1bd93371cbc6",
    "jsonData": {
        "azureAuthType": "msi",
        "subscriptionId": ""
    },
    "name": "Test Azure Monitor Data Source",
    "type": "grafana-azure-monitor-datasource"
}

test_data_source_different_uid = {
    "access": "proxy",
    "uid": "bdpe79jidbwu8d",
    "jsonData": {
        "azureAuthType": "msi",
        "subscriptionId": ""
    },
    "name": "Test Azure Monitor Data Source",
    "type": "grafana-azure-monitor-datasource"
}

test_data_source_long_uid2 = {
    "access": "proxy",
    "uid": "ea714998-ca29-4adc-851b-1bd93371cbc6",
    "jsonData": {
        "azureAuthType": "msi",
        "subscriptionId": ""
    },
    "name": "Test Azure Monitor Data Source2",
    "type": "grafana-azure-monitor-datasource"
}

test_data_source_short_uid2 = {
    "access": "proxy",
    "uid": "cdpe79jidbwu8d",
    "jsonData": {
        "azureAuthType": "msi",
        "subscriptionId": ""
    },
    "name": "Test Azure Monitor Data Source2",
    "type": "grafana-azure-monitor-datasource"
}

test_dashboard = {
    "dashboard": {
        "title": "Test Dashboard",
        "panels": [],
    }
}

test_dashboard_with_datasource = {
    "dashboard": {
        "annotations": {
            "list": [
                {
                    "builtIn": 1,
                    "datasource": {
                        "type": "grafana",
                        "uid": "-- Grafana --"
                    },
                    "enable": True,
                    "hide": True,
                    "iconColor": "rgba(0, 211, 255, 1)",
                    "name": "Annotations & Alerts",
                    "type": "dashboard"
                }
            ]
        },
        "editable": True,
        "fiscalYearStartMonth": 0,
        "graphTooltip": 0,
        "id": 39,
        "links": [],
        "liveNow": False,
        "panels": [
            {
                "datasource": {
                    "type": "grafana-azure-monitor-datasource",
                    "uid": "da714998-ca29-4adc-851b-1bd93371cbc6"
                },
                "fieldConfig": {
                    "defaults": {
                        "color": {
                            "mode": "palette-classic"
                        },
                        "custom": {
                            "axisBorderShow": False,
                            "axisCenteredZero": False,
                            "axisColorMode": "text",
                            "axisLabel": "",
                            "axisPlacement": "auto",
                            "barAlignment": 0,
                            "drawStyle": "line",
                            "fillOpacity": 0,
                            "gradientMode": "none",
                            "hideFrom": {
                                "legend": False,
                                "tooltip": False,
                                "viz": False
                            },
                            "insertNones": False,
                            "lineInterpolation": "linear",
                            "lineWidth": 1,
                            "pointSize": 5,
                            "scaleDistribution": {
                                "type": "linear"
                            },
                            "showPoints": "auto",
                            "spanNones": False,
                            "stacking": {
                                "group": "A",
                                "mode": "none"
                            },
                            "thresholdsStyle": {
                                "mode": "off"
                            }
                        },
                        "mappings": [],
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {
                                    "color": "green",
                                    "value": None
                                },
                                {
                                    "color": "red",
                                    "value": 80
                                }
                            ]
                        },
                        "unitScale": True
                    },
                    "overrides": []
                },
                "gridPos": {
                    "h": 8,
                    "w": 12,
                    "x": 0,
                    "y": 0
                },
                "id": 2,
                "options": {
                    "legend": {
                        "calcs": [],
                        "displayMode": "list",
                        "placement": "bottom",
                        "showLegend": True
                    },
                    "tooltip": {
                        "mode": "single",
                        "sort": "none"
                    }
                },
                "targets": [
                    {
                        "datasource": {
                            "type": "grafana-azure-monitor-datasource",
                            "uid": "da714998-ca29-4adc-851b-1bd93371cbc6"
                        },
                        "refId": "A",
                        "scenarioId": "random_walk"
                    }
                ],
                "title": "Panel Title",
                "type": "timeseries"
            },
            {
                "datasource": {
                    "type": "grafana-azure-monitor-datasource",
                    "uid": "da714998-ca29-4adc-851b-1bd93371cbc6"
                },
                "fieldConfig": {
                    "defaults": {
                        "color": {
                            "mode": "palette-classic"
                        },
                        "custom": {
                            "axisBorderShow": False,
                            "axisCenteredZero": False,
                            "axisColorMode": "text",
                            "axisLabel": "",
                            "axisPlacement": "auto",
                            "barAlignment": 0,
                            "drawStyle": "line",
                            "fillOpacity": 0,
                            "gradientMode": "none",
                            "hideFrom": {
                                "legend": False,
                                "tooltip": False,
                                "viz": False
                            },
                            "insertNones": False,
                            "lineInterpolation": "linear",
                            "lineWidth": 1,
                            "pointSize": 5,
                            "scaleDistribution": {
                                "type": "linear"
                            },
                            "showPoints": "auto",
                            "spanNones": False,
                            "stacking": {
                                "group": "A",
                                "mode": "none"
                            },
                            "thresholdsStyle": {
                                "mode": "off"
                            }
                        },
                        "mappings": [],
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {
                                    "color": "green",
                                    "value": None
                                },
                                {
                                    "color": "red",
                                    "value": 80
                                }
                            ]
                        },
                        "unitScale": True
                    },
                    "overrides": []
                },
                "gridPos": {
                    "h": 8,
                    "w": 12,
                    "x": 0,
                    "y": 8
                },
                "id": 1,
                "options": {
                    "legend": {
                        "calcs": [],
                        "displayMode": "list",
                        "placement": "bottom",
                        "showLegend": True
                    },
                    "tooltip": {
                        "mode": "single",
                        "sort": "none"
                    }
                },
                "targets": [
                    {
                        "datasource": {
                            "type": "grafana-azure-monitor-datasource",
                            "uid": "da714998-ca29-4adc-851b-1bd93371cbc6"
                        },
                        "refId": "A",
                        "scenarioId": "random_walk",
                        "seriesCount": 1
                    }
                ],
                "title": "Panel Title",
                "type": "timeseries"
            }
        ],
        "refresh": "",
        "schemaVersion": 39,
        "tags": [],
        "templating": {
            "list": []
        },
        "time": {
            "from": "now-6h",
            "to": "now"
        },
        "timeRangeUpdatedDuringEditOrView": False,
        "timepicker": {},
        "timezone": "",
        "title": "Test_DATASOURCE",
        "uid": "b493c0bb-f3ce-4486-8909-6d29605052bf",
        "version": 1,
        "weekStart": ""
    }
}

test_dashboard_with_datasource_short_uid = {
    "dashboard": {
        "annotations": {
            "list": [
                {
                    "builtIn": 1,
                    "datasource": {
                        "type": "grafana",
                        "uid": "-- Grafana --"
                    },
                    "enable": True,
                    "hide": True,
                    "iconColor": "rgba(0, 211, 255, 1)",
                    "name": "Annotations & Alerts",
                    "type": "dashboard"
                }
            ]
        },
        "editable": True,
        "fiscalYearStartMonth": 0,
        "graphTooltip": 0,
        "id": 39,
        "links": [],
        "liveNow": False,
        "panels": [
            {
                "datasource": {
                    "type": "grafana-azure-monitor-datasource",
                    "uid": "cdpe79jidbwu8d"
                },
                "fieldConfig": {
                    "defaults": {
                        "color": {
                            "mode": "palette-classic"
                        },
                        "custom": {
                            "axisBorderShow": False,
                            "axisCenteredZero": False,
                            "axisColorMode": "text",
                            "axisLabel": "",
                            "axisPlacement": "auto",
                            "barAlignment": 0,
                            "drawStyle": "line",
                            "fillOpacity": 0,
                            "gradientMode": "none",
                            "hideFrom": {
                                "legend": False,
                                "tooltip": False,
                                "viz": False
                            },
                            "insertNones": False,
                            "lineInterpolation": "linear",
                            "lineWidth": 1,
                            "pointSize": 5,
                            "scaleDistribution": {
                                "type": "linear"
                            },
                            "showPoints": "auto",
                            "spanNones": False,
                            "stacking": {
                                "group": "A",
                                "mode": "none"
                            },
                            "thresholdsStyle": {
                                "mode": "off"
                            }
                        },
                        "mappings": [],
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {
                                    "color": "green",
                                    "value": None
                                },
                                {
                                    "color": "red",
                                    "value": 80
                                }
                            ]
                        },
                        "unitScale": True
                    },
                    "overrides": []
                },
                "gridPos": {
                    "h": 8,
                    "w": 12,
                    "x": 0,
                    "y": 0
                },
                "id": 2,
                "options": {
                    "legend": {
                        "calcs": [],
                        "displayMode": "list",
                        "placement": "bottom",
                        "showLegend": True
                    },
                    "tooltip": {
                        "mode": "single",
                        "sort": "none"
                    }
                },
                "targets": [
                    {
                        "datasource": {
                            "type": "grafana-azure-monitor-datasource",
                            "uid": "cdpe79jidbwu8d"
                        },
                        "refId": "A",
                        "scenarioId": "random_walk"
                    }
                ],
                "title": "Panel Title",
                "type": "timeseries"
            },
            {
                "datasource": {
                    "type": "grafana-azure-monitor-datasource",
                    "uid": "cdpe79jidbwu8d"
                },
                "fieldConfig": {
                    "defaults": {
                        "color": {
                            "mode": "palette-classic"
                        },
                        "custom": {
                            "axisBorderShow": False,
                            "axisCenteredZero": False,
                            "axisColorMode": "text",
                            "axisLabel": "",
                            "axisPlacement": "auto",
                            "barAlignment": 0,
                            "drawStyle": "line",
                            "fillOpacity": 0,
                            "gradientMode": "none",
                            "hideFrom": {
                                "legend": False,
                                "tooltip": False,
                                "viz": False
                            },
                            "insertNones": False,
                            "lineInterpolation": "linear",
                            "lineWidth": 1,
                            "pointSize": 5,
                            "scaleDistribution": {
                                "type": "linear"
                            },
                            "showPoints": "auto",
                            "spanNones": False,
                            "stacking": {
                                "group": "A",
                                "mode": "none"
                            },
                            "thresholdsStyle": {
                                "mode": "off"
                            }
                        },
                        "mappings": [],
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {
                                    "color": "green",
                                    "value": None
                                },
                                {
                                    "color": "red",
                                    "value": 80
                                }
                            ]
                        },
                        "unitScale": True
                    },
                    "overrides": []
                },
                "gridPos": {
                    "h": 8,
                    "w": 12,
                    "x": 0,
                    "y": 8
                },
                "id": 1,
                "options": {
                    "legend": {
                        "calcs": [],
                        "displayMode": "list",
                        "placement": "bottom",
                        "showLegend": True
                    },
                    "tooltip": {
                        "mode": "single",
                        "sort": "none"
                    }
                },
                "targets": [
                    {
                        "datasource": {
                            "type": "grafana-azure-monitor-datasource",
                            "uid": "cdpe79jidbwu8d"
                        },
                        "refId": "A",
                        "scenarioId": "random_walk",
                        "seriesCount": 1
                    }
                ],
                "title": "Panel Title",
                "type": "timeseries"
            }
        ],
        "refresh": "",
        "schemaVersion": 39,
        "tags": [],
        "templating": {
            "list": []
        },
        "time": {
            "from": "now-6h",
            "to": "now"
        },
        "timeRangeUpdatedDuringEditOrView": False,
        "timepicker": {},
        "timezone": "",
        "title": "Test_DATASOURCE_SHORT_UID",
        "uid": "d493c0bb-f3ce-4486-8909-6d29605052bf",
        "version": 1,
        "weekStart": ""
    }
}