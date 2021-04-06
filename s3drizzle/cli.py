#!/usr/bin/env python3
import argparse
import logging
import sys

from s3drizzle import (
    infrastructure,
    materialize
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(prog='S3Drizzle')
    parser.add_argument(
        'action',
        type=str,
        choices=['provision', 'deprovision', 'materialize'],
        help='The action to perform: provision, materialize, or deprovision')
    parser.add_argument(
        '--profile',
        type=str,
        default='default',
        help="The AWS profile to use from the credentials file.")
    parser.add_argument(
        '--web-bucket',
        type=str,
        required=True,
        help="The bucket to use for web requests.")
    parser.add_argument(
        '--log-bucket',
        required=True,
        type=str,
        help="The bucket to use for logs.")
    parser.add_argument(
        '--session',
        type=str,
        default="123456",
        help="The AWS profile to use from the credentials file.")
    parser.add_argument(
        '--sleep-time',
        type=int,
        default=300,
        help="Amount of time to sleep if data not in logs.")
    parser.add_argument(
        '--output-file',
        type=str,
        default="secret.txt",
        help="The output file to save from log data.")
    parser.add_argument(
        "-v",
        "--verbose",
        help="Increase output verbosity",
        action="store_true",
        default=False,
    )

    args = parser.parse_args()

    log_level = logging.ERROR
    log_format = "%(message)s"

    if args.verbose:
        log_level = logging.INFO
        log_format = "%(message)s"

    logging.basicConfig(level=log_level, stream=sys.stderr, format=log_format)

    if args.action == "provision":
        try:
            infrastructure.create(args)
            print("Visit https://s3.amazonaws.com/{bucket}/index.html?s3_bucket={bucket}&session_id={session}".format(
                bucket=args.web_bucket,
                session=args.session
            ))
        except Exception as e:
            logger.error(e, exc_info=True)
    elif args.action == "deprovision":
        try:
            infrastructure.destroy(args)
        except Exception as e:
            logger.error(e, exc_info=True)
    elif args.action == "materialize":
        try:
            materialize.create(args)
        except Exception as e:
            logger.error(e, exc_info=True)


if __name__ == "__main__":
    main()
