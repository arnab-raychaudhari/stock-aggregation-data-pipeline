# Stock Aggregate Data Engineering Pipeline
Fully automated data engineering pipeline that ingests hourly stock aggregate data from the past seven days into AWS services, with seamless integration into Grafana for downstream visualization.

## Objective

To reveal trends that influency buy/sell decisions of the AAPL ticker by providing detailed visual insights into trading volume, price trends and volatility. Furthermore, automating data engineering workloads saves time, reduces humar error and guides financial analysts to produce reports and presentations.

## Tech Stack

Programming Language: Python

Data ingestion: AWS Lambda, AWS EventBridge Trigger, AWS Kinesis FireHose, AWS Glue Crawler, AWS IAM

Data storage: AWS Athena and Query Editor, AWS S3

Data transofrmation and validation: AWS Glue Jobs, AWS Glue Workflows, AWS Cloudwatch Logs

Data visualization: Grafana

## Architecture Diagram

![Architecture Diagram](https://github.com/arnab-raychaudhari/stock-aggregation-data-pipeline/blob/8782140878d57c7cb14357b8ba031b1f13c813c5/StockAggregateArchitectureDiagram.jpg)
