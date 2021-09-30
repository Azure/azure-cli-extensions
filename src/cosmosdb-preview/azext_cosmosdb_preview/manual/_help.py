from knack.help_files import helps

helps['cosmosdb data-transfer-job create2'] = """
    type: command
    short-summary: "Creates a Data Transfer Job."
    parameters:
      - name: --source
        short-summary: "Data Source"
        long-summary: |
            Usage: --source type=CosmosDBCassandra keyspace-name=XX table-name=XX'
                   --source type=AzureBlobStorage container-name=XX endpoint-url=XX

            type: Type of component, Possible values: CosmosDBCassandra, AzureBlobStorage
            keyspace-name: Keyspace name of CosmosDB Cassandra data source. Use with type=CosmosDBCassandra
            table-name: Table name of CosmosDB Cassandra data source. Use with type=CosmosDBCassandra
            container-name: Container name of Azure Blob Storage. Use with type=AzureBlobStorage
            endpoint-url: Endpoint Url of Azure Blob Storage. Use with type=AzureBlobStorage

      - name: --destination
        short-summary: "Data Sink"
        long-summary: |
            Usage: --destination type=AzureBlobStorage container-name=XX endpoint-url=XX
                   --destination type=CosmosDBCassandra keyspace-name=XX table-name=XX'

            type: Type of component, Possible values: CosmosDBCassandra, AzureBlobStorage
            keyspace-name: Keyspace name of CosmosDB Cassandra data source. Use with type=CosmosDBCassandra
            table-name: Table name of CosmosDB Cassandra data source. Use with type=CosmosDBCassandra
            container-name: Container name of Azure Blob Storage. Use with type=AzureBlobStorage
            endpoint-url: Endpoint Url of Azure Blob Storage. Use with type=AzureBlobStorage
            
    examples:
      - name: CosmosDBDataTransferJobCreate
        text: |-
          az cosmosdb data-transfer-job create2 --account-name "db1" --resource-group "rg1" --job-name "j1" --destination type=CosmosDBCassandra keyspace-name=keyspace table-name=t1\
 --source type=AzureBlobStorage container-name=backup1 endpoint-url=https://backupstorage.blob.core.windows.net/ 

"""