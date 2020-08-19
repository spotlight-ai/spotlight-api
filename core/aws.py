import hashlib
import os
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError
from redactors.base import FileRedactorCreator

def generate_presigned_download_link(
    bucket_name,
    object_name,
    expiration=3600,
    permissions=None,
    markers=None,
    mask=False,
):
    """
    Generate a presigned URL to share an S3 object
    Also modifies and returns marker coordinates for shared users with selective permission 
    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :param permissions: PII that should be exposed to the requesting viewer
    :param markers: PII markers detected in the dataset
    :return: Presigned URL as string. If error, returns None.
             Modified list of markers for shared users. Returns None for owners
    """
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    raw_bucket: str = "uploaded-datasets"
    redacted_bucket: str = "spotlightai-redacted-copies"
    masked_bucket: str = "spotlightai-masked-copies"

    try:
        if permissions is None:
            response = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": raw_bucket, "Key": object_name},
                ExpiresIn=expiration,
            )
        else:
            permission_descriptions: list = [perm.description for perm in permissions]
            redacted_filepath = hashlib.sha1(
                (object_name + str(permission_descriptions)).encode()
            ).hexdigest()

            if not mask:
                s3_client.head_object(Bucket=redacted_bucket, Key=redacted_filepath)

                response = s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": redacted_bucket, "Key": redacted_filepath},
                    ExpiresIn=expiration,
                )
            else:
                s3_client.head_object(Bucket=masked_bucket, Key=redacted_filepath)

                response = s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": masked_bucket, "Key": redacted_filepath},
                    ExpiresIn=expiration,
                )

            if markers:
                markers: list = modify_markers(
                    markers, permission_descriptions, mask, object_name, s3_client
                )

        return response, markers

    except ClientError as e:
        if e.response["ResponseMetadata"]["HTTPStatusCode"] == 404:
            permission_descriptions: list = [perm.description for perm in permissions]
            redacted_filepath = hashlib.sha1(
                (object_name + str(permission_descriptions)).encode()
            ).hexdigest()

            s3_client.download_file(
                raw_bucket, object_name, object_name.replace("/", "_")
            )
            
            redactor_factory: FileRedactorCreator = FileRedactorCreator()
            output_location: str = object_name.replace("/", "_")
            
            _, ext = os.path.splitext(output_location)
            modified_markers = redactor_factory.get_redactor(ext).redact_file(output_location, permission_descriptions, markers, mask)

            if not mask:
                s3_client.upload_file(
                    object_name.replace("/", "_"), redacted_bucket, redacted_filepath
                )
                os.remove(object_name.replace("/", "_"))
                return (
                    s3_client.generate_presigned_url(
                        "get_object",
                        Params={"Bucket": redacted_bucket, "Key": redacted_filepath},
                        ExpiresIn=expiration,
                    ),
                    modified_markers,
                )
            else:
                s3_client.upload_file(
                    object_name.replace("/", "_"), masked_bucket, redacted_filepath
                )
                os.remove(object_name.replace("/", "_"))
                return (
                    s3_client.generate_presigned_url(
                        "get_object",
                        Params={"Bucket": masked_bucket, "Key": redacted_filepath},
                        ExpiresIn=expiration,
                    ),
                    modified_markers,
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

    bucket = parsed_url.netloc.split(".")[0]
    key = parsed_url.path[1:]

    try:
        s3_client.delete_objects(Bucket=bucket, Delete={"Objects": [{"Key": key}]})
    except ClientError:
        return None


def modify_markers(markers, permission_descriptions, mask, object_name, s3_client):
    """
    Below is the algorithm to modify the marker co-ordinates after replacing the PII values
    with the Redaction text or a randomly generated Hash value.
    """
    raw_bucket: str = "uploaded-datasets"
    redacted_bucket: str = "spotlightai-redacted-copies"
    masked_bucket: str = "spotlightai-masked-copies"

    s3_client.download_file(
        raw_bucket, object_name, object_name.replace("/", "_")
    )

    redactor_factory: FileRedactorCreator = FileRedactorCreator()
    output_location: str = object_name.replace("/", "_")
    
    _, ext = os.path.splitext(output_location)
    modified_markers = redactor_factory.get_redactor(ext).redact_file(output_location, permission_descriptions, markers, mask)
    os.remove(output_location)
    return modified_markers
