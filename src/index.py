import requests
import pandas as pd
import awswrangler as wr

def find_receipts(name):
    url = "https://data.texas.gov/resource/naix-2893.json"
    response = requests.get(url, params = {'taxpayer_name': name})
    receipts = response.json()
    df = pd.DataFrame(receipts)
    return df

def coerce_df(df):
    numeric_cols = ['taxpayer_number', 'taxpayer_zip', 'taxpayer_county', 
    'location_zip', 'location_county', 'location_number', 'liquor_receipts',
      'beer_receipts', 'wine_receipts', 'cover_charge_receipts', 'total_receipts']
    dt_cols = ['responsibility_begin_date_yyyymmdd', 'responsibility_end_date_yyyymmdd', 'obligation_end_date_yyyymmdd']
    combined_cols = numeric_cols + dt_cols
    numeric_df = df[numeric_cols]
    dt_df = df[dt_cols]
    numeric_df_coerced = numeric_df.apply(pd.to_numeric, errors='coerce')
    dt_coerced = dt_df.apply(pd.to_datetime, errors = 'coerce')
    remaining_df = df.drop(columns = combined_cols)
    fully_coerced_df = pd.concat([numeric_df_coerced, dt_coerced, remaining_df], axis = 1)
    return fully_coerced_df

def find_and_coerce(name):
    df = find_receipts(name)
    return coerce_df(df)

maya_df = find_and_coerce("HONDURAS MAYA CAFE & BAR LLC")

mermaid_df = find_and_coerce("MERMAID KARAOKE PRIVATE CLUB, INC.")

path = "s3://jigsaw-labs-student/tx-receipts/"

# wr.s3.to_parquet(df=maya_df, 
#                 path="s3://jigsaw-labs-student/tx-receipts/",
#                 dataset=True)

# s3_df = wr.s3.read_parquet("s3://jigsaw-labs-student/tx-receipts/", dataset=True)


# we can change the mode 

# wr.s3.to_parquet(df=mermaid_df, path="s3://jigsaw-labs-student/tx-receipts/",
#                 mode = 'overwrite',
#                 dataset=True)


# Or we can also delete objects

# wr.s3.delete_objects(path)


# this time we see that the dataset consists of mermaid
# s3_df = wr.s3.read_parquet("s3://jigsaw-labs-student/tx-receipts/", dataset=True)

# s3_df.shape returns certain dataset size

# so instead let's change to append
# wr.s3.to_parquet(df=maya_df, path="s3://jigsaw-labs-student/tx-receipts/",
#                 mode = 'append',
#                 dataset=True)

# returns larger dataset size

# s3_df.taxpayer_name.unique() # returns list of two

# Then we can move onto partitioning the dataset
# wr.s3.to_parquet(df=maya_df, path="s3://jigsaw-labs-student/tx-receipts/", mode='overwrite', dataset = True, partition_cols = ["taxpayer_name"])

# And from there, 

wr.s3.to_parquet(df=mermaid_df, path=path,
                partition_cols = ["taxpayer_name"],
                mode = 'overwrite',
                dataset=True)


# Let's try crawling
# currently we have no databases
# databases = wr.catalog.databases()

# create db
wr.catalog.create_database("tx_revenue")

# From there can create the crawler

# res = wr.s3.store_parquet_metadata(
#     path=path,
#     database="tx_revenue",
#     table="receipts",
#     dataset=True,
#     mode="overwrite"
# )

# 
wr.catalog.table(database="tx_revenue", table="receipts")

# resulting_df = wr.athena.read_sql_query("SELECT * FROM receipts where total_receipts > 100 limit 10", database="tx_revenue")
