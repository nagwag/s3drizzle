from botocore.exceptions import ClientError
import boto3
import logging

from s3drizzle import (
    logs
)


def create_bucket(client, bucket):
    logging.info('Create bucket {bucket}.'.format(
        bucket=bucket
    ))
    client.create_bucket(
        Bucket=bucket,
    )


def destroy_bucket(args, client, bucket):
    logging.info('Deleting bucket {bucket}.'.format(
        bucket=bucket
    ))
    try:
        client.delete_bucket(
            Bucket=bucket
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            logging.info('Bucket {bucket} does not exist, but that is ok...continuing.'.format(
                bucket=bucket
            ))
            return
        raise e


def deploy_file(client, bucket, path, file_content):
    logging.info("Creating {path} in bucket {bucket}.".format(
        path=path,
        bucket=bucket
    ))
    client.put_object(
        ACL='public-read',
        Body=file_content,
        Bucket=bucket,
        ContentType="text/html",
        Key=path
    )


def empty_bucket(args, session, bucket):
    logging.info('Emptying bucket {bucket}.'.format(
        bucket=bucket
    ))
    try:
        bucket_session = session.Bucket(bucket)
        bucket_session.object_versions.delete()
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            logging.info('Bucket {bucket} does not exist, but that is ok...continuing.'.format(
                bucket=bucket
            ))
            return
        raise e


def enable_access_logging(client, source_bucket, log_bucket):
    logging.info('Enable bucket access logging for {bucket} to {log}.'.format(
        bucket=source_bucket,
        log=log_bucket
    ))
    client.put_bucket_logging(
        Bucket=source_bucket,
        BucketLoggingStatus={
            'LoggingEnabled': {
                'TargetBucket': log_bucket,
                'TargetPrefix': ''
            }
        },
    )


def grant_logging_access(client, log_bucket):
    logging.info('Granting logging access to {bucket}.'.format(
        bucket=log_bucket
    ))
    canonical_id = get_canonical_id(client)
    client.put_bucket_acl(
        Bucket=log_bucket,
        GrantFullControl='id={canonical_id}'.format(canonical_id=canonical_id),
        GrantWrite='uri=http://acs.amazonaws.com/groups/s3/LogDelivery',
        GrantReadACP='uri=http://acs.amazonaws.com/groups/s3/LogDelivery',
    )


def get_canonical_id(client):
    buckets = client.list_buckets()
    return buckets['Owner']['ID']


def get_relevent_requests(args):
    session = boto3.Session(profile_name=args.profile)
    client = session.client('s3')

    relevant_requests = []
    response = None
    response = client.list_objects_v2(Bucket=args.log_bucket)

    if 'Contents' in response.keys():
        for s3_object in response['Contents']:
            s3_object_body = get_object_data(
                client,
                args.log_bucket,
                s3_object['Key']
            )

            s3_log_lines = s3_object_body.splitlines()

            for line in s3_log_lines:
                if "S3Console" in line or "REST.HEAD.OBJECT" not in line:
                    continue
                parsed_line = logs.parse_s3_log_line(line)
                uri = parsed_line[8].split(" ")[1]
                if (parsed_line[6] == "REST.HEAD.OBJECT"
                        and args.session in uri):
                    relevant_requests.append(uri)

    return relevant_requests


def get_object_data(client, bucket, object_key):
    response = client.get_object(
        Bucket=bucket,
        Key=object_key)
    return response['Body'].read().decode("utf-8")
