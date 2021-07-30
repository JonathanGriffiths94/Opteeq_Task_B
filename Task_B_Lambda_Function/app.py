import json
import logging
import os
from s3_read_write import s3_image_read, s3_image_write, generate_unique_id
from image_standardisation import standardise_image


def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info('event parameter: {}'.format(event))

    # Decode json input event and extract bucket name and key
    s3_event_body = event["Records"][0]["body"]
    s3_event = json.loads(s3_event_body)

    in_bucket = s3_event["Records"][0]["s3"]["bucket"]["name"]
    in_key = s3_event["Records"][0]["s3"]["object"]["key"]
    timestamp = s3_event["Records"][0]["object"]["ApproximateFirstReceiveTimestamp"]

    # Get output bucket name from enviroment variable
    out_bucket = os.environ['out_bucket']
    table_name = os.environ['table_name']

    # Function call to generate unique id and timestamp for filename
    unique_id = generate_unique_id()

    filename = 'IMG-{}-{}.jpg'.format(unique_id, timestamp)

    # Function call to s3 bucket image read
    img = s3_image_read(in_bucket, in_key)

    # Function call to standardise image
    stand_img = standardise_image(img)

    # Function call to s3 image push
    response = s3_image_write(out_bucket, stand_img, filename)

    return {
        "statusCode": 200,
        "body": response
    }