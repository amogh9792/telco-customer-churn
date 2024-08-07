import os
import boto3
from io import BytesIO
import pandas as pd
from botocore.exceptions import ClientError
from datetime import datetime
from source.exception import ChurnException

global_timestamp = None

def generate_global_timestamp():
    global global_timestamp
    if global_timestamp is None:
        global_timestamp = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    return global_timestamp

def export_data_csv(data, filename, file_path):
    try:
        if not os.path.exists(file_path):
            os.makedirs(file_path, exist_ok=True)
        data.to_csv(os.path.join(file_path, filename), index=False)
    except Exception as e:
        raise ChurnException(f"Error exporting data to CSV: {e}")

def import_csv_file(filename, file_path):
    try:
        full_path = os.path.join(file_path, filename)
        if os.path.exists(full_path):
            return pd.read_csv(full_path)
        else:
            print(f"Path does not exist: {file_path}")
    except Exception as e:
        raise ChurnException(f"Error importing CSV file: {e}")

def upload_artifact_to_s3(df, filename, file_path, bucket_name):
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )

        try:
            s3_client.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                raise ChurnException(f"S3 bucket {bucket_name} does not exist.")
            else:
                raise e

        csv_data = df.to_csv(index=False)

        s3_object_key = os.path.join(file_path, filename).replace('\\', '/')
        s3_client.put_object(Bucket=bucket_name, Key=s3_object_key, Body=csv_data)

        print(f"CSV file uploaded to S3: s3://{bucket_name}/{s3_object_key}")

    except ClientError as e:
        raise e

    except ChurnException as e:
        raise e

def read_csv_from_s3(bucket_name, file_key):
    try:

        s3_client = boto3.client('s3')
        file_key = file_key.replace('\\', '/')
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        content = response['Body'].read()
        df = pd.read_csv(BytesIO(content))

        return df
    except ClientError as e:
        raise e
    except ChurnException as e:
        raise e
