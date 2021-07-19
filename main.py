import json
from s3_read_write import s3_image_read, generate_unique_info, s3_image_write
from image_standarisation import rotate_image, check_image_size

def lambda_hamdler(event, context):

    bucket_name = event['bucketName']
    in_key = event['inputKey']
    out_key = event['outputKey']

    # Read images from s3


    # Image standardisation

    # Push images to s3

    return {}