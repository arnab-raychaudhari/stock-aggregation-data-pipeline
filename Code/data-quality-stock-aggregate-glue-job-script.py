import sys
import awswrangler as wr
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Define multiple data quality checks

# Check 1: Count the number of rows where temp_C is outside the acceptable range (-50 to 50)
ZERO_VAL_DQ_CHECK = f"""
SELECT 
    SUM(CASE WHEN tradvol = 0
    OR volwtavg = 0
    OR openprice = 0
    OR closeprice = 0
    OR highestprice = 0
    OR lowestprice = 0
    OR day_hour_partition = '0'
    OR CAST(normal_timestamp AS VARCHAR) = '0' THEN 1 ELSE 0 END) AS res_col
FROM "stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl"
;
"""

# Check 2: Number of observations in parquet and non-parquet tables should match
NOBS_CHECK = f"""
SELECT 
    CASE 
        WHEN (SELECT COUNT(*) FROM "stockaggregatedata"."apple_stock_aggregate_data_1453891") - (SELECT COUNT(*) FROM "stockaggregatedata"."apple_stock_aggregate_data_parquet_tbl") <> 0 
        THEN 1 
        ELSE 0 
    END AS res_col
;
"""

# Check 3: Are there any duplicates when you use timestamp and day as the composite key
DUP_CHECK_TS_DAY = f"""
SELECT 
    SUM(
        CASE 
            WHEN EXISTS (
                SELECT normal_timestamp, day_hour_partition
                FROM "stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl"
                GROUP BY normal_timestamp, day_hour_partition
                HAVING COUNT(*) > 1
            ) THEN 1
            ELSE 0
        END
    ) AS res_col
FROM "stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl";
"""

# Check 4: Are there any duplicates when you look at all columns all at once
DUP_CHECK = f"""
SELECT 
    SUM(
        CASE 
            WHEN EXISTS (
                select day_hour_partition, normal_timestamp, tradvol, volwtavg, openprice, 
closeprice, highestprice, lowestprice, count(*) from 
"stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl"
group by 1,2,3,4,5,6,7,8 having count(*) > 1
            ) THEN 1
            ELSE 0
        END
    ) AS res_col
FROM "stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl";
"""

# Check 5: What % of the Days are null? We cannot allow non-zero percentages to pass!

PCT_NULL_CHECK_NT = f"""
select sum(case when normal_timestamp is null then 1 else 0 end) * 1.0 / (
select count(*) from "stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl") * 100
as res_col from "stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl"
"""
PCT_NULL_CHECK_TV = f"""
select sum(case when tradvol is null then 1 else 0 end) * 1.0 / (
select count(*) from "stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl") * 100
as res_col from "stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl"
"""
PCT_NULL_CHECK_VWT = f"""
select sum(case when volwtavg is null then 1 else 0 end) * 1.0 / (
select count(*) from "stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl") * 100
as res_col from "stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl"
"""
PCT_NULL_CHECK_OP = f"""
select sum(case when openprice is null then 1 else 0 end) * 1.0 / (
select count(*) from "stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl") * 100
as res_col from "stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl"
"""
PCT_NULL_CHECK_CP = f"""
select sum(case when closeprice is null then 1 else 0 end) * 1.0 / (
select count(*) from "stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl") * 100
as res_col from "stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl"
"""
PCT_NULL_CHECK_HP = f"""
select sum(case when highestprice is null then 1 else 0 end) * 1.0 / (
select count(*) from "stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl") * 100
as res_col from "stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl"
"""

PCT_NULL_CHECK_LP = f"""
select sum(case when lowestprice is null then 1 else 0 end) * 1.0 / (
select count(*) from "stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl") * 100
as res_col from "stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl"
"""

PCT_NULL_CHECK_DHP = f"""
select sum(case when day_hour_partition is null then 1 else 0 end) * 1.0 / (
select count(*) from "stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl") * 100
as res_col from "stockaggregatedata"."apple_stock_aggregate_data_sans_dup_parquet_tbl"
"""
# Define a function to run a check and validate results
def run_dq_check(query, check_name):
    try:
        df = wr.athena.read_sql_query(sql=query, database="stockaggregatedata")
        if df['res_col'][0] != 0:
            logger.error(f'{check_name} failed. Quality check returned results.')
            sys.exit(1)  # Exit with an error status
        else:
            logger.info(f'{check_name} passed.')
    except Exception as e:
        logger.error(f'An error occurred while running {check_name}: {str(e)}')
        sys.exit(1)

# Run the data quality checks in sequence
run_dq_check(ZERO_VAL_DQ_CHECK, "ZERO_VAL_DQ_CHECK")
run_dq_check(NOBS_CHECK, "NOBS_CHECK")
run_dq_check(DUP_CHECK_TS_DAY, "DUP_CHECK_TS_DAY")
run_dq_check(DUP_CHECK, "DUP_CHECK")
run_dq_check(PCT_NULL_CHECK_NT, "PCT_NULL_CHECK_NT")
run_dq_check(PCT_NULL_CHECK_TV, "PCT_NULL_CHECK_TV")
run_dq_check(PCT_NULL_CHECK_VWT, "PCT_NULL_CHECK_VWT")
run_dq_check(PCT_NULL_CHECK_OP, "PCT_NULL_CHECK_OP")
run_dq_check(PCT_NULL_CHECK_CP, "PCT_NULL_CHECK_CP")
run_dq_check(PCT_NULL_CHECK_HP, "PCT_NULL_CHECK_HP")
run_dq_check(PCT_NULL_CHECK_LP, "PCT_NULL_CHECK_LP")
run_dq_check(PCT_NULL_CHECK_DHP, "PCT_NULL_CHECK_DHP")

logger.info('All quality checks passed successfully.')