# Stock Aggregate Data Engineering Pipeline
Fully automated data engineering pipeline that ingests hourly stock aggregate data from the past seven days into AWS services, with seamless integration into Grafana for downstream visualization.

## Objective

To reveal trends that influency buy/sell decisions of the AAPL ticker by providing detailed visual insights into trading volume, price trends and volatility. Furthermore, automating data engineering workloads saves time, reduces humar error and guides financial analysts to produce reports and presentations.

## Tech Stack

Programming Language: ![Python](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/9f69abd4d570c16be5bc47b330bca84032e24aa5/logos--python.svg) Python

Data ingestion: ![AWS Lambda](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/1574de2d30f644046913b565ca778f22f449e567/logos--aws-lambda.svg) AWS Lambda, ![AWS EventBridge](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/1574de2d30f644046913b565ca778f22f449e567/logos--aws-eventbridge.svg) AWS Event Bridge, ![AWS Kinesis](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/1574de2d30f644046913b565ca778f22f449e567/logos--aws-kinesis.svg) AWS Kinesis FireHose, ![AWS EventBridge Trigger](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/1574de2d30f644046913b565ca778f22f449e567/logos--aws-eventbridge.svg) AWS EventBridge Trigger, ![AWS Glue Crawler](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/1574de2d30f644046913b565ca778f22f449e567/logos--aws-glue.svg) AWS Glue Crawler, ![AWS IAM](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/1574de2d30f644046913b565ca778f22f449e567/logos--aws-iam.svg) AWS IAM

Data storage: ![AWS Athena](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/1574de2d30f644046913b565ca778f22f449e567/logos--aws-athena.svg) AWS Athena and Query Editor, ![AWS S3](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/1574de2d30f644046913b565ca778f22f449e567/logos--aws-s3.svg) AWS S3

Data transofrmation and validation: ![AWS Glue Jobs](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/1574de2d30f644046913b565ca778f22f449e567/logos--aws-glue.svg) AWS Glue Jobs, ![AWS Glue WorkFlows](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/1574de2d30f644046913b565ca778f22f449e567/logos--aws-glue.svg) AWS Glue Workflows, ![AWS Cloudwatch Logs](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/1574de2d30f644046913b565ca778f22f449e567/logos--aws-cloudwatch.svg) AWS Cloudwatch Logs

Data visualization: ![Grafana](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/9f69abd4d570c16be5bc47b330bca84032e24aa5/devicon--grafana.svg) Grafana, ![AWS IAM](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/1574de2d30f644046913b565ca778f22f449e567/logos--aws-iam.svg) AWS IAM

## Architecture Diagram

![Architecture Diagram](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/8782140878d57c7cb14357b8ba031b1f13c813c5/StockAggregateArchitectureDiagram.jpg)

## Implementation

1 - Login to your AWS account

2 - Create an S3 bucket to store the results of Athena queries

3 - Create another S3 bucket where Kinesis Firehose will write the data streams coming in from the external API

4 - Create a Kinesis Firehose and configure it to be ready to receive data. Ensure the buffer is set to 5 MB and 60 secs. A .json output of the firehose configuration is available at [firehose-config.json](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/cb5a6422542fd0c9e0879f430506367eb8f2a69f/firehose-config.json)

5 - Create a Lambda function (python + x86_64) to call the external API. Update the timeout to 10 secs and use the correct name of your firehose. Before invoking the API, the date range in API URL will be updated to set the StartDate = Yesterday's date - 7 days, and EndDate = Yesterday's date. This way we will fetch hourly data for the last 7 days. Refer to the script [Lambda Function](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/cb5a6422542fd0c9e0879f430506367eb8f2a69f/stock-aggregate-data-ingestion-lambda-function.py)

6 - Add an eventbridge trigger and schedule it run everyday at 11 EDT. Refer to .json format at [eventbridge_rule_details.json](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/cb5a6422542fd0c9e0879f430506367eb8f2a69f/eventbridge_rule_details.json)

7 - Navigate to AWS Glue service and create a Crawler that reads the files created by Kinesis Firehose in the S3 bucket we created in step 3. Refer to .json format at [crawler-configuration.json](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/cb5a6422542fd0c9e0879f430506367eb8f2a69f/crawler_configuration.json)

8 - Next, create a Glue job (that runs python script) that deletes the parquet tables from previous runs. Code available at [Delete Parquet Tables Before New Run](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/b793992353ca4eac2ef41f8c3d5d9b5d54860070/delete-pqt-stock-aggregate-data-glue-job-script.py)

9 - Create another Glue job to roundup the aggregate figures to two places after decimal, and parse through the timestamp field to extract the day and hour marks to create a new feature 'day_hour_partition', which will be used to partition the parquet table. Also, this job will cast the Unixmsects into integer value for effective downstream processing. At last, the transformed dataset will be written to parquest table in AWS Athena. Code available at [Create Parquest Table](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/b793992353ca4eac2ef41f8c3d5d9b5d54860070/create-stock-aggregate-data-pqt-glue-job-script.py)

10 - Create another Glue job to identify the duplicate records in the parquet table created in step 9, and copy the unique ones to a new table. Code available at [Unique Observations](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/b793992353ca4eac2ef41f8c3d5d9b5d54860070/create-sans-dup-pqt-if-required-glue-job-script.py)

11 - Perform the following data quality checks on the table created in step 10 before using the data for insightful visualization. Code available at [Data Quality Checks](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/b793992353ca4eac2ef41f8c3d5d9b5d54860070/data-quality-stock-aggregate-glue-job-script.py)

11.a - Check for zero values in any of the financial info features

11.b - Ensure the number of rows written by Crawler in the Athena table (at step 7) and 
those in the parquet table (step 9) are the same

11.c - Perform duplicate record checks on the table created in step 10 to ensure the absence of any errors

11.d - Perform null value check on all features

12 - If the quality checks in step 11 have passed, archive a copy of the table (which is now ready for production use) for future reference. Suffix the tablename with data and timestamps to reflect when it was used for production consumption. Code available at [Publish Production Table](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/b793992353ca4eac2ef41f8c3d5d9b5d54860070/publish_prod_parquet_stock_aggregate-glue-job-script.py)

13 - Create a Glue Workflow and build the sequence of jobs between step 8 and 12 (both inclusive) while ensuring the same top down order. Schedule the workflow start trigger to run at 1200 EDT everyday. Refer to the .json file at [Glue Workflow](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/5a50abfac6b5baa007d88643db5ac3ca9487e552/glue-workflow-config.json)

14 - Login to your Grafana account, setup a new connection with AWS Athena (you need to create a new user in AWS IAM, add full permissions Athena and S3, and generate Access Keys), and build a new dashboard. Interetsted in the configuration? Refer to the .json file [Grafana SetUp](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/5a50abfac6b5baa007d88643db5ac3ca9487e552/Stock-Aggregate-Apple-xxxxxxxxxxxxx.json)

15 - In Grafana, build a SQL query that retrieves the data from the table you created in step 10. Use the query in [Grafana Query.sql](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/9f69abd4d570c16be5bc47b330bca84032e24aa5/Grafana-Query.sql)

16 - Run the query to see the plots in your dashboard. Refer to the results in the following section.

## Results

![Visualization](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/d00fb780b8e7bd3c0f63e6deab49038985481f5a/GIF-grafana-dashboard.gif)

## Future Consideration

