import json
import boto3
import urllib3
import datetime

# REPLACE WITH YOUR DATA FIREHOSE NAME
FIREHOSE_NAME = 'PUT-S3-WJCwt'

def lambda_handler(event, context):
    
    # Calculate yesterday's date
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    
    # Construct the API URL with yesterday's date
    start_date = yesterday - datetime.timedelta(days=7)  # Calculate the start date (yesterday minus 7 days)
    start_date_str = start_date.strftime('%Y-%m-%d')
    api_url = f"https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/hour/{start_date_str}/{yesterday_str}?adjusted=true&sort=asc&limit=50000&apiKey=9l3q0E5_lp3_fsutNIqpZ7XuGHFBsCtV"
    http = urllib3.PoolManager()
    r = http.request("GET", api_url)
    
    # turn it into a dictionary
    r_dict = json.loads(r.data.decode(encoding='utf-8', errors='strict'))
    
    # Check if the 'results' field contains data
    if 'results' in r_dict and len(r_dict['results']) > 0:
        # Initialize boto3 Firehose client
        fh = boto3.client('firehose')
        
        # Loop through all elements in the 'results' list
        for result in r_dict['results']:
            # extract pieces of the dictionary
            processed_dict = {}
            processed_dict['tradvol'] = result.get('v')
            processed_dict['volwtavg'] = result.get('vw')
            processed_dict['openprice'] = result.get('o')
            processed_dict['closeprice'] = result.get('c')
            processed_dict['highestprice'] = result.get('h')
            processed_dict['lowestprice'] = result.get('l')
            processed_dict['unixmsects'] = result.get('t')
            processed_dict['row_ts'] = str(datetime.datetime.now())
            
            # turn it into a string and add a newline
            msg = str(processed_dict) + '\n'
            
            # Send the processed data to the Firehose stream
            reply = fh.put_record(
                DeliveryStreamName=FIREHOSE_NAME,
                Record = {
                        'Data': msg
                        }
            )
    
    return reply