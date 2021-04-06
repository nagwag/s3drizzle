import boto3
import logging

from s3drizzle import (
    aws,
    files
)


def create(args):
    logging.info('Creating infrastructure.')
    create_buckets(args)
    deploy_files(args)


def create_buckets(args):
    logging.info('Creating buckets.')
    session = boto3.Session(profile_name=args.profile)
    client = session.client('s3')

    aws.create_bucket(client, args.web_bucket)
    aws.create_bucket(client, args.log_bucket)
    aws.grant_logging_access(client, args.log_bucket)
    aws.enable_access_logging(client, args.web_bucket, args.log_bucket)


def deploy_files(args):
    logging.info('Deploying files.')
    session = boto3.Session(profile_name=args.profile)
    client = session.client('s3')

    aws.deploy_file(
        client,
        args.web_bucket,
        'index.html',
        files.index()
    )

    aws.deploy_file(
        client,
        args.web_bucket,
        '{session}/start.js'.format(session=args.session),
        ""
    )

    aws.deploy_file(
        client,
        args.web_bucket,
        '{session}/session.js'.format(session=args.session),
        ""
    )


def destroy(args):
    logging.info('Deleting infrastructure.')
    destroy_buckets(args)


def destroy_buckets(args):
    logging.info('Deleting buckets.')
    session = boto3.Session(profile_name=args.profile)
    client = session.client('s3')
    s3 = session.resource("s3")
    aws.empty_bucket(args, s3, args.web_bucket)
    aws.empty_bucket(args, s3, args.log_bucket)
    aws.destroy_bucket(args, client, args.web_bucket)
    aws.destroy_bucket(args, client, args.log_bucket)
