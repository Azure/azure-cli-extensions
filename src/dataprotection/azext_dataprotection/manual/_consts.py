# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# AKS Backup Strategy Constants
CONST_BACKUP_STRATEGY_WEEK = "Week"
CONST_BACKUP_STRATEGY_MONTH = "Month"
CONST_BACKUP_STRATEGY_DISASTER_RECOVERY = "DisasterRecovery"
CONST_BACKUP_STRATEGY_CUSTOM = "Custom"

# List of all backup strategies for AKS
CONST_AKS_BACKUP_STRATEGIES = [
    CONST_BACKUP_STRATEGY_WEEK,
    CONST_BACKUP_STRATEGY_MONTH,
    CONST_BACKUP_STRATEGY_DISASTER_RECOVERY,
    CONST_BACKUP_STRATEGY_CUSTOM,
]
