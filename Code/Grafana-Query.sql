SELECT 
    normal_timestamp, 
    tradvol AS trad_vol, 
    volwtavg AS vol_wt_avg, 
    openprice AS open_price,
    closeprice AS close_price, 
    highestprice AS highest_price, 
    lowestprice AS lowest_price
FROM 
    apple_stock_aggregate_data_sans_dup_parquet_tbl 
WHERE 
    CAST(normal_timestamp AS DATE) BETWEEN $__timeFrom() AND $__timeTo()
ORDER BY 
    normal_timestamp;