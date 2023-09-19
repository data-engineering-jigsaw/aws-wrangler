import awswrangler as wr
import requests
import pandas as pd

# 1. Read from s3 object
url_path = "s3://data-eng-careers/"
s3_df = wr.s3.read_csv(url_path, dataset=True)


def find_receipts(name):
    url = "https://data.texas.gov/resource/naix-2893.json"
    response = requests.get(url, params = {'taxpayer_name': name})
    receipts = response.json()
    df = pd.DataFrame(receipts)
    return df

honduras = "HONDURAS MAYA CAFE & BAR LLC"

honduras_df = find_receipts(honduras)

# 2. Write to s3 object

wr.s3.to_parquet(df=honduras_df, 
                path="s3://jigsaw-labs-student/tx-receipts/",
                dataset=True)
