import boto3
import botocore
import cv2
import numpy as np
import time
import os
import json


def extract_keys(event: str) -> list:
    """
    Converts json string event containing SQS message and S3 events
    and extracts information from each S3 event.
    :param event: JSON event
    :returns: List of lists containing information from each S3 event
    """
    content = []

    records = [json.loads(el["body"])["Records"] for el in event["Records"]]

    for record in records:
        for s3_event in record:
            item_content = []

            bucket = s3_event["s3"]["bucket"]["name"]
            key = s3_event["s3"]["object"]["key"]
            timestamp = s3_event["eventTime"]
            item_content.extend([bucket, key, timestamp])
            content.append(item_content)

    return content

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
        "anotName": '0',
        "finalAnotTime": ''
    }
    try:
        response = table.put_item(Item=content)
        return response
    except botocore.exceptions.ClientError as e:
        return e.response

def resize_and_pad(img: np.ndarray, desired_size: int = 2000) -> np.ndarray:
    """
    Resizes an image to a square and pads image keep original aspect ratio.
    :param img: Image as np.ndarray
    :param desired_size: Size of image
    :return: Resized image np.ndarray
    """
    old_size = img.shape[:2]  # old_size is in (height, width) format

    ratio = float(desired_size) / max(old_size)
    new_size = tuple([int(x * ratio) for x in old_size])

    # new_size should be in (width, height) format
    img = cv2.resize(img, (new_size[1], new_size[0]))

    delta_w = desired_size - new_size[1]
    delta_h = desired_size - new_size[0]
    top, bottom = delta_h // 2, delta_h - (delta_h // 2)
    left, right = delta_w // 2, delta_w - (delta_w // 2)

    color = [0, 0, 0]
    new_img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT,
                                 value=color)
    return new_img