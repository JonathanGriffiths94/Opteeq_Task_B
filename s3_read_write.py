import boto3
import botocore
import cv2
import numpy as np
import uuid
import time

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

    # Try and load an image using boto3 and OpenCV,
    # Print exception if extension is not OpenCV compatible or there is a boto3 error
    try:
        if key.endswith(".jpg") or key.endswith(".jpeg") or key.endswith(".png") or key.endswith(".tiff"):
            content = bucket.Object(key).get().get('Body').read()
            img = cv2.imdecode(np.asarray(bytearray(content)), cv2.IMREAD_COLOR)
            return img
        else:
            print('Invalid file extension. Must be .jpg, .jpeg, .png or .tiff')
    except botocore.exceptions.ClientError as e:
        print(e.response)

# Function to generate unique id and timestamp for filename
def generate_unique_info() -> 'Tuple[str, str]':
    """
    Generate unique uuid and unix timestamp for saving files
    :return: Randomly generated uuid and a unix timestamp
    """
    unique_id = str(uuid.uuid4()) # Uuid4 generates a random uuid and we convert it to a string
    timestamp = str(int(time.time())) # Generates a unix timestamp which we convert to an int and then to string
    return unique_id, timestamp


# Function to write images to s3
def s3_image_write(bucket_name: str, key: str, processed_img: 'numpy.ndarray') -> None:
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

    # Function call to generate unique id and timestamp for filename
    unique_id, timestamp = generate_unique_info()

    # Write image to local directory using OpenCV
    if not os.path.exists('tmp'):
        os.mkdir('tmp')

    filename = 'IMG-{}-{}.jpg'.format(unique_id, timestamp)

    cv2.imwrite(os.path.join('tmp', filename), processed_img)

    # Try to upload local file to S3 bucket, print error message if upload fails
    try:
        bucket.upload_file(os.path.join('tmp', filename), os.path.join(key, filename))
        print("Image upload success")
    except botocore.exceptions.ClientError as e:
        print(e.response)