import sys
import json
import boto3

# replace these with the names from your environment
BUCKET_TO_DEL = 'pqt-stock-aggregate-data-1453891'
DATABASE_TO_DEL = 'stockaggregatedata'
TABLE_TO_DEL = 'apple_stock_aggregate_data_parquet_tbl'
SANS_DUP_TABLE_TO_DEL = 'apple_stock_aggregate_data_sans_dup_parquet_tbl'
QUERY_OUTPUT_BUCKET = 's3: //athena-query-results-first-de-project-aug-2024-1639045/'


# delete all objects in the bucket
s3_client = boto3.client('s3')

while True:
    objects = s3_client.list_objects(Bucket=BUCKET_TO_DEL)
    content = objects.get('Contents',
[])
    if len(content) == 0:
        break
    for obj in content:
        s3_client.delete_object(Bucket=BUCKET_TO_DEL, Key=obj['Key'
])


# drop the table too
client = boto3.client('athena')

queryStart1 = client.start_query_execution(
    QueryString = f"""
    DROP TABLE IF EXISTS {DATABASE_TO_DEL
}.{TABLE_TO_DEL
};
    """,
    QueryExecutionContext = {
        'Database': f'{DATABASE_TO_DEL
	}'
}, 
    ResultConfiguration = { 'OutputLocation': f'{QUERY_OUTPUT_BUCKET
	}'
}
)

queryStart2 = client.start_query_execution(
    QueryString = f"""
    DROP TABLE IF EXISTS {DATABASE_TO_DEL
}.{SANS_DUP_TABLE_TO_DEL
};
    """,
    QueryExecutionContext = {
        'Database': f'{DATABASE_TO_DEL
	}'
}, 
    ResultConfiguration = { 'OutputLocation': f'{QUERY_OUTPUT_BUCKET
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
response1 = client.get_query_execution(QueryExecutionId=queryStart1[
	"QueryExecutionId"
])
response2 = client.get_query_execution(QueryExecutionId=queryStart2[
	"QueryExecutionId"
])

# wait until query finishes
while response1[
	"QueryExecution"
][
	"Status"
][
	"State"
] not in resp:
    response1 = client.get_query_execution(QueryExecutionId=queryStart1[
	"QueryExecutionId"
])
while response2[
	"QueryExecution"
][
	"Status"
][
	"State"
] not in resp:
    response2 = client.get_query_execution(QueryExecutionId=queryStart2[
	"QueryExecutionId"
])
    
# if it fails, exit and give the Athena error message in the logs
if response1[
	"QueryExecution"
][
	"Status"
][
	"State"
] == 'FAILED':
    sys.exit(response1[
	"QueryExecution"
][
	"Status"
][
	"StateChangeReason"
])
if response2[
	"QueryExecution"
][
	"Status"
][
	"State"
] == 'FAILED':
    sys.exit(response2[
	"QueryExecution"
][
	"Status"
][
	"StateChangeReason"
])
