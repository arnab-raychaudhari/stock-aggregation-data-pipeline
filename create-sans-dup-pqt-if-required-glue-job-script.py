import sys
import boto3

client = boto3.client('athena')
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

SOURCE_TABLE_NAME = 'apple_stock_aggregate_data_parquet_tbl'
NEW_TABLE_NAME = 'apple_stock_aggregate_data_sans_dup_parquet_tbl'
NEW_TABLE_S3_BUCKET = 's3: //prod-sans-dup-pqt-stock-aggregate-data-1453891/'
MY_DATABASE = 'stockaggregatedata'
QUERY_RESULTS_S3_BUCKET = 's3: //athena-query-results-first-de-project-aug-2024-1639045/'

# Extract the bucket name and prefix from the S3 path
bucket_name = 'prod-sans-dup-pqt-stock-aggregate-data-1453891'
prefix = ''  # No prefix in the path after the bucket name

# Delete any existing files in the S3 bucket
def delete_existing_s3_folder(bucket_name, prefix):
    bucket = s3_resource.Bucket(bucket_name)
    bucket.objects.filter(Prefix=prefix).delete()

delete_existing_s3_folder(bucket_name, prefix)

# Check for duplicates
queryStart = client.start_query_execution(
    QueryString = f"""
    CREATE TABLE {NEW_TABLE_NAME
} WITH
    (external_location='{NEW_TABLE_S3_BUCKET
}',
    format='PARQUET',
    write_compression='SNAPPY',
    partitioned_by = ARRAY['day_hour_partition'
])
    AS

    SELECT
    normal_timestamp,
    TradVol,
    VolWtAvg,
    OpenPrice,
    ClosePrice,
    HighestPrice,
    LowestPrice,
    day_hour_partition
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY normal_timestamp, day_hour_partition, TradVol, VolWtAvg, OpenPrice, ClosePrice, HighestPrice, LowestPrice
            ORDER BY normal_timestamp DESC
        ) AS rn
        FROM "{MY_DATABASE}"."{SOURCE_TABLE_NAME}"
    ) AS ranked
    WHERE rn = 1
    ;
    """,

    QueryExecutionContext = {
        'Database': f'{MY_DATABASE
	}'
}, 
    ResultConfiguration = { 'OutputLocation': f'{QUERY_RESULTS_S3_BUCKET
	}'
}
)

# list of responses
resp = [
	"FAILED",
	"SUCCEEDED",
	"CANCELLED"
]

# get the response
response = client.get_query_execution(QueryExecutionId=queryStart[
	"QueryExecutionId"
])

# wait until query finishes
while response[
	"QueryExecution"
][
	"Status"
][
	"State"
] not in resp:
    response = client.get_query_execution(QueryExecutionId=queryStart[
	"QueryExecutionId"
])
    
# if it fails, exit and give the Athena error message in the logs
if response[
	"QueryExecution"
][
	"Status"
][
	"State"
] == 'FAILED':
    sys.exit(response[
	"QueryExecution"
][
	"Status"
][
	"StateChangeReason"
])