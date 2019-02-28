# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

# pylint: disable=line-too-long


helps['anf'] = """
    type: group
    short-summary: Manage Azure NetApp Files (ANF) Resources.
"""

# account

helps['anf account'] = """
    type: group
    short-summary: Manage Azure NetApp Files (ANF) Account Resources.
"""

helps['anf account create'] = """
    type: command
    short-summary: Create a new Azure NetApp Files (ANF) account.
    parameters:
        - name: --account-name
          type: string
          short-summary: The name of the ANF account
        - name: --tags
          type: string
          short-summary: A list of space separated tags to apply to the account
    examples:
        - name: Create an ANF account
          text: >
            az anf account create -g group --account-name name -l location
"""

helps['anf account update'] = """
    type: command
    short-summary: Set/modify the tags for a specified ANF account.
    parameters:
        - name: --account-name
          type: string
          short-summary: The name of the ANF account
        - name: --tags
          type: string
          short-summary: A list of space separated tags to apply to the account
    examples:
        - name: Update the tags of an ANF account
          text: >
            az anf account update -g group --account-name name --tags 'key[=value] key[=value]'
"""

helps['anf account delete'] = """
    type: command
    short-summary: Delete the specified ANF account.
    parameters:
        - name: --account-name
          type: string
          short-summary: The name of the ANF account
    examples:
        - name: Delete an ANF account
          text: >
            az anf account delete -g group --account-name name
"""

helps['anf account list'] = """
    type: command
    short-summary: List ANF accounts.
    examples:
        - name: List ANF accounts within a resource group
          text: >
            az anf account list -g group
"""

helps['anf account show'] = """
    type: command
    short-summary: Get the specified ANF account.
    parameters:
        - name: --account-name
          type: string
          short-summary: The name of the ANF account
    examples:
        - name: Get an ANF account
          text: >
            az anf account show -g group --account-name name
"""

# pools

helps['anf pool'] = """
    type: group
    short-summary: Manage Azure NetApp Files (ANF) Pool Resources.
"""

helps['anf pool create'] = """
    type: command
    short-summary: Create a new Azure NetApp Files (ANF) pool.
    parameters:
        - name: --account-name
          type: string
          short-summary: The name of the ANF account
        - name: --pool-name
          type: string
          short-summary: The name of the ANF pool
        - name: --size
          type: integer
          short-summary: The size for the ANF pool. Must be in 4 tebibytes increments, expressed in bytes
        - name: --service-level
          type: string
          short-summary: The service level for the ANF pool ["Standard"|"Premium"|"Extreme"]
        - name: --tags
          type: string
          short-summary: A list of space separated tags to apply to the pool
    examples:
        - name: Create an ANF pool
          text: >
            az anf pool create -g group --account-name aname --pool-name pname -l location --size 4398046511104 --service-level "Premium"
"""

helps['anf pool update'] = """
    type: command
    short-summary: Update the tags of the specified ANF pool.
    parameters:
        - name: --account-name
          type: string
          short-summary: The name of the ANF account
        - name: --pool-name
          type: string
          short-summary: The name of the ANF pool
        - name: --size
          type: integer
          short-summary: The size for the ANF pool. Must be in 4 tebibytes increments, expressed in bytes
        - name: --service-level
          type: string
          short-summary: The service level for the ANF pool ["Standard"|"Premium"|"Extreme"]
        - name: --tags
          type: string
          short-summary: A list of space separated tags to apply to the pool
    examples:
        - name: Update specific values for an ANF pool
          text: >
            az anf pool update -g group --account-name aname --pool-name pname --service-level "Extreme" --tags 'key[=value] key[=value]'
"""

helps['anf pool delete'] = """
    type: command
    short-summary: Delete the specified ANF pool.
    parameters:
        - name: --account-name
          type: string
          short-summary: The name of the ANF account
        - name: --pool-name
          type: string
          short-summary: The name of the ANF pool
    examples:
        - name: Delete an ANF pool
          text: >
            az anf pool delete -g group --account-name aname --pool-name pname
"""

helps['anf pool list'] = """
    type: command
    short-summary: L:ist the ANF pools for the specified account.
    parameters:
        - name: --account-name
          type: string
          short-summary: The name of the ANF account
    examples:
        - name: List the pools for the ANF account
          text: >
            az anf pool list -g group -account-name name
"""

helps['anf pool show'] = """
    type: command
    short-summary: Get the specified ANF pool.
    parameters:
        - name: --account-name
          type: string
          short-summary: The name of the ANF account
        - name: --pool-name
          type: string
          short-summary: The name of the ANF pool
    examples:
        - name: Get an ANF pool
          text: >
            az anf pool show -g group --account-name aname --pool-name pname
"""

# volumes

helps['anf volume'] = """
    type: group
    short-summary: Manage Azure NetApp Files (ANF) Volume Resources.
"""

helps['anf volume create'] = """
    type: command
    short-summary: Create a new Azure NetApp Files (ANF) volume.
    parameters:
        - name: --account-name
          type: string
          short-summary: The name of the ANF account
        - name: --pool-name
          type: string
          short-summary: The name of the ANF pool
        - name: --volume-name
          type: string
          short-summary: The name of the ANF volume
        - name: --service-level
          type: string
          short-summary: The service level ["Standard"|"Premium"|"Extreme"]
        - name: --usage-threshold
          type: int
          short-summary: The maximum storage quota allowed for a file system in bytes. Min 100 GiB, max 100TiB"
        - name: --creation-token
          type: string
          short-summary: A unique file path identifier, from 1 to 80 characters
        - name: --subnet-id
          type: string
          short-summary: The subnet identifier
        - name: --tags
          type: string
          short-summary:  A list of space separated tags to apply to the volume
    examples:
        - name: Create an ANF volume
          text: >
            az anf volume create -g group --account-name aname --pool-name pname --volume-name vname -l location --service-level "Premium" --usage-threshold 107374182400 --creation-token "unique-token" --subnet-id "/subscriptions/mysubsid/resourceGroups/myrg/providers/Microsoft.Network/virtualNetworks/myvnet/subnets/default"
"""

helps['anf volume update'] = """
    type: command
    short-summary: Update the specified ANF volume with the values provided. Unspecified values will remain unchanged.
    parameters:
        - name: --account-name
          type: string
          short-summary: The name of the ANF account
        - name: --pool-name
          type: string
          short-summary: The name of the ANF pool
        - name: --volume-name
          type: string
          short-summary: The name of the ANF volume
        - name: --service-level
          type: string
          short-summary: The service level ["Standard"|"Premium"|"Extreme"]
        - name: --usage-threshold
          type: int
          short-summary: The maximum storage quota allowed for a file system in bytes. Min 100 GiB, max 100TiB"
        - name: --tags
          type: string
          short-summary:  A list of space separated tags to apply to the volume
    examples:
        - name: Create an ANF volume
          text: >
            az anf volume update -g group --account-name aname --pool-name pname --volume-name vname --service-level level --usage-threshold 107374182400 --tags 'key[=value] key[=value]'
"""

helps['anf volume delete'] = """
    type: command
    short-summary: Delete the specified ANF volume.
    parameters:
        - name: --account-name
          type: string
          short-summary: The name of the ANF account
        - name: --pool-name
          type: string
          short-summary: The name of the ANF pool
        - name: --volume-name
          type: string
          short-summary: The name of the ANF volume
    examples:
        - name: Delete an ANF volume
          text: >
            az anf volume delete -g group --account-name aname --pool-name pname
"""

helps['anf volume list'] = """
    type: command
    short-summary: List the ANF Pools for the specified account.
    parameters:
        - name: --account-name
          type: string
          short-summary: The name of the ANF account
        - name: --pool-name
          type: string
          short-summary: The name of the ANF pool
    examples:
        - name: List the ANF volumes of the pool
          text: >
            az anf volume list -g group --account-name aname --pool-name pname
"""

helps['anf volume show'] = """
    type: command
    short-summary: Get the specified ANF volume.
    parameters:
        - name: --account-name
          type: string
          short-summary: The name of the ANF account
        - name: --pool-name
          type: string
          short-summary: The name of the ANF pool
        - name: --volume-name
          type: string
          short-summary: The name of the ANF pool
    examples:
        - name: Returns the properties of the given ANF volume
          text: >
            az anf volume show -g group --account-name aname --pool-name pname --volume_name vname
"""

# mounttargets

helps['anf mount-target'] = """
    type: group
    short-summary: Manage Azure NetApp Files (ANF) Mount Target Resources.
"""

helps['anf mount-target list'] = """
    type: command
    short-summary: List the mount targets of an ANF volume.
    parameters:
        - name: --account-name
          type: string
          short-summary: The name of the ANF account
        - name: --pool-name
          type: string
          short-summary: The name of the ANF pool
        - name: --volume-name
          type: string
          short-summary: The name of the ANF pool
    examples:
        - name: list the mount targets of an ANF volume
          text: >
            az anf mount-target list -g group --account-name aname --pool-name pname --volume-name vname
"""

# snapshots

helps['anf snapshot'] = """
    type: group
    short-summary: Manage Azure NetApp Files (ANF) Snapshot Resources.
"""

helps['anf snapshot create'] = """
    type: command
    short-summary: Create a new Azure NetApp Files (ANF) snapshot.
    parameters:
        - name: --account-name
          type: string
          short-summary: The name of the ANF account
        - name: --pool-name
          type: string
          short-summary: The name of the ANF pool
        - name: --volume-name
          type: string
          short-summary: The name of the ANF volume
        - name: --snapshot-name
          type: string
          short-summary: The name of the ANF snapshot
        - name: --file-system-id
          type: string
          short-summary: The uuid of the volume
    examples:
        - name: Create an ANF snapshot
          text: >
            az anf snapshot create -g group --account-name account-name --pool-name pname --volume-name vname --snapshot-name sname -l location --file-system-id volume-uuid
"""

helps['anf snapshot delete'] = """
    type: command
    short-summary: Delete the specified ANF snapshot.
    parameters:
        - name: --account-name
          type: string
          short-summary: The name of the ANF account
        - name: --pool-name
          type: string
          short-summary: The name of the ANF pool
        - name: --volume-name
          type: string
          short-summary: The name of the ANF volume
        - name: --snapshot-name
          type: string
          short-summary: The name of the ANF snapshot
    examples:
        - name: Delete an ANF snapshot
          text: >
            az anf volume delete -g group --account-name aname --pool-name pname --volume-name vname --snapshot-name sname
"""

helps['anf snapshot list'] = """
    type: command
    short-summary: List the snapshots of an ANF volume.
    parameters:
        - name: --account-name
          type: string
          short-summary: The name of the ANF account
        - name: --pool-name
          type: string
          short-summary: The name of the ANF pool
        - name: --volume-name
          type: string
          short-summary: The name of the ANF volume
    examples:
        - name: list the snapshots of an ANF volume
          text: >
            az anf account list -g group --account-name aname --pool-name pname --volume-name vname
"""

helps['anf snapshot show'] = """
    type: command
    short-summary: Get the specified ANF snapshot.
    parameters:
        - name: --account-name
          type: string
          short-summary: The name of the ANF account
        - name: --pool-name
          type: string
          short-summary: The name of the ANF pool
        - name: --volume-name
          type: string
          short-summary: The name of the ANF volume
        - name: --snapshot-name
          type: string
          short-summary: The name of the ANF snapshot
    examples:
        - name: Return the specified ANF snapshot
          text: >
            az anf snapshot show -g group --account-name aname --pool-name pname --volume-name vname --snapshot-name sname
"""
