# Azure CLI Module Creation Report

### datafactory activity-run query-by-pipeline-run

query-by-pipeline-run a datafactory activity-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--run-id**|string|The pipeline run identifier.|run_id|run_id|
|**--last-updated-after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|last_updated_after|last_updated_after|
|**--last-updated-before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|last_updated_before|last_updated_before|
|**--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|continuation_token|
|**--filters**|array|List of filters.|filters|filters|
|**--order-by**|array|List of OrderBy option.|order_by|order_by|
### datafactory data-flow create

create a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--data-flow-name**|string|The data flow name.|data_flow_name|data_flow_name|
|**--properties**|object|Data flow properties.|properties|properties|
|**--if-match**|string|ETag of the data flow entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
### datafactory data-flow delete

delete a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--data-flow-name**|string|The data flow name.|data_flow_name|data_flow_name|
### datafactory data-flow list

list a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
### datafactory data-flow show

show a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--data-flow-name**|string|The data flow name.|data_flow_name|data_flow_name|
|**--if-none-match**|string|ETag of the data flow entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|if_none_match|
### datafactory data-flow update

create a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--data-flow-name**|string|The data flow name.|data_flow_name|data_flow_name|
|**--properties**|object|Data flow properties.|properties|properties|
|**--if-match**|string|ETag of the data flow entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
### datafactory data-flow-debug-session add-data-flow

add-data-flow a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--session-id**|string|The ID of data flow debug session.|session_id|session_id|
|**--data-flow**|object|Data flow instance.|data_flow|data_flow|
|**--datasets**|array|List of datasets.|datasets|datasets|
|**--linked-services**|array|List of linked services.|linked_services|linked_services|
|**--staging**|object|Staging info for debug session.|staging|staging|
|**--debug-settings**|object|Data flow debug settings.|debug_settings|debug_settings|
### datafactory data-flow-debug-session create

create a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--compute-type**|string|Compute type of the cluster. The value will be overwritten by the same setting in integration runtime if provided.|compute_type|compute_type|
|**--core-count**|integer|Core count of the cluster. The value will be overwritten by the same setting in integration runtime if provided.|core_count|core_count|
|**--time-to-live**|integer|Time to live setting of the cluster in minutes.|time_to_live|time_to_live|
|**--integration-runtime**|object|Set to use integration runtime setting for data flow debug session.|integration_runtime|integration_runtime|
### datafactory data-flow-debug-session delete

delete a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--session-id**|string|The ID of data flow debug session.|session_id|session_id|
### datafactory data-flow-debug-session execute-command

execute-command a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--session-id**|string|The ID of data flow debug session.|session_id|session_id|
|**--command**|choice|The command type.|command|command|
|**--command-payload**|object|The command payload object.|command_payload|command_payload|
### datafactory data-flow-debug-session query-by-factory

query-by-factory a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
### datafactory dataset amazon-m-w-s-object create

amazon-m-w-s-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|amazonmwsobject_type|amazon_m_w_s_object_type|
|**--linked-service-name**|object|Linked service reference.|amazonmwsobject_linked_service_name|amazon_m_w_s_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|amazonmwsobject_description|amazon_m_w_s_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|amazonmwsobject_structure|amazon_m_w_s_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|amazonmwsobject_schema|amazon_m_w_s_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|amazonmwsobject_parameters|amazon_m_w_s_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|amazonmwsobject_annotations|amazon_m_w_s_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|amazonmwsobject_folder|amazon_m_w_s_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|amazonmwsobject_table_name|amazon_m_w_s_object_table_name|
### datafactory dataset amazon-m-w-s-object update

amazon-m-w-s-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|amazonmwsobject_type|amazon_m_w_s_object_type|
|**--linked-service-name**|object|Linked service reference.|amazonmwsobject_linked_service_name|amazon_m_w_s_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|amazonmwsobject_description|amazon_m_w_s_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|amazonmwsobject_structure|amazon_m_w_s_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|amazonmwsobject_schema|amazon_m_w_s_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|amazonmwsobject_parameters|amazon_m_w_s_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|amazonmwsobject_annotations|amazon_m_w_s_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|amazonmwsobject_folder|amazon_m_w_s_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|amazonmwsobject_table_name|amazon_m_w_s_object_table_name|
### datafactory dataset amazon-redshift-table create

amazon-redshift-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|amazonredshifttable_type|amazon_redshift_table_type|
|**--linked-service-name**|object|Linked service reference.|amazonredshifttable_linked_service_name|amazon_redshift_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|amazonredshifttable_description|amazon_redshift_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|amazonredshifttable_structure|amazon_redshift_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|amazonredshifttable_schema|amazon_redshift_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|amazonredshifttable_parameters|amazon_redshift_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|amazonredshifttable_annotations|amazon_redshift_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|amazonredshifttable_folder|amazon_redshift_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|amazonredshifttable_table_name|amazon_redshift_table_table_name|
|**--type-properties-table**|any|The Amazon Redshift table name. Type: string (or Expression with resultType string).|amazonredshifttable_table|amazon_redshift_table_table|
|**--type-properties-schema**|any|The Amazon Redshift schema name. Type: string (or Expression with resultType string).|amazonredshifttable_schema_type_properties_schema|amazon_redshift_table_schema_type_properties_schema|
### datafactory dataset amazon-redshift-table update

amazon-redshift-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|amazonredshifttable_type|amazon_redshift_table_type|
|**--linked-service-name**|object|Linked service reference.|amazonredshifttable_linked_service_name|amazon_redshift_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|amazonredshifttable_description|amazon_redshift_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|amazonredshifttable_structure|amazon_redshift_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|amazonredshifttable_schema|amazon_redshift_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|amazonredshifttable_parameters|amazon_redshift_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|amazonredshifttable_annotations|amazon_redshift_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|amazonredshifttable_folder|amazon_redshift_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|amazonredshifttable_table_name|amazon_redshift_table_table_name|
|**--type-properties-table**|any|The Amazon Redshift table name. Type: string (or Expression with resultType string).|amazonredshifttable_table|amazon_redshift_table_table|
|**--type-properties-schema**|any|The Amazon Redshift schema name. Type: string (or Expression with resultType string).|amazonredshifttable_schema_type_properties_schema|amazon_redshift_table_schema_type_properties_schema|
### datafactory dataset amazon-s3-object create

amazon-s3-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|amazons3object_type|amazon_s3_object_type|
|**--linked-service-name**|object|Linked service reference.|amazons3object_linked_service_name|amazon_s3_object_linked_service_name|
|**--type-properties-bucket-name**|any|The name of the Amazon S3 bucket. Type: string (or Expression with resultType string).|amazons3object_bucket_name|amazon_s3_object_bucket_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|amazons3object_description|amazon_s3_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|amazons3object_structure|amazon_s3_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|amazons3object_schema|amazon_s3_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|amazons3object_parameters|amazon_s3_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|amazons3object_annotations|amazon_s3_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|amazons3object_folder|amazon_s3_object_folder|
|**--type-properties-key**|any|The key of the Amazon S3 object. Type: string (or Expression with resultType string).|amazons3object_key|amazon_s3_object_key|
|**--type-properties-prefix**|any|The prefix filter for the S3 object name. Type: string (or Expression with resultType string).|amazons3object_prefix|amazon_s3_object_prefix|
|**--type-properties-version**|any|The version for the S3 object. Type: string (or Expression with resultType string).|amazons3object_version|amazon_s3_object_version|
|**--type-properties-modified-datetime-start**|any|The start of S3 object's modified datetime. Type: string (or Expression with resultType string).|amazons3object_modified_datetime_start|amazon_s3_object_modified_datetime_start|
|**--type-properties-modified-datetime-end**|any|The end of S3 object's modified datetime. Type: string (or Expression with resultType string).|amazons3object_modified_datetime_end|amazon_s3_object_modified_datetime_end|
|**--type-properties-format**|object|The format of files.|amazons3object_format|amazon_s3_object_format|
|**--type-properties-compression**|object|The data compression method used for the Amazon S3 object.|amazons3object_compression|amazon_s3_object_compression|
### datafactory dataset amazon-s3-object update

amazon-s3-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|amazons3object_type|amazon_s3_object_type|
|**--linked-service-name**|object|Linked service reference.|amazons3object_linked_service_name|amazon_s3_object_linked_service_name|
|**--type-properties-bucket-name**|any|The name of the Amazon S3 bucket. Type: string (or Expression with resultType string).|amazons3object_bucket_name|amazon_s3_object_bucket_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|amazons3object_description|amazon_s3_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|amazons3object_structure|amazon_s3_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|amazons3object_schema|amazon_s3_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|amazons3object_parameters|amazon_s3_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|amazons3object_annotations|amazon_s3_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|amazons3object_folder|amazon_s3_object_folder|
|**--type-properties-key**|any|The key of the Amazon S3 object. Type: string (or Expression with resultType string).|amazons3object_key|amazon_s3_object_key|
|**--type-properties-prefix**|any|The prefix filter for the S3 object name. Type: string (or Expression with resultType string).|amazons3object_prefix|amazon_s3_object_prefix|
|**--type-properties-version**|any|The version for the S3 object. Type: string (or Expression with resultType string).|amazons3object_version|amazon_s3_object_version|
|**--type-properties-modified-datetime-start**|any|The start of S3 object's modified datetime. Type: string (or Expression with resultType string).|amazons3object_modified_datetime_start|amazon_s3_object_modified_datetime_start|
|**--type-properties-modified-datetime-end**|any|The end of S3 object's modified datetime. Type: string (or Expression with resultType string).|amazons3object_modified_datetime_end|amazon_s3_object_modified_datetime_end|
|**--type-properties-format**|object|The format of files.|amazons3object_format|amazon_s3_object_format|
|**--type-properties-compression**|object|The data compression method used for the Amazon S3 object.|amazons3object_compression|amazon_s3_object_compression|
### datafactory dataset avro create

avro create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|avro_type|avro_type|
|**--linked-service-name**|object|Linked service reference.|avro_linked_service_name|avro_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|avro_description|avro_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|avro_structure|avro_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|avro_schema|avro_schema|
|**--parameters**|dictionary|Parameters for dataset.|avro_parameters|avro_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|avro_annotations|avro_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|avro_folder|avro_folder|
|**--type-properties-location**|object|The location of the avro storage.|avro_location|avro_location|
|**--type-properties-avro-compression-codec**|choice||avro_avro_compression_codec|avro_avro_compression_codec|
|**--type-properties-avro-compression-level**|integer||avro_avro_compression_level|avro_avro_compression_level|
### datafactory dataset avro update

avro create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|avro_type|avro_type|
|**--linked-service-name**|object|Linked service reference.|avro_linked_service_name|avro_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|avro_description|avro_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|avro_structure|avro_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|avro_schema|avro_schema|
|**--parameters**|dictionary|Parameters for dataset.|avro_parameters|avro_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|avro_annotations|avro_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|avro_folder|avro_folder|
|**--type-properties-location**|object|The location of the avro storage.|avro_location|avro_location|
|**--type-properties-avro-compression-codec**|choice||avro_avro_compression_codec|avro_avro_compression_codec|
|**--type-properties-avro-compression-level**|integer||avro_avro_compression_level|avro_avro_compression_level|
### datafactory dataset azure-blob create

azure-blob create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azureblob_type|azure_blob_type|
|**--linked-service-name**|object|Linked service reference.|azureblob_linked_service_name|azure_blob_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azureblob_description|azure_blob_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azureblob_structure|azure_blob_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azureblob_schema|azure_blob_schema|
|**--parameters**|dictionary|Parameters for dataset.|azureblob_parameters|azure_blob_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azureblob_annotations|azure_blob_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azureblob_folder|azure_blob_folder|
|**--type-properties-folder-path**|any|The path of the Azure Blob storage. Type: string (or Expression with resultType string).|azureblob_folder_path|azure_blob_folder_path|
|**--type-properties-table-root-location**|any|The root of blob path. Type: string (or Expression with resultType string).|azureblob_table_root_location|azure_blob_table_root_location|
|**--type-properties-file-name**|any|The name of the Azure Blob. Type: string (or Expression with resultType string).|azureblob_file_name|azure_blob_file_name|
|**--type-properties-modified-datetime-start**|any|The start of Azure Blob's modified datetime. Type: string (or Expression with resultType string).|azureblob_modified_datetime_start|azure_blob_modified_datetime_start|
|**--type-properties-modified-datetime-end**|any|The end of Azure Blob's modified datetime. Type: string (or Expression with resultType string).|azureblob_modified_datetime_end|azure_blob_modified_datetime_end|
|**--type-properties-format**|object|The format of the Azure Blob storage.|azureblob_format|azure_blob_format|
|**--type-properties-compression**|object|The data compression method used for the blob storage.|azureblob_compression|azure_blob_compression|
### datafactory dataset azure-blob update

azure-blob create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azureblob_type|azure_blob_type|
|**--linked-service-name**|object|Linked service reference.|azureblob_linked_service_name|azure_blob_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azureblob_description|azure_blob_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azureblob_structure|azure_blob_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azureblob_schema|azure_blob_schema|
|**--parameters**|dictionary|Parameters for dataset.|azureblob_parameters|azure_blob_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azureblob_annotations|azure_blob_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azureblob_folder|azure_blob_folder|
|**--type-properties-folder-path**|any|The path of the Azure Blob storage. Type: string (or Expression with resultType string).|azureblob_folder_path|azure_blob_folder_path|
|**--type-properties-table-root-location**|any|The root of blob path. Type: string (or Expression with resultType string).|azureblob_table_root_location|azure_blob_table_root_location|
|**--type-properties-file-name**|any|The name of the Azure Blob. Type: string (or Expression with resultType string).|azureblob_file_name|azure_blob_file_name|
|**--type-properties-modified-datetime-start**|any|The start of Azure Blob's modified datetime. Type: string (or Expression with resultType string).|azureblob_modified_datetime_start|azure_blob_modified_datetime_start|
|**--type-properties-modified-datetime-end**|any|The end of Azure Blob's modified datetime. Type: string (or Expression with resultType string).|azureblob_modified_datetime_end|azure_blob_modified_datetime_end|
|**--type-properties-format**|object|The format of the Azure Blob storage.|azureblob_format|azure_blob_format|
|**--type-properties-compression**|object|The data compression method used for the blob storage.|azureblob_compression|azure_blob_compression|
### datafactory dataset azure-blob-f-s-file create

azure-blob-f-s-file create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azureblobfsfile_type|azure_blob_f_s_file_type|
|**--linked-service-name**|object|Linked service reference.|azureblobfsfile_linked_service_name|azure_blob_f_s_file_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azureblobfsfile_description|azure_blob_f_s_file_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azureblobfsfile_structure|azure_blob_f_s_file_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azureblobfsfile_schema|azure_blob_f_s_file_schema|
|**--parameters**|dictionary|Parameters for dataset.|azureblobfsfile_parameters|azure_blob_f_s_file_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azureblobfsfile_annotations|azure_blob_f_s_file_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azureblobfsfile_folder|azure_blob_f_s_file_folder|
|**--type-properties-folder-path**|any|The path of the Azure Data Lake Storage Gen2 storage. Type: string (or Expression with resultType string).|azureblobfsfile_folder_path|azure_blob_f_s_file_folder_path|
|**--type-properties-file-name**|any|The name of the Azure Data Lake Storage Gen2. Type: string (or Expression with resultType string).|azureblobfsfile_file_name|azure_blob_f_s_file_file_name|
|**--type-properties-format**|object|The format of the Azure Data Lake Storage Gen2 storage.|azureblobfsfile_format|azure_blob_f_s_file_format|
|**--type-properties-compression**|object|The data compression method used for the blob storage.|azureblobfsfile_compression|azure_blob_f_s_file_compression|
### datafactory dataset azure-blob-f-s-file update

azure-blob-f-s-file create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azureblobfsfile_type|azure_blob_f_s_file_type|
|**--linked-service-name**|object|Linked service reference.|azureblobfsfile_linked_service_name|azure_blob_f_s_file_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azureblobfsfile_description|azure_blob_f_s_file_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azureblobfsfile_structure|azure_blob_f_s_file_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azureblobfsfile_schema|azure_blob_f_s_file_schema|
|**--parameters**|dictionary|Parameters for dataset.|azureblobfsfile_parameters|azure_blob_f_s_file_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azureblobfsfile_annotations|azure_blob_f_s_file_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azureblobfsfile_folder|azure_blob_f_s_file_folder|
|**--type-properties-folder-path**|any|The path of the Azure Data Lake Storage Gen2 storage. Type: string (or Expression with resultType string).|azureblobfsfile_folder_path|azure_blob_f_s_file_folder_path|
|**--type-properties-file-name**|any|The name of the Azure Data Lake Storage Gen2. Type: string (or Expression with resultType string).|azureblobfsfile_file_name|azure_blob_f_s_file_file_name|
|**--type-properties-format**|object|The format of the Azure Data Lake Storage Gen2 storage.|azureblobfsfile_format|azure_blob_f_s_file_format|
|**--type-properties-compression**|object|The data compression method used for the blob storage.|azureblobfsfile_compression|azure_blob_f_s_file_compression|
### datafactory dataset azure-data-explorer-table create

azure-data-explorer-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azuredataexplorertable_type|azure_data_explorer_table_type|
|**--linked-service-name**|object|Linked service reference.|azuredataexplorertable_linked_service_name|azure_data_explorer_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azuredataexplorertable_description|azure_data_explorer_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azuredataexplorertable_structure|azure_data_explorer_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azuredataexplorertable_schema|azure_data_explorer_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azuredataexplorertable_parameters|azure_data_explorer_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azuredataexplorertable_annotations|azure_data_explorer_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azuredataexplorertable_folder|azure_data_explorer_table_folder|
|**--type-properties-table**|any|The table name of the Azure Data Explorer database. Type: string (or Expression with resultType string).|azuredataexplorertable_table|azure_data_explorer_table_table|
### datafactory dataset azure-data-explorer-table update

azure-data-explorer-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azuredataexplorertable_type|azure_data_explorer_table_type|
|**--linked-service-name**|object|Linked service reference.|azuredataexplorertable_linked_service_name|azure_data_explorer_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azuredataexplorertable_description|azure_data_explorer_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azuredataexplorertable_structure|azure_data_explorer_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azuredataexplorertable_schema|azure_data_explorer_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azuredataexplorertable_parameters|azure_data_explorer_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azuredataexplorertable_annotations|azure_data_explorer_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azuredataexplorertable_folder|azure_data_explorer_table_folder|
|**--type-properties-table**|any|The table name of the Azure Data Explorer database. Type: string (or Expression with resultType string).|azuredataexplorertable_table|azure_data_explorer_table_table|
### datafactory dataset azure-data-lake-store-file create

azure-data-lake-store-file create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azuredatalakestorefile_type|azure_data_lake_store_file_type|
|**--linked-service-name**|object|Linked service reference.|azuredatalakestorefile_linked_service_name|azure_data_lake_store_file_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azuredatalakestorefile_description|azure_data_lake_store_file_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azuredatalakestorefile_structure|azure_data_lake_store_file_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azuredatalakestorefile_schema|azure_data_lake_store_file_schema|
|**--parameters**|dictionary|Parameters for dataset.|azuredatalakestorefile_parameters|azure_data_lake_store_file_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azuredatalakestorefile_annotations|azure_data_lake_store_file_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azuredatalakestorefile_folder|azure_data_lake_store_file_folder|
|**--type-properties-folder-path**|any|Path to the folder in the Azure Data Lake Store. Type: string (or Expression with resultType string).|azuredatalakestorefile_folder_path|azure_data_lake_store_file_folder_path|
|**--type-properties-file-name**|any|The name of the file in the Azure Data Lake Store. Type: string (or Expression with resultType string).|azuredatalakestorefile_file_name|azure_data_lake_store_file_file_name|
|**--type-properties-format**|object|The format of the Data Lake Store.|azuredatalakestorefile_format|azure_data_lake_store_file_format|
|**--type-properties-compression**|object|The data compression method used for the item(s) in the Azure Data Lake Store.|azuredatalakestorefile_compression|azure_data_lake_store_file_compression|
### datafactory dataset azure-data-lake-store-file update

azure-data-lake-store-file create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azuredatalakestorefile_type|azure_data_lake_store_file_type|
|**--linked-service-name**|object|Linked service reference.|azuredatalakestorefile_linked_service_name|azure_data_lake_store_file_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azuredatalakestorefile_description|azure_data_lake_store_file_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azuredatalakestorefile_structure|azure_data_lake_store_file_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azuredatalakestorefile_schema|azure_data_lake_store_file_schema|
|**--parameters**|dictionary|Parameters for dataset.|azuredatalakestorefile_parameters|azure_data_lake_store_file_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azuredatalakestorefile_annotations|azure_data_lake_store_file_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azuredatalakestorefile_folder|azure_data_lake_store_file_folder|
|**--type-properties-folder-path**|any|Path to the folder in the Azure Data Lake Store. Type: string (or Expression with resultType string).|azuredatalakestorefile_folder_path|azure_data_lake_store_file_folder_path|
|**--type-properties-file-name**|any|The name of the file in the Azure Data Lake Store. Type: string (or Expression with resultType string).|azuredatalakestorefile_file_name|azure_data_lake_store_file_file_name|
|**--type-properties-format**|object|The format of the Data Lake Store.|azuredatalakestorefile_format|azure_data_lake_store_file_format|
|**--type-properties-compression**|object|The data compression method used for the item(s) in the Azure Data Lake Store.|azuredatalakestorefile_compression|azure_data_lake_store_file_compression|
### datafactory dataset azure-maria-d-b-table create

azure-maria-d-b-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azuremariadbtable_type|azure_maria_d_b_table_type|
|**--linked-service-name**|object|Linked service reference.|azuremariadbtable_linked_service_name|azure_maria_d_b_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azuremariadbtable_description|azure_maria_d_b_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azuremariadbtable_structure|azure_maria_d_b_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azuremariadbtable_schema|azure_maria_d_b_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azuremariadbtable_parameters|azure_maria_d_b_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azuremariadbtable_annotations|azure_maria_d_b_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azuremariadbtable_folder|azure_maria_d_b_table_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|azuremariadbtable_table_name|azure_maria_d_b_table_table_name|
### datafactory dataset azure-maria-d-b-table update

azure-maria-d-b-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azuremariadbtable_type|azure_maria_d_b_table_type|
|**--linked-service-name**|object|Linked service reference.|azuremariadbtable_linked_service_name|azure_maria_d_b_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azuremariadbtable_description|azure_maria_d_b_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azuremariadbtable_structure|azure_maria_d_b_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azuremariadbtable_schema|azure_maria_d_b_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azuremariadbtable_parameters|azure_maria_d_b_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azuremariadbtable_annotations|azure_maria_d_b_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azuremariadbtable_folder|azure_maria_d_b_table_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|azuremariadbtable_table_name|azure_maria_d_b_table_table_name|
### datafactory dataset azure-my-sql-table create

azure-my-sql-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azuremysqltable_type|azure_my_sql_table_type|
|**--linked-service-name**|object|Linked service reference.|azuremysqltable_linked_service_name|azure_my_sql_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azuremysqltable_description|azure_my_sql_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azuremysqltable_structure|azure_my_sql_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azuremysqltable_schema|azure_my_sql_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azuremysqltable_parameters|azure_my_sql_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azuremysqltable_annotations|azure_my_sql_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azuremysqltable_folder|azure_my_sql_table_folder|
|**--type-properties-table-name**|any|The Azure MySQL database table name. Type: string (or Expression with resultType string).|azuremysqltable_table_name|azure_my_sql_table_table_name|
|**--type-properties-table**|any|The name of Azure MySQL database table. Type: string (or Expression with resultType string).|azuremysqltable_table|azure_my_sql_table_table|
### datafactory dataset azure-my-sql-table update

azure-my-sql-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azuremysqltable_type|azure_my_sql_table_type|
|**--linked-service-name**|object|Linked service reference.|azuremysqltable_linked_service_name|azure_my_sql_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azuremysqltable_description|azure_my_sql_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azuremysqltable_structure|azure_my_sql_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azuremysqltable_schema|azure_my_sql_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azuremysqltable_parameters|azure_my_sql_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azuremysqltable_annotations|azure_my_sql_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azuremysqltable_folder|azure_my_sql_table_folder|
|**--type-properties-table-name**|any|The Azure MySQL database table name. Type: string (or Expression with resultType string).|azuremysqltable_table_name|azure_my_sql_table_table_name|
|**--type-properties-table**|any|The name of Azure MySQL database table. Type: string (or Expression with resultType string).|azuremysqltable_table|azure_my_sql_table_table|
### datafactory dataset azure-postgre-sql-table create

azure-postgre-sql-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azurepostgresqltable_type|azure_postgre_sql_table_type|
|**--linked-service-name**|object|Linked service reference.|azurepostgresqltable_linked_service_name|azure_postgre_sql_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azurepostgresqltable_description|azure_postgre_sql_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azurepostgresqltable_structure|azure_postgre_sql_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azurepostgresqltable_schema|azure_postgre_sql_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azurepostgresqltable_parameters|azure_postgre_sql_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azurepostgresqltable_annotations|azure_postgre_sql_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azurepostgresqltable_folder|azure_postgre_sql_table_folder|
|**--type-properties-table-name**|any|The table name of the Azure PostgreSQL database which includes both schema and table. Type: string (or Expression with resultType string).|azurepostgresqltable_table_name|azure_postgre_sql_table_table_name|
|**--type-properties-table**|any|The table name of the Azure PostgreSQL database. Type: string (or Expression with resultType string).|azurepostgresqltable_table|azure_postgre_sql_table_table|
|**--type-properties-schema**|any|The schema name of the Azure PostgreSQL database. Type: string (or Expression with resultType string).|azurepostgresqltable_schema_type_properties_schema|azure_postgre_sql_table_schema_type_properties_schema|
### datafactory dataset azure-postgre-sql-table update

azure-postgre-sql-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azurepostgresqltable_type|azure_postgre_sql_table_type|
|**--linked-service-name**|object|Linked service reference.|azurepostgresqltable_linked_service_name|azure_postgre_sql_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azurepostgresqltable_description|azure_postgre_sql_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azurepostgresqltable_structure|azure_postgre_sql_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azurepostgresqltable_schema|azure_postgre_sql_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azurepostgresqltable_parameters|azure_postgre_sql_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azurepostgresqltable_annotations|azure_postgre_sql_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azurepostgresqltable_folder|azure_postgre_sql_table_folder|
|**--type-properties-table-name**|any|The table name of the Azure PostgreSQL database which includes both schema and table. Type: string (or Expression with resultType string).|azurepostgresqltable_table_name|azure_postgre_sql_table_table_name|
|**--type-properties-table**|any|The table name of the Azure PostgreSQL database. Type: string (or Expression with resultType string).|azurepostgresqltable_table|azure_postgre_sql_table_table|
|**--type-properties-schema**|any|The schema name of the Azure PostgreSQL database. Type: string (or Expression with resultType string).|azurepostgresqltable_schema_type_properties_schema|azure_postgre_sql_table_schema_type_properties_schema|
### datafactory dataset azure-search-index create

azure-search-index create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azuresearchindex_type|azure_search_index_type|
|**--linked-service-name**|object|Linked service reference.|azuresearchindex_linked_service_name|azure_search_index_linked_service_name|
|**--type-properties-index-name**|any|The name of the Azure Search Index. Type: string (or Expression with resultType string).|azuresearchindex_index_name|azure_search_index_index_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azuresearchindex_description|azure_search_index_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azuresearchindex_structure|azure_search_index_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azuresearchindex_schema|azure_search_index_schema|
|**--parameters**|dictionary|Parameters for dataset.|azuresearchindex_parameters|azure_search_index_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azuresearchindex_annotations|azure_search_index_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azuresearchindex_folder|azure_search_index_folder|
### datafactory dataset azure-search-index update

azure-search-index create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azuresearchindex_type|azure_search_index_type|
|**--linked-service-name**|object|Linked service reference.|azuresearchindex_linked_service_name|azure_search_index_linked_service_name|
|**--type-properties-index-name**|any|The name of the Azure Search Index. Type: string (or Expression with resultType string).|azuresearchindex_index_name|azure_search_index_index_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azuresearchindex_description|azure_search_index_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azuresearchindex_structure|azure_search_index_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azuresearchindex_schema|azure_search_index_schema|
|**--parameters**|dictionary|Parameters for dataset.|azuresearchindex_parameters|azure_search_index_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azuresearchindex_annotations|azure_search_index_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azuresearchindex_folder|azure_search_index_folder|
### datafactory dataset azure-sql-d-w-table create

azure-sql-d-w-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azuresqldwtable_type|azure_sql_d_w_table_type|
|**--linked-service-name**|object|Linked service reference.|azuresqldwtable_linked_service_name|azure_sql_d_w_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azuresqldwtable_description|azure_sql_d_w_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azuresqldwtable_structure|azure_sql_d_w_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azuresqldwtable_schema|azure_sql_d_w_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azuresqldwtable_parameters|azure_sql_d_w_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azuresqldwtable_annotations|azure_sql_d_w_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azuresqldwtable_folder|azure_sql_d_w_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|azuresqldwtable_table_name|azure_sql_d_w_table_table_name|
|**--type-properties-schema**|any|The schema name of the Azure SQL Data Warehouse. Type: string (or Expression with resultType string).|azuresqldwtable_schema_type_properties_schema|azure_sql_d_w_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the Azure SQL Data Warehouse. Type: string (or Expression with resultType string).|azuresqldwtable_table|azure_sql_d_w_table_table|
### datafactory dataset azure-sql-d-w-table update

azure-sql-d-w-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azuresqldwtable_type|azure_sql_d_w_table_type|
|**--linked-service-name**|object|Linked service reference.|azuresqldwtable_linked_service_name|azure_sql_d_w_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azuresqldwtable_description|azure_sql_d_w_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azuresqldwtable_structure|azure_sql_d_w_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azuresqldwtable_schema|azure_sql_d_w_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azuresqldwtable_parameters|azure_sql_d_w_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azuresqldwtable_annotations|azure_sql_d_w_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azuresqldwtable_folder|azure_sql_d_w_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|azuresqldwtable_table_name|azure_sql_d_w_table_table_name|
|**--type-properties-schema**|any|The schema name of the Azure SQL Data Warehouse. Type: string (or Expression with resultType string).|azuresqldwtable_schema_type_properties_schema|azure_sql_d_w_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the Azure SQL Data Warehouse. Type: string (or Expression with resultType string).|azuresqldwtable_table|azure_sql_d_w_table_table|
### datafactory dataset azure-sql-m-i-table create

azure-sql-m-i-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azuresqlmitable_type|azure_sql_m_i_table_type|
|**--linked-service-name**|object|Linked service reference.|azuresqlmitable_linked_service_name|azure_sql_m_i_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azuresqlmitable_description|azure_sql_m_i_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azuresqlmitable_structure|azure_sql_m_i_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azuresqlmitable_schema|azure_sql_m_i_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azuresqlmitable_parameters|azure_sql_m_i_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azuresqlmitable_annotations|azure_sql_m_i_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azuresqlmitable_folder|azure_sql_m_i_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|azuresqlmitable_table_name|azure_sql_m_i_table_table_name|
|**--type-properties-schema**|any|The schema name of the Azure SQL Managed Instance. Type: string (or Expression with resultType string).|azuresqlmitable_schema_type_properties_schema|azure_sql_m_i_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the Azure SQL Managed Instance dataset. Type: string (or Expression with resultType string).|azuresqlmitable_table|azure_sql_m_i_table_table|
### datafactory dataset azure-sql-m-i-table update

azure-sql-m-i-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azuresqlmitable_type|azure_sql_m_i_table_type|
|**--linked-service-name**|object|Linked service reference.|azuresqlmitable_linked_service_name|azure_sql_m_i_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azuresqlmitable_description|azure_sql_m_i_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azuresqlmitable_structure|azure_sql_m_i_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azuresqlmitable_schema|azure_sql_m_i_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azuresqlmitable_parameters|azure_sql_m_i_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azuresqlmitable_annotations|azure_sql_m_i_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azuresqlmitable_folder|azure_sql_m_i_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|azuresqlmitable_table_name|azure_sql_m_i_table_table_name|
|**--type-properties-schema**|any|The schema name of the Azure SQL Managed Instance. Type: string (or Expression with resultType string).|azuresqlmitable_schema_type_properties_schema|azure_sql_m_i_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the Azure SQL Managed Instance dataset. Type: string (or Expression with resultType string).|azuresqlmitable_table|azure_sql_m_i_table_table|
### datafactory dataset azure-sql-table create

azure-sql-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azuresqltable_type|azure_sql_table_type|
|**--linked-service-name**|object|Linked service reference.|azuresqltable_linked_service_name|azure_sql_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azuresqltable_description|azure_sql_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azuresqltable_structure|azure_sql_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azuresqltable_schema|azure_sql_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azuresqltable_parameters|azure_sql_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azuresqltable_annotations|azure_sql_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azuresqltable_folder|azure_sql_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|azuresqltable_table_name|azure_sql_table_table_name|
|**--type-properties-schema**|any|The schema name of the Azure SQL database. Type: string (or Expression with resultType string).|azuresqltable_schema_type_properties_schema|azure_sql_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the Azure SQL database. Type: string (or Expression with resultType string).|azuresqltable_table|azure_sql_table_table|
### datafactory dataset azure-sql-table update

azure-sql-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azuresqltable_type|azure_sql_table_type|
|**--linked-service-name**|object|Linked service reference.|azuresqltable_linked_service_name|azure_sql_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azuresqltable_description|azure_sql_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azuresqltable_structure|azure_sql_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azuresqltable_schema|azure_sql_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azuresqltable_parameters|azure_sql_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azuresqltable_annotations|azure_sql_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azuresqltable_folder|azure_sql_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|azuresqltable_table_name|azure_sql_table_table_name|
|**--type-properties-schema**|any|The schema name of the Azure SQL database. Type: string (or Expression with resultType string).|azuresqltable_schema_type_properties_schema|azure_sql_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the Azure SQL database. Type: string (or Expression with resultType string).|azuresqltable_table|azure_sql_table_table|
### datafactory dataset azure-table create

azure-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azuretable_type|azure_table_type|
|**--linked-service-name**|object|Linked service reference.|azuretable_linked_service_name|azure_table_linked_service_name|
|**--type-properties-table-name**|any|The table name of the Azure Table storage. Type: string (or Expression with resultType string).|azuretable_table_name|azure_table_table_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azuretable_description|azure_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azuretable_structure|azure_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azuretable_schema|azure_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azuretable_parameters|azure_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azuretable_annotations|azure_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azuretable_folder|azure_table_folder|
### datafactory dataset azure-table update

azure-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|azuretable_type|azure_table_type|
|**--linked-service-name**|object|Linked service reference.|azuretable_linked_service_name|azure_table_linked_service_name|
|**--type-properties-table-name**|any|The table name of the Azure Table storage. Type: string (or Expression with resultType string).|azuretable_table_name|azure_table_table_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|azuretable_description|azure_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|azuretable_structure|azure_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|azuretable_schema|azure_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|azuretable_parameters|azure_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|azuretable_annotations|azure_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|azuretable_folder|azure_table_folder|
### datafactory dataset binary create

binary create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|binary_type|binary_type|
|**--linked-service-name**|object|Linked service reference.|binary_linked_service_name|binary_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|binary_description|binary_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|binary_structure|binary_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|binary_schema|binary_schema|
|**--parameters**|dictionary|Parameters for dataset.|binary_parameters|binary_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|binary_annotations|binary_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|binary_folder|binary_folder|
|**--type-properties-location**|object|The location of the Binary storage.|binary_location|binary_location|
|**--type-properties-compression**|object|The data compression method used for the binary dataset.|binary_compression|binary_compression|
### datafactory dataset binary update

binary create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|binary_type|binary_type|
|**--linked-service-name**|object|Linked service reference.|binary_linked_service_name|binary_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|binary_description|binary_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|binary_structure|binary_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|binary_schema|binary_schema|
|**--parameters**|dictionary|Parameters for dataset.|binary_parameters|binary_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|binary_annotations|binary_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|binary_folder|binary_folder|
|**--type-properties-location**|object|The location of the Binary storage.|binary_location|binary_location|
|**--type-properties-compression**|object|The data compression method used for the binary dataset.|binary_compression|binary_compression|
### datafactory dataset cassandra-table create

cassandra-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|cassandratable_type|cassandra_table_type|
|**--linked-service-name**|object|Linked service reference.|cassandratable_linked_service_name|cassandra_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|cassandratable_description|cassandra_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|cassandratable_structure|cassandra_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|cassandratable_schema|cassandra_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|cassandratable_parameters|cassandra_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|cassandratable_annotations|cassandra_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|cassandratable_folder|cassandra_table_folder|
|**--type-properties-table-name**|any|The table name of the Cassandra database. Type: string (or Expression with resultType string).|cassandratable_table_name|cassandra_table_table_name|
|**--type-properties-keyspace**|any|The keyspace of the Cassandra database. Type: string (or Expression with resultType string).|cassandratable_keyspace|cassandra_table_keyspace|
### datafactory dataset cassandra-table update

cassandra-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|cassandratable_type|cassandra_table_type|
|**--linked-service-name**|object|Linked service reference.|cassandratable_linked_service_name|cassandra_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|cassandratable_description|cassandra_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|cassandratable_structure|cassandra_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|cassandratable_schema|cassandra_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|cassandratable_parameters|cassandra_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|cassandratable_annotations|cassandra_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|cassandratable_folder|cassandra_table_folder|
|**--type-properties-table-name**|any|The table name of the Cassandra database. Type: string (or Expression with resultType string).|cassandratable_table_name|cassandra_table_table_name|
|**--type-properties-keyspace**|any|The keyspace of the Cassandra database. Type: string (or Expression with resultType string).|cassandratable_keyspace|cassandra_table_keyspace|
### datafactory dataset common-data-service-for-apps-entity create

common-data-service-for-apps-entity create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|commondataserviceforappsentity_type|common_data_service_for_apps_entity_type|
|**--linked-service-name**|object|Linked service reference.|commondataserviceforappsentity_linked_service_name|common_data_service_for_apps_entity_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|commondataserviceforappsentity_description|common_data_service_for_apps_entity_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|commondataserviceforappsentity_structure|common_data_service_for_apps_entity_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|commondataserviceforappsentity_schema|common_data_service_for_apps_entity_schema|
|**--parameters**|dictionary|Parameters for dataset.|commondataserviceforappsentity_parameters|common_data_service_for_apps_entity_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|commondataserviceforappsentity_annotations|common_data_service_for_apps_entity_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|commondataserviceforappsentity_folder|common_data_service_for_apps_entity_folder|
|**--type-properties-entity-name**|any|The logical name of the entity. Type: string (or Expression with resultType string).|commondataserviceforappsentity_entity_name|common_data_service_for_apps_entity_entity_name|
### datafactory dataset common-data-service-for-apps-entity update

common-data-service-for-apps-entity create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|commondataserviceforappsentity_type|common_data_service_for_apps_entity_type|
|**--linked-service-name**|object|Linked service reference.|commondataserviceforappsentity_linked_service_name|common_data_service_for_apps_entity_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|commondataserviceforappsentity_description|common_data_service_for_apps_entity_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|commondataserviceforappsentity_structure|common_data_service_for_apps_entity_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|commondataserviceforappsentity_schema|common_data_service_for_apps_entity_schema|
|**--parameters**|dictionary|Parameters for dataset.|commondataserviceforappsentity_parameters|common_data_service_for_apps_entity_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|commondataserviceforappsentity_annotations|common_data_service_for_apps_entity_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|commondataserviceforappsentity_folder|common_data_service_for_apps_entity_folder|
|**--type-properties-entity-name**|any|The logical name of the entity. Type: string (or Expression with resultType string).|commondataserviceforappsentity_entity_name|common_data_service_for_apps_entity_entity_name|
### datafactory dataset concur-object create

concur-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|concurobject_type|concur_object_type|
|**--linked-service-name**|object|Linked service reference.|concurobject_linked_service_name|concur_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|concurobject_description|concur_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|concurobject_structure|concur_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|concurobject_schema|concur_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|concurobject_parameters|concur_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|concurobject_annotations|concur_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|concurobject_folder|concur_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|concurobject_table_name|concur_object_table_name|
### datafactory dataset concur-object update

concur-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|concurobject_type|concur_object_type|
|**--linked-service-name**|object|Linked service reference.|concurobject_linked_service_name|concur_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|concurobject_description|concur_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|concurobject_structure|concur_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|concurobject_schema|concur_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|concurobject_parameters|concur_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|concurobject_annotations|concur_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|concurobject_folder|concur_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|concurobject_table_name|concur_object_table_name|
### datafactory dataset cosmos-db-mongo-db-api-collection create

cosmos-db-mongo-db-api-collection create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|cosmosdbmongodbapicollection_type|cosmos_db_mongo_db_api_collection_type|
|**--linked-service-name**|object|Linked service reference.|cosmosdbmongodbapicollection_linked_service_name|cosmos_db_mongo_db_api_collection_linked_service_name|
|**--type-properties-collection**|any|The collection name of the CosmosDB (MongoDB API) database. Type: string (or Expression with resultType string).|cosmosdbmongodbapicollection_collection|cosmos_db_mongo_db_api_collection_collection|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|cosmosdbmongodbapicollection_description|cosmos_db_mongo_db_api_collection_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|cosmosdbmongodbapicollection_structure|cosmos_db_mongo_db_api_collection_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|cosmosdbmongodbapicollection_schema|cosmos_db_mongo_db_api_collection_schema|
|**--parameters**|dictionary|Parameters for dataset.|cosmosdbmongodbapicollection_parameters|cosmos_db_mongo_db_api_collection_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|cosmosdbmongodbapicollection_annotations|cosmos_db_mongo_db_api_collection_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|cosmosdbmongodbapicollection_folder|cosmos_db_mongo_db_api_collection_folder|
### datafactory dataset cosmos-db-mongo-db-api-collection update

cosmos-db-mongo-db-api-collection create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|cosmosdbmongodbapicollection_type|cosmos_db_mongo_db_api_collection_type|
|**--linked-service-name**|object|Linked service reference.|cosmosdbmongodbapicollection_linked_service_name|cosmos_db_mongo_db_api_collection_linked_service_name|
|**--type-properties-collection**|any|The collection name of the CosmosDB (MongoDB API) database. Type: string (or Expression with resultType string).|cosmosdbmongodbapicollection_collection|cosmos_db_mongo_db_api_collection_collection|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|cosmosdbmongodbapicollection_description|cosmos_db_mongo_db_api_collection_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|cosmosdbmongodbapicollection_structure|cosmos_db_mongo_db_api_collection_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|cosmosdbmongodbapicollection_schema|cosmos_db_mongo_db_api_collection_schema|
|**--parameters**|dictionary|Parameters for dataset.|cosmosdbmongodbapicollection_parameters|cosmos_db_mongo_db_api_collection_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|cosmosdbmongodbapicollection_annotations|cosmos_db_mongo_db_api_collection_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|cosmosdbmongodbapicollection_folder|cosmos_db_mongo_db_api_collection_folder|
### datafactory dataset cosmos-db-sql-api-collection create

cosmos-db-sql-api-collection create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--properties**|object|Dataset properties.|properties|properties|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
### datafactory dataset cosmos-db-sql-api-collection update

cosmos-db-sql-api-collection create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--properties**|object|Dataset properties.|properties|properties|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
### datafactory dataset couchbase-table create

couchbase-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|couchbasetable_type|couchbase_table_type|
|**--linked-service-name**|object|Linked service reference.|couchbasetable_linked_service_name|couchbase_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|couchbasetable_description|couchbase_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|couchbasetable_structure|couchbase_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|couchbasetable_schema|couchbase_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|couchbasetable_parameters|couchbase_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|couchbasetable_annotations|couchbase_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|couchbasetable_folder|couchbase_table_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|couchbasetable_table_name|couchbase_table_table_name|
### datafactory dataset couchbase-table update

couchbase-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|couchbasetable_type|couchbase_table_type|
|**--linked-service-name**|object|Linked service reference.|couchbasetable_linked_service_name|couchbase_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|couchbasetable_description|couchbase_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|couchbasetable_structure|couchbase_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|couchbasetable_schema|couchbase_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|couchbasetable_parameters|couchbase_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|couchbasetable_annotations|couchbase_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|couchbasetable_folder|couchbase_table_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|couchbasetable_table_name|couchbase_table_table_name|
### datafactory dataset custom-dataset create

custom-dataset create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|customdataset_type|custom_dataset_type|
|**--linked-service-name**|object|Linked service reference.|customdataset_linked_service_name|custom_dataset_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|customdataset_description|custom_dataset_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|customdataset_structure|custom_dataset_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|customdataset_schema|custom_dataset_schema|
|**--parameters**|dictionary|Parameters for dataset.|customdataset_parameters|custom_dataset_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|customdataset_annotations|custom_dataset_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|customdataset_folder|custom_dataset_folder|
|**--type-properties**|any|Custom dataset properties.|customdataset_type_properties|custom_dataset_type_properties|
### datafactory dataset custom-dataset update

custom-dataset create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|customdataset_type|custom_dataset_type|
|**--linked-service-name**|object|Linked service reference.|customdataset_linked_service_name|custom_dataset_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|customdataset_description|custom_dataset_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|customdataset_structure|custom_dataset_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|customdataset_schema|custom_dataset_schema|
|**--parameters**|dictionary|Parameters for dataset.|customdataset_parameters|custom_dataset_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|customdataset_annotations|custom_dataset_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|customdataset_folder|custom_dataset_folder|
|**--type-properties**|any|Custom dataset properties.|customdataset_type_properties|custom_dataset_type_properties|
### datafactory dataset db2-table create

db2-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|db2table_type|db2_table_type|
|**--linked-service-name**|object|Linked service reference.|db2table_linked_service_name|db2_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|db2table_description|db2_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|db2table_structure|db2_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|db2table_schema|db2_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|db2table_parameters|db2_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|db2table_annotations|db2_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|db2table_folder|db2_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|db2table_table_name|db2_table_table_name|
|**--type-properties-schema**|any|The Db2 schema name. Type: string (or Expression with resultType string).|db2table_schema_type_properties_schema|db2_table_schema_type_properties_schema|
|**--type-properties-table**|any|The Db2 table name. Type: string (or Expression with resultType string).|db2table_table|db2_table_table|
### datafactory dataset db2-table update

db2-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|db2table_type|db2_table_type|
|**--linked-service-name**|object|Linked service reference.|db2table_linked_service_name|db2_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|db2table_description|db2_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|db2table_structure|db2_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|db2table_schema|db2_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|db2table_parameters|db2_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|db2table_annotations|db2_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|db2table_folder|db2_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|db2table_table_name|db2_table_table_name|
|**--type-properties-schema**|any|The Db2 schema name. Type: string (or Expression with resultType string).|db2table_schema_type_properties_schema|db2_table_schema_type_properties_schema|
|**--type-properties-table**|any|The Db2 table name. Type: string (or Expression with resultType string).|db2table_table|db2_table_table|
### datafactory dataset delete

delete a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
### datafactory dataset delimited-text create

delimited-text create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|delimitedtext_type|delimited_text_type|
|**--linked-service-name**|object|Linked service reference.|delimitedtext_linked_service_name|delimited_text_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|delimitedtext_description|delimited_text_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|delimitedtext_structure|delimited_text_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|delimitedtext_schema|delimited_text_schema|
|**--parameters**|dictionary|Parameters for dataset.|delimitedtext_parameters|delimited_text_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|delimitedtext_annotations|delimited_text_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|delimitedtext_folder|delimited_text_folder|
|**--type-properties-location**|object|The location of the delimited text storage.|delimitedtext_location|delimited_text_location|
|**--type-properties-column-delimiter**|any|The column delimiter. Type: string (or Expression with resultType string).|delimitedtext_column_delimiter|delimited_text_column_delimiter|
|**--type-properties-row-delimiter**|any|The row delimiter. Type: string (or Expression with resultType string).|delimitedtext_row_delimiter|delimited_text_row_delimiter|
|**--type-properties-encoding-name**|any|The code page name of the preferred encoding. If miss, the default value is UTF-8, unless BOM denotes another Unicode encoding. Refer to the name column of the table in the following link to set supported values: https://msdn.microsoft.com/library/system.text.encoding.aspx. Type: string (or Expression with resultType string).|delimitedtext_encoding_name|delimited_text_encoding_name|
|**--type-properties-compression-codec**|choice||delimitedtext_compression_codec|delimited_text_compression_codec|
|**--type-properties-compression-level**|choice|The data compression method used for DelimitedText.|delimitedtext_compression_level|delimited_text_compression_level|
|**--type-properties-quote-char**|any|The quote character. Type: string (or Expression with resultType string).|delimitedtext_quote_char|delimited_text_quote_char|
|**--type-properties-escape-char**|any|The escape character. Type: string (or Expression with resultType string).|delimitedtext_escape_char|delimited_text_escape_char|
|**--type-properties-first-row-as-header**|any|When used as input, treat the first row of data as headers. When used as output,write the headers into the output as the first row of data. The default value is false. Type: boolean (or Expression with resultType boolean).|delimitedtext_first_row_as_header|delimited_text_first_row_as_header|
|**--type-properties-null-value**|any|The null value string. Type: string (or Expression with resultType string).|delimitedtext_null_value|delimited_text_null_value|
### datafactory dataset delimited-text update

delimited-text create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|delimitedtext_type|delimited_text_type|
|**--linked-service-name**|object|Linked service reference.|delimitedtext_linked_service_name|delimited_text_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|delimitedtext_description|delimited_text_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|delimitedtext_structure|delimited_text_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|delimitedtext_schema|delimited_text_schema|
|**--parameters**|dictionary|Parameters for dataset.|delimitedtext_parameters|delimited_text_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|delimitedtext_annotations|delimited_text_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|delimitedtext_folder|delimited_text_folder|
|**--type-properties-location**|object|The location of the delimited text storage.|delimitedtext_location|delimited_text_location|
|**--type-properties-column-delimiter**|any|The column delimiter. Type: string (or Expression with resultType string).|delimitedtext_column_delimiter|delimited_text_column_delimiter|
|**--type-properties-row-delimiter**|any|The row delimiter. Type: string (or Expression with resultType string).|delimitedtext_row_delimiter|delimited_text_row_delimiter|
|**--type-properties-encoding-name**|any|The code page name of the preferred encoding. If miss, the default value is UTF-8, unless BOM denotes another Unicode encoding. Refer to the name column of the table in the following link to set supported values: https://msdn.microsoft.com/library/system.text.encoding.aspx. Type: string (or Expression with resultType string).|delimitedtext_encoding_name|delimited_text_encoding_name|
|**--type-properties-compression-codec**|choice||delimitedtext_compression_codec|delimited_text_compression_codec|
|**--type-properties-compression-level**|choice|The data compression method used for DelimitedText.|delimitedtext_compression_level|delimited_text_compression_level|
|**--type-properties-quote-char**|any|The quote character. Type: string (or Expression with resultType string).|delimitedtext_quote_char|delimited_text_quote_char|
|**--type-properties-escape-char**|any|The escape character. Type: string (or Expression with resultType string).|delimitedtext_escape_char|delimited_text_escape_char|
|**--type-properties-first-row-as-header**|any|When used as input, treat the first row of data as headers. When used as output,write the headers into the output as the first row of data. The default value is false. Type: boolean (or Expression with resultType boolean).|delimitedtext_first_row_as_header|delimited_text_first_row_as_header|
|**--type-properties-null-value**|any|The null value string. Type: string (or Expression with resultType string).|delimitedtext_null_value|delimited_text_null_value|
### datafactory dataset document-db-collection create

document-db-collection create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|documentdbcollection_type|document_db_collection_type|
|**--linked-service-name**|object|Linked service reference.|documentdbcollection_linked_service_name|document_db_collection_linked_service_name|
|**--type-properties-collection-name**|any|Document Database collection name. Type: string (or Expression with resultType string).|documentdbcollection_collection_name|document_db_collection_collection_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|documentdbcollection_description|document_db_collection_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|documentdbcollection_structure|document_db_collection_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|documentdbcollection_schema|document_db_collection_schema|
|**--parameters**|dictionary|Parameters for dataset.|documentdbcollection_parameters|document_db_collection_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|documentdbcollection_annotations|document_db_collection_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|documentdbcollection_folder|document_db_collection_folder|
### datafactory dataset document-db-collection update

document-db-collection create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|documentdbcollection_type|document_db_collection_type|
|**--linked-service-name**|object|Linked service reference.|documentdbcollection_linked_service_name|document_db_collection_linked_service_name|
|**--type-properties-collection-name**|any|Document Database collection name. Type: string (or Expression with resultType string).|documentdbcollection_collection_name|document_db_collection_collection_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|documentdbcollection_description|document_db_collection_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|documentdbcollection_structure|document_db_collection_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|documentdbcollection_schema|document_db_collection_schema|
|**--parameters**|dictionary|Parameters for dataset.|documentdbcollection_parameters|document_db_collection_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|documentdbcollection_annotations|document_db_collection_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|documentdbcollection_folder|document_db_collection_folder|
### datafactory dataset drill-table create

drill-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|drilltable_type|drill_table_type|
|**--linked-service-name**|object|Linked service reference.|drilltable_linked_service_name|drill_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|drilltable_description|drill_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|drilltable_structure|drill_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|drilltable_schema|drill_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|drilltable_parameters|drill_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|drilltable_annotations|drill_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|drilltable_folder|drill_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|drilltable_table_name|drill_table_table_name|
|**--type-properties-table**|any|The table name of the Drill. Type: string (or Expression with resultType string).|drilltable_table|drill_table_table|
|**--type-properties-schema**|any|The schema name of the Drill. Type: string (or Expression with resultType string).|drilltable_schema_type_properties_schema|drill_table_schema_type_properties_schema|
### datafactory dataset drill-table update

drill-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|drilltable_type|drill_table_type|
|**--linked-service-name**|object|Linked service reference.|drilltable_linked_service_name|drill_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|drilltable_description|drill_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|drilltable_structure|drill_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|drilltable_schema|drill_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|drilltable_parameters|drill_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|drilltable_annotations|drill_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|drilltable_folder|drill_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|drilltable_table_name|drill_table_table_name|
|**--type-properties-table**|any|The table name of the Drill. Type: string (or Expression with resultType string).|drilltable_table|drill_table_table|
|**--type-properties-schema**|any|The schema name of the Drill. Type: string (or Expression with resultType string).|drilltable_schema_type_properties_schema|drill_table_schema_type_properties_schema|
### datafactory dataset dynamics-a-x-resource create

dynamics-a-x-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|dynamicsaxresource_type|dynamics_a_x_resource_type|
|**--linked-service-name**|object|Linked service reference.|dynamicsaxresource_linked_service_name|dynamics_a_x_resource_linked_service_name|
|**--type-properties-path**|any|The path of the Dynamics AX OData entity. Type: string (or Expression with resultType string).|dynamicsaxresource_path|dynamics_a_x_resource_path|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|dynamicsaxresource_description|dynamics_a_x_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|dynamicsaxresource_structure|dynamics_a_x_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|dynamicsaxresource_schema|dynamics_a_x_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|dynamicsaxresource_parameters|dynamics_a_x_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|dynamicsaxresource_annotations|dynamics_a_x_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|dynamicsaxresource_folder|dynamics_a_x_resource_folder|
### datafactory dataset dynamics-a-x-resource update

dynamics-a-x-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|dynamicsaxresource_type|dynamics_a_x_resource_type|
|**--linked-service-name**|object|Linked service reference.|dynamicsaxresource_linked_service_name|dynamics_a_x_resource_linked_service_name|
|**--type-properties-path**|any|The path of the Dynamics AX OData entity. Type: string (or Expression with resultType string).|dynamicsaxresource_path|dynamics_a_x_resource_path|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|dynamicsaxresource_description|dynamics_a_x_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|dynamicsaxresource_structure|dynamics_a_x_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|dynamicsaxresource_schema|dynamics_a_x_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|dynamicsaxresource_parameters|dynamics_a_x_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|dynamicsaxresource_annotations|dynamics_a_x_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|dynamicsaxresource_folder|dynamics_a_x_resource_folder|
### datafactory dataset dynamics-crm-entity create

dynamics-crm-entity create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|dynamicscrmentity_type|dynamics_crm_entity_type|
|**--linked-service-name**|object|Linked service reference.|dynamicscrmentity_linked_service_name|dynamics_crm_entity_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|dynamicscrmentity_description|dynamics_crm_entity_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|dynamicscrmentity_structure|dynamics_crm_entity_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|dynamicscrmentity_schema|dynamics_crm_entity_schema|
|**--parameters**|dictionary|Parameters for dataset.|dynamicscrmentity_parameters|dynamics_crm_entity_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|dynamicscrmentity_annotations|dynamics_crm_entity_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|dynamicscrmentity_folder|dynamics_crm_entity_folder|
|**--type-properties-entity-name**|any|The logical name of the entity. Type: string (or Expression with resultType string).|dynamicscrmentity_entity_name|dynamics_crm_entity_entity_name|
### datafactory dataset dynamics-crm-entity update

dynamics-crm-entity create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|dynamicscrmentity_type|dynamics_crm_entity_type|
|**--linked-service-name**|object|Linked service reference.|dynamicscrmentity_linked_service_name|dynamics_crm_entity_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|dynamicscrmentity_description|dynamics_crm_entity_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|dynamicscrmentity_structure|dynamics_crm_entity_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|dynamicscrmentity_schema|dynamics_crm_entity_schema|
|**--parameters**|dictionary|Parameters for dataset.|dynamicscrmentity_parameters|dynamics_crm_entity_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|dynamicscrmentity_annotations|dynamics_crm_entity_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|dynamicscrmentity_folder|dynamics_crm_entity_folder|
|**--type-properties-entity-name**|any|The logical name of the entity. Type: string (or Expression with resultType string).|dynamicscrmentity_entity_name|dynamics_crm_entity_entity_name|
### datafactory dataset dynamics-entity create

dynamics-entity create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|dynamicsentity_type|dynamics_entity_type|
|**--linked-service-name**|object|Linked service reference.|dynamicsentity_linked_service_name|dynamics_entity_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|dynamicsentity_description|dynamics_entity_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|dynamicsentity_structure|dynamics_entity_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|dynamicsentity_schema|dynamics_entity_schema|
|**--parameters**|dictionary|Parameters for dataset.|dynamicsentity_parameters|dynamics_entity_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|dynamicsentity_annotations|dynamics_entity_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|dynamicsentity_folder|dynamics_entity_folder|
|**--type-properties-entity-name**|any|The logical name of the entity. Type: string (or Expression with resultType string).|dynamicsentity_entity_name|dynamics_entity_entity_name|
### datafactory dataset dynamics-entity update

dynamics-entity create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|dynamicsentity_type|dynamics_entity_type|
|**--linked-service-name**|object|Linked service reference.|dynamicsentity_linked_service_name|dynamics_entity_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|dynamicsentity_description|dynamics_entity_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|dynamicsentity_structure|dynamics_entity_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|dynamicsentity_schema|dynamics_entity_schema|
|**--parameters**|dictionary|Parameters for dataset.|dynamicsentity_parameters|dynamics_entity_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|dynamicsentity_annotations|dynamics_entity_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|dynamicsentity_folder|dynamics_entity_folder|
|**--type-properties-entity-name**|any|The logical name of the entity. Type: string (or Expression with resultType string).|dynamicsentity_entity_name|dynamics_entity_entity_name|
### datafactory dataset eloqua-object create

eloqua-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|eloquaobject_type|eloqua_object_type|
|**--linked-service-name**|object|Linked service reference.|eloquaobject_linked_service_name|eloqua_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|eloquaobject_description|eloqua_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|eloquaobject_structure|eloqua_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|eloquaobject_schema|eloqua_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|eloquaobject_parameters|eloqua_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|eloquaobject_annotations|eloqua_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|eloquaobject_folder|eloqua_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|eloquaobject_table_name|eloqua_object_table_name|
### datafactory dataset eloqua-object update

eloqua-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|eloquaobject_type|eloqua_object_type|
|**--linked-service-name**|object|Linked service reference.|eloquaobject_linked_service_name|eloqua_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|eloquaobject_description|eloqua_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|eloquaobject_structure|eloqua_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|eloquaobject_schema|eloqua_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|eloquaobject_parameters|eloqua_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|eloquaobject_annotations|eloqua_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|eloquaobject_folder|eloqua_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|eloquaobject_table_name|eloqua_object_table_name|
### datafactory dataset file-share create

file-share create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|fileshare_type|file_share_type|
|**--linked-service-name**|object|Linked service reference.|fileshare_linked_service_name|file_share_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|fileshare_description|file_share_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|fileshare_structure|file_share_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|fileshare_schema|file_share_schema|
|**--parameters**|dictionary|Parameters for dataset.|fileshare_parameters|file_share_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|fileshare_annotations|file_share_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|fileshare_folder|file_share_folder|
|**--type-properties-folder-path**|any|The path of the on-premises file system. Type: string (or Expression with resultType string).|fileshare_folder_path|file_share_folder_path|
|**--type-properties-file-name**|any|The name of the on-premises file system. Type: string (or Expression with resultType string).|fileshare_file_name|file_share_file_name|
|**--type-properties-modified-datetime-start**|any|The start of file's modified datetime. Type: string (or Expression with resultType string).|fileshare_modified_datetime_start|file_share_modified_datetime_start|
|**--type-properties-modified-datetime-end**|any|The end of file's modified datetime. Type: string (or Expression with resultType string).|fileshare_modified_datetime_end|file_share_modified_datetime_end|
|**--type-properties-format**|object|The format of the files.|fileshare_format|file_share_format|
|**--type-properties-file-filter**|any|Specify a filter to be used to select a subset of files in the folderPath rather than all files. Type: string (or Expression with resultType string).|fileshare_file_filter|file_share_file_filter|
|**--type-properties-compression**|object|The data compression method used for the file system.|fileshare_compression|file_share_compression|
### datafactory dataset file-share update

file-share create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|fileshare_type|file_share_type|
|**--linked-service-name**|object|Linked service reference.|fileshare_linked_service_name|file_share_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|fileshare_description|file_share_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|fileshare_structure|file_share_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|fileshare_schema|file_share_schema|
|**--parameters**|dictionary|Parameters for dataset.|fileshare_parameters|file_share_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|fileshare_annotations|file_share_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|fileshare_folder|file_share_folder|
|**--type-properties-folder-path**|any|The path of the on-premises file system. Type: string (or Expression with resultType string).|fileshare_folder_path|file_share_folder_path|
|**--type-properties-file-name**|any|The name of the on-premises file system. Type: string (or Expression with resultType string).|fileshare_file_name|file_share_file_name|
|**--type-properties-modified-datetime-start**|any|The start of file's modified datetime. Type: string (or Expression with resultType string).|fileshare_modified_datetime_start|file_share_modified_datetime_start|
|**--type-properties-modified-datetime-end**|any|The end of file's modified datetime. Type: string (or Expression with resultType string).|fileshare_modified_datetime_end|file_share_modified_datetime_end|
|**--type-properties-format**|object|The format of the files.|fileshare_format|file_share_format|
|**--type-properties-file-filter**|any|Specify a filter to be used to select a subset of files in the folderPath rather than all files. Type: string (or Expression with resultType string).|fileshare_file_filter|file_share_file_filter|
|**--type-properties-compression**|object|The data compression method used for the file system.|fileshare_compression|file_share_compression|
### datafactory dataset google-ad-words-object create

google-ad-words-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|googleadwordsobject_type|google_ad_words_object_type|
|**--linked-service-name**|object|Linked service reference.|googleadwordsobject_linked_service_name|google_ad_words_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|googleadwordsobject_description|google_ad_words_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|googleadwordsobject_structure|google_ad_words_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|googleadwordsobject_schema|google_ad_words_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|googleadwordsobject_parameters|google_ad_words_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|googleadwordsobject_annotations|google_ad_words_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|googleadwordsobject_folder|google_ad_words_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|googleadwordsobject_table_name|google_ad_words_object_table_name|
### datafactory dataset google-ad-words-object update

google-ad-words-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|googleadwordsobject_type|google_ad_words_object_type|
|**--linked-service-name**|object|Linked service reference.|googleadwordsobject_linked_service_name|google_ad_words_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|googleadwordsobject_description|google_ad_words_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|googleadwordsobject_structure|google_ad_words_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|googleadwordsobject_schema|google_ad_words_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|googleadwordsobject_parameters|google_ad_words_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|googleadwordsobject_annotations|google_ad_words_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|googleadwordsobject_folder|google_ad_words_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|googleadwordsobject_table_name|google_ad_words_object_table_name|
### datafactory dataset google-big-query-object create

google-big-query-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|googlebigqueryobject_type|google_big_query_object_type|
|**--linked-service-name**|object|Linked service reference.|googlebigqueryobject_linked_service_name|google_big_query_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|googlebigqueryobject_description|google_big_query_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|googlebigqueryobject_structure|google_big_query_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|googlebigqueryobject_schema|google_big_query_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|googlebigqueryobject_parameters|google_big_query_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|googlebigqueryobject_annotations|google_big_query_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|googlebigqueryobject_folder|google_big_query_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using database + table properties instead.|googlebigqueryobject_table_name|google_big_query_object_table_name|
|**--type-properties-table**|any|The table name of the Google BigQuery. Type: string (or Expression with resultType string).|googlebigqueryobject_table|google_big_query_object_table|
|**--type-properties-dataset**|any|The database name of the Google BigQuery. Type: string (or Expression with resultType string).|googlebigqueryobject_dataset|google_big_query_object_dataset|
### datafactory dataset google-big-query-object update

google-big-query-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|googlebigqueryobject_type|google_big_query_object_type|
|**--linked-service-name**|object|Linked service reference.|googlebigqueryobject_linked_service_name|google_big_query_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|googlebigqueryobject_description|google_big_query_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|googlebigqueryobject_structure|google_big_query_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|googlebigqueryobject_schema|google_big_query_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|googlebigqueryobject_parameters|google_big_query_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|googlebigqueryobject_annotations|google_big_query_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|googlebigqueryobject_folder|google_big_query_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using database + table properties instead.|googlebigqueryobject_table_name|google_big_query_object_table_name|
|**--type-properties-table**|any|The table name of the Google BigQuery. Type: string (or Expression with resultType string).|googlebigqueryobject_table|google_big_query_object_table|
|**--type-properties-dataset**|any|The database name of the Google BigQuery. Type: string (or Expression with resultType string).|googlebigqueryobject_dataset|google_big_query_object_dataset|
### datafactory dataset greenplum-table create

greenplum-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|greenplumtable_type|greenplum_table_type|
|**--linked-service-name**|object|Linked service reference.|greenplumtable_linked_service_name|greenplum_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|greenplumtable_description|greenplum_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|greenplumtable_structure|greenplum_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|greenplumtable_schema|greenplum_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|greenplumtable_parameters|greenplum_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|greenplumtable_annotations|greenplum_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|greenplumtable_folder|greenplum_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|greenplumtable_table_name|greenplum_table_table_name|
|**--type-properties-table**|any|The table name of Greenplum. Type: string (or Expression with resultType string).|greenplumtable_table|greenplum_table_table|
|**--type-properties-schema**|any|The schema name of Greenplum. Type: string (or Expression with resultType string).|greenplumtable_schema_type_properties_schema|greenplum_table_schema_type_properties_schema|
### datafactory dataset greenplum-table update

greenplum-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|greenplumtable_type|greenplum_table_type|
|**--linked-service-name**|object|Linked service reference.|greenplumtable_linked_service_name|greenplum_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|greenplumtable_description|greenplum_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|greenplumtable_structure|greenplum_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|greenplumtable_schema|greenplum_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|greenplumtable_parameters|greenplum_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|greenplumtable_annotations|greenplum_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|greenplumtable_folder|greenplum_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|greenplumtable_table_name|greenplum_table_table_name|
|**--type-properties-table**|any|The table name of Greenplum. Type: string (or Expression with resultType string).|greenplumtable_table|greenplum_table_table|
|**--type-properties-schema**|any|The schema name of Greenplum. Type: string (or Expression with resultType string).|greenplumtable_schema_type_properties_schema|greenplum_table_schema_type_properties_schema|
### datafactory dataset h-base-object create

h-base-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|hbaseobject_type|h_base_object_type|
|**--linked-service-name**|object|Linked service reference.|hbaseobject_linked_service_name|h_base_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|hbaseobject_description|h_base_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|hbaseobject_structure|h_base_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|hbaseobject_schema|h_base_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|hbaseobject_parameters|h_base_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|hbaseobject_annotations|h_base_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|hbaseobject_folder|h_base_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|hbaseobject_table_name|h_base_object_table_name|
### datafactory dataset h-base-object update

h-base-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|hbaseobject_type|h_base_object_type|
|**--linked-service-name**|object|Linked service reference.|hbaseobject_linked_service_name|h_base_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|hbaseobject_description|h_base_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|hbaseobject_structure|h_base_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|hbaseobject_schema|h_base_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|hbaseobject_parameters|h_base_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|hbaseobject_annotations|h_base_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|hbaseobject_folder|h_base_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|hbaseobject_table_name|h_base_object_table_name|
### datafactory dataset hive-object create

hive-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|hiveobject_type|hive_object_type|
|**--linked-service-name**|object|Linked service reference.|hiveobject_linked_service_name|hive_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|hiveobject_description|hive_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|hiveobject_structure|hive_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|hiveobject_schema|hive_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|hiveobject_parameters|hive_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|hiveobject_annotations|hive_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|hiveobject_folder|hive_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|hiveobject_table_name|hive_object_table_name|
|**--type-properties-table**|any|The table name of the Hive. Type: string (or Expression with resultType string).|hiveobject_table|hive_object_table|
|**--type-properties-schema**|any|The schema name of the Hive. Type: string (or Expression with resultType string).|hiveobject_schema_type_properties_schema|hive_object_schema_type_properties_schema|
### datafactory dataset hive-object update

hive-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|hiveobject_type|hive_object_type|
|**--linked-service-name**|object|Linked service reference.|hiveobject_linked_service_name|hive_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|hiveobject_description|hive_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|hiveobject_structure|hive_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|hiveobject_schema|hive_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|hiveobject_parameters|hive_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|hiveobject_annotations|hive_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|hiveobject_folder|hive_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|hiveobject_table_name|hive_object_table_name|
|**--type-properties-table**|any|The table name of the Hive. Type: string (or Expression with resultType string).|hiveobject_table|hive_object_table|
|**--type-properties-schema**|any|The schema name of the Hive. Type: string (or Expression with resultType string).|hiveobject_schema_type_properties_schema|hive_object_schema_type_properties_schema|
### datafactory dataset http-file create

http-file create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|httpfile_type|http_file_type|
|**--linked-service-name**|object|Linked service reference.|httpfile_linked_service_name|http_file_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|httpfile_description|http_file_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|httpfile_structure|http_file_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|httpfile_schema|http_file_schema|
|**--parameters**|dictionary|Parameters for dataset.|httpfile_parameters|http_file_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|httpfile_annotations|http_file_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|httpfile_folder|http_file_folder|
|**--type-properties-relative-url**|any|The relative URL based on the URL in the HttpLinkedService refers to an HTTP file Type: string (or Expression with resultType string).|httpfile_relative_url|http_file_relative_url|
|**--type-properties-request-method**|any|The HTTP method for the HTTP request. Type: string (or Expression with resultType string).|httpfile_request_method|http_file_request_method|
|**--type-properties-request-body**|any|The body for the HTTP request. Type: string (or Expression with resultType string).|httpfile_request_body|http_file_request_body|
|**--type-properties-additional-headers**|any|The headers for the HTTP Request. e.g. request-header-name-1:request-header-value-1 ... request-header-name-n:request-header-value-n Type: string (or Expression with resultType string).|httpfile_additional_headers|http_file_additional_headers|
|**--type-properties-format**|object|The format of files.|httpfile_format|http_file_format|
|**--type-properties-compression**|object|The data compression method used on files.|httpfile_compression|http_file_compression|
### datafactory dataset http-file update

http-file create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|httpfile_type|http_file_type|
|**--linked-service-name**|object|Linked service reference.|httpfile_linked_service_name|http_file_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|httpfile_description|http_file_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|httpfile_structure|http_file_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|httpfile_schema|http_file_schema|
|**--parameters**|dictionary|Parameters for dataset.|httpfile_parameters|http_file_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|httpfile_annotations|http_file_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|httpfile_folder|http_file_folder|
|**--type-properties-relative-url**|any|The relative URL based on the URL in the HttpLinkedService refers to an HTTP file Type: string (or Expression with resultType string).|httpfile_relative_url|http_file_relative_url|
|**--type-properties-request-method**|any|The HTTP method for the HTTP request. Type: string (or Expression with resultType string).|httpfile_request_method|http_file_request_method|
|**--type-properties-request-body**|any|The body for the HTTP request. Type: string (or Expression with resultType string).|httpfile_request_body|http_file_request_body|
|**--type-properties-additional-headers**|any|The headers for the HTTP Request. e.g. request-header-name-1:request-header-value-1 ... request-header-name-n:request-header-value-n Type: string (or Expression with resultType string).|httpfile_additional_headers|http_file_additional_headers|
|**--type-properties-format**|object|The format of files.|httpfile_format|http_file_format|
|**--type-properties-compression**|object|The data compression method used on files.|httpfile_compression|http_file_compression|
### datafactory dataset hubspot-object create

hubspot-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|hubspotobject_type|hubspot_object_type|
|**--linked-service-name**|object|Linked service reference.|hubspotobject_linked_service_name|hubspot_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|hubspotobject_description|hubspot_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|hubspotobject_structure|hubspot_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|hubspotobject_schema|hubspot_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|hubspotobject_parameters|hubspot_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|hubspotobject_annotations|hubspot_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|hubspotobject_folder|hubspot_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|hubspotobject_table_name|hubspot_object_table_name|
### datafactory dataset hubspot-object update

hubspot-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|hubspotobject_type|hubspot_object_type|
|**--linked-service-name**|object|Linked service reference.|hubspotobject_linked_service_name|hubspot_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|hubspotobject_description|hubspot_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|hubspotobject_structure|hubspot_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|hubspotobject_schema|hubspot_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|hubspotobject_parameters|hubspot_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|hubspotobject_annotations|hubspot_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|hubspotobject_folder|hubspot_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|hubspotobject_table_name|hubspot_object_table_name|
### datafactory dataset impala-object create

impala-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|impalaobject_type|impala_object_type|
|**--linked-service-name**|object|Linked service reference.|impalaobject_linked_service_name|impala_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|impalaobject_description|impala_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|impalaobject_structure|impala_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|impalaobject_schema|impala_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|impalaobject_parameters|impala_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|impalaobject_annotations|impala_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|impalaobject_folder|impala_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|impalaobject_table_name|impala_object_table_name|
|**--type-properties-table**|any|The table name of the Impala. Type: string (or Expression with resultType string).|impalaobject_table|impala_object_table|
|**--type-properties-schema**|any|The schema name of the Impala. Type: string (or Expression with resultType string).|impalaobject_schema_type_properties_schema|impala_object_schema_type_properties_schema|
### datafactory dataset impala-object update

impala-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|impalaobject_type|impala_object_type|
|**--linked-service-name**|object|Linked service reference.|impalaobject_linked_service_name|impala_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|impalaobject_description|impala_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|impalaobject_structure|impala_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|impalaobject_schema|impala_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|impalaobject_parameters|impala_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|impalaobject_annotations|impala_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|impalaobject_folder|impala_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|impalaobject_table_name|impala_object_table_name|
|**--type-properties-table**|any|The table name of the Impala. Type: string (or Expression with resultType string).|impalaobject_table|impala_object_table|
|**--type-properties-schema**|any|The schema name of the Impala. Type: string (or Expression with resultType string).|impalaobject_schema_type_properties_schema|impala_object_schema_type_properties_schema|
### datafactory dataset informix-table create

informix-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|informixtable_type|informix_table_type|
|**--linked-service-name**|object|Linked service reference.|informixtable_linked_service_name|informix_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|informixtable_description|informix_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|informixtable_structure|informix_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|informixtable_schema|informix_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|informixtable_parameters|informix_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|informixtable_annotations|informix_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|informixtable_folder|informix_table_folder|
|**--type-properties-table-name**|any|The Informix table name. Type: string (or Expression with resultType string).|informixtable_table_name|informix_table_table_name|
### datafactory dataset informix-table update

informix-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|informixtable_type|informix_table_type|
|**--linked-service-name**|object|Linked service reference.|informixtable_linked_service_name|informix_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|informixtable_description|informix_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|informixtable_structure|informix_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|informixtable_schema|informix_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|informixtable_parameters|informix_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|informixtable_annotations|informix_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|informixtable_folder|informix_table_folder|
|**--type-properties-table-name**|any|The Informix table name. Type: string (or Expression with resultType string).|informixtable_table_name|informix_table_table_name|
### datafactory dataset jira-object create

jira-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|jiraobject_type|jira_object_type|
|**--linked-service-name**|object|Linked service reference.|jiraobject_linked_service_name|jira_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|jiraobject_description|jira_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|jiraobject_structure|jira_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|jiraobject_schema|jira_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|jiraobject_parameters|jira_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|jiraobject_annotations|jira_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|jiraobject_folder|jira_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|jiraobject_table_name|jira_object_table_name|
### datafactory dataset jira-object update

jira-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|jiraobject_type|jira_object_type|
|**--linked-service-name**|object|Linked service reference.|jiraobject_linked_service_name|jira_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|jiraobject_description|jira_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|jiraobject_structure|jira_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|jiraobject_schema|jira_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|jiraobject_parameters|jira_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|jiraobject_annotations|jira_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|jiraobject_folder|jira_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|jiraobject_table_name|jira_object_table_name|
### datafactory dataset json create

json create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|json_type|json_type|
|**--linked-service-name**|object|Linked service reference.|json_linked_service_name|json_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|json_description|json_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|json_structure|json_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|json_schema|json_schema|
|**--parameters**|dictionary|Parameters for dataset.|json_parameters|json_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|json_annotations|json_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|json_folder|json_folder|
|**--type-properties-location**|object|The location of the json data storage.|json_location|json_location|
|**--type-properties-encoding-name**|any|The code page name of the preferred encoding. If not specified, the default value is UTF-8, unless BOM denotes another Unicode encoding. Refer to the name column of the table in the following link to set supported values: https://msdn.microsoft.com/library/system.text.encoding.aspx. Type: string (or Expression with resultType string).|json_encoding_name|json_encoding_name|
|**--type-properties-compression**|object|The data compression method used for the json dataset.|json_compression|json_compression|
### datafactory dataset json update

json create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|json_type|json_type|
|**--linked-service-name**|object|Linked service reference.|json_linked_service_name|json_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|json_description|json_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|json_structure|json_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|json_schema|json_schema|
|**--parameters**|dictionary|Parameters for dataset.|json_parameters|json_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|json_annotations|json_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|json_folder|json_folder|
|**--type-properties-location**|object|The location of the json data storage.|json_location|json_location|
|**--type-properties-encoding-name**|any|The code page name of the preferred encoding. If not specified, the default value is UTF-8, unless BOM denotes another Unicode encoding. Refer to the name column of the table in the following link to set supported values: https://msdn.microsoft.com/library/system.text.encoding.aspx. Type: string (or Expression with resultType string).|json_encoding_name|json_encoding_name|
|**--type-properties-compression**|object|The data compression method used for the json dataset.|json_compression|json_compression|
### datafactory dataset list

list a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
### datafactory dataset magento-object create

magento-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|magentoobject_type|magento_object_type|
|**--linked-service-name**|object|Linked service reference.|magentoobject_linked_service_name|magento_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|magentoobject_description|magento_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|magentoobject_structure|magento_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|magentoobject_schema|magento_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|magentoobject_parameters|magento_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|magentoobject_annotations|magento_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|magentoobject_folder|magento_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|magentoobject_table_name|magento_object_table_name|
### datafactory dataset magento-object update

magento-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|magentoobject_type|magento_object_type|
|**--linked-service-name**|object|Linked service reference.|magentoobject_linked_service_name|magento_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|magentoobject_description|magento_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|magentoobject_structure|magento_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|magentoobject_schema|magento_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|magentoobject_parameters|magento_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|magentoobject_annotations|magento_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|magentoobject_folder|magento_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|magentoobject_table_name|magento_object_table_name|
### datafactory dataset maria-d-b-table create

maria-d-b-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|mariadbtable_type|maria_d_b_table_type|
|**--linked-service-name**|object|Linked service reference.|mariadbtable_linked_service_name|maria_d_b_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|mariadbtable_description|maria_d_b_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|mariadbtable_structure|maria_d_b_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|mariadbtable_schema|maria_d_b_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|mariadbtable_parameters|maria_d_b_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|mariadbtable_annotations|maria_d_b_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|mariadbtable_folder|maria_d_b_table_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|mariadbtable_table_name|maria_d_b_table_table_name|
### datafactory dataset maria-d-b-table update

maria-d-b-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|mariadbtable_type|maria_d_b_table_type|
|**--linked-service-name**|object|Linked service reference.|mariadbtable_linked_service_name|maria_d_b_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|mariadbtable_description|maria_d_b_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|mariadbtable_structure|maria_d_b_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|mariadbtable_schema|maria_d_b_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|mariadbtable_parameters|maria_d_b_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|mariadbtable_annotations|maria_d_b_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|mariadbtable_folder|maria_d_b_table_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|mariadbtable_table_name|maria_d_b_table_table_name|
### datafactory dataset marketo-object create

marketo-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|marketoobject_type|marketo_object_type|
|**--linked-service-name**|object|Linked service reference.|marketoobject_linked_service_name|marketo_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|marketoobject_description|marketo_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|marketoobject_structure|marketo_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|marketoobject_schema|marketo_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|marketoobject_parameters|marketo_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|marketoobject_annotations|marketo_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|marketoobject_folder|marketo_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|marketoobject_table_name|marketo_object_table_name|
### datafactory dataset marketo-object update

marketo-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|marketoobject_type|marketo_object_type|
|**--linked-service-name**|object|Linked service reference.|marketoobject_linked_service_name|marketo_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|marketoobject_description|marketo_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|marketoobject_structure|marketo_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|marketoobject_schema|marketo_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|marketoobject_parameters|marketo_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|marketoobject_annotations|marketo_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|marketoobject_folder|marketo_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|marketoobject_table_name|marketo_object_table_name|
### datafactory dataset microsoft-access-table create

microsoft-access-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|microsoftaccesstable_type|microsoft_access_table_type|
|**--linked-service-name**|object|Linked service reference.|microsoftaccesstable_linked_service_name|microsoft_access_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|microsoftaccesstable_description|microsoft_access_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|microsoftaccesstable_structure|microsoft_access_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|microsoftaccesstable_schema|microsoft_access_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|microsoftaccesstable_parameters|microsoft_access_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|microsoftaccesstable_annotations|microsoft_access_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|microsoftaccesstable_folder|microsoft_access_table_folder|
|**--type-properties-table-name**|any|The Microsoft Access table name. Type: string (or Expression with resultType string).|microsoftaccesstable_table_name|microsoft_access_table_table_name|
### datafactory dataset microsoft-access-table update

microsoft-access-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|microsoftaccesstable_type|microsoft_access_table_type|
|**--linked-service-name**|object|Linked service reference.|microsoftaccesstable_linked_service_name|microsoft_access_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|microsoftaccesstable_description|microsoft_access_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|microsoftaccesstable_structure|microsoft_access_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|microsoftaccesstable_schema|microsoft_access_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|microsoftaccesstable_parameters|microsoft_access_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|microsoftaccesstable_annotations|microsoft_access_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|microsoftaccesstable_folder|microsoft_access_table_folder|
|**--type-properties-table-name**|any|The Microsoft Access table name. Type: string (or Expression with resultType string).|microsoftaccesstable_table_name|microsoft_access_table_table_name|
### datafactory dataset mongo-db-collection create

mongo-db-collection create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|mongodbcollection_type|mongo_db_collection_type|
|**--linked-service-name**|object|Linked service reference.|mongodbcollection_linked_service_name|mongo_db_collection_linked_service_name|
|**--type-properties-collection-name**|any|The table name of the MongoDB database. Type: string (or Expression with resultType string).|mongodbcollection_collection_name|mongo_db_collection_collection_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|mongodbcollection_description|mongo_db_collection_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|mongodbcollection_structure|mongo_db_collection_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|mongodbcollection_schema|mongo_db_collection_schema|
|**--parameters**|dictionary|Parameters for dataset.|mongodbcollection_parameters|mongo_db_collection_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|mongodbcollection_annotations|mongo_db_collection_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|mongodbcollection_folder|mongo_db_collection_folder|
### datafactory dataset mongo-db-collection update

mongo-db-collection create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|mongodbcollection_type|mongo_db_collection_type|
|**--linked-service-name**|object|Linked service reference.|mongodbcollection_linked_service_name|mongo_db_collection_linked_service_name|
|**--type-properties-collection-name**|any|The table name of the MongoDB database. Type: string (or Expression with resultType string).|mongodbcollection_collection_name|mongo_db_collection_collection_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|mongodbcollection_description|mongo_db_collection_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|mongodbcollection_structure|mongo_db_collection_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|mongodbcollection_schema|mongo_db_collection_schema|
|**--parameters**|dictionary|Parameters for dataset.|mongodbcollection_parameters|mongo_db_collection_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|mongodbcollection_annotations|mongo_db_collection_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|mongodbcollection_folder|mongo_db_collection_folder|
### datafactory dataset mongo-db-v2-collection create

mongo-db-v2-collection create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|mongodbv2collection_type|mongo_db_v2_collection_type|
|**--linked-service-name**|object|Linked service reference.|mongodbv2collection_linked_service_name|mongo_db_v2_collection_linked_service_name|
|**--type-properties-collection**|any|The collection name of the MongoDB database. Type: string (or Expression with resultType string).|mongodbv2collection_collection|mongo_db_v2_collection_collection|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|mongodbv2collection_description|mongo_db_v2_collection_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|mongodbv2collection_structure|mongo_db_v2_collection_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|mongodbv2collection_schema|mongo_db_v2_collection_schema|
|**--parameters**|dictionary|Parameters for dataset.|mongodbv2collection_parameters|mongo_db_v2_collection_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|mongodbv2collection_annotations|mongo_db_v2_collection_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|mongodbv2collection_folder|mongo_db_v2_collection_folder|
### datafactory dataset mongo-db-v2-collection update

mongo-db-v2-collection create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|mongodbv2collection_type|mongo_db_v2_collection_type|
|**--linked-service-name**|object|Linked service reference.|mongodbv2collection_linked_service_name|mongo_db_v2_collection_linked_service_name|
|**--type-properties-collection**|any|The collection name of the MongoDB database. Type: string (or Expression with resultType string).|mongodbv2collection_collection|mongo_db_v2_collection_collection|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|mongodbv2collection_description|mongo_db_v2_collection_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|mongodbv2collection_structure|mongo_db_v2_collection_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|mongodbv2collection_schema|mongo_db_v2_collection_schema|
|**--parameters**|dictionary|Parameters for dataset.|mongodbv2collection_parameters|mongo_db_v2_collection_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|mongodbv2collection_annotations|mongo_db_v2_collection_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|mongodbv2collection_folder|mongo_db_v2_collection_folder|
### datafactory dataset my-sql-table create

my-sql-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|mysqltable_type|my_sql_table_type|
|**--linked-service-name**|object|Linked service reference.|mysqltable_linked_service_name|my_sql_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|mysqltable_description|my_sql_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|mysqltable_structure|my_sql_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|mysqltable_schema|my_sql_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|mysqltable_parameters|my_sql_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|mysqltable_annotations|my_sql_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|mysqltable_folder|my_sql_table_folder|
|**--type-properties-table-name**|any|The MySQL table name. Type: string (or Expression with resultType string).|mysqltable_table_name|my_sql_table_table_name|
### datafactory dataset my-sql-table update

my-sql-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|mysqltable_type|my_sql_table_type|
|**--linked-service-name**|object|Linked service reference.|mysqltable_linked_service_name|my_sql_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|mysqltable_description|my_sql_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|mysqltable_structure|my_sql_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|mysqltable_schema|my_sql_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|mysqltable_parameters|my_sql_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|mysqltable_annotations|my_sql_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|mysqltable_folder|my_sql_table_folder|
|**--type-properties-table-name**|any|The MySQL table name. Type: string (or Expression with resultType string).|mysqltable_table_name|my_sql_table_table_name|
### datafactory dataset netezza-table create

netezza-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|netezzatable_type|netezza_table_type|
|**--linked-service-name**|object|Linked service reference.|netezzatable_linked_service_name|netezza_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|netezzatable_description|netezza_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|netezzatable_structure|netezza_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|netezzatable_schema|netezza_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|netezzatable_parameters|netezza_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|netezzatable_annotations|netezza_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|netezzatable_folder|netezza_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|netezzatable_table_name|netezza_table_table_name|
|**--type-properties-table**|any|The table name of the Netezza. Type: string (or Expression with resultType string).|netezzatable_table|netezza_table_table|
|**--type-properties-schema**|any|The schema name of the Netezza. Type: string (or Expression with resultType string).|netezzatable_schema_type_properties_schema|netezza_table_schema_type_properties_schema|
### datafactory dataset netezza-table update

netezza-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|netezzatable_type|netezza_table_type|
|**--linked-service-name**|object|Linked service reference.|netezzatable_linked_service_name|netezza_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|netezzatable_description|netezza_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|netezzatable_structure|netezza_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|netezzatable_schema|netezza_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|netezzatable_parameters|netezza_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|netezzatable_annotations|netezza_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|netezzatable_folder|netezza_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|netezzatable_table_name|netezza_table_table_name|
|**--type-properties-table**|any|The table name of the Netezza. Type: string (or Expression with resultType string).|netezzatable_table|netezza_table_table|
|**--type-properties-schema**|any|The schema name of the Netezza. Type: string (or Expression with resultType string).|netezzatable_schema_type_properties_schema|netezza_table_schema_type_properties_schema|
### datafactory dataset o-data-resource create

o-data-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|odataresource_type|o_data_resource_type|
|**--linked-service-name**|object|Linked service reference.|odataresource_linked_service_name|o_data_resource_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|odataresource_description|o_data_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|odataresource_structure|o_data_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|odataresource_schema|o_data_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|odataresource_parameters|o_data_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|odataresource_annotations|o_data_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|odataresource_folder|o_data_resource_folder|
|**--type-properties-path**|any|The OData resource path. Type: string (or Expression with resultType string).|odataresource_path|o_data_resource_path|
### datafactory dataset o-data-resource update

o-data-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|odataresource_type|o_data_resource_type|
|**--linked-service-name**|object|Linked service reference.|odataresource_linked_service_name|o_data_resource_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|odataresource_description|o_data_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|odataresource_structure|o_data_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|odataresource_schema|o_data_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|odataresource_parameters|o_data_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|odataresource_annotations|o_data_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|odataresource_folder|o_data_resource_folder|
|**--type-properties-path**|any|The OData resource path. Type: string (or Expression with resultType string).|odataresource_path|o_data_resource_path|
### datafactory dataset odbc-table create

odbc-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|odbctable_type|odbc_table_type|
|**--linked-service-name**|object|Linked service reference.|odbctable_linked_service_name|odbc_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|odbctable_description|odbc_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|odbctable_structure|odbc_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|odbctable_schema|odbc_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|odbctable_parameters|odbc_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|odbctable_annotations|odbc_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|odbctable_folder|odbc_table_folder|
|**--type-properties-table-name**|any|The ODBC table name. Type: string (or Expression with resultType string).|odbctable_table_name|odbc_table_table_name|
### datafactory dataset odbc-table update

odbc-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|odbctable_type|odbc_table_type|
|**--linked-service-name**|object|Linked service reference.|odbctable_linked_service_name|odbc_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|odbctable_description|odbc_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|odbctable_structure|odbc_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|odbctable_schema|odbc_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|odbctable_parameters|odbc_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|odbctable_annotations|odbc_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|odbctable_folder|odbc_table_folder|
|**--type-properties-table-name**|any|The ODBC table name. Type: string (or Expression with resultType string).|odbctable_table_name|odbc_table_table_name|
### datafactory dataset office365-table create

office365-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|office365table_type|office365_table_type|
|**--linked-service-name**|object|Linked service reference.|office365table_linked_service_name|office365_table_linked_service_name|
|**--type-properties-table-name**|any|Name of the dataset to extract from Office 365. Type: string (or Expression with resultType string).|office365table_table_name|office365_table_table_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|office365table_description|office365_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|office365table_structure|office365_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|office365table_schema|office365_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|office365table_parameters|office365_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|office365table_annotations|office365_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|office365table_folder|office365_table_folder|
|**--type-properties-predicate**|any|A predicate expression that can be used to filter the specific rows to extract from Office 365. Type: string (or Expression with resultType string).|office365table_predicate|office365_table_predicate|
### datafactory dataset office365-table update

office365-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|office365table_type|office365_table_type|
|**--linked-service-name**|object|Linked service reference.|office365table_linked_service_name|office365_table_linked_service_name|
|**--type-properties-table-name**|any|Name of the dataset to extract from Office 365. Type: string (or Expression with resultType string).|office365table_table_name|office365_table_table_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|office365table_description|office365_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|office365table_structure|office365_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|office365table_schema|office365_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|office365table_parameters|office365_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|office365table_annotations|office365_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|office365table_folder|office365_table_folder|
|**--type-properties-predicate**|any|A predicate expression that can be used to filter the specific rows to extract from Office 365. Type: string (or Expression with resultType string).|office365table_predicate|office365_table_predicate|
### datafactory dataset oracle-service-cloud-object create

oracle-service-cloud-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|oracleservicecloudobject_type|oracle_service_cloud_object_type|
|**--linked-service-name**|object|Linked service reference.|oracleservicecloudobject_linked_service_name|oracle_service_cloud_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|oracleservicecloudobject_description|oracle_service_cloud_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|oracleservicecloudobject_structure|oracle_service_cloud_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|oracleservicecloudobject_schema|oracle_service_cloud_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|oracleservicecloudobject_parameters|oracle_service_cloud_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|oracleservicecloudobject_annotations|oracle_service_cloud_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|oracleservicecloudobject_folder|oracle_service_cloud_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|oracleservicecloudobject_table_name|oracle_service_cloud_object_table_name|
### datafactory dataset oracle-service-cloud-object update

oracle-service-cloud-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|oracleservicecloudobject_type|oracle_service_cloud_object_type|
|**--linked-service-name**|object|Linked service reference.|oracleservicecloudobject_linked_service_name|oracle_service_cloud_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|oracleservicecloudobject_description|oracle_service_cloud_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|oracleservicecloudobject_structure|oracle_service_cloud_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|oracleservicecloudobject_schema|oracle_service_cloud_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|oracleservicecloudobject_parameters|oracle_service_cloud_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|oracleservicecloudobject_annotations|oracle_service_cloud_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|oracleservicecloudobject_folder|oracle_service_cloud_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|oracleservicecloudobject_table_name|oracle_service_cloud_object_table_name|
### datafactory dataset oracle-table create

oracle-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|oracletable_type|oracle_table_type|
|**--linked-service-name**|object|Linked service reference.|oracletable_linked_service_name|oracle_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|oracletable_description|oracle_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|oracletable_structure|oracle_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|oracletable_schema|oracle_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|oracletable_parameters|oracle_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|oracletable_annotations|oracle_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|oracletable_folder|oracle_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|oracletable_table_name|oracle_table_table_name|
|**--type-properties-schema**|any|The schema name of the on-premises Oracle database. Type: string (or Expression with resultType string).|oracletable_schema_type_properties_schema|oracle_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the on-premises Oracle database. Type: string (or Expression with resultType string).|oracletable_table|oracle_table_table|
### datafactory dataset oracle-table update

oracle-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|oracletable_type|oracle_table_type|
|**--linked-service-name**|object|Linked service reference.|oracletable_linked_service_name|oracle_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|oracletable_description|oracle_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|oracletable_structure|oracle_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|oracletable_schema|oracle_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|oracletable_parameters|oracle_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|oracletable_annotations|oracle_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|oracletable_folder|oracle_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|oracletable_table_name|oracle_table_table_name|
|**--type-properties-schema**|any|The schema name of the on-premises Oracle database. Type: string (or Expression with resultType string).|oracletable_schema_type_properties_schema|oracle_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the on-premises Oracle database. Type: string (or Expression with resultType string).|oracletable_table|oracle_table_table|
### datafactory dataset orc create

orc create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|orc_type|orc_type|
|**--linked-service-name**|object|Linked service reference.|orc_linked_service_name|orc_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|orc_description|orc_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|orc_structure|orc_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|orc_schema|orc_schema|
|**--parameters**|dictionary|Parameters for dataset.|orc_parameters|orc_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|orc_annotations|orc_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|orc_folder|orc_folder|
|**--type-properties-location**|object|The location of the ORC data storage.|orc_location|orc_location|
|**--type-properties-orc-compression-codec**|choice||orc_orc_compression_codec|orc_orc_compression_codec|
### datafactory dataset orc update

orc create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|orc_type|orc_type|
|**--linked-service-name**|object|Linked service reference.|orc_linked_service_name|orc_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|orc_description|orc_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|orc_structure|orc_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|orc_schema|orc_schema|
|**--parameters**|dictionary|Parameters for dataset.|orc_parameters|orc_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|orc_annotations|orc_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|orc_folder|orc_folder|
|**--type-properties-location**|object|The location of the ORC data storage.|orc_location|orc_location|
|**--type-properties-orc-compression-codec**|choice||orc_orc_compression_codec|orc_orc_compression_codec|
### datafactory dataset parquet create

parquet create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|parquet_type|parquet_type|
|**--linked-service-name**|object|Linked service reference.|parquet_linked_service_name|parquet_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|parquet_description|parquet_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|parquet_structure|parquet_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|parquet_schema|parquet_schema|
|**--parameters**|dictionary|Parameters for dataset.|parquet_parameters|parquet_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|parquet_annotations|parquet_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|parquet_folder|parquet_folder|
|**--type-properties-location**|object|The location of the parquet storage.|parquet_location|parquet_location|
|**--type-properties-compression-codec**|choice||parquet_compression_codec|parquet_compression_codec|
### datafactory dataset parquet update

parquet create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|parquet_type|parquet_type|
|**--linked-service-name**|object|Linked service reference.|parquet_linked_service_name|parquet_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|parquet_description|parquet_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|parquet_structure|parquet_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|parquet_schema|parquet_schema|
|**--parameters**|dictionary|Parameters for dataset.|parquet_parameters|parquet_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|parquet_annotations|parquet_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|parquet_folder|parquet_folder|
|**--type-properties-location**|object|The location of the parquet storage.|parquet_location|parquet_location|
|**--type-properties-compression-codec**|choice||parquet_compression_codec|parquet_compression_codec|
### datafactory dataset paypal-object create

paypal-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|paypalobject_type|paypal_object_type|
|**--linked-service-name**|object|Linked service reference.|paypalobject_linked_service_name|paypal_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|paypalobject_description|paypal_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|paypalobject_structure|paypal_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|paypalobject_schema|paypal_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|paypalobject_parameters|paypal_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|paypalobject_annotations|paypal_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|paypalobject_folder|paypal_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|paypalobject_table_name|paypal_object_table_name|
### datafactory dataset paypal-object update

paypal-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|paypalobject_type|paypal_object_type|
|**--linked-service-name**|object|Linked service reference.|paypalobject_linked_service_name|paypal_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|paypalobject_description|paypal_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|paypalobject_structure|paypal_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|paypalobject_schema|paypal_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|paypalobject_parameters|paypal_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|paypalobject_annotations|paypal_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|paypalobject_folder|paypal_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|paypalobject_table_name|paypal_object_table_name|
### datafactory dataset phoenix-object create

phoenix-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|phoenixobject_type|phoenix_object_type|
|**--linked-service-name**|object|Linked service reference.|phoenixobject_linked_service_name|phoenix_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|phoenixobject_description|phoenix_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|phoenixobject_structure|phoenix_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|phoenixobject_schema|phoenix_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|phoenixobject_parameters|phoenix_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|phoenixobject_annotations|phoenix_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|phoenixobject_folder|phoenix_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|phoenixobject_table_name|phoenix_object_table_name|
|**--type-properties-table**|any|The table name of the Phoenix. Type: string (or Expression with resultType string).|phoenixobject_table|phoenix_object_table|
|**--type-properties-schema**|any|The schema name of the Phoenix. Type: string (or Expression with resultType string).|phoenixobject_schema_type_properties_schema|phoenix_object_schema_type_properties_schema|
### datafactory dataset phoenix-object update

phoenix-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|phoenixobject_type|phoenix_object_type|
|**--linked-service-name**|object|Linked service reference.|phoenixobject_linked_service_name|phoenix_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|phoenixobject_description|phoenix_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|phoenixobject_structure|phoenix_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|phoenixobject_schema|phoenix_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|phoenixobject_parameters|phoenix_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|phoenixobject_annotations|phoenix_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|phoenixobject_folder|phoenix_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|phoenixobject_table_name|phoenix_object_table_name|
|**--type-properties-table**|any|The table name of the Phoenix. Type: string (or Expression with resultType string).|phoenixobject_table|phoenix_object_table|
|**--type-properties-schema**|any|The schema name of the Phoenix. Type: string (or Expression with resultType string).|phoenixobject_schema_type_properties_schema|phoenix_object_schema_type_properties_schema|
### datafactory dataset postgre-sql-table create

postgre-sql-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|postgresqltable_type|postgre_sql_table_type|
|**--linked-service-name**|object|Linked service reference.|postgresqltable_linked_service_name|postgre_sql_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|postgresqltable_description|postgre_sql_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|postgresqltable_structure|postgre_sql_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|postgresqltable_schema|postgre_sql_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|postgresqltable_parameters|postgre_sql_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|postgresqltable_annotations|postgre_sql_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|postgresqltable_folder|postgre_sql_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|postgresqltable_table_name|postgre_sql_table_table_name|
|**--type-properties-table**|any|The PostgreSQL table name. Type: string (or Expression with resultType string).|postgresqltable_table|postgre_sql_table_table|
|**--type-properties-schema**|any|The PostgreSQL schema name. Type: string (or Expression with resultType string).|postgresqltable_schema_type_properties_schema|postgre_sql_table_schema_type_properties_schema|
### datafactory dataset postgre-sql-table update

postgre-sql-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|postgresqltable_type|postgre_sql_table_type|
|**--linked-service-name**|object|Linked service reference.|postgresqltable_linked_service_name|postgre_sql_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|postgresqltable_description|postgre_sql_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|postgresqltable_structure|postgre_sql_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|postgresqltable_schema|postgre_sql_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|postgresqltable_parameters|postgre_sql_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|postgresqltable_annotations|postgre_sql_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|postgresqltable_folder|postgre_sql_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|postgresqltable_table_name|postgre_sql_table_table_name|
|**--type-properties-table**|any|The PostgreSQL table name. Type: string (or Expression with resultType string).|postgresqltable_table|postgre_sql_table_table|
|**--type-properties-schema**|any|The PostgreSQL schema name. Type: string (or Expression with resultType string).|postgresqltable_schema_type_properties_schema|postgre_sql_table_schema_type_properties_schema|
### datafactory dataset presto-object create

presto-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|prestoobject_type|presto_object_type|
|**--linked-service-name**|object|Linked service reference.|prestoobject_linked_service_name|presto_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|prestoobject_description|presto_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|prestoobject_structure|presto_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|prestoobject_schema|presto_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|prestoobject_parameters|presto_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|prestoobject_annotations|presto_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|prestoobject_folder|presto_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|prestoobject_table_name|presto_object_table_name|
|**--type-properties-table**|any|The table name of the Presto. Type: string (or Expression with resultType string).|prestoobject_table|presto_object_table|
|**--type-properties-schema**|any|The schema name of the Presto. Type: string (or Expression with resultType string).|prestoobject_schema_type_properties_schema|presto_object_schema_type_properties_schema|
### datafactory dataset presto-object update

presto-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|prestoobject_type|presto_object_type|
|**--linked-service-name**|object|Linked service reference.|prestoobject_linked_service_name|presto_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|prestoobject_description|presto_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|prestoobject_structure|presto_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|prestoobject_schema|presto_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|prestoobject_parameters|presto_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|prestoobject_annotations|presto_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|prestoobject_folder|presto_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|prestoobject_table_name|presto_object_table_name|
|**--type-properties-table**|any|The table name of the Presto. Type: string (or Expression with resultType string).|prestoobject_table|presto_object_table|
|**--type-properties-schema**|any|The schema name of the Presto. Type: string (or Expression with resultType string).|prestoobject_schema_type_properties_schema|presto_object_schema_type_properties_schema|
### datafactory dataset quick-books-object create

quick-books-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|quickbooksobject_type|quick_books_object_type|
|**--linked-service-name**|object|Linked service reference.|quickbooksobject_linked_service_name|quick_books_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|quickbooksobject_description|quick_books_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|quickbooksobject_structure|quick_books_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|quickbooksobject_schema|quick_books_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|quickbooksobject_parameters|quick_books_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|quickbooksobject_annotations|quick_books_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|quickbooksobject_folder|quick_books_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|quickbooksobject_table_name|quick_books_object_table_name|
### datafactory dataset quick-books-object update

quick-books-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|quickbooksobject_type|quick_books_object_type|
|**--linked-service-name**|object|Linked service reference.|quickbooksobject_linked_service_name|quick_books_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|quickbooksobject_description|quick_books_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|quickbooksobject_structure|quick_books_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|quickbooksobject_schema|quick_books_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|quickbooksobject_parameters|quick_books_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|quickbooksobject_annotations|quick_books_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|quickbooksobject_folder|quick_books_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|quickbooksobject_table_name|quick_books_object_table_name|
### datafactory dataset relational-table create

relational-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|relationaltable_type|relational_table_type|
|**--linked-service-name**|object|Linked service reference.|relationaltable_linked_service_name|relational_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|relationaltable_description|relational_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|relationaltable_structure|relational_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|relationaltable_schema|relational_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|relationaltable_parameters|relational_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|relationaltable_annotations|relational_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|relationaltable_folder|relational_table_folder|
|**--type-properties-table-name**|any|The relational table name. Type: string (or Expression with resultType string).|relationaltable_table_name|relational_table_table_name|
### datafactory dataset relational-table update

relational-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|relationaltable_type|relational_table_type|
|**--linked-service-name**|object|Linked service reference.|relationaltable_linked_service_name|relational_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|relationaltable_description|relational_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|relationaltable_structure|relational_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|relationaltable_schema|relational_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|relationaltable_parameters|relational_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|relationaltable_annotations|relational_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|relationaltable_folder|relational_table_folder|
|**--type-properties-table-name**|any|The relational table name. Type: string (or Expression with resultType string).|relationaltable_table_name|relational_table_table_name|
### datafactory dataset responsys-object create

responsys-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|responsysobject_type|responsys_object_type|
|**--linked-service-name**|object|Linked service reference.|responsysobject_linked_service_name|responsys_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|responsysobject_description|responsys_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|responsysobject_structure|responsys_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|responsysobject_schema|responsys_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|responsysobject_parameters|responsys_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|responsysobject_annotations|responsys_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|responsysobject_folder|responsys_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|responsysobject_table_name|responsys_object_table_name|
### datafactory dataset responsys-object update

responsys-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|responsysobject_type|responsys_object_type|
|**--linked-service-name**|object|Linked service reference.|responsysobject_linked_service_name|responsys_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|responsysobject_description|responsys_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|responsysobject_structure|responsys_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|responsysobject_schema|responsys_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|responsysobject_parameters|responsys_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|responsysobject_annotations|responsys_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|responsysobject_folder|responsys_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|responsysobject_table_name|responsys_object_table_name|
### datafactory dataset rest-resource create

rest-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|restresource_type|rest_resource_type|
|**--linked-service-name**|object|Linked service reference.|restresource_linked_service_name|rest_resource_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|restresource_description|rest_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|restresource_structure|rest_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|restresource_schema|rest_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|restresource_parameters|rest_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|restresource_annotations|rest_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|restresource_folder|rest_resource_folder|
|**--type-properties-relative-url**|any|The relative URL to the resource that the RESTful API provides. Type: string (or Expression with resultType string).|restresource_relative_url|rest_resource_relative_url|
|**--type-properties-request-method**|any|The HTTP method used to call the RESTful API. The default is GET. Type: string (or Expression with resultType string).|restresource_request_method|rest_resource_request_method|
|**--type-properties-request-body**|any|The HTTP request body to the RESTful API if requestMethod is POST. Type: string (or Expression with resultType string).|restresource_request_body|rest_resource_request_body|
|**--type-properties-additional-headers**|any|The additional HTTP headers in the request to the RESTful API. Type: string (or Expression with resultType string).|restresource_additional_headers|rest_resource_additional_headers|
|**--type-properties-pagination-rules**|any|The pagination rules to compose next page requests. Type: string (or Expression with resultType string).|restresource_pagination_rules|rest_resource_pagination_rules|
### datafactory dataset rest-resource update

rest-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|restresource_type|rest_resource_type|
|**--linked-service-name**|object|Linked service reference.|restresource_linked_service_name|rest_resource_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|restresource_description|rest_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|restresource_structure|rest_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|restresource_schema|rest_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|restresource_parameters|rest_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|restresource_annotations|rest_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|restresource_folder|rest_resource_folder|
|**--type-properties-relative-url**|any|The relative URL to the resource that the RESTful API provides. Type: string (or Expression with resultType string).|restresource_relative_url|rest_resource_relative_url|
|**--type-properties-request-method**|any|The HTTP method used to call the RESTful API. The default is GET. Type: string (or Expression with resultType string).|restresource_request_method|rest_resource_request_method|
|**--type-properties-request-body**|any|The HTTP request body to the RESTful API if requestMethod is POST. Type: string (or Expression with resultType string).|restresource_request_body|rest_resource_request_body|
|**--type-properties-additional-headers**|any|The additional HTTP headers in the request to the RESTful API. Type: string (or Expression with resultType string).|restresource_additional_headers|rest_resource_additional_headers|
|**--type-properties-pagination-rules**|any|The pagination rules to compose next page requests. Type: string (or Expression with resultType string).|restresource_pagination_rules|rest_resource_pagination_rules|
### datafactory dataset salesforce-marketing-cloud-object create

salesforce-marketing-cloud-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|salesforcemarketingcloudobject_type|salesforce_marketing_cloud_object_type|
|**--linked-service-name**|object|Linked service reference.|salesforcemarketingcloudobject_linked_service_name|salesforce_marketing_cloud_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|salesforcemarketingcloudobject_description|salesforce_marketing_cloud_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|salesforcemarketingcloudobject_structure|salesforce_marketing_cloud_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|salesforcemarketingcloudobject_schema|salesforce_marketing_cloud_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|salesforcemarketingcloudobject_parameters|salesforce_marketing_cloud_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|salesforcemarketingcloudobject_annotations|salesforce_marketing_cloud_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|salesforcemarketingcloudobject_folder|salesforce_marketing_cloud_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|salesforcemarketingcloudobject_table_name|salesforce_marketing_cloud_object_table_name|
### datafactory dataset salesforce-marketing-cloud-object update

salesforce-marketing-cloud-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|salesforcemarketingcloudobject_type|salesforce_marketing_cloud_object_type|
|**--linked-service-name**|object|Linked service reference.|salesforcemarketingcloudobject_linked_service_name|salesforce_marketing_cloud_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|salesforcemarketingcloudobject_description|salesforce_marketing_cloud_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|salesforcemarketingcloudobject_structure|salesforce_marketing_cloud_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|salesforcemarketingcloudobject_schema|salesforce_marketing_cloud_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|salesforcemarketingcloudobject_parameters|salesforce_marketing_cloud_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|salesforcemarketingcloudobject_annotations|salesforce_marketing_cloud_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|salesforcemarketingcloudobject_folder|salesforce_marketing_cloud_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|salesforcemarketingcloudobject_table_name|salesforce_marketing_cloud_object_table_name|
### datafactory dataset salesforce-object create

salesforce-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|salesforceobject_type|salesforce_object_type|
|**--linked-service-name**|object|Linked service reference.|salesforceobject_linked_service_name|salesforce_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|salesforceobject_description|salesforce_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|salesforceobject_structure|salesforce_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|salesforceobject_schema|salesforce_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|salesforceobject_parameters|salesforce_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|salesforceobject_annotations|salesforce_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|salesforceobject_folder|salesforce_object_folder|
|**--type-properties-object-api-name**|any|The Salesforce object API name. Type: string (or Expression with resultType string).|salesforceobject_object_api_name|salesforce_object_object_api_name|
### datafactory dataset salesforce-object update

salesforce-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|salesforceobject_type|salesforce_object_type|
|**--linked-service-name**|object|Linked service reference.|salesforceobject_linked_service_name|salesforce_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|salesforceobject_description|salesforce_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|salesforceobject_structure|salesforce_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|salesforceobject_schema|salesforce_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|salesforceobject_parameters|salesforce_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|salesforceobject_annotations|salesforce_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|salesforceobject_folder|salesforce_object_folder|
|**--type-properties-object-api-name**|any|The Salesforce object API name. Type: string (or Expression with resultType string).|salesforceobject_object_api_name|salesforce_object_object_api_name|
### datafactory dataset salesforce-service-cloud-object create

salesforce-service-cloud-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|salesforceservicecloudobject_type|salesforce_service_cloud_object_type|
|**--linked-service-name**|object|Linked service reference.|salesforceservicecloudobject_linked_service_name|salesforce_service_cloud_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|salesforceservicecloudobject_description|salesforce_service_cloud_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|salesforceservicecloudobject_structure|salesforce_service_cloud_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|salesforceservicecloudobject_schema|salesforce_service_cloud_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|salesforceservicecloudobject_parameters|salesforce_service_cloud_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|salesforceservicecloudobject_annotations|salesforce_service_cloud_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|salesforceservicecloudobject_folder|salesforce_service_cloud_object_folder|
|**--type-properties-object-api-name**|any|The Salesforce Service Cloud object API name. Type: string (or Expression with resultType string).|salesforceservicecloudobject_object_api_name|salesforce_service_cloud_object_object_api_name|
### datafactory dataset salesforce-service-cloud-object update

salesforce-service-cloud-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|salesforceservicecloudobject_type|salesforce_service_cloud_object_type|
|**--linked-service-name**|object|Linked service reference.|salesforceservicecloudobject_linked_service_name|salesforce_service_cloud_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|salesforceservicecloudobject_description|salesforce_service_cloud_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|salesforceservicecloudobject_structure|salesforce_service_cloud_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|salesforceservicecloudobject_schema|salesforce_service_cloud_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|salesforceservicecloudobject_parameters|salesforce_service_cloud_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|salesforceservicecloudobject_annotations|salesforce_service_cloud_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|salesforceservicecloudobject_folder|salesforce_service_cloud_object_folder|
|**--type-properties-object-api-name**|any|The Salesforce Service Cloud object API name. Type: string (or Expression with resultType string).|salesforceservicecloudobject_object_api_name|salesforce_service_cloud_object_object_api_name|
### datafactory dataset sap-bw-cube create

sap-bw-cube create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|sapbwcube_type|sap_bw_cube_type|
|**--linked-service-name**|object|Linked service reference.|sapbwcube_linked_service_name|sap_bw_cube_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|sapbwcube_description|sap_bw_cube_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sapbwcube_structure|sap_bw_cube_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sapbwcube_schema|sap_bw_cube_schema|
|**--parameters**|dictionary|Parameters for dataset.|sapbwcube_parameters|sap_bw_cube_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sapbwcube_annotations|sap_bw_cube_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sapbwcube_folder|sap_bw_cube_folder|
### datafactory dataset sap-bw-cube update

sap-bw-cube create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|sapbwcube_type|sap_bw_cube_type|
|**--linked-service-name**|object|Linked service reference.|sapbwcube_linked_service_name|sap_bw_cube_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|sapbwcube_description|sap_bw_cube_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sapbwcube_structure|sap_bw_cube_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sapbwcube_schema|sap_bw_cube_schema|
|**--parameters**|dictionary|Parameters for dataset.|sapbwcube_parameters|sap_bw_cube_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sapbwcube_annotations|sap_bw_cube_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sapbwcube_folder|sap_bw_cube_folder|
### datafactory dataset sap-cloud-for-customer-resource create

sap-cloud-for-customer-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|sapcloudforcustomerresource_type|sap_cloud_for_customer_resource_type|
|**--linked-service-name**|object|Linked service reference.|sapcloudforcustomerresource_linked_service_name|sap_cloud_for_customer_resource_linked_service_name|
|**--type-properties-path**|any|The path of the SAP Cloud for Customer OData entity. Type: string (or Expression with resultType string).|sapcloudforcustomerresource_path|sap_cloud_for_customer_resource_path|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|sapcloudforcustomerresource_description|sap_cloud_for_customer_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sapcloudforcustomerresource_structure|sap_cloud_for_customer_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sapcloudforcustomerresource_schema|sap_cloud_for_customer_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|sapcloudforcustomerresource_parameters|sap_cloud_for_customer_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sapcloudforcustomerresource_annotations|sap_cloud_for_customer_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sapcloudforcustomerresource_folder|sap_cloud_for_customer_resource_folder|
### datafactory dataset sap-cloud-for-customer-resource update

sap-cloud-for-customer-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|sapcloudforcustomerresource_type|sap_cloud_for_customer_resource_type|
|**--linked-service-name**|object|Linked service reference.|sapcloudforcustomerresource_linked_service_name|sap_cloud_for_customer_resource_linked_service_name|
|**--type-properties-path**|any|The path of the SAP Cloud for Customer OData entity. Type: string (or Expression with resultType string).|sapcloudforcustomerresource_path|sap_cloud_for_customer_resource_path|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|sapcloudforcustomerresource_description|sap_cloud_for_customer_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sapcloudforcustomerresource_structure|sap_cloud_for_customer_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sapcloudforcustomerresource_schema|sap_cloud_for_customer_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|sapcloudforcustomerresource_parameters|sap_cloud_for_customer_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sapcloudforcustomerresource_annotations|sap_cloud_for_customer_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sapcloudforcustomerresource_folder|sap_cloud_for_customer_resource_folder|
### datafactory dataset sap-ecc-resource create

sap-ecc-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|sapeccresource_type|sap_ecc_resource_type|
|**--linked-service-name**|object|Linked service reference.|sapeccresource_linked_service_name|sap_ecc_resource_linked_service_name|
|**--type-properties-path**|any|The path of the SAP ECC OData entity. Type: string (or Expression with resultType string).|sapeccresource_path|sap_ecc_resource_path|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|sapeccresource_description|sap_ecc_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sapeccresource_structure|sap_ecc_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sapeccresource_schema|sap_ecc_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|sapeccresource_parameters|sap_ecc_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sapeccresource_annotations|sap_ecc_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sapeccresource_folder|sap_ecc_resource_folder|
### datafactory dataset sap-ecc-resource update

sap-ecc-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|sapeccresource_type|sap_ecc_resource_type|
|**--linked-service-name**|object|Linked service reference.|sapeccresource_linked_service_name|sap_ecc_resource_linked_service_name|
|**--type-properties-path**|any|The path of the SAP ECC OData entity. Type: string (or Expression with resultType string).|sapeccresource_path|sap_ecc_resource_path|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|sapeccresource_description|sap_ecc_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sapeccresource_structure|sap_ecc_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sapeccresource_schema|sap_ecc_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|sapeccresource_parameters|sap_ecc_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sapeccresource_annotations|sap_ecc_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sapeccresource_folder|sap_ecc_resource_folder|
### datafactory dataset sap-hana-table create

sap-hana-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|saphanatable_type|sap_hana_table_type|
|**--linked-service-name**|object|Linked service reference.|saphanatable_linked_service_name|sap_hana_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|saphanatable_description|sap_hana_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|saphanatable_structure|sap_hana_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|saphanatable_schema|sap_hana_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|saphanatable_parameters|sap_hana_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|saphanatable_annotations|sap_hana_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|saphanatable_folder|sap_hana_table_folder|
|**--type-properties-schema**|any|The schema name of SAP HANA. Type: string (or Expression with resultType string).|saphanatable_schema_type_properties_schema|sap_hana_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of SAP HANA. Type: string (or Expression with resultType string).|saphanatable_table|sap_hana_table_table|
### datafactory dataset sap-hana-table update

sap-hana-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|saphanatable_type|sap_hana_table_type|
|**--linked-service-name**|object|Linked service reference.|saphanatable_linked_service_name|sap_hana_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|saphanatable_description|sap_hana_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|saphanatable_structure|sap_hana_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|saphanatable_schema|sap_hana_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|saphanatable_parameters|sap_hana_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|saphanatable_annotations|sap_hana_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|saphanatable_folder|sap_hana_table_folder|
|**--type-properties-schema**|any|The schema name of SAP HANA. Type: string (or Expression with resultType string).|saphanatable_schema_type_properties_schema|sap_hana_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of SAP HANA. Type: string (or Expression with resultType string).|saphanatable_table|sap_hana_table_table|
### datafactory dataset sap-open-hub-table create

sap-open-hub-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|sapopenhubtable_type|sap_open_hub_table_type|
|**--linked-service-name**|object|Linked service reference.|sapopenhubtable_linked_service_name|sap_open_hub_table_linked_service_name|
|**--type-properties-open-hub-destination-name**|any|The name of the Open Hub Destination with destination type as Database Table. Type: string (or Expression with resultType string).|sapopenhubtable_open_hub_destination_name|sap_open_hub_table_open_hub_destination_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|sapopenhubtable_description|sap_open_hub_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sapopenhubtable_structure|sap_open_hub_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sapopenhubtable_schema|sap_open_hub_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|sapopenhubtable_parameters|sap_open_hub_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sapopenhubtable_annotations|sap_open_hub_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sapopenhubtable_folder|sap_open_hub_table_folder|
|**--type-properties-exclude-last-request**|any|Whether to exclude the records of the last request. The default value is true. Type: boolean (or Expression with resultType boolean).|sapopenhubtable_exclude_last_request|sap_open_hub_table_exclude_last_request|
|**--type-properties-base-request-id**|any|The ID of request for delta loading. Once it is set, only data with requestId larger than the value of this property will be retrieved. The default value is 0. Type: integer (or Expression with resultType integer ).|sapopenhubtable_base_request_id|sap_open_hub_table_base_request_id|
### datafactory dataset sap-open-hub-table update

sap-open-hub-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|sapopenhubtable_type|sap_open_hub_table_type|
|**--linked-service-name**|object|Linked service reference.|sapopenhubtable_linked_service_name|sap_open_hub_table_linked_service_name|
|**--type-properties-open-hub-destination-name**|any|The name of the Open Hub Destination with destination type as Database Table. Type: string (or Expression with resultType string).|sapopenhubtable_open_hub_destination_name|sap_open_hub_table_open_hub_destination_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|sapopenhubtable_description|sap_open_hub_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sapopenhubtable_structure|sap_open_hub_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sapopenhubtable_schema|sap_open_hub_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|sapopenhubtable_parameters|sap_open_hub_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sapopenhubtable_annotations|sap_open_hub_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sapopenhubtable_folder|sap_open_hub_table_folder|
|**--type-properties-exclude-last-request**|any|Whether to exclude the records of the last request. The default value is true. Type: boolean (or Expression with resultType boolean).|sapopenhubtable_exclude_last_request|sap_open_hub_table_exclude_last_request|
|**--type-properties-base-request-id**|any|The ID of request for delta loading. Once it is set, only data with requestId larger than the value of this property will be retrieved. The default value is 0. Type: integer (or Expression with resultType integer ).|sapopenhubtable_base_request_id|sap_open_hub_table_base_request_id|
### datafactory dataset sap-table-resource create

sap-table-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|saptableresource_type|sap_table_resource_type|
|**--linked-service-name**|object|Linked service reference.|saptableresource_linked_service_name|sap_table_resource_linked_service_name|
|**--type-properties-table-name**|any|The name of the SAP Table. Type: string (or Expression with resultType string).|saptableresource_table_name|sap_table_resource_table_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|saptableresource_description|sap_table_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|saptableresource_structure|sap_table_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|saptableresource_schema|sap_table_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|saptableresource_parameters|sap_table_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|saptableresource_annotations|sap_table_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|saptableresource_folder|sap_table_resource_folder|
### datafactory dataset sap-table-resource update

sap-table-resource create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|saptableresource_type|sap_table_resource_type|
|**--linked-service-name**|object|Linked service reference.|saptableresource_linked_service_name|sap_table_resource_linked_service_name|
|**--type-properties-table-name**|any|The name of the SAP Table. Type: string (or Expression with resultType string).|saptableresource_table_name|sap_table_resource_table_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|saptableresource_description|sap_table_resource_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|saptableresource_structure|sap_table_resource_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|saptableresource_schema|sap_table_resource_schema|
|**--parameters**|dictionary|Parameters for dataset.|saptableresource_parameters|sap_table_resource_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|saptableresource_annotations|sap_table_resource_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|saptableresource_folder|sap_table_resource_folder|
### datafactory dataset service-now-object create

service-now-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|servicenowobject_type|service_now_object_type|
|**--linked-service-name**|object|Linked service reference.|servicenowobject_linked_service_name|service_now_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|servicenowobject_description|service_now_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|servicenowobject_structure|service_now_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|servicenowobject_schema|service_now_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|servicenowobject_parameters|service_now_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|servicenowobject_annotations|service_now_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|servicenowobject_folder|service_now_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|servicenowobject_table_name|service_now_object_table_name|
### datafactory dataset service-now-object update

service-now-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|servicenowobject_type|service_now_object_type|
|**--linked-service-name**|object|Linked service reference.|servicenowobject_linked_service_name|service_now_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|servicenowobject_description|service_now_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|servicenowobject_structure|service_now_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|servicenowobject_schema|service_now_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|servicenowobject_parameters|service_now_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|servicenowobject_annotations|service_now_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|servicenowobject_folder|service_now_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|servicenowobject_table_name|service_now_object_table_name|
### datafactory dataset shopify-object create

shopify-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|shopifyobject_type|shopify_object_type|
|**--linked-service-name**|object|Linked service reference.|shopifyobject_linked_service_name|shopify_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|shopifyobject_description|shopify_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|shopifyobject_structure|shopify_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|shopifyobject_schema|shopify_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|shopifyobject_parameters|shopify_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|shopifyobject_annotations|shopify_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|shopifyobject_folder|shopify_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|shopifyobject_table_name|shopify_object_table_name|
### datafactory dataset shopify-object update

shopify-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|shopifyobject_type|shopify_object_type|
|**--linked-service-name**|object|Linked service reference.|shopifyobject_linked_service_name|shopify_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|shopifyobject_description|shopify_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|shopifyobject_structure|shopify_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|shopifyobject_schema|shopify_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|shopifyobject_parameters|shopify_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|shopifyobject_annotations|shopify_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|shopifyobject_folder|shopify_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|shopifyobject_table_name|shopify_object_table_name|
### datafactory dataset show

show a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--if-none-match**|string|ETag of the dataset entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|if_none_match|
### datafactory dataset snowflake-table create

snowflake-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|snowflaketable_type|snowflake_table_type|
|**--linked-service-name**|object|Linked service reference.|snowflaketable_linked_service_name|snowflake_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|snowflaketable_description|snowflake_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|snowflaketable_structure|snowflake_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|snowflaketable_schema|snowflake_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|snowflaketable_parameters|snowflake_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|snowflaketable_annotations|snowflake_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|snowflaketable_folder|snowflake_table_folder|
|**--type-properties-schema**|any|The schema name of the Snowflake database. Type: string (or Expression with resultType string).|snowflaketable_schema_type_properties_schema|snowflake_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the Snowflake database. Type: string (or Expression with resultType string).|snowflaketable_table|snowflake_table_table|
### datafactory dataset snowflake-table update

snowflake-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|snowflaketable_type|snowflake_table_type|
|**--linked-service-name**|object|Linked service reference.|snowflaketable_linked_service_name|snowflake_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|snowflaketable_description|snowflake_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|snowflaketable_structure|snowflake_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|snowflaketable_schema|snowflake_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|snowflaketable_parameters|snowflake_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|snowflaketable_annotations|snowflake_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|snowflaketable_folder|snowflake_table_folder|
|**--type-properties-schema**|any|The schema name of the Snowflake database. Type: string (or Expression with resultType string).|snowflaketable_schema_type_properties_schema|snowflake_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the Snowflake database. Type: string (or Expression with resultType string).|snowflaketable_table|snowflake_table_table|
### datafactory dataset spark-object create

spark-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|sparkobject_type|spark_object_type|
|**--linked-service-name**|object|Linked service reference.|sparkobject_linked_service_name|spark_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|sparkobject_description|spark_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sparkobject_structure|spark_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sparkobject_schema|spark_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|sparkobject_parameters|spark_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sparkobject_annotations|spark_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sparkobject_folder|spark_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|sparkobject_table_name|spark_object_table_name|
|**--type-properties-table**|any|The table name of the Spark. Type: string (or Expression with resultType string).|sparkobject_table|spark_object_table|
|**--type-properties-schema**|any|The schema name of the Spark. Type: string (or Expression with resultType string).|sparkobject_schema_type_properties_schema|spark_object_schema_type_properties_schema|
### datafactory dataset spark-object update

spark-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|sparkobject_type|spark_object_type|
|**--linked-service-name**|object|Linked service reference.|sparkobject_linked_service_name|spark_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|sparkobject_description|spark_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sparkobject_structure|spark_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sparkobject_schema|spark_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|sparkobject_parameters|spark_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sparkobject_annotations|spark_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sparkobject_folder|spark_object_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|sparkobject_table_name|spark_object_table_name|
|**--type-properties-table**|any|The table name of the Spark. Type: string (or Expression with resultType string).|sparkobject_table|spark_object_table|
|**--type-properties-schema**|any|The schema name of the Spark. Type: string (or Expression with resultType string).|sparkobject_schema_type_properties_schema|spark_object_schema_type_properties_schema|
### datafactory dataset sql-server-table create

sql-server-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|sqlservertable_type|sql_server_table_type|
|**--linked-service-name**|object|Linked service reference.|sqlservertable_linked_service_name|sql_server_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|sqlservertable_description|sql_server_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sqlservertable_structure|sql_server_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sqlservertable_schema|sql_server_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|sqlservertable_parameters|sql_server_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sqlservertable_annotations|sql_server_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sqlservertable_folder|sql_server_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|sqlservertable_table_name|sql_server_table_table_name|
|**--type-properties-schema**|any|The schema name of the SQL Server dataset. Type: string (or Expression with resultType string).|sqlservertable_schema_type_properties_schema|sql_server_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the SQL Server dataset. Type: string (or Expression with resultType string).|sqlservertable_table|sql_server_table_table|
### datafactory dataset sql-server-table update

sql-server-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|sqlservertable_type|sql_server_table_type|
|**--linked-service-name**|object|Linked service reference.|sqlservertable_linked_service_name|sql_server_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|sqlservertable_description|sql_server_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sqlservertable_structure|sql_server_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sqlservertable_schema|sql_server_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|sqlservertable_parameters|sql_server_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sqlservertable_annotations|sql_server_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sqlservertable_folder|sql_server_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|sqlservertable_table_name|sql_server_table_table_name|
|**--type-properties-schema**|any|The schema name of the SQL Server dataset. Type: string (or Expression with resultType string).|sqlservertable_schema_type_properties_schema|sql_server_table_schema_type_properties_schema|
|**--type-properties-table**|any|The table name of the SQL Server dataset. Type: string (or Expression with resultType string).|sqlservertable_table|sql_server_table_table|
### datafactory dataset square-object create

square-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|squareobject_type|square_object_type|
|**--linked-service-name**|object|Linked service reference.|squareobject_linked_service_name|square_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|squareobject_description|square_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|squareobject_structure|square_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|squareobject_schema|square_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|squareobject_parameters|square_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|squareobject_annotations|square_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|squareobject_folder|square_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|squareobject_table_name|square_object_table_name|
### datafactory dataset square-object update

square-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|squareobject_type|square_object_type|
|**--linked-service-name**|object|Linked service reference.|squareobject_linked_service_name|square_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|squareobject_description|square_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|squareobject_structure|square_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|squareobject_schema|square_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|squareobject_parameters|square_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|squareobject_annotations|square_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|squareobject_folder|square_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|squareobject_table_name|square_object_table_name|
### datafactory dataset sybase-table create

sybase-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|sybasetable_type|sybase_table_type|
|**--linked-service-name**|object|Linked service reference.|sybasetable_linked_service_name|sybase_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|sybasetable_description|sybase_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sybasetable_structure|sybase_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sybasetable_schema|sybase_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|sybasetable_parameters|sybase_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sybasetable_annotations|sybase_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sybasetable_folder|sybase_table_folder|
|**--type-properties-table-name**|any|The Sybase table name. Type: string (or Expression with resultType string).|sybasetable_table_name|sybase_table_table_name|
### datafactory dataset sybase-table update

sybase-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|sybasetable_type|sybase_table_type|
|**--linked-service-name**|object|Linked service reference.|sybasetable_linked_service_name|sybase_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|sybasetable_description|sybase_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|sybasetable_structure|sybase_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|sybasetable_schema|sybase_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|sybasetable_parameters|sybase_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|sybasetable_annotations|sybase_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|sybasetable_folder|sybase_table_folder|
|**--type-properties-table-name**|any|The Sybase table name. Type: string (or Expression with resultType string).|sybasetable_table_name|sybase_table_table_name|
### datafactory dataset teradata-table create

teradata-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|teradatatable_type|teradata_table_type|
|**--linked-service-name**|object|Linked service reference.|teradatatable_linked_service_name|teradata_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|teradatatable_description|teradata_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|teradatatable_structure|teradata_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|teradatatable_schema|teradata_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|teradatatable_parameters|teradata_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|teradatatable_annotations|teradata_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|teradatatable_folder|teradata_table_folder|
|**--type-properties-database**|any|The database name of Teradata. Type: string (or Expression with resultType string).|teradatatable_database|teradata_table_database|
|**--type-properties-table**|any|The table name of Teradata. Type: string (or Expression with resultType string).|teradatatable_table|teradata_table_table|
### datafactory dataset teradata-table update

teradata-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|teradatatable_type|teradata_table_type|
|**--linked-service-name**|object|Linked service reference.|teradatatable_linked_service_name|teradata_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|teradatatable_description|teradata_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|teradatatable_structure|teradata_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|teradatatable_schema|teradata_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|teradatatable_parameters|teradata_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|teradatatable_annotations|teradata_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|teradatatable_folder|teradata_table_folder|
|**--type-properties-database**|any|The database name of Teradata. Type: string (or Expression with resultType string).|teradatatable_database|teradata_table_database|
|**--type-properties-table**|any|The table name of Teradata. Type: string (or Expression with resultType string).|teradatatable_table|teradata_table_table|
### datafactory dataset vertica-table create

vertica-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|verticatable_type|vertica_table_type|
|**--linked-service-name**|object|Linked service reference.|verticatable_linked_service_name|vertica_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|verticatable_description|vertica_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|verticatable_structure|vertica_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|verticatable_schema|vertica_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|verticatable_parameters|vertica_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|verticatable_annotations|vertica_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|verticatable_folder|vertica_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|verticatable_table_name|vertica_table_table_name|
|**--type-properties-table**|any|The table name of the Vertica. Type: string (or Expression with resultType string).|verticatable_table|vertica_table_table|
|**--type-properties-schema**|any|The schema name of the Vertica. Type: string (or Expression with resultType string).|verticatable_schema_type_properties_schema|vertica_table_schema_type_properties_schema|
### datafactory dataset vertica-table update

vertica-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|verticatable_type|vertica_table_type|
|**--linked-service-name**|object|Linked service reference.|verticatable_linked_service_name|vertica_table_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|verticatable_description|vertica_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|verticatable_structure|vertica_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|verticatable_schema|vertica_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|verticatable_parameters|vertica_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|verticatable_annotations|vertica_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|verticatable_folder|vertica_table_folder|
|**--type-properties-table-name**|any|This property will be retired. Please consider using schema + table properties instead.|verticatable_table_name|vertica_table_table_name|
|**--type-properties-table**|any|The table name of the Vertica. Type: string (or Expression with resultType string).|verticatable_table|vertica_table_table|
|**--type-properties-schema**|any|The schema name of the Vertica. Type: string (or Expression with resultType string).|verticatable_schema_type_properties_schema|vertica_table_schema_type_properties_schema|
### datafactory dataset web-table create

web-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|webtable_type|web_table_type|
|**--linked-service-name**|object|Linked service reference.|webtable_linked_service_name|web_table_linked_service_name|
|**--type-properties-index**|any|The zero-based index of the table in the web page. Type: integer (or Expression with resultType integer), minimum: 0.|webtable_index|web_table_index|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|webtable_description|web_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|webtable_structure|web_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|webtable_schema|web_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|webtable_parameters|web_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|webtable_annotations|web_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|webtable_folder|web_table_folder|
|**--type-properties-path**|any|The relative URL to the web page from the linked service URL. Type: string (or Expression with resultType string).|webtable_path|web_table_path|
### datafactory dataset web-table update

web-table create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|webtable_type|web_table_type|
|**--linked-service-name**|object|Linked service reference.|webtable_linked_service_name|web_table_linked_service_name|
|**--type-properties-index**|any|The zero-based index of the table in the web page. Type: integer (or Expression with resultType integer), minimum: 0.|webtable_index|web_table_index|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|webtable_description|web_table_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|webtable_structure|web_table_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|webtable_schema|web_table_schema|
|**--parameters**|dictionary|Parameters for dataset.|webtable_parameters|web_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|webtable_annotations|web_table_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|webtable_folder|web_table_folder|
|**--type-properties-path**|any|The relative URL to the web page from the linked service URL. Type: string (or Expression with resultType string).|webtable_path|web_table_path|
### datafactory dataset xero-object create

xero-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|xeroobject_type|xero_object_type|
|**--linked-service-name**|object|Linked service reference.|xeroobject_linked_service_name|xero_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|xeroobject_description|xero_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|xeroobject_structure|xero_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|xeroobject_schema|xero_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|xeroobject_parameters|xero_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|xeroobject_annotations|xero_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|xeroobject_folder|xero_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|xeroobject_table_name|xero_object_table_name|
### datafactory dataset xero-object update

xero-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|xeroobject_type|xero_object_type|
|**--linked-service-name**|object|Linked service reference.|xeroobject_linked_service_name|xero_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|xeroobject_description|xero_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|xeroobject_structure|xero_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|xeroobject_schema|xero_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|xeroobject_parameters|xero_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|xeroobject_annotations|xero_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|xeroobject_folder|xero_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|xeroobject_table_name|xero_object_table_name|
### datafactory dataset zoho-object create

zoho-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|zohoobject_type|zoho_object_type|
|**--linked-service-name**|object|Linked service reference.|zohoobject_linked_service_name|zoho_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|zohoobject_description|zoho_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|zohoobject_structure|zoho_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|zohoobject_schema|zoho_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|zohoobject_parameters|zoho_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|zohoobject_annotations|zoho_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|zohoobject_folder|zoho_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|zohoobject_table_name|zoho_object_table_name|
### datafactory dataset zoho-object update

zoho-object create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|dataset_name|
|**--type**|string|Type of dataset.|zohoobject_type|zoho_object_type|
|**--linked-service-name**|object|Linked service reference.|zohoobject_linked_service_name|zoho_object_linked_service_name|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Dataset description.|zohoobject_description|zoho_object_description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|zohoobject_structure|zoho_object_structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|zohoobject_schema|zoho_object_schema|
|**--parameters**|dictionary|Parameters for dataset.|zohoobject_parameters|zoho_object_parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|zohoobject_annotations|zoho_object_annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|zohoobject_folder|zoho_object_folder|
|**--type-properties-table-name**|any|The table name. Type: string (or Expression with resultType string).|zohoobject_table_name|zoho_object_table_name|
### datafactory exposure-control get-feature-value

get-feature-value a datafactory exposure-control.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location-id**|string|The location identifier.|location_id|location_id|
|**--feature-name**|string|The feature name.|feature_name|feature_name|
|**--feature-type**|string|The feature type.|feature_type|feature_type|
### datafactory exposure-control get-feature-value-by-factory

get-feature-value-by-factory a datafactory exposure-control.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--feature-name**|string|The feature name.|feature_name|feature_name|
|**--feature-type**|string|The feature type.|feature_type|feature_type|
### datafactory factory configure-factory-repo

configure-factory-repo a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location-id**|string|The location identifier.|location_id|location_id|
|**--factory-resource-id**|string|The factory resource id.|factory_resource_id|factory_resource_id|
|**--repo-configuration**|object|Git repo information of the factory.|repo_configuration|repo_configuration|
### datafactory factory create

create a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--if-match**|string|ETag of the factory entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--identity**|object|Managed service identity of the factory.|identity|identity|
|**--repo-configuration**|object|Git repo information of the factory.|repo_configuration|repo_configuration|
### datafactory factory delete

delete a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
### datafactory factory get-data-plane-access

get-data-plane-access a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--permissions**|string|The string with permissions for Data Plane access. Currently only 'r' is supported which grants read only access.|permissions|permissions|
|**--access-resource-path**|string|The resource path to get access relative to factory. Currently only empty string is supported which corresponds to the factory resource.|access_resource_path|access_resource_path|
|**--profile-name**|string|The name of the profile. Currently only the default is supported. The default value is DefaultProfile.|profile_name|profile_name|
|**--start-time**|string|Start time for the token. If not specified the current time will be used.|start_time|start_time|
|**--expire-time**|string|Expiration time for the token. Maximum duration for the token is eight hours and by default the token will expire in eight hours.|expire_time|expire_time|
### datafactory factory get-git-hub-access-token

get-git-hub-access-token a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--git-hub-access-code**|string|GitHub access code.|git_hub_access_code|git_hub_access_code|
|**--git-hub-access-token-base-url**|string|GitHub access token base URL.|git_hub_access_token_base_url|git_hub_access_token_base_url|
|**--git-hub-client-id**|string|GitHub application client ID.|git_hub_client_id|git_hub_client_id|
### datafactory factory list

list a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
### datafactory factory show

show a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--if-none-match**|string|ETag of the factory entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|if_none_match|
### datafactory factory update

update a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--identity**|object|Managed service identity of the factory.|identity|identity|
### datafactory integration-runtime create-linked-integration-runtime

create-linked-integration-runtime a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--name**|string|The name of the linked integration runtime.|name|name|
|**--subscription-id**|string|The ID of the subscription that the linked integration runtime belongs to.|subscription_id|subscription_id|
|**--data-factory-name**|string|The name of the data factory that the linked integration runtime belongs to.|data_factory_name|data_factory_name|
|**--data-factory-location**|string|The location of the data factory that the linked integration runtime belongs to.|data_factory_location|data_factory_location|
### datafactory integration-runtime delete

delete a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
### datafactory integration-runtime get-connection-info

get-connection-info a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
### datafactory integration-runtime get-monitoring-data

get-monitoring-data a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
### datafactory integration-runtime get-status

get-status a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
### datafactory integration-runtime list

list a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
### datafactory integration-runtime list-auth-key

list-auth-key a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
### datafactory integration-runtime managed create

managed create a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--type**|choice|Type of integration runtime.|managed_type|managed_type|
|**--if-match**|string|ETag of the integration runtime entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Integration runtime description.|managed_description|managed_description|
|**--type-properties-compute-properties**|object|The compute resource for managed integration runtime.|managed_compute_properties|managed_compute_properties|
|**--type-properties-ssis-properties**|object|SSIS properties for managed integration runtime.|managed_ssis_properties|managed_ssis_properties|
### datafactory integration-runtime regenerate-auth-key

regenerate-auth-key a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--key-name**|choice|The name of the authentication key to regenerate.|key_name|key_name|
### datafactory integration-runtime remove-link

remove-link a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--linked-factory-name**|string|The data factory name for linked integration runtime.|linked_factory_name|linked_factory_name|
### datafactory integration-runtime self-hosted create

self-hosted create a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--type**|choice|Type of integration runtime.|selfhosted_type|self_hosted_type|
|**--if-match**|string|ETag of the integration runtime entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|Integration runtime description.|selfhosted_description|self_hosted_description|
|**--type-properties-linked-info**|object|The base definition of a linked integration runtime.|selfhosted_linked_info|self_hosted_linked_info|
### datafactory integration-runtime show

show a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--if-none-match**|string|ETag of the integration runtime entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|if_none_match|
### datafactory integration-runtime start

start a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
### datafactory integration-runtime stop

stop a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
### datafactory integration-runtime sync-credentials

sync-credentials a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
### datafactory integration-runtime update

update a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--auto-update**|choice|Enables or disables the auto-update feature of the self-hosted integration runtime. See https://go.microsoft.com/fwlink/?linkid=854189.|auto_update|auto_update|
|**--update-delay-offset**|string|The time offset (in hours) in the day, e.g., PT03H is 3 hours. The integration runtime auto update will happen on that time.|update_delay_offset|update_delay_offset|
### datafactory integration-runtime upgrade

upgrade a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
### datafactory integration-runtime-node delete

delete a datafactory integration-runtime-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--node-name**|string|The integration runtime node name.|node_name|node_name|
### datafactory integration-runtime-node get-ip-address

get-ip-address a datafactory integration-runtime-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--node-name**|string|The integration runtime node name.|node_name|node_name|
### datafactory integration-runtime-node show

show a datafactory integration-runtime-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--node-name**|string|The integration runtime node name.|node_name|node_name|
### datafactory integration-runtime-node update

update a datafactory integration-runtime-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--node-name**|string|The integration runtime node name.|node_name|node_name|
|**--concurrent-jobs-limit**|integer|The number of concurrent jobs permitted to run on the integration runtime node. Values between 1 and maxConcurrentJobs(inclusive) are allowed.|concurrent_jobs_limit|concurrent_jobs_limit|
### datafactory integration-runtime-object-metadata get

get a datafactory integration-runtime-object-metadata.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--metadata-path**|string|Metadata path.|metadata_path|metadata_path|
### datafactory integration-runtime-object-metadata refresh

refresh a datafactory integration-runtime-object-metadata.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
### datafactory linked-service amazon-m-w-s create

amazon-m-w-s create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|amazonmws_type|amazon_m_w_s_type|
|**--type-properties-endpoint**|any|The endpoint of the Amazon MWS server, (i.e. mws.amazonservices.com)|amazonmws_endpoint|amazon_m_w_s_endpoint|
|**--type-properties-marketplace-id**|any|The Amazon Marketplace ID you want to retrieve data from. To retrieve data from multiple Marketplace IDs, separate them with a comma (,). (i.e. A2EUQ1WTGCTBG2)|amazonmws_marketplace_id|amazon_m_w_s_marketplace_id|
|**--type-properties-seller-id**|any|The Amazon seller ID.|amazonmws_seller_id|amazon_m_w_s_seller_id|
|**--type-properties-access-key-id**|any|The access key id used to access data.|amazonmws_access_key_id|amazon_m_w_s_access_key_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|amazonmws_connect_via|amazon_m_w_s_connect_via|
|**--description**|string|Linked service description.|amazonmws_description|amazon_m_w_s_description|
|**--parameters**|dictionary|Parameters for linked service.|amazonmws_parameters|amazon_m_w_s_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|amazonmws_annotations|amazon_m_w_s_annotations|
|**--type-properties-mws-auth-token**|object|The Amazon MWS authentication token.|amazonmws_mws_auth_token|amazon_m_w_s_mws_auth_token|
|**--type-properties-secret-key**|object|The secret key used to access data.|amazonmws_secret_key|amazon_m_w_s_secret_key|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|amazonmws_use_encrypted_endpoints|amazon_m_w_s_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|amazonmws_use_host_verification|amazon_m_w_s_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|amazonmws_use_peer_verification|amazon_m_w_s_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|amazonmws_encrypted_credential|amazon_m_w_s_encrypted_credential|
### datafactory linked-service amazon-m-w-s update

amazon-m-w-s create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|amazonmws_type|amazon_m_w_s_type|
|**--type-properties-endpoint**|any|The endpoint of the Amazon MWS server, (i.e. mws.amazonservices.com)|amazonmws_endpoint|amazon_m_w_s_endpoint|
|**--type-properties-marketplace-id**|any|The Amazon Marketplace ID you want to retrieve data from. To retrieve data from multiple Marketplace IDs, separate them with a comma (,). (i.e. A2EUQ1WTGCTBG2)|amazonmws_marketplace_id|amazon_m_w_s_marketplace_id|
|**--type-properties-seller-id**|any|The Amazon seller ID.|amazonmws_seller_id|amazon_m_w_s_seller_id|
|**--type-properties-access-key-id**|any|The access key id used to access data.|amazonmws_access_key_id|amazon_m_w_s_access_key_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|amazonmws_connect_via|amazon_m_w_s_connect_via|
|**--description**|string|Linked service description.|amazonmws_description|amazon_m_w_s_description|
|**--parameters**|dictionary|Parameters for linked service.|amazonmws_parameters|amazon_m_w_s_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|amazonmws_annotations|amazon_m_w_s_annotations|
|**--type-properties-mws-auth-token**|object|The Amazon MWS authentication token.|amazonmws_mws_auth_token|amazon_m_w_s_mws_auth_token|
|**--type-properties-secret-key**|object|The secret key used to access data.|amazonmws_secret_key|amazon_m_w_s_secret_key|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|amazonmws_use_encrypted_endpoints|amazon_m_w_s_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|amazonmws_use_host_verification|amazon_m_w_s_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|amazonmws_use_peer_verification|amazon_m_w_s_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|amazonmws_encrypted_credential|amazon_m_w_s_encrypted_credential|
### datafactory linked-service amazon-redshift create

amazon-redshift create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|amazonredshift_type|amazon_redshift_type|
|**--type-properties-server**|any|The name of the Amazon Redshift server. Type: string (or Expression with resultType string).|amazonredshift_server|amazon_redshift_server|
|**--type-properties-database**|any|The database name of the Amazon Redshift source. Type: string (or Expression with resultType string).|amazonredshift_database|amazon_redshift_database|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|amazonredshift_connect_via|amazon_redshift_connect_via|
|**--description**|string|Linked service description.|amazonredshift_description|amazon_redshift_description|
|**--parameters**|dictionary|Parameters for linked service.|amazonredshift_parameters|amazon_redshift_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|amazonredshift_annotations|amazon_redshift_annotations|
|**--type-properties-username**|any|The username of the Amazon Redshift source. Type: string (or Expression with resultType string).|amazonredshift_username|amazon_redshift_username|
|**--type-properties-password**|object|The password of the Amazon Redshift source.|amazonredshift_password|amazon_redshift_password|
|**--type-properties-port**|any|The TCP port number that the Amazon Redshift server uses to listen for client connections. The default value is 5439. Type: integer (or Expression with resultType integer).|amazonredshift_port|amazon_redshift_port|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|amazonredshift_encrypted_credential|amazon_redshift_encrypted_credential|
### datafactory linked-service amazon-redshift update

amazon-redshift create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|amazonredshift_type|amazon_redshift_type|
|**--type-properties-server**|any|The name of the Amazon Redshift server. Type: string (or Expression with resultType string).|amazonredshift_server|amazon_redshift_server|
|**--type-properties-database**|any|The database name of the Amazon Redshift source. Type: string (or Expression with resultType string).|amazonredshift_database|amazon_redshift_database|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|amazonredshift_connect_via|amazon_redshift_connect_via|
|**--description**|string|Linked service description.|amazonredshift_description|amazon_redshift_description|
|**--parameters**|dictionary|Parameters for linked service.|amazonredshift_parameters|amazon_redshift_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|amazonredshift_annotations|amazon_redshift_annotations|
|**--type-properties-username**|any|The username of the Amazon Redshift source. Type: string (or Expression with resultType string).|amazonredshift_username|amazon_redshift_username|
|**--type-properties-password**|object|The password of the Amazon Redshift source.|amazonredshift_password|amazon_redshift_password|
|**--type-properties-port**|any|The TCP port number that the Amazon Redshift server uses to listen for client connections. The default value is 5439. Type: integer (or Expression with resultType integer).|amazonredshift_port|amazon_redshift_port|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|amazonredshift_encrypted_credential|amazon_redshift_encrypted_credential|
### datafactory linked-service amazon-s3 create

amazon-s3 create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|amazons3_type|amazon_s3_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|amazons3_connect_via|amazon_s3_connect_via|
|**--description**|string|Linked service description.|amazons3_description|amazon_s3_description|
|**--parameters**|dictionary|Parameters for linked service.|amazons3_parameters|amazon_s3_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|amazons3_annotations|amazon_s3_annotations|
|**--type-properties-access-key-id**|any|The access key identifier of the Amazon S3 Identity and Access Management (IAM) user. Type: string (or Expression with resultType string).|amazons3_access_key_id|amazon_s3_access_key_id|
|**--type-properties-secret-access-key**|object|The secret access key of the Amazon S3 Identity and Access Management (IAM) user.|amazons3_secret_access_key|amazon_s3_secret_access_key|
|**--type-properties-service-url**|any|This value specifies the endpoint to access with the S3 Connector. This is an optional property; change it only if you want to try a different service endpoint or want to switch between https and http. Type: string (or Expression with resultType string).|amazons3_service_url|amazon_s3_service_url|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|amazons3_encrypted_credential|amazon_s3_encrypted_credential|
### datafactory linked-service amazon-s3 update

amazon-s3 create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|amazons3_type|amazon_s3_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|amazons3_connect_via|amazon_s3_connect_via|
|**--description**|string|Linked service description.|amazons3_description|amazon_s3_description|
|**--parameters**|dictionary|Parameters for linked service.|amazons3_parameters|amazon_s3_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|amazons3_annotations|amazon_s3_annotations|
|**--type-properties-access-key-id**|any|The access key identifier of the Amazon S3 Identity and Access Management (IAM) user. Type: string (or Expression with resultType string).|amazons3_access_key_id|amazon_s3_access_key_id|
|**--type-properties-secret-access-key**|object|The secret access key of the Amazon S3 Identity and Access Management (IAM) user.|amazons3_secret_access_key|amazon_s3_secret_access_key|
|**--type-properties-service-url**|any|This value specifies the endpoint to access with the S3 Connector. This is an optional property; change it only if you want to try a different service endpoint or want to switch between https and http. Type: string (or Expression with resultType string).|amazons3_service_url|amazon_s3_service_url|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|amazons3_encrypted_credential|amazon_s3_encrypted_credential|
### datafactory linked-service azure-batch create

azure-batch create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azurebatch_type|azure_batch_type|
|**--type-properties-account-name**|any|The Azure Batch account name. Type: string (or Expression with resultType string).|azurebatch_account_name|azure_batch_account_name|
|**--type-properties-batch-uri**|any|The Azure Batch URI. Type: string (or Expression with resultType string).|azurebatch_batch_uri|azure_batch_batch_uri|
|**--type-properties-pool-name**|any|The Azure Batch pool name. Type: string (or Expression with resultType string).|azurebatch_pool_name|azure_batch_pool_name|
|**--type-properties-linked-service-name**|object|The Azure Storage linked service reference.|azurebatch_linked_service_name|azure_batch_linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azurebatch_connect_via|azure_batch_connect_via|
|**--description**|string|Linked service description.|azurebatch_description|azure_batch_description|
|**--parameters**|dictionary|Parameters for linked service.|azurebatch_parameters|azure_batch_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azurebatch_annotations|azure_batch_annotations|
|**--type-properties-access-key**|object|The Azure Batch account access key.|azurebatch_access_key|azure_batch_access_key|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azurebatch_encrypted_credential|azure_batch_encrypted_credential|
### datafactory linked-service azure-batch update

azure-batch create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azurebatch_type|azure_batch_type|
|**--type-properties-account-name**|any|The Azure Batch account name. Type: string (or Expression with resultType string).|azurebatch_account_name|azure_batch_account_name|
|**--type-properties-batch-uri**|any|The Azure Batch URI. Type: string (or Expression with resultType string).|azurebatch_batch_uri|azure_batch_batch_uri|
|**--type-properties-pool-name**|any|The Azure Batch pool name. Type: string (or Expression with resultType string).|azurebatch_pool_name|azure_batch_pool_name|
|**--type-properties-linked-service-name**|object|The Azure Storage linked service reference.|azurebatch_linked_service_name|azure_batch_linked_service_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azurebatch_connect_via|azure_batch_connect_via|
|**--description**|string|Linked service description.|azurebatch_description|azure_batch_description|
|**--parameters**|dictionary|Parameters for linked service.|azurebatch_parameters|azure_batch_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azurebatch_annotations|azure_batch_annotations|
|**--type-properties-access-key**|object|The Azure Batch account access key.|azurebatch_access_key|azure_batch_access_key|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azurebatch_encrypted_credential|azure_batch_encrypted_credential|
### datafactory linked-service azure-blob-f-s create

azure-blob-f-s create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azureblobfs_type|azure_blob_f_s_type|
|**--type-properties-url**|any|Endpoint for the Azure Data Lake Storage Gen2 service. Type: string (or Expression with resultType string).|azureblobfs_url|azure_blob_f_s_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azureblobfs_connect_via|azure_blob_f_s_connect_via|
|**--description**|string|Linked service description.|azureblobfs_description|azure_blob_f_s_description|
|**--parameters**|dictionary|Parameters for linked service.|azureblobfs_parameters|azure_blob_f_s_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azureblobfs_annotations|azure_blob_f_s_annotations|
|**--type-properties-account-key**|any|Account key for the Azure Data Lake Storage Gen2 service. Type: string (or Expression with resultType string).|azureblobfs_account_key|azure_blob_f_s_account_key|
|**--type-properties-service-principal-id**|any|The ID of the application used to authenticate against the Azure Data Lake Storage Gen2 account. Type: string (or Expression with resultType string).|azureblobfs_service_principal_id|azure_blob_f_s_service_principal_id|
|**--type-properties-service-principal-key**|object|The Key of the application used to authenticate against the Azure Data Lake Storage Gen2 account.|azureblobfs_service_principal_key|azure_blob_f_s_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azureblobfs_tenant|azure_blob_f_s_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azureblobfs_encrypted_credential|azure_blob_f_s_encrypted_credential|
### datafactory linked-service azure-blob-f-s update

azure-blob-f-s create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azureblobfs_type|azure_blob_f_s_type|
|**--type-properties-url**|any|Endpoint for the Azure Data Lake Storage Gen2 service. Type: string (or Expression with resultType string).|azureblobfs_url|azure_blob_f_s_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azureblobfs_connect_via|azure_blob_f_s_connect_via|
|**--description**|string|Linked service description.|azureblobfs_description|azure_blob_f_s_description|
|**--parameters**|dictionary|Parameters for linked service.|azureblobfs_parameters|azure_blob_f_s_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azureblobfs_annotations|azure_blob_f_s_annotations|
|**--type-properties-account-key**|any|Account key for the Azure Data Lake Storage Gen2 service. Type: string (or Expression with resultType string).|azureblobfs_account_key|azure_blob_f_s_account_key|
|**--type-properties-service-principal-id**|any|The ID of the application used to authenticate against the Azure Data Lake Storage Gen2 account. Type: string (or Expression with resultType string).|azureblobfs_service_principal_id|azure_blob_f_s_service_principal_id|
|**--type-properties-service-principal-key**|object|The Key of the application used to authenticate against the Azure Data Lake Storage Gen2 account.|azureblobfs_service_principal_key|azure_blob_f_s_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azureblobfs_tenant|azure_blob_f_s_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azureblobfs_encrypted_credential|azure_blob_f_s_encrypted_credential|
### datafactory linked-service azure-blob-storage create

azure-blob-storage create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azureblobstorage_type|azure_blob_storage_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azureblobstorage_connect_via|azure_blob_storage_connect_via|
|**--description**|string|Linked service description.|azureblobstorage_description|azure_blob_storage_description|
|**--parameters**|dictionary|Parameters for linked service.|azureblobstorage_parameters|azure_blob_storage_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azureblobstorage_annotations|azure_blob_storage_annotations|
|**--type-properties-connection-string**|any|The connection string. It is mutually exclusive with sasUri, serviceEndpoint property. Type: string, SecureString or AzureKeyVaultSecretReference.|azureblobstorage_connection_string|azure_blob_storage_connection_string|
|**--type-properties-account-key**|object|The Azure key vault secret reference of accountKey in connection string.|azureblobstorage_account_key|azure_blob_storage_account_key|
|**--type-properties-sas-uri**|any|SAS URI of the Azure Blob Storage resource. It is mutually exclusive with connectionString, serviceEndpoint property. Type: string, SecureString or AzureKeyVaultSecretReference.|azureblobstorage_sas_uri|azure_blob_storage_sas_uri|
|**--type-properties-sas-token**|object|The Azure key vault secret reference of sasToken in sas uri.|azureblobstorage_sas_token|azure_blob_storage_sas_token|
|**--type-properties-service-endpoint**|string|Blob service endpoint of the Azure Blob Storage resource. It is mutually exclusive with connectionString, sasUri property.|azureblobstorage_service_endpoint|azure_blob_storage_service_endpoint|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against Azure SQL Data Warehouse. Type: string (or Expression with resultType string).|azureblobstorage_service_principal_id|azure_blob_storage_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against Azure SQL Data Warehouse.|azureblobstorage_service_principal_key|azure_blob_storage_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azureblobstorage_tenant|azure_blob_storage_tenant|
|**--type-properties-encrypted-credential**|string|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azureblobstorage_encrypted_credential|azure_blob_storage_encrypted_credential|
### datafactory linked-service azure-blob-storage update

azure-blob-storage create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azureblobstorage_type|azure_blob_storage_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azureblobstorage_connect_via|azure_blob_storage_connect_via|
|**--description**|string|Linked service description.|azureblobstorage_description|azure_blob_storage_description|
|**--parameters**|dictionary|Parameters for linked service.|azureblobstorage_parameters|azure_blob_storage_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azureblobstorage_annotations|azure_blob_storage_annotations|
|**--type-properties-connection-string**|any|The connection string. It is mutually exclusive with sasUri, serviceEndpoint property. Type: string, SecureString or AzureKeyVaultSecretReference.|azureblobstorage_connection_string|azure_blob_storage_connection_string|
|**--type-properties-account-key**|object|The Azure key vault secret reference of accountKey in connection string.|azureblobstorage_account_key|azure_blob_storage_account_key|
|**--type-properties-sas-uri**|any|SAS URI of the Azure Blob Storage resource. It is mutually exclusive with connectionString, serviceEndpoint property. Type: string, SecureString or AzureKeyVaultSecretReference.|azureblobstorage_sas_uri|azure_blob_storage_sas_uri|
|**--type-properties-sas-token**|object|The Azure key vault secret reference of sasToken in sas uri.|azureblobstorage_sas_token|azure_blob_storage_sas_token|
|**--type-properties-service-endpoint**|string|Blob service endpoint of the Azure Blob Storage resource. It is mutually exclusive with connectionString, sasUri property.|azureblobstorage_service_endpoint|azure_blob_storage_service_endpoint|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against Azure SQL Data Warehouse. Type: string (or Expression with resultType string).|azureblobstorage_service_principal_id|azure_blob_storage_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against Azure SQL Data Warehouse.|azureblobstorage_service_principal_key|azure_blob_storage_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azureblobstorage_tenant|azure_blob_storage_tenant|
|**--type-properties-encrypted-credential**|string|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azureblobstorage_encrypted_credential|azure_blob_storage_encrypted_credential|
### datafactory linked-service azure-data-explorer create

azure-data-explorer create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuredataexplorer_type|azure_data_explorer_type|
|**--type-properties-endpoint**|any|The endpoint of Azure Data Explorer (the engine's endpoint). URL will be in the format https://:code:`<clusterName>`.:code:`<regionName>`.kusto.windows.net. Type: string (or Expression with resultType string)|azuredataexplorer_endpoint|azure_data_explorer_endpoint|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against Azure Data Explorer. Type: string (or Expression with resultType string).|azuredataexplorer_service_principal_id|azure_data_explorer_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against Kusto.|azuredataexplorer_service_principal_key|azure_data_explorer_service_principal_key|
|**--type-properties-database**|any|Database name for connection. Type: string (or Expression with resultType string).|azuredataexplorer_database|azure_data_explorer_database|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azuredataexplorer_tenant|azure_data_explorer_tenant|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuredataexplorer_connect_via|azure_data_explorer_connect_via|
|**--description**|string|Linked service description.|azuredataexplorer_description|azure_data_explorer_description|
|**--parameters**|dictionary|Parameters for linked service.|azuredataexplorer_parameters|azure_data_explorer_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuredataexplorer_annotations|azure_data_explorer_annotations|
### datafactory linked-service azure-data-explorer update

azure-data-explorer create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuredataexplorer_type|azure_data_explorer_type|
|**--type-properties-endpoint**|any|The endpoint of Azure Data Explorer (the engine's endpoint). URL will be in the format https://:code:`<clusterName>`.:code:`<regionName>`.kusto.windows.net. Type: string (or Expression with resultType string)|azuredataexplorer_endpoint|azure_data_explorer_endpoint|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against Azure Data Explorer. Type: string (or Expression with resultType string).|azuredataexplorer_service_principal_id|azure_data_explorer_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against Kusto.|azuredataexplorer_service_principal_key|azure_data_explorer_service_principal_key|
|**--type-properties-database**|any|Database name for connection. Type: string (or Expression with resultType string).|azuredataexplorer_database|azure_data_explorer_database|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azuredataexplorer_tenant|azure_data_explorer_tenant|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuredataexplorer_connect_via|azure_data_explorer_connect_via|
|**--description**|string|Linked service description.|azuredataexplorer_description|azure_data_explorer_description|
|**--parameters**|dictionary|Parameters for linked service.|azuredataexplorer_parameters|azure_data_explorer_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuredataexplorer_annotations|azure_data_explorer_annotations|
### datafactory linked-service azure-data-lake-analytics create

azure-data-lake-analytics create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuredatalakeanalytics_type|azure_data_lake_analytics_type|
|**--type-properties-account-name**|any|The Azure Data Lake Analytics account name. Type: string (or Expression with resultType string).|azuredatalakeanalytics_account_name|azure_data_lake_analytics_account_name|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azuredatalakeanalytics_tenant|azure_data_lake_analytics_tenant|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuredatalakeanalytics_connect_via|azure_data_lake_analytics_connect_via|
|**--description**|string|Linked service description.|azuredatalakeanalytics_description|azure_data_lake_analytics_description|
|**--parameters**|dictionary|Parameters for linked service.|azuredatalakeanalytics_parameters|azure_data_lake_analytics_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuredatalakeanalytics_annotations|azure_data_lake_analytics_annotations|
|**--type-properties-service-principal-id**|any|The ID of the application used to authenticate against the Azure Data Lake Analytics account. Type: string (or Expression with resultType string).|azuredatalakeanalytics_service_principal_id|azure_data_lake_analytics_service_principal_id|
|**--type-properties-service-principal-key**|object|The Key of the application used to authenticate against the Azure Data Lake Analytics account.|azuredatalakeanalytics_service_principal_key|azure_data_lake_analytics_service_principal_key|
|**--type-properties-subscription-id**|any|Data Lake Analytics account subscription ID (if different from Data Factory account). Type: string (or Expression with resultType string).|azuredatalakeanalytics_subscription_id|azure_data_lake_analytics_subscription_id|
|**--type-properties-resource-group-name**|any|Data Lake Analytics account resource group name (if different from Data Factory account). Type: string (or Expression with resultType string).|azuredatalakeanalytics_resource_group_name|azure_data_lake_analytics_resource_group_name|
|**--type-properties-data-lake-analytics-uri**|any|Azure Data Lake Analytics URI Type: string (or Expression with resultType string).|azuredatalakeanalytics_data_lake_analytics_uri|azure_data_lake_analytics_data_lake_analytics_uri|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuredatalakeanalytics_encrypted_credential|azure_data_lake_analytics_encrypted_credential|
### datafactory linked-service azure-data-lake-analytics update

azure-data-lake-analytics create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuredatalakeanalytics_type|azure_data_lake_analytics_type|
|**--type-properties-account-name**|any|The Azure Data Lake Analytics account name. Type: string (or Expression with resultType string).|azuredatalakeanalytics_account_name|azure_data_lake_analytics_account_name|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azuredatalakeanalytics_tenant|azure_data_lake_analytics_tenant|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuredatalakeanalytics_connect_via|azure_data_lake_analytics_connect_via|
|**--description**|string|Linked service description.|azuredatalakeanalytics_description|azure_data_lake_analytics_description|
|**--parameters**|dictionary|Parameters for linked service.|azuredatalakeanalytics_parameters|azure_data_lake_analytics_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuredatalakeanalytics_annotations|azure_data_lake_analytics_annotations|
|**--type-properties-service-principal-id**|any|The ID of the application used to authenticate against the Azure Data Lake Analytics account. Type: string (or Expression with resultType string).|azuredatalakeanalytics_service_principal_id|azure_data_lake_analytics_service_principal_id|
|**--type-properties-service-principal-key**|object|The Key of the application used to authenticate against the Azure Data Lake Analytics account.|azuredatalakeanalytics_service_principal_key|azure_data_lake_analytics_service_principal_key|
|**--type-properties-subscription-id**|any|Data Lake Analytics account subscription ID (if different from Data Factory account). Type: string (or Expression with resultType string).|azuredatalakeanalytics_subscription_id|azure_data_lake_analytics_subscription_id|
|**--type-properties-resource-group-name**|any|Data Lake Analytics account resource group name (if different from Data Factory account). Type: string (or Expression with resultType string).|azuredatalakeanalytics_resource_group_name|azure_data_lake_analytics_resource_group_name|
|**--type-properties-data-lake-analytics-uri**|any|Azure Data Lake Analytics URI Type: string (or Expression with resultType string).|azuredatalakeanalytics_data_lake_analytics_uri|azure_data_lake_analytics_data_lake_analytics_uri|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuredatalakeanalytics_encrypted_credential|azure_data_lake_analytics_encrypted_credential|
### datafactory linked-service azure-data-lake-store create

azure-data-lake-store create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuredatalakestore_type|azure_data_lake_store_type|
|**--type-properties-data-lake-store-uri**|any|Data Lake Store service URI. Type: string (or Expression with resultType string).|azuredatalakestore_data_lake_store_uri|azure_data_lake_store_data_lake_store_uri|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuredatalakestore_connect_via|azure_data_lake_store_connect_via|
|**--description**|string|Linked service description.|azuredatalakestore_description|azure_data_lake_store_description|
|**--parameters**|dictionary|Parameters for linked service.|azuredatalakestore_parameters|azure_data_lake_store_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuredatalakestore_annotations|azure_data_lake_store_annotations|
|**--type-properties-service-principal-id**|any|The ID of the application used to authenticate against the Azure Data Lake Store account. Type: string (or Expression with resultType string).|azuredatalakestore_service_principal_id|azure_data_lake_store_service_principal_id|
|**--type-properties-service-principal-key**|object|The Key of the application used to authenticate against the Azure Data Lake Store account.|azuredatalakestore_service_principal_key|azure_data_lake_store_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azuredatalakestore_tenant|azure_data_lake_store_tenant|
|**--type-properties-account-name**|any|Data Lake Store account name. Type: string (or Expression with resultType string).|azuredatalakestore_account_name|azure_data_lake_store_account_name|
|**--type-properties-subscription-id**|any|Data Lake Store account subscription ID (if different from Data Factory account). Type: string (or Expression with resultType string).|azuredatalakestore_subscription_id|azure_data_lake_store_subscription_id|
|**--type-properties-resource-group-name**|any|Data Lake Store account resource group name (if different from Data Factory account). Type: string (or Expression with resultType string).|azuredatalakestore_resource_group_name|azure_data_lake_store_resource_group_name|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuredatalakestore_encrypted_credential|azure_data_lake_store_encrypted_credential|
### datafactory linked-service azure-data-lake-store update

azure-data-lake-store create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuredatalakestore_type|azure_data_lake_store_type|
|**--type-properties-data-lake-store-uri**|any|Data Lake Store service URI. Type: string (or Expression with resultType string).|azuredatalakestore_data_lake_store_uri|azure_data_lake_store_data_lake_store_uri|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuredatalakestore_connect_via|azure_data_lake_store_connect_via|
|**--description**|string|Linked service description.|azuredatalakestore_description|azure_data_lake_store_description|
|**--parameters**|dictionary|Parameters for linked service.|azuredatalakestore_parameters|azure_data_lake_store_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuredatalakestore_annotations|azure_data_lake_store_annotations|
|**--type-properties-service-principal-id**|any|The ID of the application used to authenticate against the Azure Data Lake Store account. Type: string (or Expression with resultType string).|azuredatalakestore_service_principal_id|azure_data_lake_store_service_principal_id|
|**--type-properties-service-principal-key**|object|The Key of the application used to authenticate against the Azure Data Lake Store account.|azuredatalakestore_service_principal_key|azure_data_lake_store_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azuredatalakestore_tenant|azure_data_lake_store_tenant|
|**--type-properties-account-name**|any|Data Lake Store account name. Type: string (or Expression with resultType string).|azuredatalakestore_account_name|azure_data_lake_store_account_name|
|**--type-properties-subscription-id**|any|Data Lake Store account subscription ID (if different from Data Factory account). Type: string (or Expression with resultType string).|azuredatalakestore_subscription_id|azure_data_lake_store_subscription_id|
|**--type-properties-resource-group-name**|any|Data Lake Store account resource group name (if different from Data Factory account). Type: string (or Expression with resultType string).|azuredatalakestore_resource_group_name|azure_data_lake_store_resource_group_name|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuredatalakestore_encrypted_credential|azure_data_lake_store_encrypted_credential|
### datafactory linked-service azure-databricks create

azure-databricks create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuredatabricks_type|azure_databricks_type|
|**--type-properties-domain**|any|:code:`<REGION>`.azuredatabricks.net, domain name of your Databricks deployment. Type: string (or Expression with resultType string).|azuredatabricks_domain|azure_databricks_domain|
|**--type-properties-access-token**|object|Access token for databricks REST API. Refer to https://docs.azuredatabricks.net/api/latest/authentication.html. Type: string (or Expression with resultType string).|azuredatabricks_access_token|azure_databricks_access_token|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuredatabricks_connect_via|azure_databricks_connect_via|
|**--description**|string|Linked service description.|azuredatabricks_description|azure_databricks_description|
|**--parameters**|dictionary|Parameters for linked service.|azuredatabricks_parameters|azure_databricks_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuredatabricks_annotations|azure_databricks_annotations|
|**--type-properties-existing-cluster-id**|any|The id of an existing interactive cluster that will be used for all runs of this activity. Type: string (or Expression with resultType string).|azuredatabricks_existing_cluster_id|azure_databricks_existing_cluster_id|
|**--type-properties-instance-pool-id**|any|The id of an existing instance pool that will be used for all runs of this activity. Type: string (or Expression with resultType string).|azuredatabricks_instance_pool_id|azure_databricks_instance_pool_id|
|**--type-properties-new-cluster-version**|any|If not using an existing interactive cluster, this specifies the Spark version of a new job cluster or instance pool nodes created for each run of this activity. Required if instancePoolId is specified. Type: string (or Expression with resultType string).|azuredatabricks_new_cluster_version|azure_databricks_new_cluster_version|
|**--type-properties-new-cluster-num-of-worker**|any|If not using an existing interactive cluster, this specifies the number of worker nodes to use for the new job cluster or instance pool. For new job clusters, this a string-formatted Int32, like '1' means numOfWorker is 1 or '1:10' means auto-scale from 1 (min) to 10 (max). For instance pools, this is a string-formatted Int32, and can only specify a fixed number of worker nodes, such as '2'. Required if newClusterVersion is specified. Type: string (or Expression with resultType string).|azuredatabricks_new_cluster_num_of_worker|azure_databricks_new_cluster_num_of_worker|
|**--type-properties-new-cluster-node-type**|any|The node type of the new job cluster. This property is required if newClusterVersion is specified and instancePoolId is not specified. If instancePoolId is specified, this property is ignored. Type: string (or Expression with resultType string).|azuredatabricks_new_cluster_node_type|azure_databricks_new_cluster_node_type|
|**--type-properties-new-cluster-spark-conf**|dictionary|A set of optional, user-specified Spark configuration key-value pairs.|azuredatabricks_new_cluster_spark_conf|azure_databricks_new_cluster_spark_conf|
|**--type-properties-new-cluster-spark-env-vars**|dictionary|A set of optional, user-specified Spark environment variables key-value pairs.|azuredatabricks_new_cluster_spark_env_vars|azure_databricks_new_cluster_spark_env_vars|
|**--type-properties-new-cluster-custom-tags**|dictionary|Additional tags for cluster resources. This property is ignored in instance pool configurations.|azuredatabricks_new_cluster_custom_tags|azure_databricks_new_cluster_custom_tags|
|**--type-properties-new-cluster-driver-node-type**|any|The driver node type for the new job cluster. This property is ignored in instance pool configurations. Type: string (or Expression with resultType string).|azuredatabricks_new_cluster_driver_node_type|azure_databricks_new_cluster_driver_node_type|
|**--type-properties-new-cluster-init-scripts**|any|User-defined initialization scripts for the new cluster. Type: array of strings (or Expression with resultType array of strings).|azuredatabricks_new_cluster_init_scripts|azure_databricks_new_cluster_init_scripts|
|**--type-properties-new-cluster-enable-elastic-disk**|any|Enable the elastic disk on the new cluster. This property is now ignored, and takes the default elastic disk behavior in Databricks (elastic disks are always enabled). Type: boolean (or Expression with resultType boolean).|azuredatabricks_new_cluster_enable_elastic_disk|azure_databricks_new_cluster_enable_elastic_disk|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuredatabricks_encrypted_credential|azure_databricks_encrypted_credential|
### datafactory linked-service azure-databricks update

azure-databricks create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuredatabricks_type|azure_databricks_type|
|**--type-properties-domain**|any|:code:`<REGION>`.azuredatabricks.net, domain name of your Databricks deployment. Type: string (or Expression with resultType string).|azuredatabricks_domain|azure_databricks_domain|
|**--type-properties-access-token**|object|Access token for databricks REST API. Refer to https://docs.azuredatabricks.net/api/latest/authentication.html. Type: string (or Expression with resultType string).|azuredatabricks_access_token|azure_databricks_access_token|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuredatabricks_connect_via|azure_databricks_connect_via|
|**--description**|string|Linked service description.|azuredatabricks_description|azure_databricks_description|
|**--parameters**|dictionary|Parameters for linked service.|azuredatabricks_parameters|azure_databricks_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuredatabricks_annotations|azure_databricks_annotations|
|**--type-properties-existing-cluster-id**|any|The id of an existing interactive cluster that will be used for all runs of this activity. Type: string (or Expression with resultType string).|azuredatabricks_existing_cluster_id|azure_databricks_existing_cluster_id|
|**--type-properties-instance-pool-id**|any|The id of an existing instance pool that will be used for all runs of this activity. Type: string (or Expression with resultType string).|azuredatabricks_instance_pool_id|azure_databricks_instance_pool_id|
|**--type-properties-new-cluster-version**|any|If not using an existing interactive cluster, this specifies the Spark version of a new job cluster or instance pool nodes created for each run of this activity. Required if instancePoolId is specified. Type: string (or Expression with resultType string).|azuredatabricks_new_cluster_version|azure_databricks_new_cluster_version|
|**--type-properties-new-cluster-num-of-worker**|any|If not using an existing interactive cluster, this specifies the number of worker nodes to use for the new job cluster or instance pool. For new job clusters, this a string-formatted Int32, like '1' means numOfWorker is 1 or '1:10' means auto-scale from 1 (min) to 10 (max). For instance pools, this is a string-formatted Int32, and can only specify a fixed number of worker nodes, such as '2'. Required if newClusterVersion is specified. Type: string (or Expression with resultType string).|azuredatabricks_new_cluster_num_of_worker|azure_databricks_new_cluster_num_of_worker|
|**--type-properties-new-cluster-node-type**|any|The node type of the new job cluster. This property is required if newClusterVersion is specified and instancePoolId is not specified. If instancePoolId is specified, this property is ignored. Type: string (or Expression with resultType string).|azuredatabricks_new_cluster_node_type|azure_databricks_new_cluster_node_type|
|**--type-properties-new-cluster-spark-conf**|dictionary|A set of optional, user-specified Spark configuration key-value pairs.|azuredatabricks_new_cluster_spark_conf|azure_databricks_new_cluster_spark_conf|
|**--type-properties-new-cluster-spark-env-vars**|dictionary|A set of optional, user-specified Spark environment variables key-value pairs.|azuredatabricks_new_cluster_spark_env_vars|azure_databricks_new_cluster_spark_env_vars|
|**--type-properties-new-cluster-custom-tags**|dictionary|Additional tags for cluster resources. This property is ignored in instance pool configurations.|azuredatabricks_new_cluster_custom_tags|azure_databricks_new_cluster_custom_tags|
|**--type-properties-new-cluster-driver-node-type**|any|The driver node type for the new job cluster. This property is ignored in instance pool configurations. Type: string (or Expression with resultType string).|azuredatabricks_new_cluster_driver_node_type|azure_databricks_new_cluster_driver_node_type|
|**--type-properties-new-cluster-init-scripts**|any|User-defined initialization scripts for the new cluster. Type: array of strings (or Expression with resultType array of strings).|azuredatabricks_new_cluster_init_scripts|azure_databricks_new_cluster_init_scripts|
|**--type-properties-new-cluster-enable-elastic-disk**|any|Enable the elastic disk on the new cluster. This property is now ignored, and takes the default elastic disk behavior in Databricks (elastic disks are always enabled). Type: boolean (or Expression with resultType boolean).|azuredatabricks_new_cluster_enable_elastic_disk|azure_databricks_new_cluster_enable_elastic_disk|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuredatabricks_encrypted_credential|azure_databricks_encrypted_credential|
### datafactory linked-service azure-file-storage create

azure-file-storage create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azurefilestorage_type|azure_file_storage_type|
|**--type-properties-host**|any|Host name of the server. Type: string (or Expression with resultType string).|azurefilestorage_host|azure_file_storage_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azurefilestorage_connect_via|azure_file_storage_connect_via|
|**--description**|string|Linked service description.|azurefilestorage_description|azure_file_storage_description|
|**--parameters**|dictionary|Parameters for linked service.|azurefilestorage_parameters|azure_file_storage_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azurefilestorage_annotations|azure_file_storage_annotations|
|**--type-properties-user-id**|any|User ID to logon the server. Type: string (or Expression with resultType string).|azurefilestorage_user_id|azure_file_storage_user_id|
|**--type-properties-password**|object|Password to logon the server.|azurefilestorage_password|azure_file_storage_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azurefilestorage_encrypted_credential|azure_file_storage_encrypted_credential|
### datafactory linked-service azure-file-storage update

azure-file-storage create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azurefilestorage_type|azure_file_storage_type|
|**--type-properties-host**|any|Host name of the server. Type: string (or Expression with resultType string).|azurefilestorage_host|azure_file_storage_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azurefilestorage_connect_via|azure_file_storage_connect_via|
|**--description**|string|Linked service description.|azurefilestorage_description|azure_file_storage_description|
|**--parameters**|dictionary|Parameters for linked service.|azurefilestorage_parameters|azure_file_storage_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azurefilestorage_annotations|azure_file_storage_annotations|
|**--type-properties-user-id**|any|User ID to logon the server. Type: string (or Expression with resultType string).|azurefilestorage_user_id|azure_file_storage_user_id|
|**--type-properties-password**|object|Password to logon the server.|azurefilestorage_password|azure_file_storage_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azurefilestorage_encrypted_credential|azure_file_storage_encrypted_credential|
### datafactory linked-service azure-function create

azure-function create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azurefunction_type|azure_function_type|
|**--type-properties-function-app-url**|any|The endpoint of the Azure Function App. URL will be in the format https://:code:`<accountName>`.azurewebsites.net.|azurefunction_function_app_url|azure_function_function_app_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azurefunction_connect_via|azure_function_connect_via|
|**--description**|string|Linked service description.|azurefunction_description|azure_function_description|
|**--parameters**|dictionary|Parameters for linked service.|azurefunction_parameters|azure_function_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azurefunction_annotations|azure_function_annotations|
|**--type-properties-function-key**|object|Function or Host key for Azure Function App.|azurefunction_function_key|azure_function_function_key|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azurefunction_encrypted_credential|azure_function_encrypted_credential|
### datafactory linked-service azure-function update

azure-function create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azurefunction_type|azure_function_type|
|**--type-properties-function-app-url**|any|The endpoint of the Azure Function App. URL will be in the format https://:code:`<accountName>`.azurewebsites.net.|azurefunction_function_app_url|azure_function_function_app_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azurefunction_connect_via|azure_function_connect_via|
|**--description**|string|Linked service description.|azurefunction_description|azure_function_description|
|**--parameters**|dictionary|Parameters for linked service.|azurefunction_parameters|azure_function_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azurefunction_annotations|azure_function_annotations|
|**--type-properties-function-key**|object|Function or Host key for Azure Function App.|azurefunction_function_key|azure_function_function_key|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azurefunction_encrypted_credential|azure_function_encrypted_credential|
### datafactory linked-service azure-key-vault create

azure-key-vault create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azurekeyvault_type|azure_key_vault_type|
|**--type-properties-base-url**|any|The base URL of the Azure Key Vault. e.g. https://myakv.vault.azure.net Type: string (or Expression with resultType string).|azurekeyvault_base_url|azure_key_vault_base_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azurekeyvault_connect_via|azure_key_vault_connect_via|
|**--description**|string|Linked service description.|azurekeyvault_description|azure_key_vault_description|
|**--parameters**|dictionary|Parameters for linked service.|azurekeyvault_parameters|azure_key_vault_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azurekeyvault_annotations|azure_key_vault_annotations|
### datafactory linked-service azure-key-vault update

azure-key-vault create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azurekeyvault_type|azure_key_vault_type|
|**--type-properties-base-url**|any|The base URL of the Azure Key Vault. e.g. https://myakv.vault.azure.net Type: string (or Expression with resultType string).|azurekeyvault_base_url|azure_key_vault_base_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azurekeyvault_connect_via|azure_key_vault_connect_via|
|**--description**|string|Linked service description.|azurekeyvault_description|azure_key_vault_description|
|**--parameters**|dictionary|Parameters for linked service.|azurekeyvault_parameters|azure_key_vault_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azurekeyvault_annotations|azure_key_vault_annotations|
### datafactory linked-service azure-m-l create

azure-m-l create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azureml_type|azure_m_l_type|
|**--type-properties-ml-endpoint**|any|The Batch Execution REST URL for an Azure ML Studio Web Service endpoint. Type: string (or Expression with resultType string).|azureml_ml_endpoint|azure_m_l_ml_endpoint|
|**--type-properties-api-key**|object|The API key for accessing the Azure ML model endpoint.|azureml_api_key|azure_m_l_api_key|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azureml_connect_via|azure_m_l_connect_via|
|**--description**|string|Linked service description.|azureml_description|azure_m_l_description|
|**--parameters**|dictionary|Parameters for linked service.|azureml_parameters|azure_m_l_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azureml_annotations|azure_m_l_annotations|
|**--type-properties-update-resource-endpoint**|any|The Update Resource REST URL for an Azure ML Studio Web Service endpoint. Type: string (or Expression with resultType string).|azureml_update_resource_endpoint|azure_m_l_update_resource_endpoint|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against the ARM-based updateResourceEndpoint of an Azure ML Studio web service. Type: string (or Expression with resultType string).|azureml_service_principal_id|azure_m_l_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against the ARM-based updateResourceEndpoint of an Azure ML Studio web service.|azureml_service_principal_key|azure_m_l_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azureml_tenant|azure_m_l_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azureml_encrypted_credential|azure_m_l_encrypted_credential|
### datafactory linked-service azure-m-l update

azure-m-l create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azureml_type|azure_m_l_type|
|**--type-properties-ml-endpoint**|any|The Batch Execution REST URL for an Azure ML Studio Web Service endpoint. Type: string (or Expression with resultType string).|azureml_ml_endpoint|azure_m_l_ml_endpoint|
|**--type-properties-api-key**|object|The API key for accessing the Azure ML model endpoint.|azureml_api_key|azure_m_l_api_key|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azureml_connect_via|azure_m_l_connect_via|
|**--description**|string|Linked service description.|azureml_description|azure_m_l_description|
|**--parameters**|dictionary|Parameters for linked service.|azureml_parameters|azure_m_l_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azureml_annotations|azure_m_l_annotations|
|**--type-properties-update-resource-endpoint**|any|The Update Resource REST URL for an Azure ML Studio Web Service endpoint. Type: string (or Expression with resultType string).|azureml_update_resource_endpoint|azure_m_l_update_resource_endpoint|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against the ARM-based updateResourceEndpoint of an Azure ML Studio web service. Type: string (or Expression with resultType string).|azureml_service_principal_id|azure_m_l_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against the ARM-based updateResourceEndpoint of an Azure ML Studio web service.|azureml_service_principal_key|azure_m_l_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azureml_tenant|azure_m_l_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azureml_encrypted_credential|azure_m_l_encrypted_credential|
### datafactory linked-service azure-m-l-service create

azure-m-l-service create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuremlservice_type|azure_m_l_service_type|
|**--type-properties-subscription-id**|any|Azure ML Service workspace subscription ID. Type: string (or Expression with resultType string).|azuremlservice_subscription_id|azure_m_l_service_subscription_id|
|**--type-properties-resource-group-name**|any|Azure ML Service workspace resource group name. Type: string (or Expression with resultType string).|azuremlservice_resource_group_name|azure_m_l_service_resource_group_name|
|**--type-properties-ml-workspace-name**|any|Azure ML Service workspace name. Type: string (or Expression with resultType string).|azuremlservice_ml_workspace_name|azure_m_l_service_ml_workspace_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuremlservice_connect_via|azure_m_l_service_connect_via|
|**--description**|string|Linked service description.|azuremlservice_description|azure_m_l_service_description|
|**--parameters**|dictionary|Parameters for linked service.|azuremlservice_parameters|azure_m_l_service_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuremlservice_annotations|azure_m_l_service_annotations|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against the endpoint of a published Azure ML Service pipeline. Type: string (or Expression with resultType string).|azuremlservice_service_principal_id|azure_m_l_service_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against the endpoint of a published Azure ML Service pipeline.|azuremlservice_service_principal_key|azure_m_l_service_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azuremlservice_tenant|azure_m_l_service_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuremlservice_encrypted_credential|azure_m_l_service_encrypted_credential|
### datafactory linked-service azure-m-l-service update

azure-m-l-service create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuremlservice_type|azure_m_l_service_type|
|**--type-properties-subscription-id**|any|Azure ML Service workspace subscription ID. Type: string (or Expression with resultType string).|azuremlservice_subscription_id|azure_m_l_service_subscription_id|
|**--type-properties-resource-group-name**|any|Azure ML Service workspace resource group name. Type: string (or Expression with resultType string).|azuremlservice_resource_group_name|azure_m_l_service_resource_group_name|
|**--type-properties-ml-workspace-name**|any|Azure ML Service workspace name. Type: string (or Expression with resultType string).|azuremlservice_ml_workspace_name|azure_m_l_service_ml_workspace_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuremlservice_connect_via|azure_m_l_service_connect_via|
|**--description**|string|Linked service description.|azuremlservice_description|azure_m_l_service_description|
|**--parameters**|dictionary|Parameters for linked service.|azuremlservice_parameters|azure_m_l_service_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuremlservice_annotations|azure_m_l_service_annotations|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against the endpoint of a published Azure ML Service pipeline. Type: string (or Expression with resultType string).|azuremlservice_service_principal_id|azure_m_l_service_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against the endpoint of a published Azure ML Service pipeline.|azuremlservice_service_principal_key|azure_m_l_service_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azuremlservice_tenant|azure_m_l_service_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuremlservice_encrypted_credential|azure_m_l_service_encrypted_credential|
### datafactory linked-service azure-maria-d-b create

azure-maria-d-b create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuremariadb_type|azure_maria_d_b_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuremariadb_connect_via|azure_maria_d_b_connect_via|
|**--description**|string|Linked service description.|azuremariadb_description|azure_maria_d_b_description|
|**--parameters**|dictionary|Parameters for linked service.|azuremariadb_parameters|azure_maria_d_b_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuremariadb_annotations|azure_maria_d_b_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|azuremariadb_connection_string|azure_maria_d_b_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|azuremariadb_pwd|azure_maria_d_b_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuremariadb_encrypted_credential|azure_maria_d_b_encrypted_credential|
### datafactory linked-service azure-maria-d-b update

azure-maria-d-b create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuremariadb_type|azure_maria_d_b_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuremariadb_connect_via|azure_maria_d_b_connect_via|
|**--description**|string|Linked service description.|azuremariadb_description|azure_maria_d_b_description|
|**--parameters**|dictionary|Parameters for linked service.|azuremariadb_parameters|azure_maria_d_b_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuremariadb_annotations|azure_maria_d_b_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|azuremariadb_connection_string|azure_maria_d_b_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|azuremariadb_pwd|azure_maria_d_b_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuremariadb_encrypted_credential|azure_maria_d_b_encrypted_credential|
### datafactory linked-service azure-my-sql create

azure-my-sql create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuremysql_type|azure_my_sql_type|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|azuremysql_connection_string|azure_my_sql_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuremysql_connect_via|azure_my_sql_connect_via|
|**--description**|string|Linked service description.|azuremysql_description|azure_my_sql_description|
|**--parameters**|dictionary|Parameters for linked service.|azuremysql_parameters|azure_my_sql_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuremysql_annotations|azure_my_sql_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|azuremysql_password|azure_my_sql_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuremysql_encrypted_credential|azure_my_sql_encrypted_credential|
### datafactory linked-service azure-my-sql update

azure-my-sql create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuremysql_type|azure_my_sql_type|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|azuremysql_connection_string|azure_my_sql_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuremysql_connect_via|azure_my_sql_connect_via|
|**--description**|string|Linked service description.|azuremysql_description|azure_my_sql_description|
|**--parameters**|dictionary|Parameters for linked service.|azuremysql_parameters|azure_my_sql_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuremysql_annotations|azure_my_sql_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|azuremysql_password|azure_my_sql_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuremysql_encrypted_credential|azure_my_sql_encrypted_credential|
### datafactory linked-service azure-postgre-sql create

azure-postgre-sql create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azurepostgresql_type|azure_postgre_sql_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azurepostgresql_connect_via|azure_postgre_sql_connect_via|
|**--description**|string|Linked service description.|azurepostgresql_description|azure_postgre_sql_description|
|**--parameters**|dictionary|Parameters for linked service.|azurepostgresql_parameters|azure_postgre_sql_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azurepostgresql_annotations|azure_postgre_sql_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|azurepostgresql_connection_string|azure_postgre_sql_connection_string|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|azurepostgresql_password|azure_postgre_sql_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azurepostgresql_encrypted_credential|azure_postgre_sql_encrypted_credential|
### datafactory linked-service azure-postgre-sql update

azure-postgre-sql create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azurepostgresql_type|azure_postgre_sql_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azurepostgresql_connect_via|azure_postgre_sql_connect_via|
|**--description**|string|Linked service description.|azurepostgresql_description|azure_postgre_sql_description|
|**--parameters**|dictionary|Parameters for linked service.|azurepostgresql_parameters|azure_postgre_sql_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azurepostgresql_annotations|azure_postgre_sql_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|azurepostgresql_connection_string|azure_postgre_sql_connection_string|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|azurepostgresql_password|azure_postgre_sql_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azurepostgresql_encrypted_credential|azure_postgre_sql_encrypted_credential|
### datafactory linked-service azure-search create

azure-search create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuresearch_type|azure_search_type|
|**--type-properties-url**|any|URL for Azure Search service. Type: string (or Expression with resultType string).|azuresearch_url|azure_search_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuresearch_connect_via|azure_search_connect_via|
|**--description**|string|Linked service description.|azuresearch_description|azure_search_description|
|**--parameters**|dictionary|Parameters for linked service.|azuresearch_parameters|azure_search_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuresearch_annotations|azure_search_annotations|
|**--type-properties-key**|object|Admin Key for Azure Search service|azuresearch_key|azure_search_key|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuresearch_encrypted_credential|azure_search_encrypted_credential|
### datafactory linked-service azure-search update

azure-search create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuresearch_type|azure_search_type|
|**--type-properties-url**|any|URL for Azure Search service. Type: string (or Expression with resultType string).|azuresearch_url|azure_search_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuresearch_connect_via|azure_search_connect_via|
|**--description**|string|Linked service description.|azuresearch_description|azure_search_description|
|**--parameters**|dictionary|Parameters for linked service.|azuresearch_parameters|azure_search_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuresearch_annotations|azure_search_annotations|
|**--type-properties-key**|object|Admin Key for Azure Search service|azuresearch_key|azure_search_key|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuresearch_encrypted_credential|azure_search_encrypted_credential|
### datafactory linked-service azure-sql-d-w create

azure-sql-d-w create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuresqldw_type|azure_sql_d_w_type|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference. Type: string, SecureString or AzureKeyVaultSecretReference.|azuresqldw_connection_string|azure_sql_d_w_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuresqldw_connect_via|azure_sql_d_w_connect_via|
|**--description**|string|Linked service description.|azuresqldw_description|azure_sql_d_w_description|
|**--parameters**|dictionary|Parameters for linked service.|azuresqldw_parameters|azure_sql_d_w_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuresqldw_annotations|azure_sql_d_w_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|azuresqldw_password|azure_sql_d_w_password|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against Azure SQL Data Warehouse. Type: string (or Expression with resultType string).|azuresqldw_service_principal_id|azure_sql_d_w_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against Azure SQL Data Warehouse.|azuresqldw_service_principal_key|azure_sql_d_w_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azuresqldw_tenant|azure_sql_d_w_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuresqldw_encrypted_credential|azure_sql_d_w_encrypted_credential|
### datafactory linked-service azure-sql-d-w update

azure-sql-d-w create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuresqldw_type|azure_sql_d_w_type|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference. Type: string, SecureString or AzureKeyVaultSecretReference.|azuresqldw_connection_string|azure_sql_d_w_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuresqldw_connect_via|azure_sql_d_w_connect_via|
|**--description**|string|Linked service description.|azuresqldw_description|azure_sql_d_w_description|
|**--parameters**|dictionary|Parameters for linked service.|azuresqldw_parameters|azure_sql_d_w_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuresqldw_annotations|azure_sql_d_w_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|azuresqldw_password|azure_sql_d_w_password|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against Azure SQL Data Warehouse. Type: string (or Expression with resultType string).|azuresqldw_service_principal_id|azure_sql_d_w_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against Azure SQL Data Warehouse.|azuresqldw_service_principal_key|azure_sql_d_w_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azuresqldw_tenant|azure_sql_d_w_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuresqldw_encrypted_credential|azure_sql_d_w_encrypted_credential|
### datafactory linked-service azure-sql-database create

azure-sql-database create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuresqldatabase_type|azure_sql_database_type|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|azuresqldatabase_connection_string|azure_sql_database_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuresqldatabase_connect_via|azure_sql_database_connect_via|
|**--description**|string|Linked service description.|azuresqldatabase_description|azure_sql_database_description|
|**--parameters**|dictionary|Parameters for linked service.|azuresqldatabase_parameters|azure_sql_database_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuresqldatabase_annotations|azure_sql_database_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|azuresqldatabase_password|azure_sql_database_password|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against Azure SQL Database. Type: string (or Expression with resultType string).|azuresqldatabase_service_principal_id|azure_sql_database_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against Azure SQL Database.|azuresqldatabase_service_principal_key|azure_sql_database_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azuresqldatabase_tenant|azure_sql_database_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuresqldatabase_encrypted_credential|azure_sql_database_encrypted_credential|
### datafactory linked-service azure-sql-database update

azure-sql-database create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuresqldatabase_type|azure_sql_database_type|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|azuresqldatabase_connection_string|azure_sql_database_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuresqldatabase_connect_via|azure_sql_database_connect_via|
|**--description**|string|Linked service description.|azuresqldatabase_description|azure_sql_database_description|
|**--parameters**|dictionary|Parameters for linked service.|azuresqldatabase_parameters|azure_sql_database_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuresqldatabase_annotations|azure_sql_database_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|azuresqldatabase_password|azure_sql_database_password|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against Azure SQL Database. Type: string (or Expression with resultType string).|azuresqldatabase_service_principal_id|azure_sql_database_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against Azure SQL Database.|azuresqldatabase_service_principal_key|azure_sql_database_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azuresqldatabase_tenant|azure_sql_database_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuresqldatabase_encrypted_credential|azure_sql_database_encrypted_credential|
### datafactory linked-service azure-sql-m-i create

azure-sql-m-i create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuresqlmi_type|azure_sql_m_i_type|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|azuresqlmi_connection_string|azure_sql_m_i_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuresqlmi_connect_via|azure_sql_m_i_connect_via|
|**--description**|string|Linked service description.|azuresqlmi_description|azure_sql_m_i_description|
|**--parameters**|dictionary|Parameters for linked service.|azuresqlmi_parameters|azure_sql_m_i_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuresqlmi_annotations|azure_sql_m_i_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|azuresqlmi_password|azure_sql_m_i_password|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against Azure SQL Managed Instance. Type: string (or Expression with resultType string).|azuresqlmi_service_principal_id|azure_sql_m_i_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against Azure SQL Managed Instance.|azuresqlmi_service_principal_key|azure_sql_m_i_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azuresqlmi_tenant|azure_sql_m_i_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuresqlmi_encrypted_credential|azure_sql_m_i_encrypted_credential|
### datafactory linked-service azure-sql-m-i update

azure-sql-m-i create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuresqlmi_type|azure_sql_m_i_type|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|azuresqlmi_connection_string|azure_sql_m_i_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuresqlmi_connect_via|azure_sql_m_i_connect_via|
|**--description**|string|Linked service description.|azuresqlmi_description|azure_sql_m_i_description|
|**--parameters**|dictionary|Parameters for linked service.|azuresqlmi_parameters|azure_sql_m_i_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuresqlmi_annotations|azure_sql_m_i_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|azuresqlmi_password|azure_sql_m_i_password|
|**--type-properties-service-principal-id**|any|The ID of the service principal used to authenticate against Azure SQL Managed Instance. Type: string (or Expression with resultType string).|azuresqlmi_service_principal_id|azure_sql_m_i_service_principal_id|
|**--type-properties-service-principal-key**|object|The key of the service principal used to authenticate against Azure SQL Managed Instance.|azuresqlmi_service_principal_key|azure_sql_m_i_service_principal_key|
|**--type-properties-tenant**|any|The name or ID of the tenant to which the service principal belongs. Type: string (or Expression with resultType string).|azuresqlmi_tenant|azure_sql_m_i_tenant|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuresqlmi_encrypted_credential|azure_sql_m_i_encrypted_credential|
### datafactory linked-service azure-storage create

azure-storage create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azurestorage_type|azure_storage_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azurestorage_connect_via|azure_storage_connect_via|
|**--description**|string|Linked service description.|azurestorage_description|azure_storage_description|
|**--parameters**|dictionary|Parameters for linked service.|azurestorage_parameters|azure_storage_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azurestorage_annotations|azure_storage_annotations|
|**--type-properties-connection-string**|any|The connection string. It is mutually exclusive with sasUri property. Type: string, SecureString or AzureKeyVaultSecretReference.|azurestorage_connection_string|azure_storage_connection_string|
|**--type-properties-account-key**|object|The Azure key vault secret reference of accountKey in connection string.|azurestorage_account_key|azure_storage_account_key|
|**--type-properties-sas-uri**|any|SAS URI of the Azure Storage resource. It is mutually exclusive with connectionString property. Type: string, SecureString or AzureKeyVaultSecretReference.|azurestorage_sas_uri|azure_storage_sas_uri|
|**--type-properties-sas-token**|object|The Azure key vault secret reference of sasToken in sas uri.|azurestorage_sas_token|azure_storage_sas_token|
|**--type-properties-encrypted-credential**|string|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azurestorage_encrypted_credential|azure_storage_encrypted_credential|
### datafactory linked-service azure-storage update

azure-storage create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azurestorage_type|azure_storage_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azurestorage_connect_via|azure_storage_connect_via|
|**--description**|string|Linked service description.|azurestorage_description|azure_storage_description|
|**--parameters**|dictionary|Parameters for linked service.|azurestorage_parameters|azure_storage_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azurestorage_annotations|azure_storage_annotations|
|**--type-properties-connection-string**|any|The connection string. It is mutually exclusive with sasUri property. Type: string, SecureString or AzureKeyVaultSecretReference.|azurestorage_connection_string|azure_storage_connection_string|
|**--type-properties-account-key**|object|The Azure key vault secret reference of accountKey in connection string.|azurestorage_account_key|azure_storage_account_key|
|**--type-properties-sas-uri**|any|SAS URI of the Azure Storage resource. It is mutually exclusive with connectionString property. Type: string, SecureString or AzureKeyVaultSecretReference.|azurestorage_sas_uri|azure_storage_sas_uri|
|**--type-properties-sas-token**|object|The Azure key vault secret reference of sasToken in sas uri.|azurestorage_sas_token|azure_storage_sas_token|
|**--type-properties-encrypted-credential**|string|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azurestorage_encrypted_credential|azure_storage_encrypted_credential|
### datafactory linked-service azure-table-storage create

azure-table-storage create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuretablestorage_type|azure_table_storage_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuretablestorage_connect_via|azure_table_storage_connect_via|
|**--description**|string|Linked service description.|azuretablestorage_description|azure_table_storage_description|
|**--parameters**|dictionary|Parameters for linked service.|azuretablestorage_parameters|azure_table_storage_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuretablestorage_annotations|azure_table_storage_annotations|
|**--type-properties-connection-string**|any|The connection string. It is mutually exclusive with sasUri property. Type: string, SecureString or AzureKeyVaultSecretReference.|azuretablestorage_connection_string|azure_table_storage_connection_string|
|**--type-properties-account-key**|object|The Azure key vault secret reference of accountKey in connection string.|azuretablestorage_account_key|azure_table_storage_account_key|
|**--type-properties-sas-uri**|any|SAS URI of the Azure Storage resource. It is mutually exclusive with connectionString property. Type: string, SecureString or AzureKeyVaultSecretReference.|azuretablestorage_sas_uri|azure_table_storage_sas_uri|
|**--type-properties-sas-token**|object|The Azure key vault secret reference of sasToken in sas uri.|azuretablestorage_sas_token|azure_table_storage_sas_token|
|**--type-properties-encrypted-credential**|string|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuretablestorage_encrypted_credential|azure_table_storage_encrypted_credential|
### datafactory linked-service azure-table-storage update

azure-table-storage create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|azuretablestorage_type|azure_table_storage_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|azuretablestorage_connect_via|azure_table_storage_connect_via|
|**--description**|string|Linked service description.|azuretablestorage_description|azure_table_storage_description|
|**--parameters**|dictionary|Parameters for linked service.|azuretablestorage_parameters|azure_table_storage_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|azuretablestorage_annotations|azure_table_storage_annotations|
|**--type-properties-connection-string**|any|The connection string. It is mutually exclusive with sasUri property. Type: string, SecureString or AzureKeyVaultSecretReference.|azuretablestorage_connection_string|azure_table_storage_connection_string|
|**--type-properties-account-key**|object|The Azure key vault secret reference of accountKey in connection string.|azuretablestorage_account_key|azure_table_storage_account_key|
|**--type-properties-sas-uri**|any|SAS URI of the Azure Storage resource. It is mutually exclusive with connectionString property. Type: string, SecureString or AzureKeyVaultSecretReference.|azuretablestorage_sas_uri|azure_table_storage_sas_uri|
|**--type-properties-sas-token**|object|The Azure key vault secret reference of sasToken in sas uri.|azuretablestorage_sas_token|azure_table_storage_sas_token|
|**--type-properties-encrypted-credential**|string|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|azuretablestorage_encrypted_credential|azure_table_storage_encrypted_credential|
### datafactory linked-service cassandra create

cassandra create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|cassandra_type|cassandra_type|
|**--type-properties-host**|any|Host name for connection. Type: string (or Expression with resultType string).|cassandra_host|cassandra_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|cassandra_connect_via|cassandra_connect_via|
|**--description**|string|Linked service description.|cassandra_description|cassandra_description|
|**--parameters**|dictionary|Parameters for linked service.|cassandra_parameters|cassandra_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|cassandra_annotations|cassandra_annotations|
|**--type-properties-authentication-type**|any|AuthenticationType to be used for connection. Type: string (or Expression with resultType string).|cassandra_authentication_type|cassandra_authentication_type|
|**--type-properties-port**|any|The port for the connection. Type: integer (or Expression with resultType integer).|cassandra_port|cassandra_port|
|**--type-properties-username**|any|Username for authentication. Type: string (or Expression with resultType string).|cassandra_username|cassandra_username|
|**--type-properties-password**|object|Password for authentication.|cassandra_password|cassandra_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|cassandra_encrypted_credential|cassandra_encrypted_credential|
### datafactory linked-service cassandra update

cassandra create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|cassandra_type|cassandra_type|
|**--type-properties-host**|any|Host name for connection. Type: string (or Expression with resultType string).|cassandra_host|cassandra_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|cassandra_connect_via|cassandra_connect_via|
|**--description**|string|Linked service description.|cassandra_description|cassandra_description|
|**--parameters**|dictionary|Parameters for linked service.|cassandra_parameters|cassandra_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|cassandra_annotations|cassandra_annotations|
|**--type-properties-authentication-type**|any|AuthenticationType to be used for connection. Type: string (or Expression with resultType string).|cassandra_authentication_type|cassandra_authentication_type|
|**--type-properties-port**|any|The port for the connection. Type: integer (or Expression with resultType integer).|cassandra_port|cassandra_port|
|**--type-properties-username**|any|Username for authentication. Type: string (or Expression with resultType string).|cassandra_username|cassandra_username|
|**--type-properties-password**|object|Password for authentication.|cassandra_password|cassandra_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|cassandra_encrypted_credential|cassandra_encrypted_credential|
### datafactory linked-service common-data-service-for-apps create

common-data-service-for-apps create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|commondataserviceforapps_type|common_data_service_for_apps_type|
|**--type-properties-deployment-type**|choice|The deployment type of the Common Data Service for Apps instance. 'Online' for Common Data Service for Apps Online and 'OnPremisesWithIfd' for Common Data Service for Apps on-premises with Ifd. Type: string (or Expression with resultType string).|commondataserviceforapps_deployment_type|common_data_service_for_apps_deployment_type|
|**--type-properties-authentication-type**|choice|The authentication type to connect to Common Data Service for Apps server. 'Office365' for online scenario, 'Ifd' for on-premises with Ifd scenario. 'AADServicePrincipal' for Server-To-Server authentication in online scenario. Type: string (or Expression with resultType string).|commondataserviceforapps_authentication_type|common_data_service_for_apps_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|commondataserviceforapps_connect_via|common_data_service_for_apps_connect_via|
|**--description**|string|Linked service description.|commondataserviceforapps_description|common_data_service_for_apps_description|
|**--parameters**|dictionary|Parameters for linked service.|commondataserviceforapps_parameters|common_data_service_for_apps_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|commondataserviceforapps_annotations|common_data_service_for_apps_annotations|
|**--type-properties-host-name**|any|The host name of the on-premises Common Data Service for Apps server. The property is required for on-prem and not allowed for online. Type: string (or Expression with resultType string).|commondataserviceforapps_host_name|common_data_service_for_apps_host_name|
|**--type-properties-port**|any|The port of on-premises Common Data Service for Apps server. The property is required for on-prem and not allowed for online. Default is 443. Type: integer (or Expression with resultType integer), minimum: 0.|commondataserviceforapps_port|common_data_service_for_apps_port|
|**--type-properties-service-uri**|any|The URL to the Microsoft Common Data Service for Apps server. The property is required for on-line and not allowed for on-prem. Type: string (or Expression with resultType string).|commondataserviceforapps_service_uri|common_data_service_for_apps_service_uri|
|**--type-properties-organization-name**|any|The organization name of the Common Data Service for Apps instance. The property is required for on-prem and required for online when there are more than one Common Data Service for Apps instances associated with the user. Type: string (or Expression with resultType string).|commondataserviceforapps_organization_name|common_data_service_for_apps_organization_name|
|**--type-properties-username**|any|User name to access the Common Data Service for Apps instance. Type: string (or Expression with resultType string).|commondataserviceforapps_username|common_data_service_for_apps_username|
|**--type-properties-password**|object|Password to access the Common Data Service for Apps instance.|commondataserviceforapps_password|common_data_service_for_apps_password|
|**--type-properties-service-principal-id**|any|The client ID of the application in Azure Active Directory used for Server-To-Server authentication. Type: string (or Expression with resultType string).|commondataserviceforapps_service_principal_id|common_data_service_for_apps_service_principal_id|
|**--type-properties-service-principal-credential-type**|choice|The service principal credential type to use in Server-To-Server authentication. 'ServicePrincipalKey' for key/secret, 'ServicePrincipalCert' for certificate. Type: string (or Expression with resultType string).|commondataserviceforapps_service_principal_credential_type|common_data_service_for_apps_service_principal_credential_type|
|**--type-properties-service-principal-credential**|object|The credential of the service principal object in Azure Active Directory. If servicePrincipalCredentialType is 'ServicePrincipalKey', servicePrincipalCredential can be SecureString or AzureKeyVaultSecretReference. If servicePrincipalCredentialType is 'ServicePrincipalCert', servicePrincipalCredential can only be AzureKeyVaultSecretReference.|commondataserviceforapps_service_principal_credential|common_data_service_for_apps_service_principal_credential|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|commondataserviceforapps_encrypted_credential|common_data_service_for_apps_encrypted_credential|
### datafactory linked-service common-data-service-for-apps update

common-data-service-for-apps create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|commondataserviceforapps_type|common_data_service_for_apps_type|
|**--type-properties-deployment-type**|choice|The deployment type of the Common Data Service for Apps instance. 'Online' for Common Data Service for Apps Online and 'OnPremisesWithIfd' for Common Data Service for Apps on-premises with Ifd. Type: string (or Expression with resultType string).|commondataserviceforapps_deployment_type|common_data_service_for_apps_deployment_type|
|**--type-properties-authentication-type**|choice|The authentication type to connect to Common Data Service for Apps server. 'Office365' for online scenario, 'Ifd' for on-premises with Ifd scenario. 'AADServicePrincipal' for Server-To-Server authentication in online scenario. Type: string (or Expression with resultType string).|commondataserviceforapps_authentication_type|common_data_service_for_apps_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|commondataserviceforapps_connect_via|common_data_service_for_apps_connect_via|
|**--description**|string|Linked service description.|commondataserviceforapps_description|common_data_service_for_apps_description|
|**--parameters**|dictionary|Parameters for linked service.|commondataserviceforapps_parameters|common_data_service_for_apps_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|commondataserviceforapps_annotations|common_data_service_for_apps_annotations|
|**--type-properties-host-name**|any|The host name of the on-premises Common Data Service for Apps server. The property is required for on-prem and not allowed for online. Type: string (or Expression with resultType string).|commondataserviceforapps_host_name|common_data_service_for_apps_host_name|
|**--type-properties-port**|any|The port of on-premises Common Data Service for Apps server. The property is required for on-prem and not allowed for online. Default is 443. Type: integer (or Expression with resultType integer), minimum: 0.|commondataserviceforapps_port|common_data_service_for_apps_port|
|**--type-properties-service-uri**|any|The URL to the Microsoft Common Data Service for Apps server. The property is required for on-line and not allowed for on-prem. Type: string (or Expression with resultType string).|commondataserviceforapps_service_uri|common_data_service_for_apps_service_uri|
|**--type-properties-organization-name**|any|The organization name of the Common Data Service for Apps instance. The property is required for on-prem and required for online when there are more than one Common Data Service for Apps instances associated with the user. Type: string (or Expression with resultType string).|commondataserviceforapps_organization_name|common_data_service_for_apps_organization_name|
|**--type-properties-username**|any|User name to access the Common Data Service for Apps instance. Type: string (or Expression with resultType string).|commondataserviceforapps_username|common_data_service_for_apps_username|
|**--type-properties-password**|object|Password to access the Common Data Service for Apps instance.|commondataserviceforapps_password|common_data_service_for_apps_password|
|**--type-properties-service-principal-id**|any|The client ID of the application in Azure Active Directory used for Server-To-Server authentication. Type: string (or Expression with resultType string).|commondataserviceforapps_service_principal_id|common_data_service_for_apps_service_principal_id|
|**--type-properties-service-principal-credential-type**|choice|The service principal credential type to use in Server-To-Server authentication. 'ServicePrincipalKey' for key/secret, 'ServicePrincipalCert' for certificate. Type: string (or Expression with resultType string).|commondataserviceforapps_service_principal_credential_type|common_data_service_for_apps_service_principal_credential_type|
|**--type-properties-service-principal-credential**|object|The credential of the service principal object in Azure Active Directory. If servicePrincipalCredentialType is 'ServicePrincipalKey', servicePrincipalCredential can be SecureString or AzureKeyVaultSecretReference. If servicePrincipalCredentialType is 'ServicePrincipalCert', servicePrincipalCredential can only be AzureKeyVaultSecretReference.|commondataserviceforapps_service_principal_credential|common_data_service_for_apps_service_principal_credential|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|commondataserviceforapps_encrypted_credential|common_data_service_for_apps_encrypted_credential|
### datafactory linked-service concur create

concur create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|concur_type|concur_type|
|**--type-properties-client-id**|any|Application client_id supplied by Concur App Management.|concur_client_id|concur_client_id|
|**--type-properties-username**|any|The user name that you use to access Concur Service.|concur_username|concur_username|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|concur_connect_via|concur_connect_via|
|**--description**|string|Linked service description.|concur_description|concur_description|
|**--parameters**|dictionary|Parameters for linked service.|concur_parameters|concur_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|concur_annotations|concur_annotations|
|**--type-properties-password**|object|The password corresponding to the user name that you provided in the username field.|concur_password|concur_password|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|concur_use_encrypted_endpoints|concur_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|concur_use_host_verification|concur_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|concur_use_peer_verification|concur_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|concur_encrypted_credential|concur_encrypted_credential|
### datafactory linked-service concur update

concur create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|concur_type|concur_type|
|**--type-properties-client-id**|any|Application client_id supplied by Concur App Management.|concur_client_id|concur_client_id|
|**--type-properties-username**|any|The user name that you use to access Concur Service.|concur_username|concur_username|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|concur_connect_via|concur_connect_via|
|**--description**|string|Linked service description.|concur_description|concur_description|
|**--parameters**|dictionary|Parameters for linked service.|concur_parameters|concur_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|concur_annotations|concur_annotations|
|**--type-properties-password**|object|The password corresponding to the user name that you provided in the username field.|concur_password|concur_password|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|concur_use_encrypted_endpoints|concur_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|concur_use_host_verification|concur_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|concur_use_peer_verification|concur_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|concur_encrypted_credential|concur_encrypted_credential|
### datafactory linked-service cosmos-db create

cosmos-db create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|cosmosdb_type|cosmos_db_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|cosmosdb_connect_via|cosmos_db_connect_via|
|**--description**|string|Linked service description.|cosmosdb_description|cosmos_db_description|
|**--parameters**|dictionary|Parameters for linked service.|cosmosdb_parameters|cosmos_db_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|cosmosdb_annotations|cosmos_db_annotations|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|cosmosdb_connection_string|cosmos_db_connection_string|
|**--type-properties-account-endpoint**|any|The endpoint of the Azure CosmosDB account. Type: string (or Expression with resultType string)|cosmosdb_account_endpoint|cosmos_db_account_endpoint|
|**--type-properties-database**|any|The name of the database. Type: string (or Expression with resultType string)|cosmosdb_database|cosmos_db_database|
|**--type-properties-account-key**|object|The account key of the Azure CosmosDB account. Type: SecureString or AzureKeyVaultSecretReference.|cosmosdb_account_key|cosmos_db_account_key|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|cosmosdb_encrypted_credential|cosmos_db_encrypted_credential|
### datafactory linked-service cosmos-db update

cosmos-db create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|cosmosdb_type|cosmos_db_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|cosmosdb_connect_via|cosmos_db_connect_via|
|**--description**|string|Linked service description.|cosmosdb_description|cosmos_db_description|
|**--parameters**|dictionary|Parameters for linked service.|cosmosdb_parameters|cosmos_db_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|cosmosdb_annotations|cosmos_db_annotations|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|cosmosdb_connection_string|cosmos_db_connection_string|
|**--type-properties-account-endpoint**|any|The endpoint of the Azure CosmosDB account. Type: string (or Expression with resultType string)|cosmosdb_account_endpoint|cosmos_db_account_endpoint|
|**--type-properties-database**|any|The name of the database. Type: string (or Expression with resultType string)|cosmosdb_database|cosmos_db_database|
|**--type-properties-account-key**|object|The account key of the Azure CosmosDB account. Type: SecureString or AzureKeyVaultSecretReference.|cosmosdb_account_key|cosmos_db_account_key|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|cosmosdb_encrypted_credential|cosmos_db_encrypted_credential|
### datafactory linked-service cosmos-db-mongo-db-api create

cosmos-db-mongo-db-api create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|cosmosdbmongodbapi_type|cosmos_db_mongo_db_api_type|
|**--type-properties-connection-string**|any|The CosmosDB (MongoDB API) connection string. Type: string, SecureString or AzureKeyVaultSecretReference. Type: string, SecureString or AzureKeyVaultSecretReference.|cosmosdbmongodbapi_connection_string|cosmos_db_mongo_db_api_connection_string|
|**--type-properties-database**|any|The name of the CosmosDB (MongoDB API) database that you want to access. Type: string (or Expression with resultType string).|cosmosdbmongodbapi_database|cosmos_db_mongo_db_api_database|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|cosmosdbmongodbapi_connect_via|cosmos_db_mongo_db_api_connect_via|
|**--description**|string|Linked service description.|cosmosdbmongodbapi_description|cosmos_db_mongo_db_api_description|
|**--parameters**|dictionary|Parameters for linked service.|cosmosdbmongodbapi_parameters|cosmos_db_mongo_db_api_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|cosmosdbmongodbapi_annotations|cosmos_db_mongo_db_api_annotations|
### datafactory linked-service cosmos-db-mongo-db-api update

cosmos-db-mongo-db-api create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|cosmosdbmongodbapi_type|cosmos_db_mongo_db_api_type|
|**--type-properties-connection-string**|any|The CosmosDB (MongoDB API) connection string. Type: string, SecureString or AzureKeyVaultSecretReference. Type: string, SecureString or AzureKeyVaultSecretReference.|cosmosdbmongodbapi_connection_string|cosmos_db_mongo_db_api_connection_string|
|**--type-properties-database**|any|The name of the CosmosDB (MongoDB API) database that you want to access. Type: string (or Expression with resultType string).|cosmosdbmongodbapi_database|cosmos_db_mongo_db_api_database|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|cosmosdbmongodbapi_connect_via|cosmos_db_mongo_db_api_connect_via|
|**--description**|string|Linked service description.|cosmosdbmongodbapi_description|cosmos_db_mongo_db_api_description|
|**--parameters**|dictionary|Parameters for linked service.|cosmosdbmongodbapi_parameters|cosmos_db_mongo_db_api_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|cosmosdbmongodbapi_annotations|cosmos_db_mongo_db_api_annotations|
### datafactory linked-service couchbase create

couchbase create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|couchbase_type|couchbase_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|couchbase_connect_via|couchbase_connect_via|
|**--description**|string|Linked service description.|couchbase_description|couchbase_description|
|**--parameters**|dictionary|Parameters for linked service.|couchbase_parameters|couchbase_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|couchbase_annotations|couchbase_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|couchbase_connection_string|couchbase_connection_string|
|**--type-properties-cred-string**|object|The Azure key vault secret reference of credString in connection string.|couchbase_cred_string|couchbase_cred_string|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|couchbase_encrypted_credential|couchbase_encrypted_credential|
### datafactory linked-service couchbase update

couchbase create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|couchbase_type|couchbase_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|couchbase_connect_via|couchbase_connect_via|
|**--description**|string|Linked service description.|couchbase_description|couchbase_description|
|**--parameters**|dictionary|Parameters for linked service.|couchbase_parameters|couchbase_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|couchbase_annotations|couchbase_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|couchbase_connection_string|couchbase_connection_string|
|**--type-properties-cred-string**|object|The Azure key vault secret reference of credString in connection string.|couchbase_cred_string|couchbase_cred_string|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|couchbase_encrypted_credential|couchbase_encrypted_credential|
### datafactory linked-service custom-data-source create

custom-data-source create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|customdatasource_type|custom_data_source_type|
|**--type-properties**|any|Custom linked service properties.|customdatasource_type_properties|custom_data_source_type_properties|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|customdatasource_connect_via|custom_data_source_connect_via|
|**--description**|string|Linked service description.|customdatasource_description|custom_data_source_description|
|**--parameters**|dictionary|Parameters for linked service.|customdatasource_parameters|custom_data_source_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|customdatasource_annotations|custom_data_source_annotations|
### datafactory linked-service custom-data-source update

custom-data-source create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|customdatasource_type|custom_data_source_type|
|**--type-properties**|any|Custom linked service properties.|customdatasource_type_properties|custom_data_source_type_properties|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|customdatasource_connect_via|custom_data_source_connect_via|
|**--description**|string|Linked service description.|customdatasource_description|custom_data_source_description|
|**--parameters**|dictionary|Parameters for linked service.|customdatasource_parameters|custom_data_source_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|customdatasource_annotations|custom_data_source_annotations|
### datafactory linked-service db2 create

db2 create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|db2_type|db2_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|db2_connect_via|db2_connect_via|
|**--description**|string|Linked service description.|db2_description|db2_description|
|**--parameters**|dictionary|Parameters for linked service.|db2_parameters|db2_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|db2_annotations|db2_annotations|
|**--type-properties-connection-string**|any|The connection string. It is mutually exclusive with server, database, authenticationType, userName, packageCollection and certificateCommonName property. Type: string, SecureString or AzureKeyVaultSecretReference.|db2_connection_string|db2_connection_string|
|**--type-properties-server**|any|Server name for connection. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_server|db2_server|
|**--type-properties-database**|any|Database name for connection. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_database|db2_database|
|**--type-properties-username**|any|Username for authentication. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_username|db2_username|
|**--type-properties-password**|object|Password for authentication.|db2_password|db2_password|
|**--type-properties-package-collection**|any|Under where packages are created when querying database. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_package_collection|db2_package_collection|
|**--type-properties-certificate-common-name**|any|Certificate Common Name when TLS is enabled. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_certificate_common_name|db2_certificate_common_name|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_encrypted_credential|db2_encrypted_credential|
### datafactory linked-service db2 update

db2 create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|db2_type|db2_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|db2_connect_via|db2_connect_via|
|**--description**|string|Linked service description.|db2_description|db2_description|
|**--parameters**|dictionary|Parameters for linked service.|db2_parameters|db2_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|db2_annotations|db2_annotations|
|**--type-properties-connection-string**|any|The connection string. It is mutually exclusive with server, database, authenticationType, userName, packageCollection and certificateCommonName property. Type: string, SecureString or AzureKeyVaultSecretReference.|db2_connection_string|db2_connection_string|
|**--type-properties-server**|any|Server name for connection. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_server|db2_server|
|**--type-properties-database**|any|Database name for connection. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_database|db2_database|
|**--type-properties-username**|any|Username for authentication. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_username|db2_username|
|**--type-properties-password**|object|Password for authentication.|db2_password|db2_password|
|**--type-properties-package-collection**|any|Under where packages are created when querying database. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_package_collection|db2_package_collection|
|**--type-properties-certificate-common-name**|any|Certificate Common Name when TLS is enabled. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_certificate_common_name|db2_certificate_common_name|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. It is mutually exclusive with connectionString property. Type: string (or Expression with resultType string).|db2_encrypted_credential|db2_encrypted_credential|
### datafactory linked-service delete

delete a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
### datafactory linked-service drill create

drill create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|drill_type|drill_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|drill_connect_via|drill_connect_via|
|**--description**|string|Linked service description.|drill_description|drill_description|
|**--parameters**|dictionary|Parameters for linked service.|drill_parameters|drill_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|drill_annotations|drill_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|drill_connection_string|drill_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|drill_pwd|drill_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|drill_encrypted_credential|drill_encrypted_credential|
### datafactory linked-service drill update

drill create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|drill_type|drill_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|drill_connect_via|drill_connect_via|
|**--description**|string|Linked service description.|drill_description|drill_description|
|**--parameters**|dictionary|Parameters for linked service.|drill_parameters|drill_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|drill_annotations|drill_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|drill_connection_string|drill_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|drill_pwd|drill_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|drill_encrypted_credential|drill_encrypted_credential|
### datafactory linked-service dynamics create

dynamics create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|dynamics_type|dynamics_type|
|**--type-properties-deployment-type**|choice|The deployment type of the Dynamics instance. 'Online' for Dynamics Online and 'OnPremisesWithIfd' for Dynamics on-premises with Ifd. Type: string (or Expression with resultType string).|dynamics_deployment_type|dynamics_deployment_type|
|**--type-properties-authentication-type**|choice|The authentication type to connect to Dynamics server. 'Office365' for online scenario, 'Ifd' for on-premises with Ifd scenario, 'AADServicePrincipal' for Server-To-Server authentication in online scenario. Type: string (or Expression with resultType string).|dynamics_authentication_type|dynamics_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|dynamics_connect_via|dynamics_connect_via|
|**--description**|string|Linked service description.|dynamics_description|dynamics_description|
|**--parameters**|dictionary|Parameters for linked service.|dynamics_parameters|dynamics_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|dynamics_annotations|dynamics_annotations|
|**--type-properties-host-name**|any|The host name of the on-premises Dynamics server. The property is required for on-prem and not allowed for online. Type: string (or Expression with resultType string).|dynamics_host_name|dynamics_host_name|
|**--type-properties-port**|any|The port of on-premises Dynamics server. The property is required for on-prem and not allowed for online. Default is 443. Type: integer (or Expression with resultType integer), minimum: 0.|dynamics_port|dynamics_port|
|**--type-properties-service-uri**|any|The URL to the Microsoft Dynamics server. The property is required for on-line and not allowed for on-prem. Type: string (or Expression with resultType string).|dynamics_service_uri|dynamics_service_uri|
|**--type-properties-organization-name**|any|The organization name of the Dynamics instance. The property is required for on-prem and required for online when there are more than one Dynamics instances associated with the user. Type: string (or Expression with resultType string).|dynamics_organization_name|dynamics_organization_name|
|**--type-properties-username**|any|User name to access the Dynamics instance. Type: string (or Expression with resultType string).|dynamics_username|dynamics_username|
|**--type-properties-password**|object|Password to access the Dynamics instance.|dynamics_password|dynamics_password|
|**--type-properties-service-principal-id**|any|The client ID of the application in Azure Active Directory used for Server-To-Server authentication. Type: string (or Expression with resultType string).|dynamics_service_principal_id|dynamics_service_principal_id|
|**--type-properties-service-principal-credential-type**|choice|The service principal credential type to use in Server-To-Server authentication. 'ServicePrincipalKey' for key/secret, 'ServicePrincipalCert' for certificate. Type: string (or Expression with resultType string).|dynamics_service_principal_credential_type|dynamics_service_principal_credential_type|
|**--type-properties-service-principal-credential**|object|The credential of the service principal object in Azure Active Directory. If servicePrincipalCredentialType is 'ServicePrincipalKey', servicePrincipalCredential can be SecureString or AzureKeyVaultSecretReference. If servicePrincipalCredentialType is 'ServicePrincipalCert', servicePrincipalCredential can only be AzureKeyVaultSecretReference.|dynamics_service_principal_credential|dynamics_service_principal_credential|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|dynamics_encrypted_credential|dynamics_encrypted_credential|
### datafactory linked-service dynamics update

dynamics create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|dynamics_type|dynamics_type|
|**--type-properties-deployment-type**|choice|The deployment type of the Dynamics instance. 'Online' for Dynamics Online and 'OnPremisesWithIfd' for Dynamics on-premises with Ifd. Type: string (or Expression with resultType string).|dynamics_deployment_type|dynamics_deployment_type|
|**--type-properties-authentication-type**|choice|The authentication type to connect to Dynamics server. 'Office365' for online scenario, 'Ifd' for on-premises with Ifd scenario, 'AADServicePrincipal' for Server-To-Server authentication in online scenario. Type: string (or Expression with resultType string).|dynamics_authentication_type|dynamics_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|dynamics_connect_via|dynamics_connect_via|
|**--description**|string|Linked service description.|dynamics_description|dynamics_description|
|**--parameters**|dictionary|Parameters for linked service.|dynamics_parameters|dynamics_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|dynamics_annotations|dynamics_annotations|
|**--type-properties-host-name**|any|The host name of the on-premises Dynamics server. The property is required for on-prem and not allowed for online. Type: string (or Expression with resultType string).|dynamics_host_name|dynamics_host_name|
|**--type-properties-port**|any|The port of on-premises Dynamics server. The property is required for on-prem and not allowed for online. Default is 443. Type: integer (or Expression with resultType integer), minimum: 0.|dynamics_port|dynamics_port|
|**--type-properties-service-uri**|any|The URL to the Microsoft Dynamics server. The property is required for on-line and not allowed for on-prem. Type: string (or Expression with resultType string).|dynamics_service_uri|dynamics_service_uri|
|**--type-properties-organization-name**|any|The organization name of the Dynamics instance. The property is required for on-prem and required for online when there are more than one Dynamics instances associated with the user. Type: string (or Expression with resultType string).|dynamics_organization_name|dynamics_organization_name|
|**--type-properties-username**|any|User name to access the Dynamics instance. Type: string (or Expression with resultType string).|dynamics_username|dynamics_username|
|**--type-properties-password**|object|Password to access the Dynamics instance.|dynamics_password|dynamics_password|
|**--type-properties-service-principal-id**|any|The client ID of the application in Azure Active Directory used for Server-To-Server authentication. Type: string (or Expression with resultType string).|dynamics_service_principal_id|dynamics_service_principal_id|
|**--type-properties-service-principal-credential-type**|choice|The service principal credential type to use in Server-To-Server authentication. 'ServicePrincipalKey' for key/secret, 'ServicePrincipalCert' for certificate. Type: string (or Expression with resultType string).|dynamics_service_principal_credential_type|dynamics_service_principal_credential_type|
|**--type-properties-service-principal-credential**|object|The credential of the service principal object in Azure Active Directory. If servicePrincipalCredentialType is 'ServicePrincipalKey', servicePrincipalCredential can be SecureString or AzureKeyVaultSecretReference. If servicePrincipalCredentialType is 'ServicePrincipalCert', servicePrincipalCredential can only be AzureKeyVaultSecretReference.|dynamics_service_principal_credential|dynamics_service_principal_credential|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|dynamics_encrypted_credential|dynamics_encrypted_credential|
### datafactory linked-service dynamics-a-x create

dynamics-a-x create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|dynamicsax_type|dynamics_a_x_type|
|**--type-properties-url**|any|The Dynamics AX (or Dynamics 365 Finance and Operations) instance OData endpoint.|dynamicsax_url|dynamics_a_x_url|
|**--type-properties-service-principal-id**|any|Specify the application's client ID. Type: string (or Expression with resultType string).|dynamicsax_service_principal_id|dynamics_a_x_service_principal_id|
|**--type-properties-service-principal-key**|object|Specify the application's key. Mark this field as a SecureString to store it securely in Data Factory, or reference a secret stored in Azure Key Vault. Type: string (or Expression with resultType string).|dynamicsax_service_principal_key|dynamics_a_x_service_principal_key|
|**--type-properties-tenant**|any|Specify the tenant information (domain name or tenant ID) under which your application resides. Retrieve it by hovering the mouse in the top-right corner of the Azure portal. Type: string (or Expression with resultType string).|dynamicsax_tenant|dynamics_a_x_tenant|
|**--type-properties-aad-resource-id**|any|Specify the resource you are requesting authorization. Type: string (or Expression with resultType string).|dynamicsax_aad_resource_id|dynamics_a_x_aad_resource_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|dynamicsax_connect_via|dynamics_a_x_connect_via|
|**--description**|string|Linked service description.|dynamicsax_description|dynamics_a_x_description|
|**--parameters**|dictionary|Parameters for linked service.|dynamicsax_parameters|dynamics_a_x_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|dynamicsax_annotations|dynamics_a_x_annotations|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|dynamicsax_encrypted_credential|dynamics_a_x_encrypted_credential|
### datafactory linked-service dynamics-a-x update

dynamics-a-x create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|dynamicsax_type|dynamics_a_x_type|
|**--type-properties-url**|any|The Dynamics AX (or Dynamics 365 Finance and Operations) instance OData endpoint.|dynamicsax_url|dynamics_a_x_url|
|**--type-properties-service-principal-id**|any|Specify the application's client ID. Type: string (or Expression with resultType string).|dynamicsax_service_principal_id|dynamics_a_x_service_principal_id|
|**--type-properties-service-principal-key**|object|Specify the application's key. Mark this field as a SecureString to store it securely in Data Factory, or reference a secret stored in Azure Key Vault. Type: string (or Expression with resultType string).|dynamicsax_service_principal_key|dynamics_a_x_service_principal_key|
|**--type-properties-tenant**|any|Specify the tenant information (domain name or tenant ID) under which your application resides. Retrieve it by hovering the mouse in the top-right corner of the Azure portal. Type: string (or Expression with resultType string).|dynamicsax_tenant|dynamics_a_x_tenant|
|**--type-properties-aad-resource-id**|any|Specify the resource you are requesting authorization. Type: string (or Expression with resultType string).|dynamicsax_aad_resource_id|dynamics_a_x_aad_resource_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|dynamicsax_connect_via|dynamics_a_x_connect_via|
|**--description**|string|Linked service description.|dynamicsax_description|dynamics_a_x_description|
|**--parameters**|dictionary|Parameters for linked service.|dynamicsax_parameters|dynamics_a_x_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|dynamicsax_annotations|dynamics_a_x_annotations|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|dynamicsax_encrypted_credential|dynamics_a_x_encrypted_credential|
### datafactory linked-service dynamics-crm create

dynamics-crm create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|dynamicscrm_type|dynamics_crm_type|
|**--type-properties-deployment-type**|choice|The deployment type of the Dynamics CRM instance. 'Online' for Dynamics CRM Online and 'OnPremisesWithIfd' for Dynamics CRM on-premises with Ifd. Type: string (or Expression with resultType string).|dynamicscrm_deployment_type|dynamics_crm_deployment_type|
|**--type-properties-authentication-type**|choice|The authentication type to connect to Dynamics CRM server. 'Office365' for online scenario, 'Ifd' for on-premises with Ifd scenario, 'AADServicePrincipal' for Server-To-Server authentication in online scenario. Type: string (or Expression with resultType string).|dynamicscrm_authentication_type|dynamics_crm_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|dynamicscrm_connect_via|dynamics_crm_connect_via|
|**--description**|string|Linked service description.|dynamicscrm_description|dynamics_crm_description|
|**--parameters**|dictionary|Parameters for linked service.|dynamicscrm_parameters|dynamics_crm_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|dynamicscrm_annotations|dynamics_crm_annotations|
|**--type-properties-host-name**|any|The host name of the on-premises Dynamics CRM server. The property is required for on-prem and not allowed for online. Type: string (or Expression with resultType string).|dynamicscrm_host_name|dynamics_crm_host_name|
|**--type-properties-port**|any|The port of on-premises Dynamics CRM server. The property is required for on-prem and not allowed for online. Default is 443. Type: integer (or Expression with resultType integer), minimum: 0.|dynamicscrm_port|dynamics_crm_port|
|**--type-properties-service-uri**|any|The URL to the Microsoft Dynamics CRM server. The property is required for on-line and not allowed for on-prem. Type: string (or Expression with resultType string).|dynamicscrm_service_uri|dynamics_crm_service_uri|
|**--type-properties-organization-name**|any|The organization name of the Dynamics CRM instance. The property is required for on-prem and required for online when there are more than one Dynamics CRM instances associated with the user. Type: string (or Expression with resultType string).|dynamicscrm_organization_name|dynamics_crm_organization_name|
|**--type-properties-username**|any|User name to access the Dynamics CRM instance. Type: string (or Expression with resultType string).|dynamicscrm_username|dynamics_crm_username|
|**--type-properties-password**|object|Password to access the Dynamics CRM instance.|dynamicscrm_password|dynamics_crm_password|
|**--type-properties-service-principal-id**|any|The client ID of the application in Azure Active Directory used for Server-To-Server authentication. Type: string (or Expression with resultType string).|dynamicscrm_service_principal_id|dynamics_crm_service_principal_id|
|**--type-properties-service-principal-credential-type**|choice|The service principal credential type to use in Server-To-Server authentication. 'ServicePrincipalKey' for key/secret, 'ServicePrincipalCert' for certificate. Type: string (or Expression with resultType string).|dynamicscrm_service_principal_credential_type|dynamics_crm_service_principal_credential_type|
|**--type-properties-service-principal-credential**|object|The credential of the service principal object in Azure Active Directory. If servicePrincipalCredentialType is 'ServicePrincipalKey', servicePrincipalCredential can be SecureString or AzureKeyVaultSecretReference. If servicePrincipalCredentialType is 'ServicePrincipalCert', servicePrincipalCredential can only be AzureKeyVaultSecretReference.|dynamicscrm_service_principal_credential|dynamics_crm_service_principal_credential|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|dynamicscrm_encrypted_credential|dynamics_crm_encrypted_credential|
### datafactory linked-service dynamics-crm update

dynamics-crm create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|dynamicscrm_type|dynamics_crm_type|
|**--type-properties-deployment-type**|choice|The deployment type of the Dynamics CRM instance. 'Online' for Dynamics CRM Online and 'OnPremisesWithIfd' for Dynamics CRM on-premises with Ifd. Type: string (or Expression with resultType string).|dynamicscrm_deployment_type|dynamics_crm_deployment_type|
|**--type-properties-authentication-type**|choice|The authentication type to connect to Dynamics CRM server. 'Office365' for online scenario, 'Ifd' for on-premises with Ifd scenario, 'AADServicePrincipal' for Server-To-Server authentication in online scenario. Type: string (or Expression with resultType string).|dynamicscrm_authentication_type|dynamics_crm_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|dynamicscrm_connect_via|dynamics_crm_connect_via|
|**--description**|string|Linked service description.|dynamicscrm_description|dynamics_crm_description|
|**--parameters**|dictionary|Parameters for linked service.|dynamicscrm_parameters|dynamics_crm_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|dynamicscrm_annotations|dynamics_crm_annotations|
|**--type-properties-host-name**|any|The host name of the on-premises Dynamics CRM server. The property is required for on-prem and not allowed for online. Type: string (or Expression with resultType string).|dynamicscrm_host_name|dynamics_crm_host_name|
|**--type-properties-port**|any|The port of on-premises Dynamics CRM server. The property is required for on-prem and not allowed for online. Default is 443. Type: integer (or Expression with resultType integer), minimum: 0.|dynamicscrm_port|dynamics_crm_port|
|**--type-properties-service-uri**|any|The URL to the Microsoft Dynamics CRM server. The property is required for on-line and not allowed for on-prem. Type: string (or Expression with resultType string).|dynamicscrm_service_uri|dynamics_crm_service_uri|
|**--type-properties-organization-name**|any|The organization name of the Dynamics CRM instance. The property is required for on-prem and required for online when there are more than one Dynamics CRM instances associated with the user. Type: string (or Expression with resultType string).|dynamicscrm_organization_name|dynamics_crm_organization_name|
|**--type-properties-username**|any|User name to access the Dynamics CRM instance. Type: string (or Expression with resultType string).|dynamicscrm_username|dynamics_crm_username|
|**--type-properties-password**|object|Password to access the Dynamics CRM instance.|dynamicscrm_password|dynamics_crm_password|
|**--type-properties-service-principal-id**|any|The client ID of the application in Azure Active Directory used for Server-To-Server authentication. Type: string (or Expression with resultType string).|dynamicscrm_service_principal_id|dynamics_crm_service_principal_id|
|**--type-properties-service-principal-credential-type**|choice|The service principal credential type to use in Server-To-Server authentication. 'ServicePrincipalKey' for key/secret, 'ServicePrincipalCert' for certificate. Type: string (or Expression with resultType string).|dynamicscrm_service_principal_credential_type|dynamics_crm_service_principal_credential_type|
|**--type-properties-service-principal-credential**|object|The credential of the service principal object in Azure Active Directory. If servicePrincipalCredentialType is 'ServicePrincipalKey', servicePrincipalCredential can be SecureString or AzureKeyVaultSecretReference. If servicePrincipalCredentialType is 'ServicePrincipalCert', servicePrincipalCredential can only be AzureKeyVaultSecretReference.|dynamicscrm_service_principal_credential|dynamics_crm_service_principal_credential|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|dynamicscrm_encrypted_credential|dynamics_crm_encrypted_credential|
### datafactory linked-service eloqua create

eloqua create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|eloqua_type|eloqua_type|
|**--type-properties-endpoint**|any|The endpoint of the Eloqua server. (i.e. eloqua.example.com)|eloqua_endpoint|eloqua_endpoint|
|**--type-properties-username**|any|The site name and user name of your Eloqua account in the form: sitename/username. (i.e. Eloqua/Alice)|eloqua_username|eloqua_username|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|eloqua_connect_via|eloqua_connect_via|
|**--description**|string|Linked service description.|eloqua_description|eloqua_description|
|**--parameters**|dictionary|Parameters for linked service.|eloqua_parameters|eloqua_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|eloqua_annotations|eloqua_annotations|
|**--type-properties-password**|object|The password corresponding to the user name.|eloqua_password|eloqua_password|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|eloqua_use_encrypted_endpoints|eloqua_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|eloqua_use_host_verification|eloqua_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|eloqua_use_peer_verification|eloqua_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|eloqua_encrypted_credential|eloqua_encrypted_credential|
### datafactory linked-service eloqua update

eloqua create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|eloqua_type|eloqua_type|
|**--type-properties-endpoint**|any|The endpoint of the Eloqua server. (i.e. eloqua.example.com)|eloqua_endpoint|eloqua_endpoint|
|**--type-properties-username**|any|The site name and user name of your Eloqua account in the form: sitename/username. (i.e. Eloqua/Alice)|eloqua_username|eloqua_username|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|eloqua_connect_via|eloqua_connect_via|
|**--description**|string|Linked service description.|eloqua_description|eloqua_description|
|**--parameters**|dictionary|Parameters for linked service.|eloqua_parameters|eloqua_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|eloqua_annotations|eloqua_annotations|
|**--type-properties-password**|object|The password corresponding to the user name.|eloqua_password|eloqua_password|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|eloqua_use_encrypted_endpoints|eloqua_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|eloqua_use_host_verification|eloqua_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|eloqua_use_peer_verification|eloqua_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|eloqua_encrypted_credential|eloqua_encrypted_credential|
### datafactory linked-service file-server create

file-server create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|fileserver_type|file_server_type|
|**--type-properties-host**|any|Host name of the server. Type: string (or Expression with resultType string).|fileserver_host|file_server_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|fileserver_connect_via|file_server_connect_via|
|**--description**|string|Linked service description.|fileserver_description|file_server_description|
|**--parameters**|dictionary|Parameters for linked service.|fileserver_parameters|file_server_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|fileserver_annotations|file_server_annotations|
|**--type-properties-user-id**|any|User ID to logon the server. Type: string (or Expression with resultType string).|fileserver_user_id|file_server_user_id|
|**--type-properties-password**|object|Password to logon the server.|fileserver_password|file_server_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|fileserver_encrypted_credential|file_server_encrypted_credential|
### datafactory linked-service file-server update

file-server create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|fileserver_type|file_server_type|
|**--type-properties-host**|any|Host name of the server. Type: string (or Expression with resultType string).|fileserver_host|file_server_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|fileserver_connect_via|file_server_connect_via|
|**--description**|string|Linked service description.|fileserver_description|file_server_description|
|**--parameters**|dictionary|Parameters for linked service.|fileserver_parameters|file_server_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|fileserver_annotations|file_server_annotations|
|**--type-properties-user-id**|any|User ID to logon the server. Type: string (or Expression with resultType string).|fileserver_user_id|file_server_user_id|
|**--type-properties-password**|object|Password to logon the server.|fileserver_password|file_server_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|fileserver_encrypted_credential|file_server_encrypted_credential|
### datafactory linked-service ftp-server create

ftp-server create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|ftpserver_type|ftp_server_type|
|**--type-properties-host**|any|Host name of the FTP server. Type: string (or Expression with resultType string).|ftpserver_host|ftp_server_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|ftpserver_connect_via|ftp_server_connect_via|
|**--description**|string|Linked service description.|ftpserver_description|ftp_server_description|
|**--parameters**|dictionary|Parameters for linked service.|ftpserver_parameters|ftp_server_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|ftpserver_annotations|ftp_server_annotations|
|**--type-properties-port**|any|The TCP port number that the FTP server uses to listen for client connections. Default value is 21. Type: integer (or Expression with resultType integer), minimum: 0.|ftpserver_port|ftp_server_port|
|**--type-properties-authentication-type**|choice|The authentication type to be used to connect to the FTP server.|ftpserver_authentication_type|ftp_server_authentication_type|
|**--type-properties-user-name**|any|Username to logon the FTP server. Type: string (or Expression with resultType string).|ftpserver_user_name|ftp_server_user_name|
|**--type-properties-password**|object|Password to logon the FTP server.|ftpserver_password|ftp_server_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|ftpserver_encrypted_credential|ftp_server_encrypted_credential|
|**--type-properties-enable-ssl**|any|If true, connect to the FTP server over SSL/TLS channel. Default value is true. Type: boolean (or Expression with resultType boolean).|ftpserver_enable_ssl|ftp_server_enable_ssl|
|**--type-properties-enable-server-certificate-validation**|any|If true, validate the FTP server SSL certificate when connect over SSL/TLS channel. Default value is true. Type: boolean (or Expression with resultType boolean).|ftpserver_enable_server_certificate_validation|ftp_server_enable_server_certificate_validation|
### datafactory linked-service ftp-server update

ftp-server create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|ftpserver_type|ftp_server_type|
|**--type-properties-host**|any|Host name of the FTP server. Type: string (or Expression with resultType string).|ftpserver_host|ftp_server_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|ftpserver_connect_via|ftp_server_connect_via|
|**--description**|string|Linked service description.|ftpserver_description|ftp_server_description|
|**--parameters**|dictionary|Parameters for linked service.|ftpserver_parameters|ftp_server_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|ftpserver_annotations|ftp_server_annotations|
|**--type-properties-port**|any|The TCP port number that the FTP server uses to listen for client connections. Default value is 21. Type: integer (or Expression with resultType integer), minimum: 0.|ftpserver_port|ftp_server_port|
|**--type-properties-authentication-type**|choice|The authentication type to be used to connect to the FTP server.|ftpserver_authentication_type|ftp_server_authentication_type|
|**--type-properties-user-name**|any|Username to logon the FTP server. Type: string (or Expression with resultType string).|ftpserver_user_name|ftp_server_user_name|
|**--type-properties-password**|object|Password to logon the FTP server.|ftpserver_password|ftp_server_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|ftpserver_encrypted_credential|ftp_server_encrypted_credential|
|**--type-properties-enable-ssl**|any|If true, connect to the FTP server over SSL/TLS channel. Default value is true. Type: boolean (or Expression with resultType boolean).|ftpserver_enable_ssl|ftp_server_enable_ssl|
|**--type-properties-enable-server-certificate-validation**|any|If true, validate the FTP server SSL certificate when connect over SSL/TLS channel. Default value is true. Type: boolean (or Expression with resultType boolean).|ftpserver_enable_server_certificate_validation|ftp_server_enable_server_certificate_validation|
### datafactory linked-service google-ad-words create

google-ad-words create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|googleadwords_type|google_ad_words_type|
|**--type-properties-client-customer-id**|any|The Client customer ID of the AdWords account that you want to fetch report data for.|googleadwords_client_customer_id|google_ad_words_client_customer_id|
|**--type-properties-developer-token**|object|The developer token associated with the manager account that you use to grant access to the AdWords API.|googleadwords_developer_token|google_ad_words_developer_token|
|**--type-properties-authentication-type**|choice|The OAuth 2.0 authentication mechanism used for authentication. ServiceAuthentication can only be used on self-hosted IR.|googleadwords_authentication_type|google_ad_words_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|googleadwords_connect_via|google_ad_words_connect_via|
|**--description**|string|Linked service description.|googleadwords_description|google_ad_words_description|
|**--parameters**|dictionary|Parameters for linked service.|googleadwords_parameters|google_ad_words_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|googleadwords_annotations|google_ad_words_annotations|
|**--type-properties-refresh-token**|object|The refresh token obtained from Google for authorizing access to AdWords for UserAuthentication.|googleadwords_refresh_token|google_ad_words_refresh_token|
|**--type-properties-client-id**|any|The client id of the google application used to acquire the refresh token. Type: string (or Expression with resultType string).|googleadwords_client_id|google_ad_words_client_id|
|**--type-properties-client-secret**|object|The client secret of the google application used to acquire the refresh token.|googleadwords_client_secret|google_ad_words_client_secret|
|**--type-properties-email**|any|The service account email ID that is used for ServiceAuthentication and can only be used on self-hosted IR.|googleadwords_email|google_ad_words_email|
|**--type-properties-key-file-path**|any|The full path to the .p12 key file that is used to authenticate the service account email address and can only be used on self-hosted IR.|googleadwords_key_file_path|google_ad_words_key_file_path|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|googleadwords_trusted_cert_path|google_ad_words_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|googleadwords_use_system_trust_store|google_ad_words_use_system_trust_store|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|googleadwords_encrypted_credential|google_ad_words_encrypted_credential|
### datafactory linked-service google-ad-words update

google-ad-words create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|googleadwords_type|google_ad_words_type|
|**--type-properties-client-customer-id**|any|The Client customer ID of the AdWords account that you want to fetch report data for.|googleadwords_client_customer_id|google_ad_words_client_customer_id|
|**--type-properties-developer-token**|object|The developer token associated with the manager account that you use to grant access to the AdWords API.|googleadwords_developer_token|google_ad_words_developer_token|
|**--type-properties-authentication-type**|choice|The OAuth 2.0 authentication mechanism used for authentication. ServiceAuthentication can only be used on self-hosted IR.|googleadwords_authentication_type|google_ad_words_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|googleadwords_connect_via|google_ad_words_connect_via|
|**--description**|string|Linked service description.|googleadwords_description|google_ad_words_description|
|**--parameters**|dictionary|Parameters for linked service.|googleadwords_parameters|google_ad_words_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|googleadwords_annotations|google_ad_words_annotations|
|**--type-properties-refresh-token**|object|The refresh token obtained from Google for authorizing access to AdWords for UserAuthentication.|googleadwords_refresh_token|google_ad_words_refresh_token|
|**--type-properties-client-id**|any|The client id of the google application used to acquire the refresh token. Type: string (or Expression with resultType string).|googleadwords_client_id|google_ad_words_client_id|
|**--type-properties-client-secret**|object|The client secret of the google application used to acquire the refresh token.|googleadwords_client_secret|google_ad_words_client_secret|
|**--type-properties-email**|any|The service account email ID that is used for ServiceAuthentication and can only be used on self-hosted IR.|googleadwords_email|google_ad_words_email|
|**--type-properties-key-file-path**|any|The full path to the .p12 key file that is used to authenticate the service account email address and can only be used on self-hosted IR.|googleadwords_key_file_path|google_ad_words_key_file_path|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|googleadwords_trusted_cert_path|google_ad_words_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|googleadwords_use_system_trust_store|google_ad_words_use_system_trust_store|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|googleadwords_encrypted_credential|google_ad_words_encrypted_credential|
### datafactory linked-service google-big-query create

google-big-query create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|googlebigquery_type|google_big_query_type|
|**--type-properties-project**|any|The default BigQuery project to query against.|googlebigquery_project|google_big_query_project|
|**--type-properties-authentication-type**|choice|The OAuth 2.0 authentication mechanism used for authentication. ServiceAuthentication can only be used on self-hosted IR.|googlebigquery_authentication_type|google_big_query_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|googlebigquery_connect_via|google_big_query_connect_via|
|**--description**|string|Linked service description.|googlebigquery_description|google_big_query_description|
|**--parameters**|dictionary|Parameters for linked service.|googlebigquery_parameters|google_big_query_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|googlebigquery_annotations|google_big_query_annotations|
|**--type-properties-additional-projects**|any|A comma-separated list of public BigQuery projects to access.|googlebigquery_additional_projects|google_big_query_additional_projects|
|**--type-properties-request-google-drive-scope**|any|Whether to request access to Google Drive. Allowing Google Drive access enables support for federated tables that combine BigQuery data with data from Google Drive. The default value is false.|googlebigquery_request_google_drive_scope|google_big_query_request_google_drive_scope|
|**--type-properties-refresh-token**|object|The refresh token obtained from Google for authorizing access to BigQuery for UserAuthentication.|googlebigquery_refresh_token|google_big_query_refresh_token|
|**--type-properties-client-id**|any|The client id of the google application used to acquire the refresh token. Type: string (or Expression with resultType string).|googlebigquery_client_id|google_big_query_client_id|
|**--type-properties-client-secret**|object|The client secret of the google application used to acquire the refresh token.|googlebigquery_client_secret|google_big_query_client_secret|
|**--type-properties-email**|any|The service account email ID that is used for ServiceAuthentication and can only be used on self-hosted IR.|googlebigquery_email|google_big_query_email|
|**--type-properties-key-file-path**|any|The full path to the .p12 key file that is used to authenticate the service account email address and can only be used on self-hosted IR.|googlebigquery_key_file_path|google_big_query_key_file_path|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|googlebigquery_trusted_cert_path|google_big_query_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|googlebigquery_use_system_trust_store|google_big_query_use_system_trust_store|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|googlebigquery_encrypted_credential|google_big_query_encrypted_credential|
### datafactory linked-service google-big-query update

google-big-query create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|googlebigquery_type|google_big_query_type|
|**--type-properties-project**|any|The default BigQuery project to query against.|googlebigquery_project|google_big_query_project|
|**--type-properties-authentication-type**|choice|The OAuth 2.0 authentication mechanism used for authentication. ServiceAuthentication can only be used on self-hosted IR.|googlebigquery_authentication_type|google_big_query_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|googlebigquery_connect_via|google_big_query_connect_via|
|**--description**|string|Linked service description.|googlebigquery_description|google_big_query_description|
|**--parameters**|dictionary|Parameters for linked service.|googlebigquery_parameters|google_big_query_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|googlebigquery_annotations|google_big_query_annotations|
|**--type-properties-additional-projects**|any|A comma-separated list of public BigQuery projects to access.|googlebigquery_additional_projects|google_big_query_additional_projects|
|**--type-properties-request-google-drive-scope**|any|Whether to request access to Google Drive. Allowing Google Drive access enables support for federated tables that combine BigQuery data with data from Google Drive. The default value is false.|googlebigquery_request_google_drive_scope|google_big_query_request_google_drive_scope|
|**--type-properties-refresh-token**|object|The refresh token obtained from Google for authorizing access to BigQuery for UserAuthentication.|googlebigquery_refresh_token|google_big_query_refresh_token|
|**--type-properties-client-id**|any|The client id of the google application used to acquire the refresh token. Type: string (or Expression with resultType string).|googlebigquery_client_id|google_big_query_client_id|
|**--type-properties-client-secret**|object|The client secret of the google application used to acquire the refresh token.|googlebigquery_client_secret|google_big_query_client_secret|
|**--type-properties-email**|any|The service account email ID that is used for ServiceAuthentication and can only be used on self-hosted IR.|googlebigquery_email|google_big_query_email|
|**--type-properties-key-file-path**|any|The full path to the .p12 key file that is used to authenticate the service account email address and can only be used on self-hosted IR.|googlebigquery_key_file_path|google_big_query_key_file_path|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|googlebigquery_trusted_cert_path|google_big_query_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|googlebigquery_use_system_trust_store|google_big_query_use_system_trust_store|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|googlebigquery_encrypted_credential|google_big_query_encrypted_credential|
### datafactory linked-service google-cloud-storage create

google-cloud-storage create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|googlecloudstorage_type|google_cloud_storage_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|googlecloudstorage_connect_via|google_cloud_storage_connect_via|
|**--description**|string|Linked service description.|googlecloudstorage_description|google_cloud_storage_description|
|**--parameters**|dictionary|Parameters for linked service.|googlecloudstorage_parameters|google_cloud_storage_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|googlecloudstorage_annotations|google_cloud_storage_annotations|
|**--type-properties-access-key-id**|any|The access key identifier of the Google Cloud Storage Identity and Access Management (IAM) user. Type: string (or Expression with resultType string).|googlecloudstorage_access_key_id|google_cloud_storage_access_key_id|
|**--type-properties-secret-access-key**|object|The secret access key of the Google Cloud Storage Identity and Access Management (IAM) user.|googlecloudstorage_secret_access_key|google_cloud_storage_secret_access_key|
|**--type-properties-service-url**|any|This value specifies the endpoint to access with the Google Cloud Storage Connector. This is an optional property; change it only if you want to try a different service endpoint or want to switch between https and http. Type: string (or Expression with resultType string).|googlecloudstorage_service_url|google_cloud_storage_service_url|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|googlecloudstorage_encrypted_credential|google_cloud_storage_encrypted_credential|
### datafactory linked-service google-cloud-storage update

google-cloud-storage create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|googlecloudstorage_type|google_cloud_storage_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|googlecloudstorage_connect_via|google_cloud_storage_connect_via|
|**--description**|string|Linked service description.|googlecloudstorage_description|google_cloud_storage_description|
|**--parameters**|dictionary|Parameters for linked service.|googlecloudstorage_parameters|google_cloud_storage_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|googlecloudstorage_annotations|google_cloud_storage_annotations|
|**--type-properties-access-key-id**|any|The access key identifier of the Google Cloud Storage Identity and Access Management (IAM) user. Type: string (or Expression with resultType string).|googlecloudstorage_access_key_id|google_cloud_storage_access_key_id|
|**--type-properties-secret-access-key**|object|The secret access key of the Google Cloud Storage Identity and Access Management (IAM) user.|googlecloudstorage_secret_access_key|google_cloud_storage_secret_access_key|
|**--type-properties-service-url**|any|This value specifies the endpoint to access with the Google Cloud Storage Connector. This is an optional property; change it only if you want to try a different service endpoint or want to switch between https and http. Type: string (or Expression with resultType string).|googlecloudstorage_service_url|google_cloud_storage_service_url|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|googlecloudstorage_encrypted_credential|google_cloud_storage_encrypted_credential|
### datafactory linked-service greenplum create

greenplum create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|greenplum_type|greenplum_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|greenplum_connect_via|greenplum_connect_via|
|**--description**|string|Linked service description.|greenplum_description|greenplum_description|
|**--parameters**|dictionary|Parameters for linked service.|greenplum_parameters|greenplum_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|greenplum_annotations|greenplum_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|greenplum_connection_string|greenplum_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|greenplum_pwd|greenplum_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|greenplum_encrypted_credential|greenplum_encrypted_credential|
### datafactory linked-service greenplum update

greenplum create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|greenplum_type|greenplum_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|greenplum_connect_via|greenplum_connect_via|
|**--description**|string|Linked service description.|greenplum_description|greenplum_description|
|**--parameters**|dictionary|Parameters for linked service.|greenplum_parameters|greenplum_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|greenplum_annotations|greenplum_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|greenplum_connection_string|greenplum_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|greenplum_pwd|greenplum_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|greenplum_encrypted_credential|greenplum_encrypted_credential|
### datafactory linked-service h-base create

h-base create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|hbase_type|h_base_type|
|**--type-properties-host**|any|The IP address or host name of the HBase server. (i.e. 192.168.222.160)|hbase_host|h_base_host|
|**--type-properties-authentication-type**|choice|The authentication mechanism to use to connect to the HBase server.|hbase_authentication_type|h_base_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|hbase_connect_via|h_base_connect_via|
|**--description**|string|Linked service description.|hbase_description|h_base_description|
|**--parameters**|dictionary|Parameters for linked service.|hbase_parameters|h_base_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hbase_annotations|h_base_annotations|
|**--type-properties-port**|any|The TCP port that the HBase instance uses to listen for client connections. The default value is 9090.|hbase_port|h_base_port|
|**--type-properties-http-path**|any|The partial URL corresponding to the HBase server. (i.e. /gateway/sandbox/hbase/version)|hbase_http_path|h_base_http_path|
|**--type-properties-username**|any|The user name used to connect to the HBase instance.|hbase_username|h_base_username|
|**--type-properties-password**|object|The password corresponding to the user name.|hbase_password|h_base_password|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|hbase_enable_ssl|h_base_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|hbase_trusted_cert_path|h_base_trusted_cert_path|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|hbase_allow_host_name_cn_mismatch|h_base_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|hbase_allow_self_signed_server_cert|h_base_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hbase_encrypted_credential|h_base_encrypted_credential|
### datafactory linked-service h-base update

h-base create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|hbase_type|h_base_type|
|**--type-properties-host**|any|The IP address or host name of the HBase server. (i.e. 192.168.222.160)|hbase_host|h_base_host|
|**--type-properties-authentication-type**|choice|The authentication mechanism to use to connect to the HBase server.|hbase_authentication_type|h_base_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|hbase_connect_via|h_base_connect_via|
|**--description**|string|Linked service description.|hbase_description|h_base_description|
|**--parameters**|dictionary|Parameters for linked service.|hbase_parameters|h_base_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hbase_annotations|h_base_annotations|
|**--type-properties-port**|any|The TCP port that the HBase instance uses to listen for client connections. The default value is 9090.|hbase_port|h_base_port|
|**--type-properties-http-path**|any|The partial URL corresponding to the HBase server. (i.e. /gateway/sandbox/hbase/version)|hbase_http_path|h_base_http_path|
|**--type-properties-username**|any|The user name used to connect to the HBase instance.|hbase_username|h_base_username|
|**--type-properties-password**|object|The password corresponding to the user name.|hbase_password|h_base_password|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|hbase_enable_ssl|h_base_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|hbase_trusted_cert_path|h_base_trusted_cert_path|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|hbase_allow_host_name_cn_mismatch|h_base_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|hbase_allow_self_signed_server_cert|h_base_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hbase_encrypted_credential|h_base_encrypted_credential|
### datafactory linked-service h-d-insight create

h-d-insight create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|hdinsight_type|h_d_insight_type|
|**--type-properties-cluster-uri**|any|HDInsight cluster URI. Type: string (or Expression with resultType string).|hdinsight_cluster_uri|h_d_insight_cluster_uri|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|hdinsight_connect_via|h_d_insight_connect_via|
|**--description**|string|Linked service description.|hdinsight_description|h_d_insight_description|
|**--parameters**|dictionary|Parameters for linked service.|hdinsight_parameters|h_d_insight_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hdinsight_annotations|h_d_insight_annotations|
|**--type-properties-user-name**|any|HDInsight cluster user name. Type: string (or Expression with resultType string).|hdinsight_user_name|h_d_insight_user_name|
|**--type-properties-password**|object|HDInsight cluster password.|hdinsight_password|h_d_insight_password|
|**--type-properties-linked-service-name**|object|The Azure Storage linked service reference.|hdinsight_linked_service_name|h_d_insight_linked_service_name|
|**--type-properties-hcatalog-linked-service-name**|object|A reference to the Azure SQL linked service that points to the HCatalog database.|hdinsight_hcatalog_linked_service_name|h_d_insight_hcatalog_linked_service_name|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hdinsight_encrypted_credential|h_d_insight_encrypted_credential|
|**--type-properties-is-esp-enabled**|any|Specify if the HDInsight is created with ESP (Enterprise Security Package). Type: Boolean.|hdinsight_is_esp_enabled|h_d_insight_is_esp_enabled|
|**--type-properties-file-system**|any|Specify the FileSystem if the main storage for the HDInsight is ADLS Gen2. Type: string (or Expression with resultType string).|hdinsight_file_system|h_d_insight_file_system|
### datafactory linked-service h-d-insight update

h-d-insight create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|hdinsight_type|h_d_insight_type|
|**--type-properties-cluster-uri**|any|HDInsight cluster URI. Type: string (or Expression with resultType string).|hdinsight_cluster_uri|h_d_insight_cluster_uri|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|hdinsight_connect_via|h_d_insight_connect_via|
|**--description**|string|Linked service description.|hdinsight_description|h_d_insight_description|
|**--parameters**|dictionary|Parameters for linked service.|hdinsight_parameters|h_d_insight_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hdinsight_annotations|h_d_insight_annotations|
|**--type-properties-user-name**|any|HDInsight cluster user name. Type: string (or Expression with resultType string).|hdinsight_user_name|h_d_insight_user_name|
|**--type-properties-password**|object|HDInsight cluster password.|hdinsight_password|h_d_insight_password|
|**--type-properties-linked-service-name**|object|The Azure Storage linked service reference.|hdinsight_linked_service_name|h_d_insight_linked_service_name|
|**--type-properties-hcatalog-linked-service-name**|object|A reference to the Azure SQL linked service that points to the HCatalog database.|hdinsight_hcatalog_linked_service_name|h_d_insight_hcatalog_linked_service_name|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hdinsight_encrypted_credential|h_d_insight_encrypted_credential|
|**--type-properties-is-esp-enabled**|any|Specify if the HDInsight is created with ESP (Enterprise Security Package). Type: Boolean.|hdinsight_is_esp_enabled|h_d_insight_is_esp_enabled|
|**--type-properties-file-system**|any|Specify the FileSystem if the main storage for the HDInsight is ADLS Gen2. Type: string (or Expression with resultType string).|hdinsight_file_system|h_d_insight_file_system|
### datafactory linked-service h-d-insight-on-demand create

h-d-insight-on-demand create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|hdinsightondemand_type|h_d_insight_on_demand_type|
|**--type-properties-cluster-size**|any|Number of worker/data nodes in the cluster. Suggestion value: 4. Type: string (or Expression with resultType string).|hdinsightondemand_cluster_size|h_d_insight_on_demand_cluster_size|
|**--type-properties-time-to-live**|any|The allowed idle time for the on-demand HDInsight cluster. Specifies how long the on-demand HDInsight cluster stays alive after completion of an activity run if there are no other active jobs in the cluster. The minimum value is 5 mins. Type: string (or Expression with resultType string).|hdinsightondemand_time_to_live|h_d_insight_on_demand_time_to_live|
|**--type-properties-version**|any|Version of the HDInsight cluster.  Type: string (or Expression with resultType string).|hdinsightondemand_version|h_d_insight_on_demand_version|
|**--type-properties-linked-service-name**|object|Azure Storage linked service to be used by the on-demand cluster for storing and processing data.|hdinsightondemand_linked_service_name|h_d_insight_on_demand_linked_service_name|
|**--type-properties-host-subscription-id**|any|The customer’s subscription to host the cluster. Type: string (or Expression with resultType string).|hdinsightondemand_host_subscription_id|h_d_insight_on_demand_host_subscription_id|
|**--type-properties-tenant**|any|The Tenant id/name to which the service principal belongs. Type: string (or Expression with resultType string).|hdinsightondemand_tenant|h_d_insight_on_demand_tenant|
|**--type-properties-cluster-resource-group**|any|The resource group where the cluster belongs. Type: string (or Expression with resultType string).|hdinsightondemand_cluster_resource_group|h_d_insight_on_demand_cluster_resource_group|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|hdinsightondemand_connect_via|h_d_insight_on_demand_connect_via|
|**--description**|string|Linked service description.|hdinsightondemand_description|h_d_insight_on_demand_description|
|**--parameters**|dictionary|Parameters for linked service.|hdinsightondemand_parameters|h_d_insight_on_demand_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hdinsightondemand_annotations|h_d_insight_on_demand_annotations|
|**--type-properties-service-principal-id**|any|The service principal id for the hostSubscriptionId. Type: string (or Expression with resultType string).|hdinsightondemand_service_principal_id|h_d_insight_on_demand_service_principal_id|
|**--type-properties-service-principal-key**|object|The key for the service principal id.|hdinsightondemand_service_principal_key|h_d_insight_on_demand_service_principal_key|
|**--type-properties-cluster-name-prefix**|any|The prefix of cluster name, postfix will be distinct with timestamp. Type: string (or Expression with resultType string).|hdinsightondemand_cluster_name_prefix|h_d_insight_on_demand_cluster_name_prefix|
|**--type-properties-cluster-user-name**|any|The username to access the cluster. Type: string (or Expression with resultType string).|hdinsightondemand_cluster_user_name|h_d_insight_on_demand_cluster_user_name|
|**--type-properties-cluster-password**|object|The password to access the cluster.|hdinsightondemand_cluster_password|h_d_insight_on_demand_cluster_password|
|**--type-properties-cluster-ssh-user-name**|any|The username to SSH remotely connect to cluster’s node (for Linux). Type: string (or Expression with resultType string).|hdinsightondemand_cluster_ssh_user_name|h_d_insight_on_demand_cluster_ssh_user_name|
|**--type-properties-cluster-ssh-password**|object|The password to SSH remotely connect cluster’s node (for Linux).|hdinsightondemand_cluster_ssh_password|h_d_insight_on_demand_cluster_ssh_password|
|**--type-properties-additional-linked-service-names**|array|Specifies additional storage accounts for the HDInsight linked service so that the Data Factory service can register them on your behalf.|hdinsightondemand_additional_linked_service_names|h_d_insight_on_demand_additional_linked_service_names|
|**--type-properties-hcatalog-linked-service-name**|object|The name of Azure SQL linked service that point to the HCatalog database. The on-demand HDInsight cluster is created by using the Azure SQL database as the metastore.|hdinsightondemand_hcatalog_linked_service_name|h_d_insight_on_demand_hcatalog_linked_service_name|
|**--type-properties-cluster-type**|any|The cluster type. Type: string (or Expression with resultType string).|hdinsightondemand_cluster_type|h_d_insight_on_demand_cluster_type|
|**--type-properties-spark-version**|any|The version of spark if the cluster type is 'spark'. Type: string (or Expression with resultType string).|hdinsightondemand_spark_version|h_d_insight_on_demand_spark_version|
|**--type-properties-core-configuration**|any|Specifies the core configuration parameters (as in core-site.xml) for the HDInsight cluster to be created.|hdinsightondemand_core_configuration|h_d_insight_on_demand_core_configuration|
|**--type-properties-h-base-configuration**|any|Specifies the HBase configuration parameters (hbase-site.xml) for the HDInsight cluster.|hdinsightondemand_h_base_configuration|h_d_insight_on_demand_h_base_configuration|
|**--type-properties-hdfs-configuration**|any|Specifies the HDFS configuration parameters (hdfs-site.xml) for the HDInsight cluster.|hdinsightondemand_hdfs_configuration|h_d_insight_on_demand_hdfs_configuration|
|**--type-properties-hive-configuration**|any|Specifies the hive configuration parameters (hive-site.xml) for the HDInsight cluster.|hdinsightondemand_hive_configuration|h_d_insight_on_demand_hive_configuration|
|**--type-properties-map-reduce-configuration**|any|Specifies the MapReduce configuration parameters (mapred-site.xml) for the HDInsight cluster.|hdinsightondemand_map_reduce_configuration|h_d_insight_on_demand_map_reduce_configuration|
|**--type-properties-oozie-configuration**|any|Specifies the Oozie configuration parameters (oozie-site.xml) for the HDInsight cluster.|hdinsightondemand_oozie_configuration|h_d_insight_on_demand_oozie_configuration|
|**--type-properties-storm-configuration**|any|Specifies the Storm configuration parameters (storm-site.xml) for the HDInsight cluster.|hdinsightondemand_storm_configuration|h_d_insight_on_demand_storm_configuration|
|**--type-properties-yarn-configuration**|any|Specifies the Yarn configuration parameters (yarn-site.xml) for the HDInsight cluster.|hdinsightondemand_yarn_configuration|h_d_insight_on_demand_yarn_configuration|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hdinsightondemand_encrypted_credential|h_d_insight_on_demand_encrypted_credential|
|**--type-properties-head-node-size**|any|Specifies the size of the head node for the HDInsight cluster.|hdinsightondemand_head_node_size|h_d_insight_on_demand_head_node_size|
|**--type-properties-data-node-size**|any|Specifies the size of the data node for the HDInsight cluster.|hdinsightondemand_data_node_size|h_d_insight_on_demand_data_node_size|
|**--type-properties-zookeeper-node-size**|any|Specifies the size of the Zoo Keeper node for the HDInsight cluster.|hdinsightondemand_zookeeper_node_size|h_d_insight_on_demand_zookeeper_node_size|
|**--type-properties-script-actions**|array|Custom script actions to run on HDI ondemand cluster once it's up. Please refer to https://docs.microsoft.com/en-us/azure/hdinsight/hdinsight-hadoop-customize-cluster-linux?toc=%2Fen-us%2Fazure%2Fhdinsight%2Fr-server%2FTOC.json&bc=%2Fen-us%2Fazure%2Fbread%2Ftoc.json#understanding-script-actions.|hdinsightondemand_script_actions|h_d_insight_on_demand_script_actions|
|**--type-properties-virtual-network-id**|any|The ARM resource ID for the vNet to which the cluster should be joined after creation. Type: string (or Expression with resultType string).|hdinsightondemand_virtual_network_id|h_d_insight_on_demand_virtual_network_id|
|**--type-properties-subnet-name**|any|The ARM resource ID for the subnet in the vNet. If virtualNetworkId was specified, then this property is required. Type: string (or Expression with resultType string).|hdinsightondemand_subnet_name|h_d_insight_on_demand_subnet_name|
### datafactory linked-service h-d-insight-on-demand update

h-d-insight-on-demand create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|hdinsightondemand_type|h_d_insight_on_demand_type|
|**--type-properties-cluster-size**|any|Number of worker/data nodes in the cluster. Suggestion value: 4. Type: string (or Expression with resultType string).|hdinsightondemand_cluster_size|h_d_insight_on_demand_cluster_size|
|**--type-properties-time-to-live**|any|The allowed idle time for the on-demand HDInsight cluster. Specifies how long the on-demand HDInsight cluster stays alive after completion of an activity run if there are no other active jobs in the cluster. The minimum value is 5 mins. Type: string (or Expression with resultType string).|hdinsightondemand_time_to_live|h_d_insight_on_demand_time_to_live|
|**--type-properties-version**|any|Version of the HDInsight cluster.  Type: string (or Expression with resultType string).|hdinsightondemand_version|h_d_insight_on_demand_version|
|**--type-properties-linked-service-name**|object|Azure Storage linked service to be used by the on-demand cluster for storing and processing data.|hdinsightondemand_linked_service_name|h_d_insight_on_demand_linked_service_name|
|**--type-properties-host-subscription-id**|any|The customer’s subscription to host the cluster. Type: string (or Expression with resultType string).|hdinsightondemand_host_subscription_id|h_d_insight_on_demand_host_subscription_id|
|**--type-properties-tenant**|any|The Tenant id/name to which the service principal belongs. Type: string (or Expression with resultType string).|hdinsightondemand_tenant|h_d_insight_on_demand_tenant|
|**--type-properties-cluster-resource-group**|any|The resource group where the cluster belongs. Type: string (or Expression with resultType string).|hdinsightondemand_cluster_resource_group|h_d_insight_on_demand_cluster_resource_group|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|hdinsightondemand_connect_via|h_d_insight_on_demand_connect_via|
|**--description**|string|Linked service description.|hdinsightondemand_description|h_d_insight_on_demand_description|
|**--parameters**|dictionary|Parameters for linked service.|hdinsightondemand_parameters|h_d_insight_on_demand_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hdinsightondemand_annotations|h_d_insight_on_demand_annotations|
|**--type-properties-service-principal-id**|any|The service principal id for the hostSubscriptionId. Type: string (or Expression with resultType string).|hdinsightondemand_service_principal_id|h_d_insight_on_demand_service_principal_id|
|**--type-properties-service-principal-key**|object|The key for the service principal id.|hdinsightondemand_service_principal_key|h_d_insight_on_demand_service_principal_key|
|**--type-properties-cluster-name-prefix**|any|The prefix of cluster name, postfix will be distinct with timestamp. Type: string (or Expression with resultType string).|hdinsightondemand_cluster_name_prefix|h_d_insight_on_demand_cluster_name_prefix|
|**--type-properties-cluster-user-name**|any|The username to access the cluster. Type: string (or Expression with resultType string).|hdinsightondemand_cluster_user_name|h_d_insight_on_demand_cluster_user_name|
|**--type-properties-cluster-password**|object|The password to access the cluster.|hdinsightondemand_cluster_password|h_d_insight_on_demand_cluster_password|
|**--type-properties-cluster-ssh-user-name**|any|The username to SSH remotely connect to cluster’s node (for Linux). Type: string (or Expression with resultType string).|hdinsightondemand_cluster_ssh_user_name|h_d_insight_on_demand_cluster_ssh_user_name|
|**--type-properties-cluster-ssh-password**|object|The password to SSH remotely connect cluster’s node (for Linux).|hdinsightondemand_cluster_ssh_password|h_d_insight_on_demand_cluster_ssh_password|
|**--type-properties-additional-linked-service-names**|array|Specifies additional storage accounts for the HDInsight linked service so that the Data Factory service can register them on your behalf.|hdinsightondemand_additional_linked_service_names|h_d_insight_on_demand_additional_linked_service_names|
|**--type-properties-hcatalog-linked-service-name**|object|The name of Azure SQL linked service that point to the HCatalog database. The on-demand HDInsight cluster is created by using the Azure SQL database as the metastore.|hdinsightondemand_hcatalog_linked_service_name|h_d_insight_on_demand_hcatalog_linked_service_name|
|**--type-properties-cluster-type**|any|The cluster type. Type: string (or Expression with resultType string).|hdinsightondemand_cluster_type|h_d_insight_on_demand_cluster_type|
|**--type-properties-spark-version**|any|The version of spark if the cluster type is 'spark'. Type: string (or Expression with resultType string).|hdinsightondemand_spark_version|h_d_insight_on_demand_spark_version|
|**--type-properties-core-configuration**|any|Specifies the core configuration parameters (as in core-site.xml) for the HDInsight cluster to be created.|hdinsightondemand_core_configuration|h_d_insight_on_demand_core_configuration|
|**--type-properties-h-base-configuration**|any|Specifies the HBase configuration parameters (hbase-site.xml) for the HDInsight cluster.|hdinsightondemand_h_base_configuration|h_d_insight_on_demand_h_base_configuration|
|**--type-properties-hdfs-configuration**|any|Specifies the HDFS configuration parameters (hdfs-site.xml) for the HDInsight cluster.|hdinsightondemand_hdfs_configuration|h_d_insight_on_demand_hdfs_configuration|
|**--type-properties-hive-configuration**|any|Specifies the hive configuration parameters (hive-site.xml) for the HDInsight cluster.|hdinsightondemand_hive_configuration|h_d_insight_on_demand_hive_configuration|
|**--type-properties-map-reduce-configuration**|any|Specifies the MapReduce configuration parameters (mapred-site.xml) for the HDInsight cluster.|hdinsightondemand_map_reduce_configuration|h_d_insight_on_demand_map_reduce_configuration|
|**--type-properties-oozie-configuration**|any|Specifies the Oozie configuration parameters (oozie-site.xml) for the HDInsight cluster.|hdinsightondemand_oozie_configuration|h_d_insight_on_demand_oozie_configuration|
|**--type-properties-storm-configuration**|any|Specifies the Storm configuration parameters (storm-site.xml) for the HDInsight cluster.|hdinsightondemand_storm_configuration|h_d_insight_on_demand_storm_configuration|
|**--type-properties-yarn-configuration**|any|Specifies the Yarn configuration parameters (yarn-site.xml) for the HDInsight cluster.|hdinsightondemand_yarn_configuration|h_d_insight_on_demand_yarn_configuration|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hdinsightondemand_encrypted_credential|h_d_insight_on_demand_encrypted_credential|
|**--type-properties-head-node-size**|any|Specifies the size of the head node for the HDInsight cluster.|hdinsightondemand_head_node_size|h_d_insight_on_demand_head_node_size|
|**--type-properties-data-node-size**|any|Specifies the size of the data node for the HDInsight cluster.|hdinsightondemand_data_node_size|h_d_insight_on_demand_data_node_size|
|**--type-properties-zookeeper-node-size**|any|Specifies the size of the Zoo Keeper node for the HDInsight cluster.|hdinsightondemand_zookeeper_node_size|h_d_insight_on_demand_zookeeper_node_size|
|**--type-properties-script-actions**|array|Custom script actions to run on HDI ondemand cluster once it's up. Please refer to https://docs.microsoft.com/en-us/azure/hdinsight/hdinsight-hadoop-customize-cluster-linux?toc=%2Fen-us%2Fazure%2Fhdinsight%2Fr-server%2FTOC.json&bc=%2Fen-us%2Fazure%2Fbread%2Ftoc.json#understanding-script-actions.|hdinsightondemand_script_actions|h_d_insight_on_demand_script_actions|
|**--type-properties-virtual-network-id**|any|The ARM resource ID for the vNet to which the cluster should be joined after creation. Type: string (or Expression with resultType string).|hdinsightondemand_virtual_network_id|h_d_insight_on_demand_virtual_network_id|
|**--type-properties-subnet-name**|any|The ARM resource ID for the subnet in the vNet. If virtualNetworkId was specified, then this property is required. Type: string (or Expression with resultType string).|hdinsightondemand_subnet_name|h_d_insight_on_demand_subnet_name|
### datafactory linked-service hdfs create

hdfs create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|hdfs_type|hdfs_type|
|**--type-properties-url**|any|The URL of the HDFS service endpoint, e.g. http://myhostname:50070/webhdfs/v1 . Type: string (or Expression with resultType string).|hdfs_url|hdfs_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|hdfs_connect_via|hdfs_connect_via|
|**--description**|string|Linked service description.|hdfs_description|hdfs_description|
|**--parameters**|dictionary|Parameters for linked service.|hdfs_parameters|hdfs_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hdfs_annotations|hdfs_annotations|
|**--type-properties-authentication-type**|any|Type of authentication used to connect to the HDFS. Possible values are: Anonymous and Windows. Type: string (or Expression with resultType string).|hdfs_authentication_type|hdfs_authentication_type|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hdfs_encrypted_credential|hdfs_encrypted_credential|
|**--type-properties-user-name**|any|User name for Windows authentication. Type: string (or Expression with resultType string).|hdfs_user_name|hdfs_user_name|
|**--type-properties-password**|object|Password for Windows authentication.|hdfs_password|hdfs_password|
### datafactory linked-service hdfs update

hdfs create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|hdfs_type|hdfs_type|
|**--type-properties-url**|any|The URL of the HDFS service endpoint, e.g. http://myhostname:50070/webhdfs/v1 . Type: string (or Expression with resultType string).|hdfs_url|hdfs_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|hdfs_connect_via|hdfs_connect_via|
|**--description**|string|Linked service description.|hdfs_description|hdfs_description|
|**--parameters**|dictionary|Parameters for linked service.|hdfs_parameters|hdfs_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hdfs_annotations|hdfs_annotations|
|**--type-properties-authentication-type**|any|Type of authentication used to connect to the HDFS. Possible values are: Anonymous and Windows. Type: string (or Expression with resultType string).|hdfs_authentication_type|hdfs_authentication_type|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hdfs_encrypted_credential|hdfs_encrypted_credential|
|**--type-properties-user-name**|any|User name for Windows authentication. Type: string (or Expression with resultType string).|hdfs_user_name|hdfs_user_name|
|**--type-properties-password**|object|Password for Windows authentication.|hdfs_password|hdfs_password|
### datafactory linked-service hive create

hive create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|hive_type|hive_type|
|**--type-properties-host**|any|IP address or host name of the Hive server, separated by ';' for multiple hosts (only when serviceDiscoveryMode is enable).|hive_host|hive_host|
|**--type-properties-authentication-type**|choice|The authentication method used to access the Hive server.|hive_authentication_type|hive_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|hive_connect_via|hive_connect_via|
|**--description**|string|Linked service description.|hive_description|hive_description|
|**--parameters**|dictionary|Parameters for linked service.|hive_parameters|hive_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hive_annotations|hive_annotations|
|**--type-properties-port**|any|The TCP port that the Hive server uses to listen for client connections.|hive_port|hive_port|
|**--type-properties-server-type**|choice|The type of Hive server.|hive_server_type|hive_server_type|
|**--type-properties-thrift-transport-protocol**|choice|The transport protocol to use in the Thrift layer.|hive_thrift_transport_protocol|hive_thrift_transport_protocol|
|**--type-properties-service-discovery-mode**|any|true to indicate using the ZooKeeper service, false not.|hive_service_discovery_mode|hive_service_discovery_mode|
|**--type-properties-zoo-keeper-name-space**|any|The namespace on ZooKeeper under which Hive Server 2 nodes are added.|hive_zoo_keeper_name_space|hive_zoo_keeper_name_space|
|**--type-properties-use-native-query**|any|Specifies whether the driver uses native HiveQL queries,or converts them into an equivalent form in HiveQL.|hive_use_native_query|hive_use_native_query|
|**--type-properties-username**|any|The user name that you use to access Hive Server.|hive_username|hive_username|
|**--type-properties-password**|object|The password corresponding to the user name that you provided in the Username field|hive_password|hive_password|
|**--type-properties-http-path**|any|The partial URL corresponding to the Hive server.|hive_http_path|hive_http_path|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|hive_enable_ssl|hive_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|hive_trusted_cert_path|hive_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|hive_use_system_trust_store|hive_use_system_trust_store|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|hive_allow_host_name_cn_mismatch|hive_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|hive_allow_self_signed_server_cert|hive_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hive_encrypted_credential|hive_encrypted_credential|
### datafactory linked-service hive update

hive create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|hive_type|hive_type|
|**--type-properties-host**|any|IP address or host name of the Hive server, separated by ';' for multiple hosts (only when serviceDiscoveryMode is enable).|hive_host|hive_host|
|**--type-properties-authentication-type**|choice|The authentication method used to access the Hive server.|hive_authentication_type|hive_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|hive_connect_via|hive_connect_via|
|**--description**|string|Linked service description.|hive_description|hive_description|
|**--parameters**|dictionary|Parameters for linked service.|hive_parameters|hive_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hive_annotations|hive_annotations|
|**--type-properties-port**|any|The TCP port that the Hive server uses to listen for client connections.|hive_port|hive_port|
|**--type-properties-server-type**|choice|The type of Hive server.|hive_server_type|hive_server_type|
|**--type-properties-thrift-transport-protocol**|choice|The transport protocol to use in the Thrift layer.|hive_thrift_transport_protocol|hive_thrift_transport_protocol|
|**--type-properties-service-discovery-mode**|any|true to indicate using the ZooKeeper service, false not.|hive_service_discovery_mode|hive_service_discovery_mode|
|**--type-properties-zoo-keeper-name-space**|any|The namespace on ZooKeeper under which Hive Server 2 nodes are added.|hive_zoo_keeper_name_space|hive_zoo_keeper_name_space|
|**--type-properties-use-native-query**|any|Specifies whether the driver uses native HiveQL queries,or converts them into an equivalent form in HiveQL.|hive_use_native_query|hive_use_native_query|
|**--type-properties-username**|any|The user name that you use to access Hive Server.|hive_username|hive_username|
|**--type-properties-password**|object|The password corresponding to the user name that you provided in the Username field|hive_password|hive_password|
|**--type-properties-http-path**|any|The partial URL corresponding to the Hive server.|hive_http_path|hive_http_path|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|hive_enable_ssl|hive_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|hive_trusted_cert_path|hive_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|hive_use_system_trust_store|hive_use_system_trust_store|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|hive_allow_host_name_cn_mismatch|hive_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|hive_allow_self_signed_server_cert|hive_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hive_encrypted_credential|hive_encrypted_credential|
### datafactory linked-service http-server create

http-server create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|httpserver_type|http_server_type|
|**--type-properties-url**|any|The base URL of the HTTP endpoint, e.g. http://www.microsoft.com. Type: string (or Expression with resultType string).|httpserver_url|http_server_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|httpserver_connect_via|http_server_connect_via|
|**--description**|string|Linked service description.|httpserver_description|http_server_description|
|**--parameters**|dictionary|Parameters for linked service.|httpserver_parameters|http_server_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|httpserver_annotations|http_server_annotations|
|**--type-properties-authentication-type**|choice|The authentication type to be used to connect to the HTTP server.|httpserver_authentication_type|http_server_authentication_type|
|**--type-properties-user-name**|any|User name for Basic, Digest, or Windows authentication. Type: string (or Expression with resultType string).|httpserver_user_name|http_server_user_name|
|**--type-properties-password**|object|Password for Basic, Digest, Windows, or ClientCertificate with EmbeddedCertData authentication.|httpserver_password|http_server_password|
|**--type-properties-embedded-cert-data**|any|Base64 encoded certificate data for ClientCertificate authentication. For on-premises copy with ClientCertificate authentication, either CertThumbprint or EmbeddedCertData/Password should be specified. Type: string (or Expression with resultType string).|httpserver_embedded_cert_data|http_server_embedded_cert_data|
|**--type-properties-cert-thumbprint**|any|Thumbprint of certificate for ClientCertificate authentication. Only valid for on-premises copy. For on-premises copy with ClientCertificate authentication, either CertThumbprint or EmbeddedCertData/Password should be specified. Type: string (or Expression with resultType string).|httpserver_cert_thumbprint|http_server_cert_thumbprint|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|httpserver_encrypted_credential|http_server_encrypted_credential|
|**--type-properties-enable-server-certificate-validation**|any|If true, validate the HTTPS server SSL certificate. Default value is true. Type: boolean (or Expression with resultType boolean).|httpserver_enable_server_certificate_validation|http_server_enable_server_certificate_validation|
### datafactory linked-service http-server update

http-server create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|httpserver_type|http_server_type|
|**--type-properties-url**|any|The base URL of the HTTP endpoint, e.g. http://www.microsoft.com. Type: string (or Expression with resultType string).|httpserver_url|http_server_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|httpserver_connect_via|http_server_connect_via|
|**--description**|string|Linked service description.|httpserver_description|http_server_description|
|**--parameters**|dictionary|Parameters for linked service.|httpserver_parameters|http_server_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|httpserver_annotations|http_server_annotations|
|**--type-properties-authentication-type**|choice|The authentication type to be used to connect to the HTTP server.|httpserver_authentication_type|http_server_authentication_type|
|**--type-properties-user-name**|any|User name for Basic, Digest, or Windows authentication. Type: string (or Expression with resultType string).|httpserver_user_name|http_server_user_name|
|**--type-properties-password**|object|Password for Basic, Digest, Windows, or ClientCertificate with EmbeddedCertData authentication.|httpserver_password|http_server_password|
|**--type-properties-embedded-cert-data**|any|Base64 encoded certificate data for ClientCertificate authentication. For on-premises copy with ClientCertificate authentication, either CertThumbprint or EmbeddedCertData/Password should be specified. Type: string (or Expression with resultType string).|httpserver_embedded_cert_data|http_server_embedded_cert_data|
|**--type-properties-cert-thumbprint**|any|Thumbprint of certificate for ClientCertificate authentication. Only valid for on-premises copy. For on-premises copy with ClientCertificate authentication, either CertThumbprint or EmbeddedCertData/Password should be specified. Type: string (or Expression with resultType string).|httpserver_cert_thumbprint|http_server_cert_thumbprint|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|httpserver_encrypted_credential|http_server_encrypted_credential|
|**--type-properties-enable-server-certificate-validation**|any|If true, validate the HTTPS server SSL certificate. Default value is true. Type: boolean (or Expression with resultType boolean).|httpserver_enable_server_certificate_validation|http_server_enable_server_certificate_validation|
### datafactory linked-service hubspot create

hubspot create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|hubspot_type|hubspot_type|
|**--type-properties-client-id**|any|The client ID associated with your Hubspot application.|hubspot_client_id|hubspot_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|hubspot_connect_via|hubspot_connect_via|
|**--description**|string|Linked service description.|hubspot_description|hubspot_description|
|**--parameters**|dictionary|Parameters for linked service.|hubspot_parameters|hubspot_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hubspot_annotations|hubspot_annotations|
|**--type-properties-client-secret**|object|The client secret associated with your Hubspot application.|hubspot_client_secret|hubspot_client_secret|
|**--type-properties-access-token**|object|The access token obtained when initially authenticating your OAuth integration.|hubspot_access_token|hubspot_access_token|
|**--type-properties-refresh-token**|object|The refresh token obtained when initially authenticating your OAuth integration.|hubspot_refresh_token|hubspot_refresh_token|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|hubspot_use_encrypted_endpoints|hubspot_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|hubspot_use_host_verification|hubspot_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|hubspot_use_peer_verification|hubspot_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hubspot_encrypted_credential|hubspot_encrypted_credential|
### datafactory linked-service hubspot update

hubspot create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|hubspot_type|hubspot_type|
|**--type-properties-client-id**|any|The client ID associated with your Hubspot application.|hubspot_client_id|hubspot_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|hubspot_connect_via|hubspot_connect_via|
|**--description**|string|Linked service description.|hubspot_description|hubspot_description|
|**--parameters**|dictionary|Parameters for linked service.|hubspot_parameters|hubspot_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|hubspot_annotations|hubspot_annotations|
|**--type-properties-client-secret**|object|The client secret associated with your Hubspot application.|hubspot_client_secret|hubspot_client_secret|
|**--type-properties-access-token**|object|The access token obtained when initially authenticating your OAuth integration.|hubspot_access_token|hubspot_access_token|
|**--type-properties-refresh-token**|object|The refresh token obtained when initially authenticating your OAuth integration.|hubspot_refresh_token|hubspot_refresh_token|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|hubspot_use_encrypted_endpoints|hubspot_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|hubspot_use_host_verification|hubspot_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|hubspot_use_peer_verification|hubspot_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|hubspot_encrypted_credential|hubspot_encrypted_credential|
### datafactory linked-service impala create

impala create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|impala_type|impala_type|
|**--type-properties-host**|any|The IP address or host name of the Impala server. (i.e. 192.168.222.160)|impala_host|impala_host|
|**--type-properties-authentication-type**|choice|The authentication type to use.|impala_authentication_type|impala_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|impala_connect_via|impala_connect_via|
|**--description**|string|Linked service description.|impala_description|impala_description|
|**--parameters**|dictionary|Parameters for linked service.|impala_parameters|impala_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|impala_annotations|impala_annotations|
|**--type-properties-port**|any|The TCP port that the Impala server uses to listen for client connections. The default value is 21050.|impala_port|impala_port|
|**--type-properties-username**|any|The user name used to access the Impala server. The default value is anonymous when using SASLUsername.|impala_username|impala_username|
|**--type-properties-password**|object|The password corresponding to the user name when using UsernameAndPassword.|impala_password|impala_password|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|impala_enable_ssl|impala_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|impala_trusted_cert_path|impala_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|impala_use_system_trust_store|impala_use_system_trust_store|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|impala_allow_host_name_cn_mismatch|impala_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|impala_allow_self_signed_server_cert|impala_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|impala_encrypted_credential|impala_encrypted_credential|
### datafactory linked-service impala update

impala create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|impala_type|impala_type|
|**--type-properties-host**|any|The IP address or host name of the Impala server. (i.e. 192.168.222.160)|impala_host|impala_host|
|**--type-properties-authentication-type**|choice|The authentication type to use.|impala_authentication_type|impala_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|impala_connect_via|impala_connect_via|
|**--description**|string|Linked service description.|impala_description|impala_description|
|**--parameters**|dictionary|Parameters for linked service.|impala_parameters|impala_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|impala_annotations|impala_annotations|
|**--type-properties-port**|any|The TCP port that the Impala server uses to listen for client connections. The default value is 21050.|impala_port|impala_port|
|**--type-properties-username**|any|The user name used to access the Impala server. The default value is anonymous when using SASLUsername.|impala_username|impala_username|
|**--type-properties-password**|object|The password corresponding to the user name when using UsernameAndPassword.|impala_password|impala_password|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|impala_enable_ssl|impala_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|impala_trusted_cert_path|impala_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|impala_use_system_trust_store|impala_use_system_trust_store|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|impala_allow_host_name_cn_mismatch|impala_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|impala_allow_self_signed_server_cert|impala_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|impala_encrypted_credential|impala_encrypted_credential|
### datafactory linked-service informix create

informix create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|informix_type|informix_type|
|**--type-properties-connection-string**|any|The non-access credential portion of the connection string as well as an optional encrypted credential. Type: string, SecureString or AzureKeyVaultSecretReference.|informix_connection_string|informix_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|informix_connect_via|informix_connect_via|
|**--description**|string|Linked service description.|informix_description|informix_description|
|**--parameters**|dictionary|Parameters for linked service.|informix_parameters|informix_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|informix_annotations|informix_annotations|
|**--type-properties-authentication-type**|any|Type of authentication used to connect to the Informix as ODBC data store. Possible values are: Anonymous and Basic. Type: string (or Expression with resultType string).|informix_authentication_type|informix_authentication_type|
|**--type-properties-credential**|object|The access credential portion of the connection string specified in driver-specific property-value format.|informix_credential|informix_credential|
|**--type-properties-user-name**|any|User name for Basic authentication. Type: string (or Expression with resultType string).|informix_user_name|informix_user_name|
|**--type-properties-password**|object|Password for Basic authentication.|informix_password|informix_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|informix_encrypted_credential|informix_encrypted_credential|
### datafactory linked-service informix update

informix create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|informix_type|informix_type|
|**--type-properties-connection-string**|any|The non-access credential portion of the connection string as well as an optional encrypted credential. Type: string, SecureString or AzureKeyVaultSecretReference.|informix_connection_string|informix_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|informix_connect_via|informix_connect_via|
|**--description**|string|Linked service description.|informix_description|informix_description|
|**--parameters**|dictionary|Parameters for linked service.|informix_parameters|informix_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|informix_annotations|informix_annotations|
|**--type-properties-authentication-type**|any|Type of authentication used to connect to the Informix as ODBC data store. Possible values are: Anonymous and Basic. Type: string (or Expression with resultType string).|informix_authentication_type|informix_authentication_type|
|**--type-properties-credential**|object|The access credential portion of the connection string specified in driver-specific property-value format.|informix_credential|informix_credential|
|**--type-properties-user-name**|any|User name for Basic authentication. Type: string (or Expression with resultType string).|informix_user_name|informix_user_name|
|**--type-properties-password**|object|Password for Basic authentication.|informix_password|informix_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|informix_encrypted_credential|informix_encrypted_credential|
### datafactory linked-service jira create

jira create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|jira_type|jira_type|
|**--type-properties-host**|any|The IP address or host name of the Jira service. (e.g. jira.example.com)|jira_host|jira_host|
|**--type-properties-username**|any|The user name that you use to access Jira Service.|jira_username|jira_username|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|jira_connect_via|jira_connect_via|
|**--description**|string|Linked service description.|jira_description|jira_description|
|**--parameters**|dictionary|Parameters for linked service.|jira_parameters|jira_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|jira_annotations|jira_annotations|
|**--type-properties-port**|any|The TCP port that the Jira server uses to listen for client connections. The default value is 443 if connecting through HTTPS, or 8080 if connecting through HTTP.|jira_port|jira_port|
|**--type-properties-password**|object|The password corresponding to the user name that you provided in the username field.|jira_password|jira_password|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|jira_use_encrypted_endpoints|jira_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|jira_use_host_verification|jira_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|jira_use_peer_verification|jira_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|jira_encrypted_credential|jira_encrypted_credential|
### datafactory linked-service jira update

jira create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|jira_type|jira_type|
|**--type-properties-host**|any|The IP address or host name of the Jira service. (e.g. jira.example.com)|jira_host|jira_host|
|**--type-properties-username**|any|The user name that you use to access Jira Service.|jira_username|jira_username|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|jira_connect_via|jira_connect_via|
|**--description**|string|Linked service description.|jira_description|jira_description|
|**--parameters**|dictionary|Parameters for linked service.|jira_parameters|jira_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|jira_annotations|jira_annotations|
|**--type-properties-port**|any|The TCP port that the Jira server uses to listen for client connections. The default value is 443 if connecting through HTTPS, or 8080 if connecting through HTTP.|jira_port|jira_port|
|**--type-properties-password**|object|The password corresponding to the user name that you provided in the username field.|jira_password|jira_password|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|jira_use_encrypted_endpoints|jira_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|jira_use_host_verification|jira_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|jira_use_peer_verification|jira_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|jira_encrypted_credential|jira_encrypted_credential|
### datafactory linked-service list

list a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
### datafactory linked-service magento create

magento create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|magento_type|magento_type|
|**--type-properties-host**|any|The URL of the Magento instance. (i.e. 192.168.222.110/magento3)|magento_host|magento_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|magento_connect_via|magento_connect_via|
|**--description**|string|Linked service description.|magento_description|magento_description|
|**--parameters**|dictionary|Parameters for linked service.|magento_parameters|magento_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|magento_annotations|magento_annotations|
|**--type-properties-access-token**|object|The access token from Magento.|magento_access_token|magento_access_token|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|magento_use_encrypted_endpoints|magento_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|magento_use_host_verification|magento_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|magento_use_peer_verification|magento_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|magento_encrypted_credential|magento_encrypted_credential|
### datafactory linked-service magento update

magento create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|magento_type|magento_type|
|**--type-properties-host**|any|The URL of the Magento instance. (i.e. 192.168.222.110/magento3)|magento_host|magento_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|magento_connect_via|magento_connect_via|
|**--description**|string|Linked service description.|magento_description|magento_description|
|**--parameters**|dictionary|Parameters for linked service.|magento_parameters|magento_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|magento_annotations|magento_annotations|
|**--type-properties-access-token**|object|The access token from Magento.|magento_access_token|magento_access_token|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|magento_use_encrypted_endpoints|magento_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|magento_use_host_verification|magento_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|magento_use_peer_verification|magento_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|magento_encrypted_credential|magento_encrypted_credential|
### datafactory linked-service maria-d-b create

maria-d-b create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|mariadb_type|maria_d_b_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|mariadb_connect_via|maria_d_b_connect_via|
|**--description**|string|Linked service description.|mariadb_description|maria_d_b_description|
|**--parameters**|dictionary|Parameters for linked service.|mariadb_parameters|maria_d_b_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|mariadb_annotations|maria_d_b_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|mariadb_connection_string|maria_d_b_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|mariadb_pwd|maria_d_b_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|mariadb_encrypted_credential|maria_d_b_encrypted_credential|
### datafactory linked-service maria-d-b update

maria-d-b create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|mariadb_type|maria_d_b_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|mariadb_connect_via|maria_d_b_connect_via|
|**--description**|string|Linked service description.|mariadb_description|maria_d_b_description|
|**--parameters**|dictionary|Parameters for linked service.|mariadb_parameters|maria_d_b_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|mariadb_annotations|maria_d_b_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|mariadb_connection_string|maria_d_b_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|mariadb_pwd|maria_d_b_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|mariadb_encrypted_credential|maria_d_b_encrypted_credential|
### datafactory linked-service marketo create

marketo create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|marketo_type|marketo_type|
|**--type-properties-endpoint**|any|The endpoint of the Marketo server. (i.e. 123-ABC-321.mktorest.com)|marketo_endpoint|marketo_endpoint|
|**--type-properties-client-id**|any|The client Id of your Marketo service.|marketo_client_id|marketo_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|marketo_connect_via|marketo_connect_via|
|**--description**|string|Linked service description.|marketo_description|marketo_description|
|**--parameters**|dictionary|Parameters for linked service.|marketo_parameters|marketo_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|marketo_annotations|marketo_annotations|
|**--type-properties-client-secret**|object|The client secret of your Marketo service.|marketo_client_secret|marketo_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|marketo_use_encrypted_endpoints|marketo_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|marketo_use_host_verification|marketo_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|marketo_use_peer_verification|marketo_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|marketo_encrypted_credential|marketo_encrypted_credential|
### datafactory linked-service marketo update

marketo create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|marketo_type|marketo_type|
|**--type-properties-endpoint**|any|The endpoint of the Marketo server. (i.e. 123-ABC-321.mktorest.com)|marketo_endpoint|marketo_endpoint|
|**--type-properties-client-id**|any|The client Id of your Marketo service.|marketo_client_id|marketo_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|marketo_connect_via|marketo_connect_via|
|**--description**|string|Linked service description.|marketo_description|marketo_description|
|**--parameters**|dictionary|Parameters for linked service.|marketo_parameters|marketo_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|marketo_annotations|marketo_annotations|
|**--type-properties-client-secret**|object|The client secret of your Marketo service.|marketo_client_secret|marketo_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|marketo_use_encrypted_endpoints|marketo_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|marketo_use_host_verification|marketo_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|marketo_use_peer_verification|marketo_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|marketo_encrypted_credential|marketo_encrypted_credential|
### datafactory linked-service microsoft-access create

microsoft-access create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|microsoftaccess_type|microsoft_access_type|
|**--type-properties-connection-string**|any|The non-access credential portion of the connection string as well as an optional encrypted credential. Type: string, SecureString or AzureKeyVaultSecretReference.|microsoftaccess_connection_string|microsoft_access_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|microsoftaccess_connect_via|microsoft_access_connect_via|
|**--description**|string|Linked service description.|microsoftaccess_description|microsoft_access_description|
|**--parameters**|dictionary|Parameters for linked service.|microsoftaccess_parameters|microsoft_access_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|microsoftaccess_annotations|microsoft_access_annotations|
|**--type-properties-authentication-type**|any|Type of authentication used to connect to the Microsoft Access as ODBC data store. Possible values are: Anonymous and Basic. Type: string (or Expression with resultType string).|microsoftaccess_authentication_type|microsoft_access_authentication_type|
|**--type-properties-credential**|object|The access credential portion of the connection string specified in driver-specific property-value format.|microsoftaccess_credential|microsoft_access_credential|
|**--type-properties-user-name**|any|User name for Basic authentication. Type: string (or Expression with resultType string).|microsoftaccess_user_name|microsoft_access_user_name|
|**--type-properties-password**|object|Password for Basic authentication.|microsoftaccess_password|microsoft_access_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|microsoftaccess_encrypted_credential|microsoft_access_encrypted_credential|
### datafactory linked-service microsoft-access update

microsoft-access create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|microsoftaccess_type|microsoft_access_type|
|**--type-properties-connection-string**|any|The non-access credential portion of the connection string as well as an optional encrypted credential. Type: string, SecureString or AzureKeyVaultSecretReference.|microsoftaccess_connection_string|microsoft_access_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|microsoftaccess_connect_via|microsoft_access_connect_via|
|**--description**|string|Linked service description.|microsoftaccess_description|microsoft_access_description|
|**--parameters**|dictionary|Parameters for linked service.|microsoftaccess_parameters|microsoft_access_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|microsoftaccess_annotations|microsoft_access_annotations|
|**--type-properties-authentication-type**|any|Type of authentication used to connect to the Microsoft Access as ODBC data store. Possible values are: Anonymous and Basic. Type: string (or Expression with resultType string).|microsoftaccess_authentication_type|microsoft_access_authentication_type|
|**--type-properties-credential**|object|The access credential portion of the connection string specified in driver-specific property-value format.|microsoftaccess_credential|microsoft_access_credential|
|**--type-properties-user-name**|any|User name for Basic authentication. Type: string (or Expression with resultType string).|microsoftaccess_user_name|microsoft_access_user_name|
|**--type-properties-password**|object|Password for Basic authentication.|microsoftaccess_password|microsoft_access_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|microsoftaccess_encrypted_credential|microsoft_access_encrypted_credential|
### datafactory linked-service mongo-db create

mongo-db create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|mongodb_type|mongo_db_type|
|**--type-properties-server**|any|The IP address or server name of the MongoDB server. Type: string (or Expression with resultType string).|mongodb_server|mongo_db_server|
|**--type-properties-database-name**|any|The name of the MongoDB database that you want to access. Type: string (or Expression with resultType string).|mongodb_database_name|mongo_db_database_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|mongodb_connect_via|mongo_db_connect_via|
|**--description**|string|Linked service description.|mongodb_description|mongo_db_description|
|**--parameters**|dictionary|Parameters for linked service.|mongodb_parameters|mongo_db_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|mongodb_annotations|mongo_db_annotations|
|**--type-properties-authentication-type**|choice|The authentication type to be used to connect to the MongoDB database.|mongodb_authentication_type|mongo_db_authentication_type|
|**--type-properties-username**|any|Username for authentication. Type: string (or Expression with resultType string).|mongodb_username|mongo_db_username|
|**--type-properties-password**|object|Password for authentication.|mongodb_password|mongo_db_password|
|**--type-properties-auth-source**|any|Database to verify the username and password. Type: string (or Expression with resultType string).|mongodb_auth_source|mongo_db_auth_source|
|**--type-properties-port**|any|The TCP port number that the MongoDB server uses to listen for client connections. The default value is 27017. Type: integer (or Expression with resultType integer), minimum: 0.|mongodb_port|mongo_db_port|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false. Type: boolean (or Expression with resultType boolean).|mongodb_enable_ssl|mongo_db_enable_ssl|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false. Type: boolean (or Expression with resultType boolean).|mongodb_allow_self_signed_server_cert|mongo_db_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|mongodb_encrypted_credential|mongo_db_encrypted_credential|
### datafactory linked-service mongo-db update

mongo-db create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|mongodb_type|mongo_db_type|
|**--type-properties-server**|any|The IP address or server name of the MongoDB server. Type: string (or Expression with resultType string).|mongodb_server|mongo_db_server|
|**--type-properties-database-name**|any|The name of the MongoDB database that you want to access. Type: string (or Expression with resultType string).|mongodb_database_name|mongo_db_database_name|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|mongodb_connect_via|mongo_db_connect_via|
|**--description**|string|Linked service description.|mongodb_description|mongo_db_description|
|**--parameters**|dictionary|Parameters for linked service.|mongodb_parameters|mongo_db_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|mongodb_annotations|mongo_db_annotations|
|**--type-properties-authentication-type**|choice|The authentication type to be used to connect to the MongoDB database.|mongodb_authentication_type|mongo_db_authentication_type|
|**--type-properties-username**|any|Username for authentication. Type: string (or Expression with resultType string).|mongodb_username|mongo_db_username|
|**--type-properties-password**|object|Password for authentication.|mongodb_password|mongo_db_password|
|**--type-properties-auth-source**|any|Database to verify the username and password. Type: string (or Expression with resultType string).|mongodb_auth_source|mongo_db_auth_source|
|**--type-properties-port**|any|The TCP port number that the MongoDB server uses to listen for client connections. The default value is 27017. Type: integer (or Expression with resultType integer), minimum: 0.|mongodb_port|mongo_db_port|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false. Type: boolean (or Expression with resultType boolean).|mongodb_enable_ssl|mongo_db_enable_ssl|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false. Type: boolean (or Expression with resultType boolean).|mongodb_allow_self_signed_server_cert|mongo_db_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|mongodb_encrypted_credential|mongo_db_encrypted_credential|
### datafactory linked-service mongo-db-v2 create

mongo-db-v2 create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|mongodbv2_type|mongo_db_v2_type|
|**--type-properties-connection-string**|any|The MongoDB connection string. Type: string, SecureString or AzureKeyVaultSecretReference. Type: string, SecureString or AzureKeyVaultSecretReference.|mongodbv2_connection_string|mongo_db_v2_connection_string|
|**--type-properties-database**|any|The name of the MongoDB database that you want to access. Type: string (or Expression with resultType string).|mongodbv2_database|mongo_db_v2_database|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|mongodbv2_connect_via|mongo_db_v2_connect_via|
|**--description**|string|Linked service description.|mongodbv2_description|mongo_db_v2_description|
|**--parameters**|dictionary|Parameters for linked service.|mongodbv2_parameters|mongo_db_v2_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|mongodbv2_annotations|mongo_db_v2_annotations|
### datafactory linked-service mongo-db-v2 update

mongo-db-v2 create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|mongodbv2_type|mongo_db_v2_type|
|**--type-properties-connection-string**|any|The MongoDB connection string. Type: string, SecureString or AzureKeyVaultSecretReference. Type: string, SecureString or AzureKeyVaultSecretReference.|mongodbv2_connection_string|mongo_db_v2_connection_string|
|**--type-properties-database**|any|The name of the MongoDB database that you want to access. Type: string (or Expression with resultType string).|mongodbv2_database|mongo_db_v2_database|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|mongodbv2_connect_via|mongo_db_v2_connect_via|
|**--description**|string|Linked service description.|mongodbv2_description|mongo_db_v2_description|
|**--parameters**|dictionary|Parameters for linked service.|mongodbv2_parameters|mongo_db_v2_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|mongodbv2_annotations|mongo_db_v2_annotations|
### datafactory linked-service my-sql create

my-sql create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|mysql_type|my_sql_type|
|**--type-properties-connection-string**|any|The connection string.|mysql_connection_string|my_sql_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|mysql_connect_via|my_sql_connect_via|
|**--description**|string|Linked service description.|mysql_description|my_sql_description|
|**--parameters**|dictionary|Parameters for linked service.|mysql_parameters|my_sql_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|mysql_annotations|my_sql_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|mysql_password|my_sql_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|mysql_encrypted_credential|my_sql_encrypted_credential|
### datafactory linked-service my-sql update

my-sql create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|mysql_type|my_sql_type|
|**--type-properties-connection-string**|any|The connection string.|mysql_connection_string|my_sql_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|mysql_connect_via|my_sql_connect_via|
|**--description**|string|Linked service description.|mysql_description|my_sql_description|
|**--parameters**|dictionary|Parameters for linked service.|mysql_parameters|my_sql_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|mysql_annotations|my_sql_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|mysql_password|my_sql_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|mysql_encrypted_credential|my_sql_encrypted_credential|
### datafactory linked-service netezza create

netezza create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|netezza_type|netezza_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|netezza_connect_via|netezza_connect_via|
|**--description**|string|Linked service description.|netezza_description|netezza_description|
|**--parameters**|dictionary|Parameters for linked service.|netezza_parameters|netezza_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|netezza_annotations|netezza_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|netezza_connection_string|netezza_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|netezza_pwd|netezza_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|netezza_encrypted_credential|netezza_encrypted_credential|
### datafactory linked-service netezza update

netezza create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|netezza_type|netezza_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|netezza_connect_via|netezza_connect_via|
|**--description**|string|Linked service description.|netezza_description|netezza_description|
|**--parameters**|dictionary|Parameters for linked service.|netezza_parameters|netezza_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|netezza_annotations|netezza_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|netezza_connection_string|netezza_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|netezza_pwd|netezza_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|netezza_encrypted_credential|netezza_encrypted_credential|
### datafactory linked-service o-data create

o-data create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|odata_type|o_data_type|
|**--type-properties-url**|any|The URL of the OData service endpoint. Type: string (or Expression with resultType string).|odata_url|o_data_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|odata_connect_via|o_data_connect_via|
|**--description**|string|Linked service description.|odata_description|o_data_description|
|**--parameters**|dictionary|Parameters for linked service.|odata_parameters|o_data_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|odata_annotations|o_data_annotations|
|**--type-properties-authentication-type**|choice|Type of authentication used to connect to the OData service.|odata_authentication_type|o_data_authentication_type|
|**--type-properties-user-name**|any|User name of the OData service. Type: string (or Expression with resultType string).|odata_user_name|o_data_user_name|
|**--type-properties-password**|object|Password of the OData service.|odata_password|o_data_password|
|**--type-properties-tenant**|any|Specify the tenant information (domain name or tenant ID) under which your application resides. Type: string (or Expression with resultType string).|odata_tenant|o_data_tenant|
|**--type-properties-service-principal-id**|any|Specify the application id of your application registered in Azure Active Directory. Type: string (or Expression with resultType string).|odata_service_principal_id|o_data_service_principal_id|
|**--type-properties-aad-resource-id**|any|Specify the resource you are requesting authorization to use Directory. Type: string (or Expression with resultType string).|odata_aad_resource_id|o_data_aad_resource_id|
|**--type-properties-aad-service-principal-credential-type**|choice|Specify the credential type (key or cert) is used for service principal.|odata_aad_service_principal_credential_type|o_data_aad_service_principal_credential_type|
|**--type-properties-service-principal-key**|object|Specify the secret of your application registered in Azure Active Directory. Type: string (or Expression with resultType string).|odata_service_principal_key|o_data_service_principal_key|
|**--type-properties-service-principal-embedded-cert**|object|Specify the base64 encoded certificate of your application registered in Azure Active Directory. Type: string (or Expression with resultType string).|odata_service_principal_embedded_cert|o_data_service_principal_embedded_cert|
|**--type-properties-service-principal-embedded-cert-password**|object|Specify the password of your certificate if your certificate has a password and you are using AadServicePrincipal authentication. Type: string (or Expression with resultType string).|odata_service_principal_embedded_cert_password|o_data_service_principal_embedded_cert_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|odata_encrypted_credential|o_data_encrypted_credential|
### datafactory linked-service o-data update

o-data create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|odata_type|o_data_type|
|**--type-properties-url**|any|The URL of the OData service endpoint. Type: string (or Expression with resultType string).|odata_url|o_data_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|odata_connect_via|o_data_connect_via|
|**--description**|string|Linked service description.|odata_description|o_data_description|
|**--parameters**|dictionary|Parameters for linked service.|odata_parameters|o_data_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|odata_annotations|o_data_annotations|
|**--type-properties-authentication-type**|choice|Type of authentication used to connect to the OData service.|odata_authentication_type|o_data_authentication_type|
|**--type-properties-user-name**|any|User name of the OData service. Type: string (or Expression with resultType string).|odata_user_name|o_data_user_name|
|**--type-properties-password**|object|Password of the OData service.|odata_password|o_data_password|
|**--type-properties-tenant**|any|Specify the tenant information (domain name or tenant ID) under which your application resides. Type: string (or Expression with resultType string).|odata_tenant|o_data_tenant|
|**--type-properties-service-principal-id**|any|Specify the application id of your application registered in Azure Active Directory. Type: string (or Expression with resultType string).|odata_service_principal_id|o_data_service_principal_id|
|**--type-properties-aad-resource-id**|any|Specify the resource you are requesting authorization to use Directory. Type: string (or Expression with resultType string).|odata_aad_resource_id|o_data_aad_resource_id|
|**--type-properties-aad-service-principal-credential-type**|choice|Specify the credential type (key or cert) is used for service principal.|odata_aad_service_principal_credential_type|o_data_aad_service_principal_credential_type|
|**--type-properties-service-principal-key**|object|Specify the secret of your application registered in Azure Active Directory. Type: string (or Expression with resultType string).|odata_service_principal_key|o_data_service_principal_key|
|**--type-properties-service-principal-embedded-cert**|object|Specify the base64 encoded certificate of your application registered in Azure Active Directory. Type: string (or Expression with resultType string).|odata_service_principal_embedded_cert|o_data_service_principal_embedded_cert|
|**--type-properties-service-principal-embedded-cert-password**|object|Specify the password of your certificate if your certificate has a password and you are using AadServicePrincipal authentication. Type: string (or Expression with resultType string).|odata_service_principal_embedded_cert_password|o_data_service_principal_embedded_cert_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|odata_encrypted_credential|o_data_encrypted_credential|
### datafactory linked-service odbc create

odbc create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|odbc_type|odbc_type|
|**--type-properties-connection-string**|any|The non-access credential portion of the connection string as well as an optional encrypted credential. Type: string, SecureString or AzureKeyVaultSecretReference.|odbc_connection_string|odbc_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|odbc_connect_via|odbc_connect_via|
|**--description**|string|Linked service description.|odbc_description|odbc_description|
|**--parameters**|dictionary|Parameters for linked service.|odbc_parameters|odbc_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|odbc_annotations|odbc_annotations|
|**--type-properties-authentication-type**|any|Type of authentication used to connect to the ODBC data store. Possible values are: Anonymous and Basic. Type: string (or Expression with resultType string).|odbc_authentication_type|odbc_authentication_type|
|**--type-properties-credential**|object|The access credential portion of the connection string specified in driver-specific property-value format.|odbc_credential|odbc_credential|
|**--type-properties-user-name**|any|User name for Basic authentication. Type: string (or Expression with resultType string).|odbc_user_name|odbc_user_name|
|**--type-properties-password**|object|Password for Basic authentication.|odbc_password|odbc_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|odbc_encrypted_credential|odbc_encrypted_credential|
### datafactory linked-service odbc update

odbc create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|odbc_type|odbc_type|
|**--type-properties-connection-string**|any|The non-access credential portion of the connection string as well as an optional encrypted credential. Type: string, SecureString or AzureKeyVaultSecretReference.|odbc_connection_string|odbc_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|odbc_connect_via|odbc_connect_via|
|**--description**|string|Linked service description.|odbc_description|odbc_description|
|**--parameters**|dictionary|Parameters for linked service.|odbc_parameters|odbc_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|odbc_annotations|odbc_annotations|
|**--type-properties-authentication-type**|any|Type of authentication used to connect to the ODBC data store. Possible values are: Anonymous and Basic. Type: string (or Expression with resultType string).|odbc_authentication_type|odbc_authentication_type|
|**--type-properties-credential**|object|The access credential portion of the connection string specified in driver-specific property-value format.|odbc_credential|odbc_credential|
|**--type-properties-user-name**|any|User name for Basic authentication. Type: string (or Expression with resultType string).|odbc_user_name|odbc_user_name|
|**--type-properties-password**|object|Password for Basic authentication.|odbc_password|odbc_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|odbc_encrypted_credential|odbc_encrypted_credential|
### datafactory linked-service office365 create

office365 create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|office365_type|office365_type|
|**--type-properties-office365tenant-id**|any|Azure tenant ID to which the Office 365 account belongs. Type: string (or Expression with resultType string).|office365_office365_tenant_id|office365_office365_tenant_id|
|**--type-properties-service-principal-tenant-id**|any|Specify the tenant information under which your Azure AD web application resides. Type: string (or Expression with resultType string).|office365_service_principal_tenant_id|office365_service_principal_tenant_id|
|**--type-properties-service-principal-id**|any|Specify the application's client ID. Type: string (or Expression with resultType string).|office365_service_principal_id|office365_service_principal_id|
|**--type-properties-service-principal-key**|object|Specify the application's key.|office365_service_principal_key|office365_service_principal_key|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|office365_connect_via|office365_connect_via|
|**--description**|string|Linked service description.|office365_description|office365_description|
|**--parameters**|dictionary|Parameters for linked service.|office365_parameters|office365_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|office365_annotations|office365_annotations|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|office365_encrypted_credential|office365_encrypted_credential|
### datafactory linked-service office365 update

office365 create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|office365_type|office365_type|
|**--type-properties-office365tenant-id**|any|Azure tenant ID to which the Office 365 account belongs. Type: string (or Expression with resultType string).|office365_office365_tenant_id|office365_office365_tenant_id|
|**--type-properties-service-principal-tenant-id**|any|Specify the tenant information under which your Azure AD web application resides. Type: string (or Expression with resultType string).|office365_service_principal_tenant_id|office365_service_principal_tenant_id|
|**--type-properties-service-principal-id**|any|Specify the application's client ID. Type: string (or Expression with resultType string).|office365_service_principal_id|office365_service_principal_id|
|**--type-properties-service-principal-key**|object|Specify the application's key.|office365_service_principal_key|office365_service_principal_key|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|office365_connect_via|office365_connect_via|
|**--description**|string|Linked service description.|office365_description|office365_description|
|**--parameters**|dictionary|Parameters for linked service.|office365_parameters|office365_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|office365_annotations|office365_annotations|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|office365_encrypted_credential|office365_encrypted_credential|
### datafactory linked-service oracle create

oracle create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|oracle_type|oracle_type|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|oracle_connection_string|oracle_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|oracle_connect_via|oracle_connect_via|
|**--description**|string|Linked service description.|oracle_description|oracle_description|
|**--parameters**|dictionary|Parameters for linked service.|oracle_parameters|oracle_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|oracle_annotations|oracle_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|oracle_password|oracle_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|oracle_encrypted_credential|oracle_encrypted_credential|
### datafactory linked-service oracle update

oracle create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|oracle_type|oracle_type|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|oracle_connection_string|oracle_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|oracle_connect_via|oracle_connect_via|
|**--description**|string|Linked service description.|oracle_description|oracle_description|
|**--parameters**|dictionary|Parameters for linked service.|oracle_parameters|oracle_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|oracle_annotations|oracle_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|oracle_password|oracle_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|oracle_encrypted_credential|oracle_encrypted_credential|
### datafactory linked-service oracle-service-cloud create

oracle-service-cloud create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|oracleservicecloud_type|oracle_service_cloud_type|
|**--type-properties-host**|any|The URL of the Oracle Service Cloud instance.|oracleservicecloud_host|oracle_service_cloud_host|
|**--type-properties-username**|any|The user name that you use to access Oracle Service Cloud server.|oracleservicecloud_username|oracle_service_cloud_username|
|**--type-properties-password**|object|The password corresponding to the user name that you provided in the username key.|oracleservicecloud_password|oracle_service_cloud_password|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|oracleservicecloud_connect_via|oracle_service_cloud_connect_via|
|**--description**|string|Linked service description.|oracleservicecloud_description|oracle_service_cloud_description|
|**--parameters**|dictionary|Parameters for linked service.|oracleservicecloud_parameters|oracle_service_cloud_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|oracleservicecloud_annotations|oracle_service_cloud_annotations|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true. Type: boolean (or Expression with resultType boolean).|oracleservicecloud_use_encrypted_endpoints|oracle_service_cloud_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|oracleservicecloud_use_host_verification|oracle_service_cloud_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|oracleservicecloud_use_peer_verification|oracle_service_cloud_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|oracleservicecloud_encrypted_credential|oracle_service_cloud_encrypted_credential|
### datafactory linked-service oracle-service-cloud update

oracle-service-cloud create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|oracleservicecloud_type|oracle_service_cloud_type|
|**--type-properties-host**|any|The URL of the Oracle Service Cloud instance.|oracleservicecloud_host|oracle_service_cloud_host|
|**--type-properties-username**|any|The user name that you use to access Oracle Service Cloud server.|oracleservicecloud_username|oracle_service_cloud_username|
|**--type-properties-password**|object|The password corresponding to the user name that you provided in the username key.|oracleservicecloud_password|oracle_service_cloud_password|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|oracleservicecloud_connect_via|oracle_service_cloud_connect_via|
|**--description**|string|Linked service description.|oracleservicecloud_description|oracle_service_cloud_description|
|**--parameters**|dictionary|Parameters for linked service.|oracleservicecloud_parameters|oracle_service_cloud_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|oracleservicecloud_annotations|oracle_service_cloud_annotations|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true. Type: boolean (or Expression with resultType boolean).|oracleservicecloud_use_encrypted_endpoints|oracle_service_cloud_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|oracleservicecloud_use_host_verification|oracle_service_cloud_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|oracleservicecloud_use_peer_verification|oracle_service_cloud_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|oracleservicecloud_encrypted_credential|oracle_service_cloud_encrypted_credential|
### datafactory linked-service paypal create

paypal create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|paypal_type|paypal_type|
|**--type-properties-host**|any|The URL of the PayPal instance. (i.e. api.sandbox.paypal.com)|paypal_host|paypal_host|
|**--type-properties-client-id**|any|The client ID associated with your PayPal application.|paypal_client_id|paypal_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|paypal_connect_via|paypal_connect_via|
|**--description**|string|Linked service description.|paypal_description|paypal_description|
|**--parameters**|dictionary|Parameters for linked service.|paypal_parameters|paypal_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|paypal_annotations|paypal_annotations|
|**--type-properties-client-secret**|object|The client secret associated with your PayPal application.|paypal_client_secret|paypal_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|paypal_use_encrypted_endpoints|paypal_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|paypal_use_host_verification|paypal_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|paypal_use_peer_verification|paypal_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|paypal_encrypted_credential|paypal_encrypted_credential|
### datafactory linked-service paypal update

paypal create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|paypal_type|paypal_type|
|**--type-properties-host**|any|The URL of the PayPal instance. (i.e. api.sandbox.paypal.com)|paypal_host|paypal_host|
|**--type-properties-client-id**|any|The client ID associated with your PayPal application.|paypal_client_id|paypal_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|paypal_connect_via|paypal_connect_via|
|**--description**|string|Linked service description.|paypal_description|paypal_description|
|**--parameters**|dictionary|Parameters for linked service.|paypal_parameters|paypal_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|paypal_annotations|paypal_annotations|
|**--type-properties-client-secret**|object|The client secret associated with your PayPal application.|paypal_client_secret|paypal_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|paypal_use_encrypted_endpoints|paypal_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|paypal_use_host_verification|paypal_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|paypal_use_peer_verification|paypal_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|paypal_encrypted_credential|paypal_encrypted_credential|
### datafactory linked-service phoenix create

phoenix create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|phoenix_type|phoenix_type|
|**--type-properties-host**|any|The IP address or host name of the Phoenix server. (i.e. 192.168.222.160)|phoenix_host|phoenix_host|
|**--type-properties-authentication-type**|choice|The authentication mechanism used to connect to the Phoenix server.|phoenix_authentication_type|phoenix_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|phoenix_connect_via|phoenix_connect_via|
|**--description**|string|Linked service description.|phoenix_description|phoenix_description|
|**--parameters**|dictionary|Parameters for linked service.|phoenix_parameters|phoenix_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|phoenix_annotations|phoenix_annotations|
|**--type-properties-port**|any|The TCP port that the Phoenix server uses to listen for client connections. The default value is 8765.|phoenix_port|phoenix_port|
|**--type-properties-http-path**|any|The partial URL corresponding to the Phoenix server. (i.e. /gateway/sandbox/phoenix/version). The default value is hbasephoenix if using WindowsAzureHDInsightService.|phoenix_http_path|phoenix_http_path|
|**--type-properties-username**|any|The user name used to connect to the Phoenix server.|phoenix_username|phoenix_username|
|**--type-properties-password**|object|The password corresponding to the user name.|phoenix_password|phoenix_password|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|phoenix_enable_ssl|phoenix_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|phoenix_trusted_cert_path|phoenix_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|phoenix_use_system_trust_store|phoenix_use_system_trust_store|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|phoenix_allow_host_name_cn_mismatch|phoenix_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|phoenix_allow_self_signed_server_cert|phoenix_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|phoenix_encrypted_credential|phoenix_encrypted_credential|
### datafactory linked-service phoenix update

phoenix create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|phoenix_type|phoenix_type|
|**--type-properties-host**|any|The IP address or host name of the Phoenix server. (i.e. 192.168.222.160)|phoenix_host|phoenix_host|
|**--type-properties-authentication-type**|choice|The authentication mechanism used to connect to the Phoenix server.|phoenix_authentication_type|phoenix_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|phoenix_connect_via|phoenix_connect_via|
|**--description**|string|Linked service description.|phoenix_description|phoenix_description|
|**--parameters**|dictionary|Parameters for linked service.|phoenix_parameters|phoenix_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|phoenix_annotations|phoenix_annotations|
|**--type-properties-port**|any|The TCP port that the Phoenix server uses to listen for client connections. The default value is 8765.|phoenix_port|phoenix_port|
|**--type-properties-http-path**|any|The partial URL corresponding to the Phoenix server. (i.e. /gateway/sandbox/phoenix/version). The default value is hbasephoenix if using WindowsAzureHDInsightService.|phoenix_http_path|phoenix_http_path|
|**--type-properties-username**|any|The user name used to connect to the Phoenix server.|phoenix_username|phoenix_username|
|**--type-properties-password**|object|The password corresponding to the user name.|phoenix_password|phoenix_password|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|phoenix_enable_ssl|phoenix_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|phoenix_trusted_cert_path|phoenix_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|phoenix_use_system_trust_store|phoenix_use_system_trust_store|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|phoenix_allow_host_name_cn_mismatch|phoenix_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|phoenix_allow_self_signed_server_cert|phoenix_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|phoenix_encrypted_credential|phoenix_encrypted_credential|
### datafactory linked-service postgre-sql create

postgre-sql create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|postgresql_type|postgre_sql_type|
|**--type-properties-connection-string**|any|The connection string.|postgresql_connection_string|postgre_sql_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|postgresql_connect_via|postgre_sql_connect_via|
|**--description**|string|Linked service description.|postgresql_description|postgre_sql_description|
|**--parameters**|dictionary|Parameters for linked service.|postgresql_parameters|postgre_sql_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|postgresql_annotations|postgre_sql_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|postgresql_password|postgre_sql_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|postgresql_encrypted_credential|postgre_sql_encrypted_credential|
### datafactory linked-service postgre-sql update

postgre-sql create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|postgresql_type|postgre_sql_type|
|**--type-properties-connection-string**|any|The connection string.|postgresql_connection_string|postgre_sql_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|postgresql_connect_via|postgre_sql_connect_via|
|**--description**|string|Linked service description.|postgresql_description|postgre_sql_description|
|**--parameters**|dictionary|Parameters for linked service.|postgresql_parameters|postgre_sql_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|postgresql_annotations|postgre_sql_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|postgresql_password|postgre_sql_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|postgresql_encrypted_credential|postgre_sql_encrypted_credential|
### datafactory linked-service presto create

presto create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|presto_type|presto_type|
|**--type-properties-host**|any|The IP address or host name of the Presto server. (i.e. 192.168.222.160)|presto_host|presto_host|
|**--type-properties-server-version**|any|The version of the Presto server. (i.e. 0.148-t)|presto_server_version|presto_server_version|
|**--type-properties-catalog**|any|The catalog context for all request against the server.|presto_catalog|presto_catalog|
|**--type-properties-authentication-type**|choice|The authentication mechanism used to connect to the Presto server.|presto_authentication_type|presto_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|presto_connect_via|presto_connect_via|
|**--description**|string|Linked service description.|presto_description|presto_description|
|**--parameters**|dictionary|Parameters for linked service.|presto_parameters|presto_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|presto_annotations|presto_annotations|
|**--type-properties-port**|any|The TCP port that the Presto server uses to listen for client connections. The default value is 8080.|presto_port|presto_port|
|**--type-properties-username**|any|The user name used to connect to the Presto server.|presto_username|presto_username|
|**--type-properties-password**|object|The password corresponding to the user name.|presto_password|presto_password|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|presto_enable_ssl|presto_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|presto_trusted_cert_path|presto_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|presto_use_system_trust_store|presto_use_system_trust_store|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|presto_allow_host_name_cn_mismatch|presto_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|presto_allow_self_signed_server_cert|presto_allow_self_signed_server_cert|
|**--type-properties-time-zone-id**|any|The local time zone used by the connection. Valid values for this option are specified in the IANA Time Zone Database. The default value is the system time zone.|presto_time_zone_id|presto_time_zone_id|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|presto_encrypted_credential|presto_encrypted_credential|
### datafactory linked-service presto update

presto create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|presto_type|presto_type|
|**--type-properties-host**|any|The IP address or host name of the Presto server. (i.e. 192.168.222.160)|presto_host|presto_host|
|**--type-properties-server-version**|any|The version of the Presto server. (i.e. 0.148-t)|presto_server_version|presto_server_version|
|**--type-properties-catalog**|any|The catalog context for all request against the server.|presto_catalog|presto_catalog|
|**--type-properties-authentication-type**|choice|The authentication mechanism used to connect to the Presto server.|presto_authentication_type|presto_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|presto_connect_via|presto_connect_via|
|**--description**|string|Linked service description.|presto_description|presto_description|
|**--parameters**|dictionary|Parameters for linked service.|presto_parameters|presto_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|presto_annotations|presto_annotations|
|**--type-properties-port**|any|The TCP port that the Presto server uses to listen for client connections. The default value is 8080.|presto_port|presto_port|
|**--type-properties-username**|any|The user name used to connect to the Presto server.|presto_username|presto_username|
|**--type-properties-password**|object|The password corresponding to the user name.|presto_password|presto_password|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|presto_enable_ssl|presto_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|presto_trusted_cert_path|presto_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|presto_use_system_trust_store|presto_use_system_trust_store|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|presto_allow_host_name_cn_mismatch|presto_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|presto_allow_self_signed_server_cert|presto_allow_self_signed_server_cert|
|**--type-properties-time-zone-id**|any|The local time zone used by the connection. Valid values for this option are specified in the IANA Time Zone Database. The default value is the system time zone.|presto_time_zone_id|presto_time_zone_id|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|presto_encrypted_credential|presto_encrypted_credential|
### datafactory linked-service quick-books create

quick-books create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|quickbooks_type|quick_books_type|
|**--type-properties-endpoint**|any|The endpoint of the QuickBooks server. (i.e. quickbooks.api.intuit.com)|quickbooks_endpoint|quick_books_endpoint|
|**--type-properties-company-id**|any|The company ID of the QuickBooks company to authorize.|quickbooks_company_id|quick_books_company_id|
|**--type-properties-consumer-key**|any|The consumer key for OAuth 1.0 authentication.|quickbooks_consumer_key|quick_books_consumer_key|
|**--type-properties-consumer-secret**|object|The consumer secret for OAuth 1.0 authentication.|quickbooks_consumer_secret|quick_books_consumer_secret|
|**--type-properties-access-token**|object|The access token for OAuth 1.0 authentication.|quickbooks_access_token|quick_books_access_token|
|**--type-properties-access-token-secret**|object|The access token secret for OAuth 1.0 authentication.|quickbooks_access_token_secret|quick_books_access_token_secret|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|quickbooks_connect_via|quick_books_connect_via|
|**--description**|string|Linked service description.|quickbooks_description|quick_books_description|
|**--parameters**|dictionary|Parameters for linked service.|quickbooks_parameters|quick_books_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|quickbooks_annotations|quick_books_annotations|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|quickbooks_use_encrypted_endpoints|quick_books_use_encrypted_endpoints|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|quickbooks_encrypted_credential|quick_books_encrypted_credential|
### datafactory linked-service quick-books update

quick-books create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|quickbooks_type|quick_books_type|
|**--type-properties-endpoint**|any|The endpoint of the QuickBooks server. (i.e. quickbooks.api.intuit.com)|quickbooks_endpoint|quick_books_endpoint|
|**--type-properties-company-id**|any|The company ID of the QuickBooks company to authorize.|quickbooks_company_id|quick_books_company_id|
|**--type-properties-consumer-key**|any|The consumer key for OAuth 1.0 authentication.|quickbooks_consumer_key|quick_books_consumer_key|
|**--type-properties-consumer-secret**|object|The consumer secret for OAuth 1.0 authentication.|quickbooks_consumer_secret|quick_books_consumer_secret|
|**--type-properties-access-token**|object|The access token for OAuth 1.0 authentication.|quickbooks_access_token|quick_books_access_token|
|**--type-properties-access-token-secret**|object|The access token secret for OAuth 1.0 authentication.|quickbooks_access_token_secret|quick_books_access_token_secret|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|quickbooks_connect_via|quick_books_connect_via|
|**--description**|string|Linked service description.|quickbooks_description|quick_books_description|
|**--parameters**|dictionary|Parameters for linked service.|quickbooks_parameters|quick_books_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|quickbooks_annotations|quick_books_annotations|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|quickbooks_use_encrypted_endpoints|quick_books_use_encrypted_endpoints|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|quickbooks_encrypted_credential|quick_books_encrypted_credential|
### datafactory linked-service responsys create

responsys create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|responsys_type|responsys_type|
|**--type-properties-endpoint**|any|The endpoint of the Responsys server.|responsys_endpoint|responsys_endpoint|
|**--type-properties-client-id**|any|The client ID associated with the Responsys application. Type: string (or Expression with resultType string).|responsys_client_id|responsys_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|responsys_connect_via|responsys_connect_via|
|**--description**|string|Linked service description.|responsys_description|responsys_description|
|**--parameters**|dictionary|Parameters for linked service.|responsys_parameters|responsys_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|responsys_annotations|responsys_annotations|
|**--type-properties-client-secret**|object|The client secret associated with the Responsys application. Type: string (or Expression with resultType string).|responsys_client_secret|responsys_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true. Type: boolean (or Expression with resultType boolean).|responsys_use_encrypted_endpoints|responsys_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|responsys_use_host_verification|responsys_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|responsys_use_peer_verification|responsys_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|responsys_encrypted_credential|responsys_encrypted_credential|
### datafactory linked-service responsys update

responsys create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|responsys_type|responsys_type|
|**--type-properties-endpoint**|any|The endpoint of the Responsys server.|responsys_endpoint|responsys_endpoint|
|**--type-properties-client-id**|any|The client ID associated with the Responsys application. Type: string (or Expression with resultType string).|responsys_client_id|responsys_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|responsys_connect_via|responsys_connect_via|
|**--description**|string|Linked service description.|responsys_description|responsys_description|
|**--parameters**|dictionary|Parameters for linked service.|responsys_parameters|responsys_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|responsys_annotations|responsys_annotations|
|**--type-properties-client-secret**|object|The client secret associated with the Responsys application. Type: string (or Expression with resultType string).|responsys_client_secret|responsys_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true. Type: boolean (or Expression with resultType boolean).|responsys_use_encrypted_endpoints|responsys_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|responsys_use_host_verification|responsys_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|responsys_use_peer_verification|responsys_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|responsys_encrypted_credential|responsys_encrypted_credential|
### datafactory linked-service rest-service create

rest-service create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|restservice_type|rest_service_type|
|**--type-properties-url**|any|The base URL of the REST service.|restservice_url|rest_service_url|
|**--type-properties-authentication-type**|choice|Type of authentication used to connect to the REST service.|restservice_authentication_type|rest_service_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|restservice_connect_via|rest_service_connect_via|
|**--description**|string|Linked service description.|restservice_description|rest_service_description|
|**--parameters**|dictionary|Parameters for linked service.|restservice_parameters|rest_service_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|restservice_annotations|rest_service_annotations|
|**--type-properties-enable-server-certificate-validation**|any|Whether to validate server side SSL certificate when connecting to the endpoint.The default value is true. Type: boolean (or Expression with resultType boolean).|restservice_enable_server_certificate_validation|rest_service_enable_server_certificate_validation|
|**--type-properties-user-name**|any|The user name used in Basic authentication type.|restservice_user_name|rest_service_user_name|
|**--type-properties-password**|object|The password used in Basic authentication type.|restservice_password|rest_service_password|
|**--type-properties-service-principal-id**|any|The application's client ID used in AadServicePrincipal authentication type.|restservice_service_principal_id|rest_service_service_principal_id|
|**--type-properties-service-principal-key**|object|The application's key used in AadServicePrincipal authentication type.|restservice_service_principal_key|rest_service_service_principal_key|
|**--type-properties-tenant**|any|The tenant information (domain name or tenant ID) used in AadServicePrincipal authentication type under which your application resides.|restservice_tenant|rest_service_tenant|
|**--type-properties-aad-resource-id**|any|The resource you are requesting authorization to use.|restservice_aad_resource_id|rest_service_aad_resource_id|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|restservice_encrypted_credential|rest_service_encrypted_credential|
### datafactory linked-service rest-service update

rest-service create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|restservice_type|rest_service_type|
|**--type-properties-url**|any|The base URL of the REST service.|restservice_url|rest_service_url|
|**--type-properties-authentication-type**|choice|Type of authentication used to connect to the REST service.|restservice_authentication_type|rest_service_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|restservice_connect_via|rest_service_connect_via|
|**--description**|string|Linked service description.|restservice_description|rest_service_description|
|**--parameters**|dictionary|Parameters for linked service.|restservice_parameters|rest_service_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|restservice_annotations|rest_service_annotations|
|**--type-properties-enable-server-certificate-validation**|any|Whether to validate server side SSL certificate when connecting to the endpoint.The default value is true. Type: boolean (or Expression with resultType boolean).|restservice_enable_server_certificate_validation|rest_service_enable_server_certificate_validation|
|**--type-properties-user-name**|any|The user name used in Basic authentication type.|restservice_user_name|rest_service_user_name|
|**--type-properties-password**|object|The password used in Basic authentication type.|restservice_password|rest_service_password|
|**--type-properties-service-principal-id**|any|The application's client ID used in AadServicePrincipal authentication type.|restservice_service_principal_id|rest_service_service_principal_id|
|**--type-properties-service-principal-key**|object|The application's key used in AadServicePrincipal authentication type.|restservice_service_principal_key|rest_service_service_principal_key|
|**--type-properties-tenant**|any|The tenant information (domain name or tenant ID) used in AadServicePrincipal authentication type under which your application resides.|restservice_tenant|rest_service_tenant|
|**--type-properties-aad-resource-id**|any|The resource you are requesting authorization to use.|restservice_aad_resource_id|rest_service_aad_resource_id|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|restservice_encrypted_credential|rest_service_encrypted_credential|
### datafactory linked-service salesforce create

salesforce create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|salesforce_type|salesforce_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|salesforce_connect_via|salesforce_connect_via|
|**--description**|string|Linked service description.|salesforce_description|salesforce_description|
|**--parameters**|dictionary|Parameters for linked service.|salesforce_parameters|salesforce_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|salesforce_annotations|salesforce_annotations|
|**--type-properties-environment-url**|any|The URL of Salesforce instance. Default is 'https://login.salesforce.com'. To copy data from sandbox, specify 'https://test.salesforce.com'. To copy data from custom domain, specify, for example, 'https://[domain].my.salesforce.com'. Type: string (or Expression with resultType string).|salesforce_environment_url|salesforce_environment_url|
|**--type-properties-username**|any|The username for Basic authentication of the Salesforce instance. Type: string (or Expression with resultType string).|salesforce_username|salesforce_username|
|**--type-properties-password**|object|The password for Basic authentication of the Salesforce instance.|salesforce_password|salesforce_password|
|**--type-properties-security-token**|object|The security token is optional to remotely access Salesforce instance.|salesforce_security_token|salesforce_security_token|
|**--type-properties-api-version**|any|The Salesforce API version used in ADF. Type: string (or Expression with resultType string).|salesforce_api_version|salesforce_api_version|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|salesforce_encrypted_credential|salesforce_encrypted_credential|
### datafactory linked-service salesforce update

salesforce create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|salesforce_type|salesforce_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|salesforce_connect_via|salesforce_connect_via|
|**--description**|string|Linked service description.|salesforce_description|salesforce_description|
|**--parameters**|dictionary|Parameters for linked service.|salesforce_parameters|salesforce_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|salesforce_annotations|salesforce_annotations|
|**--type-properties-environment-url**|any|The URL of Salesforce instance. Default is 'https://login.salesforce.com'. To copy data from sandbox, specify 'https://test.salesforce.com'. To copy data from custom domain, specify, for example, 'https://[domain].my.salesforce.com'. Type: string (or Expression with resultType string).|salesforce_environment_url|salesforce_environment_url|
|**--type-properties-username**|any|The username for Basic authentication of the Salesforce instance. Type: string (or Expression with resultType string).|salesforce_username|salesforce_username|
|**--type-properties-password**|object|The password for Basic authentication of the Salesforce instance.|salesforce_password|salesforce_password|
|**--type-properties-security-token**|object|The security token is optional to remotely access Salesforce instance.|salesforce_security_token|salesforce_security_token|
|**--type-properties-api-version**|any|The Salesforce API version used in ADF. Type: string (or Expression with resultType string).|salesforce_api_version|salesforce_api_version|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|salesforce_encrypted_credential|salesforce_encrypted_credential|
### datafactory linked-service salesforce-marketing-cloud create

salesforce-marketing-cloud create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|salesforcemarketingcloud_type|salesforce_marketing_cloud_type|
|**--type-properties-client-id**|any|The client ID associated with the Salesforce Marketing Cloud application. Type: string (or Expression with resultType string).|salesforcemarketingcloud_client_id|salesforce_marketing_cloud_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|salesforcemarketingcloud_connect_via|salesforce_marketing_cloud_connect_via|
|**--description**|string|Linked service description.|salesforcemarketingcloud_description|salesforce_marketing_cloud_description|
|**--parameters**|dictionary|Parameters for linked service.|salesforcemarketingcloud_parameters|salesforce_marketing_cloud_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|salesforcemarketingcloud_annotations|salesforce_marketing_cloud_annotations|
|**--type-properties-client-secret**|object|The client secret associated with the Salesforce Marketing Cloud application. Type: string (or Expression with resultType string).|salesforcemarketingcloud_client_secret|salesforce_marketing_cloud_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true. Type: boolean (or Expression with resultType boolean).|salesforcemarketingcloud_use_encrypted_endpoints|salesforce_marketing_cloud_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|salesforcemarketingcloud_use_host_verification|salesforce_marketing_cloud_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|salesforcemarketingcloud_use_peer_verification|salesforce_marketing_cloud_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|salesforcemarketingcloud_encrypted_credential|salesforce_marketing_cloud_encrypted_credential|
### datafactory linked-service salesforce-marketing-cloud update

salesforce-marketing-cloud create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|salesforcemarketingcloud_type|salesforce_marketing_cloud_type|
|**--type-properties-client-id**|any|The client ID associated with the Salesforce Marketing Cloud application. Type: string (or Expression with resultType string).|salesforcemarketingcloud_client_id|salesforce_marketing_cloud_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|salesforcemarketingcloud_connect_via|salesforce_marketing_cloud_connect_via|
|**--description**|string|Linked service description.|salesforcemarketingcloud_description|salesforce_marketing_cloud_description|
|**--parameters**|dictionary|Parameters for linked service.|salesforcemarketingcloud_parameters|salesforce_marketing_cloud_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|salesforcemarketingcloud_annotations|salesforce_marketing_cloud_annotations|
|**--type-properties-client-secret**|object|The client secret associated with the Salesforce Marketing Cloud application. Type: string (or Expression with resultType string).|salesforcemarketingcloud_client_secret|salesforce_marketing_cloud_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true. Type: boolean (or Expression with resultType boolean).|salesforcemarketingcloud_use_encrypted_endpoints|salesforce_marketing_cloud_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|salesforcemarketingcloud_use_host_verification|salesforce_marketing_cloud_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true. Type: boolean (or Expression with resultType boolean).|salesforcemarketingcloud_use_peer_verification|salesforce_marketing_cloud_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|salesforcemarketingcloud_encrypted_credential|salesforce_marketing_cloud_encrypted_credential|
### datafactory linked-service salesforce-service-cloud create

salesforce-service-cloud create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|salesforceservicecloud_type|salesforce_service_cloud_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|salesforceservicecloud_connect_via|salesforce_service_cloud_connect_via|
|**--description**|string|Linked service description.|salesforceservicecloud_description|salesforce_service_cloud_description|
|**--parameters**|dictionary|Parameters for linked service.|salesforceservicecloud_parameters|salesforce_service_cloud_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|salesforceservicecloud_annotations|salesforce_service_cloud_annotations|
|**--type-properties-environment-url**|any|The URL of Salesforce Service Cloud instance. Default is 'https://login.salesforce.com'. To copy data from sandbox, specify 'https://test.salesforce.com'. To copy data from custom domain, specify, for example, 'https://[domain].my.salesforce.com'. Type: string (or Expression with resultType string).|salesforceservicecloud_environment_url|salesforce_service_cloud_environment_url|
|**--type-properties-username**|any|The username for Basic authentication of the Salesforce instance. Type: string (or Expression with resultType string).|salesforceservicecloud_username|salesforce_service_cloud_username|
|**--type-properties-password**|object|The password for Basic authentication of the Salesforce instance.|salesforceservicecloud_password|salesforce_service_cloud_password|
|**--type-properties-security-token**|object|The security token is optional to remotely access Salesforce instance.|salesforceservicecloud_security_token|salesforce_service_cloud_security_token|
|**--type-properties-api-version**|any|The Salesforce API version used in ADF. Type: string (or Expression with resultType string).|salesforceservicecloud_api_version|salesforce_service_cloud_api_version|
|**--type-properties-extended-properties**|any|Extended properties appended to the connection string. Type: string (or Expression with resultType string).|salesforceservicecloud_extended_properties|salesforce_service_cloud_extended_properties|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|salesforceservicecloud_encrypted_credential|salesforce_service_cloud_encrypted_credential|
### datafactory linked-service salesforce-service-cloud update

salesforce-service-cloud create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|salesforceservicecloud_type|salesforce_service_cloud_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|salesforceservicecloud_connect_via|salesforce_service_cloud_connect_via|
|**--description**|string|Linked service description.|salesforceservicecloud_description|salesforce_service_cloud_description|
|**--parameters**|dictionary|Parameters for linked service.|salesforceservicecloud_parameters|salesforce_service_cloud_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|salesforceservicecloud_annotations|salesforce_service_cloud_annotations|
|**--type-properties-environment-url**|any|The URL of Salesforce Service Cloud instance. Default is 'https://login.salesforce.com'. To copy data from sandbox, specify 'https://test.salesforce.com'. To copy data from custom domain, specify, for example, 'https://[domain].my.salesforce.com'. Type: string (or Expression with resultType string).|salesforceservicecloud_environment_url|salesforce_service_cloud_environment_url|
|**--type-properties-username**|any|The username for Basic authentication of the Salesforce instance. Type: string (or Expression with resultType string).|salesforceservicecloud_username|salesforce_service_cloud_username|
|**--type-properties-password**|object|The password for Basic authentication of the Salesforce instance.|salesforceservicecloud_password|salesforce_service_cloud_password|
|**--type-properties-security-token**|object|The security token is optional to remotely access Salesforce instance.|salesforceservicecloud_security_token|salesforce_service_cloud_security_token|
|**--type-properties-api-version**|any|The Salesforce API version used in ADF. Type: string (or Expression with resultType string).|salesforceservicecloud_api_version|salesforce_service_cloud_api_version|
|**--type-properties-extended-properties**|any|Extended properties appended to the connection string. Type: string (or Expression with resultType string).|salesforceservicecloud_extended_properties|salesforce_service_cloud_extended_properties|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|salesforceservicecloud_encrypted_credential|salesforce_service_cloud_encrypted_credential|
### datafactory linked-service sap-b-w create

sap-b-w create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|sapbw_type|sap_b_w_type|
|**--type-properties-server**|any|Host name of the SAP BW instance. Type: string (or Expression with resultType string).|sapbw_server|sap_b_w_server|
|**--type-properties-system-number**|any|System number of the BW system. (Usually a two-digit decimal number represented as a string.) Type: string (or Expression with resultType string).|sapbw_system_number|sap_b_w_system_number|
|**--type-properties-client-id**|any|Client ID of the client on the BW system. (Usually a three-digit decimal number represented as a string) Type: string (or Expression with resultType string).|sapbw_client_id|sap_b_w_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|sapbw_connect_via|sap_b_w_connect_via|
|**--description**|string|Linked service description.|sapbw_description|sap_b_w_description|
|**--parameters**|dictionary|Parameters for linked service.|sapbw_parameters|sap_b_w_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sapbw_annotations|sap_b_w_annotations|
|**--type-properties-user-name**|any|Username to access the SAP BW server. Type: string (or Expression with resultType string).|sapbw_user_name|sap_b_w_user_name|
|**--type-properties-password**|object|Password to access the SAP BW server.|sapbw_password|sap_b_w_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sapbw_encrypted_credential|sap_b_w_encrypted_credential|
### datafactory linked-service sap-b-w update

sap-b-w create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|sapbw_type|sap_b_w_type|
|**--type-properties-server**|any|Host name of the SAP BW instance. Type: string (or Expression with resultType string).|sapbw_server|sap_b_w_server|
|**--type-properties-system-number**|any|System number of the BW system. (Usually a two-digit decimal number represented as a string.) Type: string (or Expression with resultType string).|sapbw_system_number|sap_b_w_system_number|
|**--type-properties-client-id**|any|Client ID of the client on the BW system. (Usually a three-digit decimal number represented as a string) Type: string (or Expression with resultType string).|sapbw_client_id|sap_b_w_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|sapbw_connect_via|sap_b_w_connect_via|
|**--description**|string|Linked service description.|sapbw_description|sap_b_w_description|
|**--parameters**|dictionary|Parameters for linked service.|sapbw_parameters|sap_b_w_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sapbw_annotations|sap_b_w_annotations|
|**--type-properties-user-name**|any|Username to access the SAP BW server. Type: string (or Expression with resultType string).|sapbw_user_name|sap_b_w_user_name|
|**--type-properties-password**|object|Password to access the SAP BW server.|sapbw_password|sap_b_w_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sapbw_encrypted_credential|sap_b_w_encrypted_credential|
### datafactory linked-service sap-cloud-for-customer create

sap-cloud-for-customer create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|sapcloudforcustomer_type|sap_cloud_for_customer_type|
|**--type-properties-url**|any|The URL of SAP Cloud for Customer OData API. For example, '[https://[tenantname].crm.ondemand.com/sap/c4c/odata/v1]'. Type: string (or Expression with resultType string).|sapcloudforcustomer_url|sap_cloud_for_customer_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|sapcloudforcustomer_connect_via|sap_cloud_for_customer_connect_via|
|**--description**|string|Linked service description.|sapcloudforcustomer_description|sap_cloud_for_customer_description|
|**--parameters**|dictionary|Parameters for linked service.|sapcloudforcustomer_parameters|sap_cloud_for_customer_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sapcloudforcustomer_annotations|sap_cloud_for_customer_annotations|
|**--type-properties-username**|any|The username for Basic authentication. Type: string (or Expression with resultType string).|sapcloudforcustomer_username|sap_cloud_for_customer_username|
|**--type-properties-password**|object|The password for Basic authentication.|sapcloudforcustomer_password|sap_cloud_for_customer_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Either encryptedCredential or username/password must be provided. Type: string (or Expression with resultType string).|sapcloudforcustomer_encrypted_credential|sap_cloud_for_customer_encrypted_credential|
### datafactory linked-service sap-cloud-for-customer update

sap-cloud-for-customer create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|sapcloudforcustomer_type|sap_cloud_for_customer_type|
|**--type-properties-url**|any|The URL of SAP Cloud for Customer OData API. For example, '[https://[tenantname].crm.ondemand.com/sap/c4c/odata/v1]'. Type: string (or Expression with resultType string).|sapcloudforcustomer_url|sap_cloud_for_customer_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|sapcloudforcustomer_connect_via|sap_cloud_for_customer_connect_via|
|**--description**|string|Linked service description.|sapcloudforcustomer_description|sap_cloud_for_customer_description|
|**--parameters**|dictionary|Parameters for linked service.|sapcloudforcustomer_parameters|sap_cloud_for_customer_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sapcloudforcustomer_annotations|sap_cloud_for_customer_annotations|
|**--type-properties-username**|any|The username for Basic authentication. Type: string (or Expression with resultType string).|sapcloudforcustomer_username|sap_cloud_for_customer_username|
|**--type-properties-password**|object|The password for Basic authentication.|sapcloudforcustomer_password|sap_cloud_for_customer_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Either encryptedCredential or username/password must be provided. Type: string (or Expression with resultType string).|sapcloudforcustomer_encrypted_credential|sap_cloud_for_customer_encrypted_credential|
### datafactory linked-service sap-ecc create

sap-ecc create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|sapecc_type|sap_ecc_type|
|**--type-properties-url**|string|The URL of SAP ECC OData API. For example, '[https://hostname:port/sap/opu/odata/sap/servicename/]'. Type: string (or Expression with resultType string).|sapecc_url|sap_ecc_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|sapecc_connect_via|sap_ecc_connect_via|
|**--description**|string|Linked service description.|sapecc_description|sap_ecc_description|
|**--parameters**|dictionary|Parameters for linked service.|sapecc_parameters|sap_ecc_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sapecc_annotations|sap_ecc_annotations|
|**--type-properties-username**|string|The username for Basic authentication. Type: string (or Expression with resultType string).|sapecc_username|sap_ecc_username|
|**--type-properties-password**|object|The password for Basic authentication.|sapecc_password|sap_ecc_password|
|**--type-properties-encrypted-credential**|string|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Either encryptedCredential or username/password must be provided. Type: string (or Expression with resultType string).|sapecc_encrypted_credential|sap_ecc_encrypted_credential|
### datafactory linked-service sap-ecc update

sap-ecc create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|sapecc_type|sap_ecc_type|
|**--type-properties-url**|string|The URL of SAP ECC OData API. For example, '[https://hostname:port/sap/opu/odata/sap/servicename/]'. Type: string (or Expression with resultType string).|sapecc_url|sap_ecc_url|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|sapecc_connect_via|sap_ecc_connect_via|
|**--description**|string|Linked service description.|sapecc_description|sap_ecc_description|
|**--parameters**|dictionary|Parameters for linked service.|sapecc_parameters|sap_ecc_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sapecc_annotations|sap_ecc_annotations|
|**--type-properties-username**|string|The username for Basic authentication. Type: string (or Expression with resultType string).|sapecc_username|sap_ecc_username|
|**--type-properties-password**|object|The password for Basic authentication.|sapecc_password|sap_ecc_password|
|**--type-properties-encrypted-credential**|string|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Either encryptedCredential or username/password must be provided. Type: string (or Expression with resultType string).|sapecc_encrypted_credential|sap_ecc_encrypted_credential|
### datafactory linked-service sap-hana create

sap-hana create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|saphana_type|sap_hana_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|saphana_connect_via|sap_hana_connect_via|
|**--description**|string|Linked service description.|saphana_description|sap_hana_description|
|**--parameters**|dictionary|Parameters for linked service.|saphana_parameters|sap_hana_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|saphana_annotations|sap_hana_annotations|
|**--type-properties-connection-string**|any|SAP HANA ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|saphana_connection_string|sap_hana_connection_string|
|**--type-properties-server**|any|Host name of the SAP HANA server. Type: string (or Expression with resultType string).|saphana_server|sap_hana_server|
|**--type-properties-authentication-type**|choice|The authentication type to be used to connect to the SAP HANA server.|saphana_authentication_type|sap_hana_authentication_type|
|**--type-properties-user-name**|any|Username to access the SAP HANA server. Type: string (or Expression with resultType string).|saphana_user_name|sap_hana_user_name|
|**--type-properties-password**|object|Password to access the SAP HANA server.|saphana_password|sap_hana_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|saphana_encrypted_credential|sap_hana_encrypted_credential|
### datafactory linked-service sap-hana update

sap-hana create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|saphana_type|sap_hana_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|saphana_connect_via|sap_hana_connect_via|
|**--description**|string|Linked service description.|saphana_description|sap_hana_description|
|**--parameters**|dictionary|Parameters for linked service.|saphana_parameters|sap_hana_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|saphana_annotations|sap_hana_annotations|
|**--type-properties-connection-string**|any|SAP HANA ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|saphana_connection_string|sap_hana_connection_string|
|**--type-properties-server**|any|Host name of the SAP HANA server. Type: string (or Expression with resultType string).|saphana_server|sap_hana_server|
|**--type-properties-authentication-type**|choice|The authentication type to be used to connect to the SAP HANA server.|saphana_authentication_type|sap_hana_authentication_type|
|**--type-properties-user-name**|any|Username to access the SAP HANA server. Type: string (or Expression with resultType string).|saphana_user_name|sap_hana_user_name|
|**--type-properties-password**|object|Password to access the SAP HANA server.|saphana_password|sap_hana_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|saphana_encrypted_credential|sap_hana_encrypted_credential|
### datafactory linked-service sap-open-hub create

sap-open-hub create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|sapopenhub_type|sap_open_hub_type|
|**--type-properties-server**|any|Host name of the SAP BW instance where the open hub destination is located. Type: string (or Expression with resultType string).|sapopenhub_server|sap_open_hub_server|
|**--type-properties-system-number**|any|System number of the BW system where the open hub destination is located. (Usually a two-digit decimal number represented as a string.) Type: string (or Expression with resultType string).|sapopenhub_system_number|sap_open_hub_system_number|
|**--type-properties-client-id**|any|Client ID of the client on the BW system where the open hub destination is located. (Usually a three-digit decimal number represented as a string) Type: string (or Expression with resultType string).|sapopenhub_client_id|sap_open_hub_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|sapopenhub_connect_via|sap_open_hub_connect_via|
|**--description**|string|Linked service description.|sapopenhub_description|sap_open_hub_description|
|**--parameters**|dictionary|Parameters for linked service.|sapopenhub_parameters|sap_open_hub_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sapopenhub_annotations|sap_open_hub_annotations|
|**--type-properties-language**|any|Language of the BW system where the open hub destination is located. The default value is EN. Type: string (or Expression with resultType string).|sapopenhub_language|sap_open_hub_language|
|**--type-properties-user-name**|any|Username to access the SAP BW server where the open hub destination is located. Type: string (or Expression with resultType string).|sapopenhub_user_name|sap_open_hub_user_name|
|**--type-properties-password**|object|Password to access the SAP BW server where the open hub destination is located.|sapopenhub_password|sap_open_hub_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sapopenhub_encrypted_credential|sap_open_hub_encrypted_credential|
### datafactory linked-service sap-open-hub update

sap-open-hub create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|sapopenhub_type|sap_open_hub_type|
|**--type-properties-server**|any|Host name of the SAP BW instance where the open hub destination is located. Type: string (or Expression with resultType string).|sapopenhub_server|sap_open_hub_server|
|**--type-properties-system-number**|any|System number of the BW system where the open hub destination is located. (Usually a two-digit decimal number represented as a string.) Type: string (or Expression with resultType string).|sapopenhub_system_number|sap_open_hub_system_number|
|**--type-properties-client-id**|any|Client ID of the client on the BW system where the open hub destination is located. (Usually a three-digit decimal number represented as a string) Type: string (or Expression with resultType string).|sapopenhub_client_id|sap_open_hub_client_id|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|sapopenhub_connect_via|sap_open_hub_connect_via|
|**--description**|string|Linked service description.|sapopenhub_description|sap_open_hub_description|
|**--parameters**|dictionary|Parameters for linked service.|sapopenhub_parameters|sap_open_hub_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sapopenhub_annotations|sap_open_hub_annotations|
|**--type-properties-language**|any|Language of the BW system where the open hub destination is located. The default value is EN. Type: string (or Expression with resultType string).|sapopenhub_language|sap_open_hub_language|
|**--type-properties-user-name**|any|Username to access the SAP BW server where the open hub destination is located. Type: string (or Expression with resultType string).|sapopenhub_user_name|sap_open_hub_user_name|
|**--type-properties-password**|object|Password to access the SAP BW server where the open hub destination is located.|sapopenhub_password|sap_open_hub_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sapopenhub_encrypted_credential|sap_open_hub_encrypted_credential|
### datafactory linked-service sap-table create

sap-table create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|saptable_type|sap_table_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|saptable_connect_via|sap_table_connect_via|
|**--description**|string|Linked service description.|saptable_description|sap_table_description|
|**--parameters**|dictionary|Parameters for linked service.|saptable_parameters|sap_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|saptable_annotations|sap_table_annotations|
|**--type-properties-server**|any|Host name of the SAP instance where the table is located. Type: string (or Expression with resultType string).|saptable_server|sap_table_server|
|**--type-properties-system-number**|any|System number of the SAP system where the table is located. (Usually a two-digit decimal number represented as a string.) Type: string (or Expression with resultType string).|saptable_system_number|sap_table_system_number|
|**--type-properties-client-id**|any|Client ID of the client on the SAP system where the table is located. (Usually a three-digit decimal number represented as a string) Type: string (or Expression with resultType string).|saptable_client_id|sap_table_client_id|
|**--type-properties-language**|any|Language of the SAP system where the table is located. The default value is EN. Type: string (or Expression with resultType string).|saptable_language|sap_table_language|
|**--type-properties-system-id**|any|SystemID of the SAP system where the table is located. Type: string (or Expression with resultType string).|saptable_system_id|sap_table_system_id|
|**--type-properties-user-name**|any|Username to access the SAP server where the table is located. Type: string (or Expression with resultType string).|saptable_user_name|sap_table_user_name|
|**--type-properties-password**|object|Password to access the SAP server where the table is located.|saptable_password|sap_table_password|
|**--type-properties-message-server**|any|The hostname of the SAP Message Server. Type: string (or Expression with resultType string).|saptable_message_server|sap_table_message_server|
|**--type-properties-message-server-service**|any|The service name or port number of the Message Server. Type: string (or Expression with resultType string).|saptable_message_server_service|sap_table_message_server_service|
|**--type-properties-snc-mode**|any|SNC activation indicator to access the SAP server where the table is located. Must be either 0 (off) or 1 (on). Type: string (or Expression with resultType string).|saptable_snc_mode|sap_table_snc_mode|
|**--type-properties-snc-my-name**|any|Initiator's SNC name to access the SAP server where the table is located. Type: string (or Expression with resultType string).|saptable_snc_my_name|sap_table_snc_my_name|
|**--type-properties-snc-partner-name**|any|Communication partner's SNC name to access the SAP server where the table is located. Type: string (or Expression with resultType string).|saptable_snc_partner_name|sap_table_snc_partner_name|
|**--type-properties-snc-library-path**|any|External security product's library to access the SAP server where the table is located. Type: string (or Expression with resultType string).|saptable_snc_library_path|sap_table_snc_library_path|
|**--type-properties-snc-qop**|any|SNC Quality of Protection. Allowed value include: 1, 2, 3, 8, 9. Type: string (or Expression with resultType string).|saptable_snc_qop|sap_table_snc_qop|
|**--type-properties-logon-group**|any|The Logon Group for the SAP System. Type: string (or Expression with resultType string).|saptable_logon_group|sap_table_logon_group|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|saptable_encrypted_credential|sap_table_encrypted_credential|
### datafactory linked-service sap-table update

sap-table create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|saptable_type|sap_table_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|saptable_connect_via|sap_table_connect_via|
|**--description**|string|Linked service description.|saptable_description|sap_table_description|
|**--parameters**|dictionary|Parameters for linked service.|saptable_parameters|sap_table_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|saptable_annotations|sap_table_annotations|
|**--type-properties-server**|any|Host name of the SAP instance where the table is located. Type: string (or Expression with resultType string).|saptable_server|sap_table_server|
|**--type-properties-system-number**|any|System number of the SAP system where the table is located. (Usually a two-digit decimal number represented as a string.) Type: string (or Expression with resultType string).|saptable_system_number|sap_table_system_number|
|**--type-properties-client-id**|any|Client ID of the client on the SAP system where the table is located. (Usually a three-digit decimal number represented as a string) Type: string (or Expression with resultType string).|saptable_client_id|sap_table_client_id|
|**--type-properties-language**|any|Language of the SAP system where the table is located. The default value is EN. Type: string (or Expression with resultType string).|saptable_language|sap_table_language|
|**--type-properties-system-id**|any|SystemID of the SAP system where the table is located. Type: string (or Expression with resultType string).|saptable_system_id|sap_table_system_id|
|**--type-properties-user-name**|any|Username to access the SAP server where the table is located. Type: string (or Expression with resultType string).|saptable_user_name|sap_table_user_name|
|**--type-properties-password**|object|Password to access the SAP server where the table is located.|saptable_password|sap_table_password|
|**--type-properties-message-server**|any|The hostname of the SAP Message Server. Type: string (or Expression with resultType string).|saptable_message_server|sap_table_message_server|
|**--type-properties-message-server-service**|any|The service name or port number of the Message Server. Type: string (or Expression with resultType string).|saptable_message_server_service|sap_table_message_server_service|
|**--type-properties-snc-mode**|any|SNC activation indicator to access the SAP server where the table is located. Must be either 0 (off) or 1 (on). Type: string (or Expression with resultType string).|saptable_snc_mode|sap_table_snc_mode|
|**--type-properties-snc-my-name**|any|Initiator's SNC name to access the SAP server where the table is located. Type: string (or Expression with resultType string).|saptable_snc_my_name|sap_table_snc_my_name|
|**--type-properties-snc-partner-name**|any|Communication partner's SNC name to access the SAP server where the table is located. Type: string (or Expression with resultType string).|saptable_snc_partner_name|sap_table_snc_partner_name|
|**--type-properties-snc-library-path**|any|External security product's library to access the SAP server where the table is located. Type: string (or Expression with resultType string).|saptable_snc_library_path|sap_table_snc_library_path|
|**--type-properties-snc-qop**|any|SNC Quality of Protection. Allowed value include: 1, 2, 3, 8, 9. Type: string (or Expression with resultType string).|saptable_snc_qop|sap_table_snc_qop|
|**--type-properties-logon-group**|any|The Logon Group for the SAP System. Type: string (or Expression with resultType string).|saptable_logon_group|sap_table_logon_group|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|saptable_encrypted_credential|sap_table_encrypted_credential|
### datafactory linked-service service-now create

service-now create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|servicenow_type|service_now_type|
|**--type-properties-endpoint**|any|The endpoint of the ServiceNow server. (i.e. :code:`<instance>`.service-now.com)|servicenow_endpoint|service_now_endpoint|
|**--type-properties-authentication-type**|choice|The authentication type to use.|servicenow_authentication_type|service_now_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|servicenow_connect_via|service_now_connect_via|
|**--description**|string|Linked service description.|servicenow_description|service_now_description|
|**--parameters**|dictionary|Parameters for linked service.|servicenow_parameters|service_now_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|servicenow_annotations|service_now_annotations|
|**--type-properties-username**|any|The user name used to connect to the ServiceNow server for Basic and OAuth2 authentication.|servicenow_username|service_now_username|
|**--type-properties-password**|object|The password corresponding to the user name for Basic and OAuth2 authentication.|servicenow_password|service_now_password|
|**--type-properties-client-id**|any|The client id for OAuth2 authentication.|servicenow_client_id|service_now_client_id|
|**--type-properties-client-secret**|object|The client secret for OAuth2 authentication.|servicenow_client_secret|service_now_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|servicenow_use_encrypted_endpoints|service_now_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|servicenow_use_host_verification|service_now_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|servicenow_use_peer_verification|service_now_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|servicenow_encrypted_credential|service_now_encrypted_credential|
### datafactory linked-service service-now update

service-now create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|servicenow_type|service_now_type|
|**--type-properties-endpoint**|any|The endpoint of the ServiceNow server. (i.e. :code:`<instance>`.service-now.com)|servicenow_endpoint|service_now_endpoint|
|**--type-properties-authentication-type**|choice|The authentication type to use.|servicenow_authentication_type|service_now_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|servicenow_connect_via|service_now_connect_via|
|**--description**|string|Linked service description.|servicenow_description|service_now_description|
|**--parameters**|dictionary|Parameters for linked service.|servicenow_parameters|service_now_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|servicenow_annotations|service_now_annotations|
|**--type-properties-username**|any|The user name used to connect to the ServiceNow server for Basic and OAuth2 authentication.|servicenow_username|service_now_username|
|**--type-properties-password**|object|The password corresponding to the user name for Basic and OAuth2 authentication.|servicenow_password|service_now_password|
|**--type-properties-client-id**|any|The client id for OAuth2 authentication.|servicenow_client_id|service_now_client_id|
|**--type-properties-client-secret**|object|The client secret for OAuth2 authentication.|servicenow_client_secret|service_now_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|servicenow_use_encrypted_endpoints|service_now_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|servicenow_use_host_verification|service_now_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|servicenow_use_peer_verification|service_now_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|servicenow_encrypted_credential|service_now_encrypted_credential|
### datafactory linked-service sftp create

sftp create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|sftp_type|sftp_type|
|**--type-properties-host**|any|The SFTP server host name. Type: string (or Expression with resultType string).|sftp_host|sftp_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|sftp_connect_via|sftp_connect_via|
|**--description**|string|Linked service description.|sftp_description|sftp_description|
|**--parameters**|dictionary|Parameters for linked service.|sftp_parameters|sftp_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sftp_annotations|sftp_annotations|
|**--type-properties-port**|any|The TCP port number that the SFTP server uses to listen for client connections. Default value is 22. Type: integer (or Expression with resultType integer), minimum: 0.|sftp_port|sftp_port|
|**--type-properties-authentication-type**|choice|The authentication type to be used to connect to the FTP server.|sftp_authentication_type|sftp_authentication_type|
|**--type-properties-user-name**|any|The username used to log on to the SFTP server. Type: string (or Expression with resultType string).|sftp_user_name|sftp_user_name|
|**--type-properties-password**|object|Password to logon the SFTP server for Basic authentication.|sftp_password|sftp_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sftp_encrypted_credential|sftp_encrypted_credential|
|**--type-properties-private-key-path**|any|The SSH private key file path for SshPublicKey authentication. Only valid for on-premises copy. For on-premises copy with SshPublicKey authentication, either PrivateKeyPath or PrivateKeyContent should be specified. SSH private key should be OpenSSH format. Type: string (or Expression with resultType string).|sftp_private_key_path|sftp_private_key_path|
|**--type-properties-private-key-content**|object|Base64 encoded SSH private key content for SshPublicKey authentication. For on-premises copy with SshPublicKey authentication, either PrivateKeyPath or PrivateKeyContent should be specified. SSH private key should be OpenSSH format.|sftp_private_key_content|sftp_private_key_content|
|**--type-properties-pass-phrase**|object|The password to decrypt the SSH private key if the SSH private key is encrypted.|sftp_pass_phrase|sftp_pass_phrase|
|**--type-properties-skip-host-key-validation**|any|If true, skip the SSH host key validation. Default value is false. Type: boolean (or Expression with resultType boolean).|sftp_skip_host_key_validation|sftp_skip_host_key_validation|
|**--type-properties-host-key-fingerprint**|any|The host key finger-print of the SFTP server. When SkipHostKeyValidation is false, HostKeyFingerprint should be specified. Type: string (or Expression with resultType string).|sftp_host_key_fingerprint|sftp_host_key_fingerprint|
### datafactory linked-service sftp update

sftp create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|sftp_type|sftp_type|
|**--type-properties-host**|any|The SFTP server host name. Type: string (or Expression with resultType string).|sftp_host|sftp_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|sftp_connect_via|sftp_connect_via|
|**--description**|string|Linked service description.|sftp_description|sftp_description|
|**--parameters**|dictionary|Parameters for linked service.|sftp_parameters|sftp_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sftp_annotations|sftp_annotations|
|**--type-properties-port**|any|The TCP port number that the SFTP server uses to listen for client connections. Default value is 22. Type: integer (or Expression with resultType integer), minimum: 0.|sftp_port|sftp_port|
|**--type-properties-authentication-type**|choice|The authentication type to be used to connect to the FTP server.|sftp_authentication_type|sftp_authentication_type|
|**--type-properties-user-name**|any|The username used to log on to the SFTP server. Type: string (or Expression with resultType string).|sftp_user_name|sftp_user_name|
|**--type-properties-password**|object|Password to logon the SFTP server for Basic authentication.|sftp_password|sftp_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sftp_encrypted_credential|sftp_encrypted_credential|
|**--type-properties-private-key-path**|any|The SSH private key file path for SshPublicKey authentication. Only valid for on-premises copy. For on-premises copy with SshPublicKey authentication, either PrivateKeyPath or PrivateKeyContent should be specified. SSH private key should be OpenSSH format. Type: string (or Expression with resultType string).|sftp_private_key_path|sftp_private_key_path|
|**--type-properties-private-key-content**|object|Base64 encoded SSH private key content for SshPublicKey authentication. For on-premises copy with SshPublicKey authentication, either PrivateKeyPath or PrivateKeyContent should be specified. SSH private key should be OpenSSH format.|sftp_private_key_content|sftp_private_key_content|
|**--type-properties-pass-phrase**|object|The password to decrypt the SSH private key if the SSH private key is encrypted.|sftp_pass_phrase|sftp_pass_phrase|
|**--type-properties-skip-host-key-validation**|any|If true, skip the SSH host key validation. Default value is false. Type: boolean (or Expression with resultType boolean).|sftp_skip_host_key_validation|sftp_skip_host_key_validation|
|**--type-properties-host-key-fingerprint**|any|The host key finger-print of the SFTP server. When SkipHostKeyValidation is false, HostKeyFingerprint should be specified. Type: string (or Expression with resultType string).|sftp_host_key_fingerprint|sftp_host_key_fingerprint|
### datafactory linked-service shopify create

shopify create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|shopify_type|shopify_type|
|**--type-properties-host**|any|The endpoint of the Shopify server. (i.e. mystore.myshopify.com)|shopify_host|shopify_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|shopify_connect_via|shopify_connect_via|
|**--description**|string|Linked service description.|shopify_description|shopify_description|
|**--parameters**|dictionary|Parameters for linked service.|shopify_parameters|shopify_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|shopify_annotations|shopify_annotations|
|**--type-properties-access-token**|object|The API access token that can be used to access Shopify’s data. The token won't expire if it is offline mode.|shopify_access_token|shopify_access_token|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|shopify_use_encrypted_endpoints|shopify_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|shopify_use_host_verification|shopify_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|shopify_use_peer_verification|shopify_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|shopify_encrypted_credential|shopify_encrypted_credential|
### datafactory linked-service shopify update

shopify create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|shopify_type|shopify_type|
|**--type-properties-host**|any|The endpoint of the Shopify server. (i.e. mystore.myshopify.com)|shopify_host|shopify_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|shopify_connect_via|shopify_connect_via|
|**--description**|string|Linked service description.|shopify_description|shopify_description|
|**--parameters**|dictionary|Parameters for linked service.|shopify_parameters|shopify_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|shopify_annotations|shopify_annotations|
|**--type-properties-access-token**|object|The API access token that can be used to access Shopify’s data. The token won't expire if it is offline mode.|shopify_access_token|shopify_access_token|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|shopify_use_encrypted_endpoints|shopify_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|shopify_use_host_verification|shopify_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|shopify_use_peer_verification|shopify_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|shopify_encrypted_credential|shopify_encrypted_credential|
### datafactory linked-service show

show a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--if-none-match**|string|ETag of the linked service entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|if_none_match|
### datafactory linked-service snowflake create

snowflake create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|snowflake_type|snowflake_type|
|**--type-properties-connection-string**|any|The connection string of snowflake. Type: string, SecureString.|snowflake_connection_string|snowflake_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|snowflake_connect_via|snowflake_connect_via|
|**--description**|string|Linked service description.|snowflake_description|snowflake_description|
|**--parameters**|dictionary|Parameters for linked service.|snowflake_parameters|snowflake_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|snowflake_annotations|snowflake_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|snowflake_password|snowflake_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|snowflake_encrypted_credential|snowflake_encrypted_credential|
### datafactory linked-service snowflake update

snowflake create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|snowflake_type|snowflake_type|
|**--type-properties-connection-string**|any|The connection string of snowflake. Type: string, SecureString.|snowflake_connection_string|snowflake_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|snowflake_connect_via|snowflake_connect_via|
|**--description**|string|Linked service description.|snowflake_description|snowflake_description|
|**--parameters**|dictionary|Parameters for linked service.|snowflake_parameters|snowflake_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|snowflake_annotations|snowflake_annotations|
|**--type-properties-password**|object|The Azure key vault secret reference of password in connection string.|snowflake_password|snowflake_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|snowflake_encrypted_credential|snowflake_encrypted_credential|
### datafactory linked-service spark create

spark create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|spark_type|spark_type|
|**--type-properties-host**|any|IP address or host name of the Spark server|spark_host|spark_host|
|**--type-properties-port**|any|The TCP port that the Spark server uses to listen for client connections.|spark_port|spark_port|
|**--type-properties-authentication-type**|choice|The authentication method used to access the Spark server.|spark_authentication_type|spark_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|spark_connect_via|spark_connect_via|
|**--description**|string|Linked service description.|spark_description|spark_description|
|**--parameters**|dictionary|Parameters for linked service.|spark_parameters|spark_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|spark_annotations|spark_annotations|
|**--type-properties-server-type**|choice|The type of Spark server.|spark_server_type|spark_server_type|
|**--type-properties-thrift-transport-protocol**|choice|The transport protocol to use in the Thrift layer.|spark_thrift_transport_protocol|spark_thrift_transport_protocol|
|**--type-properties-username**|any|The user name that you use to access Spark Server.|spark_username|spark_username|
|**--type-properties-password**|object|The password corresponding to the user name that you provided in the Username field|spark_password|spark_password|
|**--type-properties-http-path**|any|The partial URL corresponding to the Spark server.|spark_http_path|spark_http_path|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|spark_enable_ssl|spark_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|spark_trusted_cert_path|spark_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|spark_use_system_trust_store|spark_use_system_trust_store|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|spark_allow_host_name_cn_mismatch|spark_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|spark_allow_self_signed_server_cert|spark_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|spark_encrypted_credential|spark_encrypted_credential|
### datafactory linked-service spark update

spark create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|spark_type|spark_type|
|**--type-properties-host**|any|IP address or host name of the Spark server|spark_host|spark_host|
|**--type-properties-port**|any|The TCP port that the Spark server uses to listen for client connections.|spark_port|spark_port|
|**--type-properties-authentication-type**|choice|The authentication method used to access the Spark server.|spark_authentication_type|spark_authentication_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|spark_connect_via|spark_connect_via|
|**--description**|string|Linked service description.|spark_description|spark_description|
|**--parameters**|dictionary|Parameters for linked service.|spark_parameters|spark_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|spark_annotations|spark_annotations|
|**--type-properties-server-type**|choice|The type of Spark server.|spark_server_type|spark_server_type|
|**--type-properties-thrift-transport-protocol**|choice|The transport protocol to use in the Thrift layer.|spark_thrift_transport_protocol|spark_thrift_transport_protocol|
|**--type-properties-username**|any|The user name that you use to access Spark Server.|spark_username|spark_username|
|**--type-properties-password**|object|The password corresponding to the user name that you provided in the Username field|spark_password|spark_password|
|**--type-properties-http-path**|any|The partial URL corresponding to the Spark server.|spark_http_path|spark_http_path|
|**--type-properties-enable-ssl**|any|Specifies whether the connections to the server are encrypted using SSL. The default value is false.|spark_enable_ssl|spark_enable_ssl|
|**--type-properties-trusted-cert-path**|any|The full path of the .pem file containing trusted CA certificates for verifying the server when connecting over SSL. This property can only be set when using SSL on self-hosted IR. The default value is the cacerts.pem file installed with the IR.|spark_trusted_cert_path|spark_trusted_cert_path|
|**--type-properties-use-system-trust-store**|any|Specifies whether to use a CA certificate from the system trust store or from a specified PEM file. The default value is false.|spark_use_system_trust_store|spark_use_system_trust_store|
|**--type-properties-allow-host-name-cnmismatch**|any|Specifies whether to require a CA-issued SSL certificate name to match the host name of the server when connecting over SSL. The default value is false.|spark_allow_host_name_cn_mismatch|spark_allow_host_name_cn_mismatch|
|**--type-properties-allow-self-signed-server-cert**|any|Specifies whether to allow self-signed certificates from the server. The default value is false.|spark_allow_self_signed_server_cert|spark_allow_self_signed_server_cert|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|spark_encrypted_credential|spark_encrypted_credential|
### datafactory linked-service sql-server create

sql-server create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|sqlserver_type|sql_server_type|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|sqlserver_connection_string|sql_server_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|sqlserver_connect_via|sql_server_connect_via|
|**--description**|string|Linked service description.|sqlserver_description|sql_server_description|
|**--parameters**|dictionary|Parameters for linked service.|sqlserver_parameters|sql_server_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sqlserver_annotations|sql_server_annotations|
|**--type-properties-user-name**|any|The on-premises Windows authentication user name. Type: string (or Expression with resultType string).|sqlserver_user_name|sql_server_user_name|
|**--type-properties-password**|object|The on-premises Windows authentication password.|sqlserver_password|sql_server_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sqlserver_encrypted_credential|sql_server_encrypted_credential|
### datafactory linked-service sql-server update

sql-server create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|sqlserver_type|sql_server_type|
|**--type-properties-connection-string**|any|The connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|sqlserver_connection_string|sql_server_connection_string|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|sqlserver_connect_via|sql_server_connect_via|
|**--description**|string|Linked service description.|sqlserver_description|sql_server_description|
|**--parameters**|dictionary|Parameters for linked service.|sqlserver_parameters|sql_server_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sqlserver_annotations|sql_server_annotations|
|**--type-properties-user-name**|any|The on-premises Windows authentication user name. Type: string (or Expression with resultType string).|sqlserver_user_name|sql_server_user_name|
|**--type-properties-password**|object|The on-premises Windows authentication password.|sqlserver_password|sql_server_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sqlserver_encrypted_credential|sql_server_encrypted_credential|
### datafactory linked-service square create

square create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|square_type|square_type|
|**--type-properties-host**|any|The URL of the Square instance. (i.e. mystore.mysquare.com)|square_host|square_host|
|**--type-properties-client-id**|any|The client ID associated with your Square application.|square_client_id|square_client_id|
|**--type-properties-redirect-uri**|any|The redirect URL assigned in the Square application dashboard. (i.e. http://localhost:2500)|square_redirect_uri|square_redirect_uri|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|square_connect_via|square_connect_via|
|**--description**|string|Linked service description.|square_description|square_description|
|**--parameters**|dictionary|Parameters for linked service.|square_parameters|square_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|square_annotations|square_annotations|
|**--type-properties-client-secret**|object|The client secret associated with your Square application.|square_client_secret|square_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|square_use_encrypted_endpoints|square_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|square_use_host_verification|square_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|square_use_peer_verification|square_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|square_encrypted_credential|square_encrypted_credential|
### datafactory linked-service square update

square create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|square_type|square_type|
|**--type-properties-host**|any|The URL of the Square instance. (i.e. mystore.mysquare.com)|square_host|square_host|
|**--type-properties-client-id**|any|The client ID associated with your Square application.|square_client_id|square_client_id|
|**--type-properties-redirect-uri**|any|The redirect URL assigned in the Square application dashboard. (i.e. http://localhost:2500)|square_redirect_uri|square_redirect_uri|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|square_connect_via|square_connect_via|
|**--description**|string|Linked service description.|square_description|square_description|
|**--parameters**|dictionary|Parameters for linked service.|square_parameters|square_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|square_annotations|square_annotations|
|**--type-properties-client-secret**|object|The client secret associated with your Square application.|square_client_secret|square_client_secret|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|square_use_encrypted_endpoints|square_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|square_use_host_verification|square_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|square_use_peer_verification|square_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|square_encrypted_credential|square_encrypted_credential|
### datafactory linked-service sybase create

sybase create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|sybase_type|sybase_type|
|**--type-properties-server**|any|Server name for connection. Type: string (or Expression with resultType string).|sybase_server|sybase_server|
|**--type-properties-database**|any|Database name for connection. Type: string (or Expression with resultType string).|sybase_database|sybase_database|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|sybase_connect_via|sybase_connect_via|
|**--description**|string|Linked service description.|sybase_description|sybase_description|
|**--parameters**|dictionary|Parameters for linked service.|sybase_parameters|sybase_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sybase_annotations|sybase_annotations|
|**--type-properties-schema**|any|Schema name for connection. Type: string (or Expression with resultType string).|sybase_schema|sybase_schema|
|**--type-properties-authentication-type**|choice|AuthenticationType to be used for connection.|sybase_authentication_type|sybase_authentication_type|
|**--type-properties-username**|any|Username for authentication. Type: string (or Expression with resultType string).|sybase_username|sybase_username|
|**--type-properties-password**|object|Password for authentication.|sybase_password|sybase_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sybase_encrypted_credential|sybase_encrypted_credential|
### datafactory linked-service sybase update

sybase create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|sybase_type|sybase_type|
|**--type-properties-server**|any|Server name for connection. Type: string (or Expression with resultType string).|sybase_server|sybase_server|
|**--type-properties-database**|any|Database name for connection. Type: string (or Expression with resultType string).|sybase_database|sybase_database|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|sybase_connect_via|sybase_connect_via|
|**--description**|string|Linked service description.|sybase_description|sybase_description|
|**--parameters**|dictionary|Parameters for linked service.|sybase_parameters|sybase_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|sybase_annotations|sybase_annotations|
|**--type-properties-schema**|any|Schema name for connection. Type: string (or Expression with resultType string).|sybase_schema|sybase_schema|
|**--type-properties-authentication-type**|choice|AuthenticationType to be used for connection.|sybase_authentication_type|sybase_authentication_type|
|**--type-properties-username**|any|Username for authentication. Type: string (or Expression with resultType string).|sybase_username|sybase_username|
|**--type-properties-password**|object|Password for authentication.|sybase_password|sybase_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|sybase_encrypted_credential|sybase_encrypted_credential|
### datafactory linked-service teradata create

teradata create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|teradata_type|teradata_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|teradata_connect_via|teradata_connect_via|
|**--description**|string|Linked service description.|teradata_description|teradata_description|
|**--parameters**|dictionary|Parameters for linked service.|teradata_parameters|teradata_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|teradata_annotations|teradata_annotations|
|**--type-properties-connection-string**|any|Teradata ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|teradata_connection_string|teradata_connection_string|
|**--type-properties-server**|any|Server name for connection. Type: string (or Expression with resultType string).|teradata_server|teradata_server|
|**--type-properties-authentication-type**|choice|AuthenticationType to be used for connection.|teradata_authentication_type|teradata_authentication_type|
|**--type-properties-username**|any|Username for authentication. Type: string (or Expression with resultType string).|teradata_username|teradata_username|
|**--type-properties-password**|object|Password for authentication.|teradata_password|teradata_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|teradata_encrypted_credential|teradata_encrypted_credential|
### datafactory linked-service teradata update

teradata create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|teradata_type|teradata_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|teradata_connect_via|teradata_connect_via|
|**--description**|string|Linked service description.|teradata_description|teradata_description|
|**--parameters**|dictionary|Parameters for linked service.|teradata_parameters|teradata_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|teradata_annotations|teradata_annotations|
|**--type-properties-connection-string**|any|Teradata ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|teradata_connection_string|teradata_connection_string|
|**--type-properties-server**|any|Server name for connection. Type: string (or Expression with resultType string).|teradata_server|teradata_server|
|**--type-properties-authentication-type**|choice|AuthenticationType to be used for connection.|teradata_authentication_type|teradata_authentication_type|
|**--type-properties-username**|any|Username for authentication. Type: string (or Expression with resultType string).|teradata_username|teradata_username|
|**--type-properties-password**|object|Password for authentication.|teradata_password|teradata_password|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|teradata_encrypted_credential|teradata_encrypted_credential|
### datafactory linked-service vertica create

vertica create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|vertica_type|vertica_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|vertica_connect_via|vertica_connect_via|
|**--description**|string|Linked service description.|vertica_description|vertica_description|
|**--parameters**|dictionary|Parameters for linked service.|vertica_parameters|vertica_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|vertica_annotations|vertica_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|vertica_connection_string|vertica_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|vertica_pwd|vertica_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|vertica_encrypted_credential|vertica_encrypted_credential|
### datafactory linked-service vertica update

vertica create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|vertica_type|vertica_type|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|vertica_connect_via|vertica_connect_via|
|**--description**|string|Linked service description.|vertica_description|vertica_description|
|**--parameters**|dictionary|Parameters for linked service.|vertica_parameters|vertica_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|vertica_annotations|vertica_annotations|
|**--type-properties-connection-string**|any|An ODBC connection string. Type: string, SecureString or AzureKeyVaultSecretReference.|vertica_connection_string|vertica_connection_string|
|**--type-properties-pwd**|object|The Azure key vault secret reference of password in connection string.|vertica_pwd|vertica_pwd|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|vertica_encrypted_credential|vertica_encrypted_credential|
### datafactory linked-service web create

web create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|web_type|web_type|
|**--type-properties**|object|Web linked service properties.|web_type_properties|web_type_properties|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|web_connect_via|web_connect_via|
|**--description**|string|Linked service description.|web_description|web_description|
|**--parameters**|dictionary|Parameters for linked service.|web_parameters|web_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|web_annotations|web_annotations|
### datafactory linked-service web update

web create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|web_type|web_type|
|**--type-properties**|object|Web linked service properties.|web_type_properties|web_type_properties|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|web_connect_via|web_connect_via|
|**--description**|string|Linked service description.|web_description|web_description|
|**--parameters**|dictionary|Parameters for linked service.|web_parameters|web_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|web_annotations|web_annotations|
### datafactory linked-service xero create

xero create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|xero_type|xero_type|
|**--type-properties-host**|any|The endpoint of the Xero server. (i.e. api.xero.com)|xero_host|xero_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|xero_connect_via|xero_connect_via|
|**--description**|string|Linked service description.|xero_description|xero_description|
|**--parameters**|dictionary|Parameters for linked service.|xero_parameters|xero_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|xero_annotations|xero_annotations|
|**--type-properties-consumer-key**|object|The consumer key associated with the Xero application.|xero_consumer_key|xero_consumer_key|
|**--type-properties-private-key**|object|The private key from the .pem file that was generated for your Xero private application. You must include all the text from the .pem file, including the Unix line endings( ).|xero_private_key|xero_private_key|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|xero_use_encrypted_endpoints|xero_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|xero_use_host_verification|xero_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|xero_use_peer_verification|xero_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|xero_encrypted_credential|xero_encrypted_credential|
### datafactory linked-service xero update

xero create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|xero_type|xero_type|
|**--type-properties-host**|any|The endpoint of the Xero server. (i.e. api.xero.com)|xero_host|xero_host|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|xero_connect_via|xero_connect_via|
|**--description**|string|Linked service description.|xero_description|xero_description|
|**--parameters**|dictionary|Parameters for linked service.|xero_parameters|xero_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|xero_annotations|xero_annotations|
|**--type-properties-consumer-key**|object|The consumer key associated with the Xero application.|xero_consumer_key|xero_consumer_key|
|**--type-properties-private-key**|object|The private key from the .pem file that was generated for your Xero private application. You must include all the text from the .pem file, including the Unix line endings( ).|xero_private_key|xero_private_key|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|xero_use_encrypted_endpoints|xero_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|xero_use_host_verification|xero_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|xero_use_peer_verification|xero_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|xero_encrypted_credential|xero_encrypted_credential|
### datafactory linked-service zoho create

zoho create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|zoho_type|zoho_type|
|**--type-properties-endpoint**|any|The endpoint of the Zoho server. (i.e. crm.zoho.com/crm/private)|zoho_endpoint|zoho_endpoint|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|zoho_connect_via|zoho_connect_via|
|**--description**|string|Linked service description.|zoho_description|zoho_description|
|**--parameters**|dictionary|Parameters for linked service.|zoho_parameters|zoho_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|zoho_annotations|zoho_annotations|
|**--type-properties-access-token**|object|The access token for Zoho authentication.|zoho_access_token|zoho_access_token|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|zoho_use_encrypted_endpoints|zoho_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|zoho_use_host_verification|zoho_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|zoho_use_peer_verification|zoho_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|zoho_encrypted_credential|zoho_encrypted_credential|
### datafactory linked-service zoho update

zoho create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--type**|string|Type of linked service.|zoho_type|zoho_type|
|**--type-properties-endpoint**|any|The endpoint of the Zoho server. (i.e. crm.zoho.com/crm/private)|zoho_endpoint|zoho_endpoint|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--connect-via**|object|The integration runtime reference.|zoho_connect_via|zoho_connect_via|
|**--description**|string|Linked service description.|zoho_description|zoho_description|
|**--parameters**|dictionary|Parameters for linked service.|zoho_parameters|zoho_parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|zoho_annotations|zoho_annotations|
|**--type-properties-access-token**|object|The access token for Zoho authentication.|zoho_access_token|zoho_access_token|
|**--type-properties-use-encrypted-endpoints**|any|Specifies whether the data source endpoints are encrypted using HTTPS. The default value is true.|zoho_use_encrypted_endpoints|zoho_use_encrypted_endpoints|
|**--type-properties-use-host-verification**|any|Specifies whether to require the host name in the server's certificate to match the host name of the server when connecting over SSL. The default value is true.|zoho_use_host_verification|zoho_use_host_verification|
|**--type-properties-use-peer-verification**|any|Specifies whether to verify the identity of the server when connecting over SSL. The default value is true.|zoho_use_peer_verification|zoho_use_peer_verification|
|**--type-properties-encrypted-credential**|any|The encrypted credential used for authentication. Credentials are encrypted using the integration runtime credential manager. Type: string (or Expression with resultType string).|zoho_encrypted_credential|zoho_encrypted_credential|
### datafactory pipeline create

create a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|pipeline_name|
|**--pipeline**|object|Pipeline resource definition.|pipeline|pipeline|
|**--if-match**|string|ETag of the pipeline entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
### datafactory pipeline create-run

create-run a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|pipeline_name|
|**--reference-pipeline-run-id**|string|The pipeline run identifier. If run ID is specified the parameters of the specified run will be used to create a new run.|reference_pipeline_run_id|reference_pipeline_run_id|
|**--is-recovery**|boolean|Recovery mode flag. If recovery mode is set to true, the specified referenced pipeline run and the new run will be grouped under the same groupId.|is_recovery|is_recovery|
|**--start-activity-name**|string|In recovery mode, the rerun will start from this activity. If not specified, all activities will run.|start_activity_name|start_activity_name|
|**--start-from-failure**|boolean|In recovery mode, if set to true, the rerun will start from failed activities. The property will be used only if startActivityName is not specified.|start_from_failure|start_from_failure|
|**--parameters**|dictionary|Parameters of the pipeline run. These parameters will be used only if the runId is not specified.|parameters|parameters|
### datafactory pipeline delete

delete a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|pipeline_name|
### datafactory pipeline list

list a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
### datafactory pipeline show

show a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|pipeline_name|
|**--if-none-match**|string|ETag of the pipeline entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|if_none_match|
### datafactory pipeline update

create a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|pipeline_name|
|**--pipeline**|object|Pipeline resource definition.|pipeline|pipeline|
|**--if-match**|string|ETag of the pipeline entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
### datafactory pipeline-run cancel

cancel a datafactory pipeline-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--run-id**|string|The pipeline run identifier.|run_id|run_id|
|**--is-recursive**|boolean|If true, cancel all the Child pipelines that are triggered by the current pipeline.|is_recursive|is_recursive|
### datafactory pipeline-run query-by-factory

query-by-factory a datafactory pipeline-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--last-updated-after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|last_updated_after|last_updated_after|
|**--last-updated-before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|last_updated_before|last_updated_before|
|**--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|continuation_token|
|**--filters**|array|List of filters.|filters|filters|
|**--order-by**|array|List of OrderBy option.|order_by|order_by|
### datafactory pipeline-run show

show a datafactory pipeline-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--run-id**|string|The pipeline run identifier.|run_id|run_id|
### datafactory trigger create

create a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|trigger_name|
|**--properties**|object|Properties of the trigger.|properties|properties|
|**--if-match**|string|ETag of the trigger entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
### datafactory trigger delete

delete a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|trigger_name|
### datafactory trigger get-event-subscription-status

get-event-subscription-status a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|trigger_name|
### datafactory trigger list

list a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
### datafactory trigger query-by-factory

query-by-factory a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|continuation_token|
|**--parent-trigger-name**|string|The name of the parent TumblingWindowTrigger to get the child rerun triggers|parent_trigger_name|parent_trigger_name|
### datafactory trigger show

show a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|trigger_name|
|**--if-none-match**|string|ETag of the trigger entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|if_none_match|
### datafactory trigger start

start a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|trigger_name|
### datafactory trigger stop

stop a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|trigger_name|
### datafactory trigger subscribe-to-event

subscribe-to-event a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|trigger_name|
### datafactory trigger unsubscribe-from-event

unsubscribe-from-event a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|trigger_name|
### datafactory trigger update

create a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|trigger_name|
|**--properties**|object|Properties of the trigger.|properties|properties|
|**--if-match**|string|ETag of the trigger entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
### datafactory trigger-run query-by-factory

query-by-factory a datafactory trigger-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--last-updated-after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|last_updated_after|last_updated_after|
|**--last-updated-before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|last_updated_before|last_updated_before|
|**--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|continuation_token|
|**--filters**|array|List of filters.|filters|filters|
|**--order-by**|array|List of OrderBy option.|order_by|order_by|
### datafactory trigger-run rerun

rerun a datafactory trigger-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|trigger_name|
|**--run-id**|string|The pipeline run identifier.|run_id|run_id|