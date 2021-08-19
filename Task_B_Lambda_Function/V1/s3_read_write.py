import boto3
import botocore
import json
import cv2
import numpy as np
import os
import dateutil.parser as dp


def extract_keys(event: str) -> list:
    """
    Converts json string event containing SQS message and S3 events
    and extracts information from each S3 event.
    :param event: JSON event
    :returns: List of lists containing information from each S3 event
    """
    content = []

    ll = [json.loads(el["body"])["Records"] for el in event["Records"]]

    for el in ll:
        for single_el in el:
            item_content = []

            bucket = single_el["s3"]["bucket"]["name"]
            key = single_el["s3"]["object"]["key"]
            timestamp = single_el["eventTime"]
            item_content.extend([bucket, key, timestamp])
            content.append(item_content)

    return content


# Function to read image from s3
def s3_image_read(bucket_name: str, key: str) -> np.ndarray:
    """
    Read a single image from AWS S3 bucket into a numpy array using OpenCV
    :param bucket_name: Bucket name
    :param key: Key to S3 bucket directory
    :return: Image array
    """
    # Create s3 resource and s3 bucket object using boto3
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(bucket_name)

    ext = (".jpg", ".jpeg", ".png", ".tiff")

    # Try and load an image using boto3 and OpenCV,
    # Print exception if extension is not OpenCV compatible or there is a boto3 error
    try:
        # if key.lower().endswith(tuple(ext)):
        content = bucket.Object(key).get().get('Body').read()
        print(content)
        img = cv2.imdecode(np.asarray(bytearray(content)), cv2.IMREAD_COLOR)
        return img
    except botocore.exceptions.ClientError as e:
        print(e.response)


# Function to write images to s3
def s3_image_write(bucket_name: str, processed_img: np.ndarray, filename: str) -> 'Str':
    """
    Write a single image to a local file then push to an S3 bucket in .jpg format
    :param bucket_name: Bucket name
    :param key: Key to S3 bucket directory
    :param processed_img: Standardised image array
    :param unique_id: Unique randomly generated uuid
    :param timestamp: Unix timestamp
    :return: None
    """
    # Create s3 resource and s3 bucket object using boto3
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(bucket_name)

    # Write image to local directory
    local_path = os.path.join('/tmp', filename)
    cv2.imwrite(local_path, processed_img)

    # Try to upload local file to S3 bucket, return error message if upload fails
    try:
        bucket.upload_file(local_path, filename)
        return "Image upload success"
    except botocore.exceptions.ClientError as e:
        return e.response


def db_write(in_key: str, filename: str, timestamp: str, table_name: str, region: str = 'eu-west-1') -> str:
    """
    Write an image to AWS DynamoDB
    :param table_name: DynamoDB Table name
    :param processed_img: Standardised image array
    :param region: AWS region name where database is located
    :return: None
    """
    # Extract name of uploader and increment information from file name
    uploader_name, _ = in_key.split('_')[:2]

    # Convert timestamp to unix timestamp
    unix_timestamp = round(dp.parse(timestamp).timestamp())

    # Creation of boto3 resource for dynamodb
    table = boto3.resource('dynamodb', region_name=region).Table(table_name)

    content = {
        "standKey": filename,
        "rawKey": in_key,
        "uploaderName": uploader_name,
        "uploadTime": unix_timestamp,
        "initAnotKey": '',
        "finalAnotKey": '',
        "anotName": '0',
        "finalAnotTime": ''
    }
    try:
        response = table.put_item(Item=content)
        return response
    except botocore.exceptions.ClientError as e:
        return e.response