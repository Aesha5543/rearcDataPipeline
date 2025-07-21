import os
import boto3
import json
import requests
import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urljoin

s3 = boto3.client("s3")

BUCKET = os.environ.get("BUCKET_NAME")
BLS_URL = "https://download.bls.gov/pub/time.series/pr/"
POP_URL = "https://honolulu-api.datausa.io/tesseract/data.jsonrecords?cube=acs_yg_total_population_1&drilldowns=Year%2CNation&locale=en&measures=Population"
BLS_PREFIX = "bls-data/"
POP_S3_KEY = "datausa/acs_population.json"
HEADERS = {
    "User-Agent": "Pipeline/1.0 (contact: stackjerry@google.com)"
}
def sync_bls():
    try:
        def list_s3_objects(bucket, prefix=""):
            paginator = s3.get_paginator("list_objects_v2")
            keys = {}
            for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                for obj in page.get("Contents", []):
                    keys[obj["Key"]] = obj["ETag"].strip('"')
            return keys

        def get_md5(content):
            return hashlib.md5(content).hexdigest()

        def fetch_remote_files():
            resp = requests.get(BLS_URL, headers=HEADERS)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            files = {}
            for link in soup.find_all("a", href=True):
                href = link['href']
                if not href.endswith("/") and not href.startswith("?"):
                    full_url = urljoin(BLS_URL, href)
                    fname = href.split("/")[-1].strip()
                    files[fname] = full_url
            return files

        def upload_file_to_s3(filename, url):
            print(f"Uploading: {filename}")
            r = requests.get(url, headers=HEADERS)
            r.raise_for_status()
            s3.put_object(Bucket=BUCKET, Key=BLS_PREFIX + filename, Body=r.content)

        print("Checking current S3 bucket state...")
        s3_files = list_s3_objects(BUCKET, BLS_PREFIX)

        print("Fetching file list from BLS...")
        remote_files = fetch_remote_files()

        if not s3_files:
            print("S3 is empty — uploading all files.")
            for fname, url in remote_files.items():
                upload_file_to_s3(fname, url)
        else:
            for fname, url in remote_files.items():
                s3_key = BLS_PREFIX + fname
                r = requests.get(url, headers=HEADERS)
                r.raise_for_status()
                md5 = get_md5(r.content)

                if s3_key not in s3_files:
                    print(f"Uploading new file: {fname}")
                    s3.put_object(Bucket=BUCKET, Key=s3_key, Body=r.content)
                elif s3_files[s3_key] != md5:
                    print(f"Updating modified file: {fname}")
                    s3.put_object(Bucket=BUCKET, Key=s3_key, Body=r.content)
                else:
                    print(f"✅ Up-to-date: {fname}")

            remote_keys = set(BLS_PREFIX + fname for fname in remote_files)
            for key in s3_files:
                if key not in remote_keys:
                    print(f"Deleting removed file from S3: {key}")
                    s3.delete_object(Bucket=BUCKET, Key=key)
        return True

    except Exception as e:
        print(f"sync_bls error: {e}")
        return False

def load_population_to_s3():
    try:
        response = requests.get(POP_URL)
        response.raise_for_status()
        data = response.json()
        json_data = json.dumps(data)
        s3.put_object(Bucket=BUCKET, Key=POP_S3_KEY, Body=json_data, ContentType='application/json')
        print(f"Uploaded data to s3://{BUCKET}/{POP_S3_KEY}")
        return True
    except Exception as e:
        print(f"load_population_to_s3 error: {e}")
        return False

def main(event, context):
    bls_result = sync_bls()
    pop_result = load_population_to_s3()
    status_code = 200 if bls_result and pop_result else 500

    return {
        "statusCode": status_code,
        "body": json.dumps({
            "bls_sync": bls_result,
            "population_upload_success": pop_result
        }),
    }
