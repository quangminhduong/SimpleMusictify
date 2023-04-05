import boto3
import json
import time
import requests
from io import BytesIO

def create_s3_bucket():
    s3 = boto3.client('s3')
    bucket_name = "trapforment"
    region = "ap-southeast-2" 

    try:
        if region == "us-east-1":
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"Bucket '{bucket_name}' already exists.")
    except Exception as e:
        print(f"Error creating bucket: {e}")

def create_login_entries():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('login')

    student_id = "s3759757"

    for i in range(10):
        email = f"{student_id}{i}@student.rmit.edu.au"
        user_name = f"QuangMinhDuong{i}"
        
        password = ''.join(str((i + j) % 10) for j in range(6))

        table.put_item(Item={'email': email, 'user_name': user_name, 'password': password})


def create_music_table():
    dynamodb = boto3.resource('dynamodb')
    table_name = 'music'

    # Create the music table
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'title', 'KeyType': 'HASH'},
            {'AttributeName': 'artist', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'title', 'AttributeType': 'S'},
            {'AttributeName': 'artist', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

def wait_for_table_to_become_active(table_name):
    dynamodb = boto3.client('dynamodb')
    while True:
        response = dynamodb.describe_table(TableName=table_name)
        status = response['Table']['TableStatus']
        if status == 'ACTIVE':
            break
        print(f"Waiting for table '{table_name}' to become active...")
        time.sleep(5)


def load_music_data():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('music')

    # Load the JSON data from a1.json
    with open('a1.json', 'r') as f:
        data = json.load(f)

    # Insert the data into the DynamoDB music table
    for entry in data['songs']:
        # Rename 'year' to 'release_year' because 'year' is AWS reserved keyword :(
        entry['release_year'] = entry.pop('year')
        table.put_item(Item=entry)


def download_images_and_upload_to_s3():
    s3 = boto3.client('s3')
    bucket_name = "trapforment"  

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

def lambda_handler(event, context):
    create_s3_bucket()
    create_login_entries()
    create_music_table()
    wait_for_table_to_become_active('music')
    load_music_data()
    download_images_and_upload_to_s3()

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps('DynamoDB and S3 setup completed.')
    }
