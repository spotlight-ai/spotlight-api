import hashlib
import os
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError


def generate_presigned_download_link(
        bucket_name, object_name, expiration=3600, permissions=None, markers=None
):
    """
    Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :param permissions: PII that should be exposed to the requesting viewer
    :param markers: PII markers detected in the dataset
    :return: Presigned URL as string. If error, returns None.
    """
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    raw_bucket = "uploaded-datasets"
    redacted_bucket = "spotlightai-redacted-copies"
    
    try:
        if permissions is None:
            response = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": raw_bucket, "Key": object_name},
                ExpiresIn=expiration,
            )
        else:
            permission_descriptions = [perm.description for perm in permissions]
            redacted_filepath = hashlib.sha1(
                (object_name + str(permission_descriptions)).encode()
            ).hexdigest()
            
            s3_client.head_object(Bucket=redacted_bucket, Key=redacted_filepath)
            response = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": redacted_bucket, "Key": redacted_filepath},
                ExpiresIn=expiration,
            )
        
        return response
    
    except ClientError as e:
        if e.response["ResponseMetadata"]["HTTPStatusCode"] == 404:
            permission_descriptions = [perm.description for perm in permissions]
            redacted_filepath = hashlib.sha1(
                (object_name + str(permission_descriptions)).encode()
            ).hexdigest()
            
            s3_client.download_file(
                raw_bucket, object_name, object_name.replace("/", "_")
            )
            file = open(object_name.replace("/", "_"), "r+").read()
            
            total_diff = 0
            sorted_markers = sorted(markers, key=lambda k: k.start_location)
            
            for marker in sorted_markers:
                if marker.pii_type not in permission_descriptions:
                    curr_diff = marker.end_location - marker.start_location - 10
                    start = marker.start_location - total_diff
                    end = marker.end_location - total_diff
                    file = ("<REDACTED>").join([file[:start], file[end:]])
                    total_diff += curr_diff
            
            open(object_name.replace("/", "_"), "w").write(file)
            
            s3_client.upload_file(
                object_name.replace("/", "_"), redacted_bucket, redacted_filepath
            )
            
            os.remove(object_name.replace("/", "_"))
            
            return s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": redacted_bucket, "Key": redacted_filepath},
                ExpiresIn=expiration,
            )


def generate_presigned_link(
        bucket_name, object_name, fields=None, conditions=None, expiration=3600
):
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
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    try:
        response = s3_client.generate_presigned_post(
            bucket_name,
            object_name,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=expiration,
        )
    except ClientError as e:
        return None
    
    return response


def dataset_cleanup(filepath):
    """
    Removes all traces of dataset from S3 location.
    :param: filepath: Filepath of dataset to delete from S3
    :return: None
    """
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    
    parsed_url = urlparse(filepath)
    
    bucket = parsed_url.netloc.split('.')[0]
    key = parsed_url.path[1:]
    
    try:
        s3_client.delete_objects(Bucket=bucket, Delete={"Objects": [{"Key": key}]})
    except ClientError:
        return None
