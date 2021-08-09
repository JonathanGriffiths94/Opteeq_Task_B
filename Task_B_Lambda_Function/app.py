import json
import logging
import os
import uuid
from s3_read_write import s3_image_read, s3_image_write, db_write
from image_standardisation import standardise_image


def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info('event parameter: {}'.format(event))

    # Decode json input event and extract bucket name and key
    s3_event_body = event["Records"][0]["body"]
    timestamp = event["Records"][0]["attributes"]["ApproximateFirstReceiveTimestamp"]
    s3_event = json.loads(s3_event_body)

    in_bucket = s3_event["Records"][0]["s3"]["bucket"]["name"]
    in_key = s3_event["Records"][0]["s3"]["object"]["key"]


    # Get output bucket name from enviroment variable
    out_bucket = os.environ['out_bucket']
    table_name = os.environ['dynamodb_table_name']

    # Function call to generate unique id and timestamp for filename
    unique_id = str(uuid.uuid4())

    filename = '{}.jpg'.format(unique_id)

    # Function call to s3 bucket image read
    img = s3_image_read(in_bucket, in_key)

    # Function call to standardise image
    stand_img = standardise_image(img)

    # Function call to s3 image push
    s3_response = s3_image_write(out_bucket, stand_img, filename)

    # Function call to create item in dynamoDB
    dynamodb_response = db_write(in_key, filename, timestamp, table_name)

    return {
        "statusCode": 200,
        "body": {"s3_response": s3_response,
                 "dynamodb_response": dynamodb_response
                 }
    }