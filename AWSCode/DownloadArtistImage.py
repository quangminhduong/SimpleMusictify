
import requests
from io import BytesIO
import boto3
import json

s3 = boto3.client('s3')
bucket_name = "trapforment"  # Replace with your S3 bucket name

# Load the JSON data from a1.json
with open('a1.json', 'r') as f:
    data = json.load(f)
    images = [song['img_url'] for song in data['songs']]

for image_url in images:
    response = requests.get(image_url)
    file_object = BytesIO(response.content)
    filename = image_url.split('/')[-1]

    # Upload the image to S3 and make it public
    s3.put_object(
        Bucket=bucket_name,
        Key=filename,
        Body=file_object,
        ContentType='image/jpeg',
        ACL='public-read'  # This makes the uploaded image public
    )