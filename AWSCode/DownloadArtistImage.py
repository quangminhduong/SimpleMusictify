import boto3
import json
import requests
from io import BytesIO

# Initialize S3 client
s3 = boto3.client('s3')
bucket_name = 'trapforment4'

# Load JSON file and retrieve the image URLs
with open('a1.json') as f:
    data = json.load(f)
    images = [song['img_url'] for song in data['songs']]

# Download and upload images to S3
for image_url in images:
    response = requests.get(image_url)
    file_object = BytesIO(response.content)
    filename = image_url.split('/')[-1]
    s3.upload_fileobj(file_object, bucket_name, filename)
    print(f"Uploaded {filename} to S3 bucket {bucket_name}.")
