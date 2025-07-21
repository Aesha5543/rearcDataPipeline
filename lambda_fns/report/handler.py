import json
import pandas as pd
import boto3
from io import StringIO
import os
import re

s3 = boto3.client("s3")
BUCKET = os.environ["BUCKET_NAME"]

PR_KEY = "bls-data/pr.data.0.Current"
POP_KEY = "datausa/acs_population.json"

def main(event, context):
    pr_dtypes = {
        'series_id': str,
        'year': int,
        'period': str,
        'value': float,
        'footnote_codes': str
    }

    # ---------- Load Time-Series Data ----------
    response = s3.get_object(Bucket=BUCKET, Key=PR_KEY)
    body = response['Body'].read().decode('utf-8')
    pr_df = pd.read_csv(StringIO(body), sep='\t', dtype=pr_dtypes)

    pr_df.columns = pr_df.columns.str.strip()
    pr_df = pr_df.map(lambda x: x.strip() if isinstance(x, str) else x)

    # ---------- Load Population JSON ----------
    response = s3.get_object(Bucket=BUCKET, Key=POP_KEY)
    population_json = json.loads(response['Body'].read())
    pop_df = pd.DataFrame(population_json['data'])

    pop_df = pop_df.astype({
        'Nation ID': str,
        'Nation': str,
        'Year': int,
        'Population': float
    })

    pop_df.columns = pop_df.columns.str.strip()
    pop_df.columns = pop_df.columns.map(
        lambda col: re.sub(r'\W+', '_', col.strip()).replace(' ', '_').lower()
    )
    pop_df = pop_df.map(lambda x: x.strip() if isinstance(x, str) else x)

    # ---------- Section 1: Population Stats (2013–2018) ----------
    filtered_pop_df = pop_df[(pop_df["year"] > 2012) & (pop_df["year"] < 2019)]
    mean_population = filtered_pop_df["population"].mean()
    std_population = filtered_pop_df["population"].std()

    print("\n--- Population Stats (2013–2018) ---")
    print("Mean:", mean_population)
    print("Standard Deviation:", std_population)

    # ---------- Section 2: Best Year per Series ----------
    grouped_pr_df = pr_df.groupby(['series_id', 'year'])['value'].sum().reset_index()
    best_years = grouped_pr_df.loc[grouped_pr_df.groupby('series_id')['value'].idxmax()].reset_index(drop=True)

    print("\n--- Best Year for Each Series ---")
    print(best_years)

    # ---------- Section 3: Report for PRS30006032 Q01 ----------
    filtered_pr_df = pr_df[
        (pr_df['series_id'] == 'PRS30006032') & 
        (pr_df['period'] == 'Q01')
    ]
    merged_df = pd.merge(filtered_pr_df, pop_df, on='year', how='left')
    final_report = merged_df[['series_id', 'year', 'period', 'value', 'population']]

    print("\n--- Final Report for PRS30006032 Q01 ---")
    print(final_report)

    # ---------- Return JSON Response ----------
    response = {
        "statusCode": 200,
        "body": json.dumps({
            "status": "success",
            "details": "Data processing completed and results are available.",
            "population_summary": {
                "average": round(mean_population),
                "standard_deviation": round(std_population)
            },
            "top_yearly_values": best_years.to_dict(orient="records"),
            "series_population_data": final_report.to_dict(orient="records")
        })
    }
    return response