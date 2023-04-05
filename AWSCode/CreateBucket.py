import logging
import boto3
from botocore.exceptions import ClientError
def create_bucket(bucket_name, region="ap-southeast-2"):
    
# Create bucket
    try:
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return False
    return True

if create_bucket("trapforment"):
    print(f"Bucket trapforment created successfully.")
else:
    print(f"Bucket trapforment creation failed.")
