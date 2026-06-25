temp_cluster_capabilities = {
    "value": [
        {
            "name": "HorizondbCapabilities",
            "supportedProcessor": [
                {
                    "name": "Intel",
                    "defaultVCores": "4",
                    "supportedMemoryPerVcoreMb": 8192,
                    "supportedVcores": ["2", "4", "8", "16", "20", "32", "48", "64", "96", "128", "192"],
                    "supportedZones": ["1", "2", "3"],
                }
            ],
            "supportedVersions": [
                {
                    "name": "18",
                    "supportedVersionsToUpgrade": [],
                },
                {
                    "name": "17",
                    "supportedVersionsToUpgrade": [],
                },
            ],
            "supportedFeatures": {
                "zoneRedundantHa": "Enabled",
            },
        }
    ],
}
