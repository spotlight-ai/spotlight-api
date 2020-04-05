import boto3
from botocore.exceptions import ClientError
import os


def generate_presigned_link(bucket_name, object_name, fields=None, conditions=None, expiration=3600):
    """
    Generates an AWS pre-signed link to access files in S3 location.
    :param bucket_name: Bucket to access
    :param object_name: Object to access
    :param fields: Dictionary of pre-filled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time for link to remain valid
    :return: Dictionary with following keys:
        url: pre-signed URL
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error
    """
    s3_client = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                             aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
    try:
        response = s3_client.generate_presigned_post(bucket_name, object_name, Fields=fields, Conditions=conditions,
                                                     ExpiresIn=expiration)
    except ClientError as e:
        return None

    return response

