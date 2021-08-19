import json
import logging
import os
import uuid
from tools import extract_keys, s3_image_read, resize_and_pad, db_write, s3_image_write

def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info('event parameter: {}'.format(event))

    # Get output bucket name from enviroment variable
    out_bucket = os.environ["out_bucket"]
    table_name = os.environ["dynamodb_table_name"]

    # Extract information from s3_event
    item_content = extract_keys(event)
    logger.info('item_content: {}'.format(item_content))

    # Loop through items in event and process one by one
    for item in item_content:
        in_bucket, in_key, timestamp = item

        # Function call to generate unique id and timestamp for filename
        unique_id = str(uuid.uuid4())

        # Set filename
        filename = '{}.jpg'.format(unique_id)

        # Function call to s3 bucket image read
        img = s3_image_read(in_bucket, in_key)

        # Function call to resize and pad image
        resized_img = resize_and_pad(img)

        # Function call to create item in dynamoDB
        dynamodb_response = db_write(in_key, filename, timestamp, table_name)
        logger.info('Dyanmodb response: {}'.format(dynamodb_response))

        # Function call to s3 image push
        s3_response = s3_image_write(out_bucket, resized_img, filename)
        logger.info('S3 response: {}'.format(s3_response))
    return {
        "statusCode": 200
    }