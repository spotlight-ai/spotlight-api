import hashlib
import os
from urllib.parse import urlparse

import boto3
from botocore import client
from botocore.exceptions import ClientError

from core.constants import AnonymizationTypes
from redactors.base import FileRedactorCreator


def generate_anonymized_filepath(filepath: str, anon_method: str, permissions: list) -> str:
    """
    Utility method to generate a hashed filepath for anonymized files to reduce duplication.
    :param filepath: Original filepath of the raw file.
    :param anon_method: Anonymization method used.
    :param permissions: List of permissions requested in the file.
    :return: Hashed filepath
    """
    perm_descriptions: list = [perm.description for perm in permissions]
    return hashlib.sha1(filepath + str(perm_descriptions) + anon_method).encode().hexdigest()


def generate_presigned_download_link(filepath: str, expiration: int = 3600, permissions: list = None,
                                     markers: list = None, anon_method: str = AnonymizationTypes.REDACT):
    s3_client: client = boto3.client("s3", aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                                     aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
    
    # Configurable S3 paths for raw files and ephemeral copies
    raw_file_bucket: str = "uploaded-datasets"
    anonymized_copy_bucket: str = "spotlight-anonymized-copies"
    
    redacted_bucket: str = "spotlightai-redacted-copies"
    masked_bucket: str = "spotlightai-masked-copies"
    
    try:
        if permissions is None:  # Owner has requested the file, return the raw version
            response = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": raw_file_bucket, "Key": filepath},
                ExpiresIn=expiration,
            )
        else:
            anonymized_filepath = generate_anonymized_filepath(filepath, anon_method, permissions)
            
            try:  # Check to see if this anonymized file has already been created
                s3_client.head_object(Bucket=anonymized_copy_bucket, Key=anonymized_filepath)
            except ClientError as e:  # Generate the anonymized file
                if e.response["ResponseMetadata"]["HTTPStatusCode"] == 404:
                    output_location: str = filepath.replace("/", "_")
                    
                    s3_client.download_file(raw_file_bucket, filepath, output_location)
                    _, ext = os.path.splitext(output_location)
                    
                    anonymizer_factory: FileRedactorCreator = FileRedactorCreator()
                    anonymizer_factory.get_redactor(ext).redact_file(output_location, permission_descriptions, markers,
                                                                     mask)
                    
                    # TODO: Anonymize the file
                    
                    s3_client.upload_file(output_location, anonymized_copy_bucket, anonymized_filepath)
                    os.remove(output_location)
            
            response = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": anonymized_copy_bucket, "Key": anonymized_filepath},
                ExpiresIn=expiration,
            )
            
            if markers:
                permission_descriptions = [perm.description for perm in permissions]
                
                markers: list = modify_markers(
                    markers, permission_descriptions, anon_method, filepath, s3_client
                )
        
        return response, markers
    
    except ClientError as e:
        if e.response["ResponseMetadata"]["HTTPStatusCode"] == 404:
            permission_descriptions: list = [perm.description for perm in permissions]
            redacted_filepath = hashlib.sha1(
                (filepath + str(permission_descriptions)).encode()
            ).hexdigest()
            
            s3_client.download_file(
                raw_file_bucket, filepath, filepath.replace("/", "_")
            )
            
            redactor_factory: FileRedactorCreator = FileRedactorCreator()
            output_location: str = filepath.replace("/", "_")
            
            _, ext = os.path.splitext(output_location)
            modified_markers = redactor_factory.get_redactor(ext).redact_file(output_location, permission_descriptions,
                                                                              markers, mask)
            
            if not mask:
                s3_client.upload_file(
                    filepath.replace("/", "_"), redacted_bucket, redacted_filepath
                )
                os.remove(filepath.replace("/", "_"))
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
                    filepath.replace("/", "_"), masked_bucket, redacted_filepath
                )
                os.remove(filepath.replace("/", "_"))
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


def modify_markers(markers, permission_descriptions, anon_method, object_name, s3_client):
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
    mask = anon_method == AnonymizationTypes.MASK
    modified_markers = redactor_factory.get_redactor(ext).redact_file(output_location, permission_descriptions, markers,
                                                                      mask)
    os.remove(output_location)
    return modified_markers
