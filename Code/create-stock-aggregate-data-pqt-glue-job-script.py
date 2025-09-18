import sys
import boto3

client = boto3.client('athena')

SOURCE_TABLE_NAME = 'apple_stock_aggregate_data_1453891'
NEW_TABLE_NAME = 'apple_stock_aggregate_data_parquet_tbl'
NEW_TABLE_S3_BUCKET = 's3: //pqt-stock-aggregate-data-1453891/'
MY_DATABASE = 'stockaggregatedata'
QUERY_RESULTS_S3_BUCKET = 's3: //athena-query-results-first-de-project-aug-2024-1639045/'

# Refresh the table
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
    ROUND(tradvol,
2) AS TradVol,
    ROUND(volwtavg,
2) AS VolWtAvg,
    ROUND(openprice,
2) AS OpenPrice,
    ROUND(closeprice,
2) AS ClosePrice,
    ROUND(highestprice,
2) AS HighestPrice,
    ROUND(lowestprice,
2) AS LowestPrice,
    CONCAT(
        SUBSTRING(CAST(normal_timestamp AS VARCHAR),
9,
2), 
        SUBSTRING(CAST(normal_timestamp AS VARCHAR),
12,
2)
    ) AS day_hour_partition
FROM (
    SELECT
        from_unixtime(CAST(unixmsects / 1000 AS BIGINT)) AS normal_timestamp,
        tradvol,
        volwtavg,
        openprice,
        closeprice,
        highestprice,
        lowestprice
        FROM "{MY_DATABASE}"."{SOURCE_TABLE_NAME}"
    ) subquery
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