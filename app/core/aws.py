import hashlib
import os
from urllib.parse import urlparse

import boto3
from botocore import client
from botocore.exceptions import ClientError

from core.anon import anonymize_file
from core.constants import AnonymizationType


def generate_anonymized_filepath(filepath: str, anon_method: AnonymizationType, permissions: list) -> str:
    """
    Utility method to generate a hashed filepath for anonymized files to reduce duplication.
    :param filepath: Original filepath of the raw file.
    :param anon_method: Anonymization method used.
    :param permissions: List of permissions requested in the file.
    :return: Hashed filepath
    """
    return hashlib.sha1((filepath + str(permissions) + anon_method.name).encode()).hexdigest()


def generate_presigned_download_link(filepath: str, markers: list, permissions: list, expiration: int = 3600,
                                     anon_method: AnonymizationType = AnonymizationType.REDACT):
    s3_client: client = boto3.client("s3", aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                                     aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
    
    # Configurable S3 paths for raw files and ephemeral copies
    raw_file_bucket: str = "uploaded-datasets"
    anonymized_copy_bucket: str = "spotlight-anonymized-copies"
    anonymized_filepath = generate_anonymized_filepath(filepath, anon_method, permissions)
    
    try:  # Check to see if this anonymized file has already been created
        s3_client.head_object(Bucket=anonymized_copy_bucket, Key=anonymized_filepath)

        response = s3_client.generate_presigned_url("get_object", Params={"Bucket": anonymized_copy_bucket, "Key": anonymized_filepath}, ExpiresIn=expiration)
    except ClientError as e:  # Generate the anonymized file
        if e.response["ResponseMetadata"]["HTTPStatusCode"] == 404:
            output_location: str = filepath.replace("/", "_")

            s3_client.download_file(raw_file_bucket, filepath, output_location)

            # Anonymizes the file and updates the marker positions
            markers: list = anonymize_file(output_location, markers, permissions, anon_method=anon_method)

            s3_client.upload_file(output_location, anonymized_copy_bucket, anonymized_filepath)
            os.remove(output_location)

        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": anonymized_copy_bucket, "Key": anonymized_filepath},
            ExpiresIn=expiration,
        )

    return response, markers


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
    
    bucket = parsed_url.netloc.split(".")[0]
    key = parsed_url.path[1:]
    
    try:
        s3_client.delete_objects(Bucket=bucket, Delete={"Objects": [{"Key": key}]})
    except ClientError:
        return None
