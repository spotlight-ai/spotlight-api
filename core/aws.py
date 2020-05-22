import os

import boto3
from botocore.exceptions import ClientError


def generate_presigned_download_link(bucket_name, object_name, expiration=3600):
    """
    Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """
    s3_client = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                             aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
    try:
        response = s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        return None
    
    return response


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
