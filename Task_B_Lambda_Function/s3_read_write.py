import boto3
import botocore
import cv2
import numpy as np
import time
import os


# Function to read image from s3
def s3_image_read(bucket_name: str, key: str) -> 'numpy.ndarray':
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
        if key.lower().endswith(tuple(ext)):
            content = bucket.Object(key).get().get('Body').read()
            img = cv2.imdecode(np.asarray(bytearray(content)), cv2.IMREAD_COLOR)
            return img
        else:
            print('Invalid file extension. Must be .jpg, .jpeg, .png or .tiff')
    except botocore.exceptions.ClientError as e:
        return e.response

# Function to write images to s3
def s3_image_write(bucket_name: str, processed_img: 'numpy.ndarray', filename: str) -> 'Str':
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


def db_write(in_key: str, filename : str, timestamp: str, table_name: str, region: str = 'eu-west-1') -> str:
    """
    Write an image to AWS DynamoDB
    :param table_name: DynamoDB Table name
    :param processed_img: Standardised image array
    :param region: AWS region name where database is located
    :return: None
    """
    # Extract name of uploader and increment information from file name
    uploader_name, _ = in_key.split('_')[:2]

    # Creation of boto3 resource for dynamodb
    table = boto3.resource('dynamodb', region_name=region).Table(table_name)

    content = {
        "standKey": filename,
        "rawKey": in_key,
        "uploaderName": uploader_name,
        "uploadTime": timestamp,
        "initAnotKey": '',
        "finalAnotKey": '',
        "anotName": '',
        "finalAnotTime": 0
    }
    try:
        response = table.put_item(Item=content)
        return response
    except botocore.exceptions.ClientError as e:
        return e.response