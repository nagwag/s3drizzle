import base64
import hashlib
import logging
# import re
import time


from s3drizzle import (
    aws,
    logs
)


def create(args):
    logging.info('Attempting to materialize data.')
    while True:
        relevant_requests = aws.get_relevent_requests(args)
        if relevant_requests is None or len(relevant_requests) == 0:
            logging.info("No relevant requests found, sleeping for {sleep} seconds".format(
                sleep=args.sleep_time
            ))
            time.sleep(args.sleep_time)
            continue

        logging.info("Found {x} relevant requests for session {session}".format(
            x=len(relevant_requests),
            session=args.session)
        )
        logging.info("Looking for start...")

        expected_size, expected_hash = logs.find_start_request(
            args, relevant_requests)

        # malformed start request
        if expected_size == -1:
            break

        if expected_hash == "" and expected_size == 0:
            logging.info("Didn't find start request, sleeping for {sleep} seconds".format(
                sleep=args.sleep_time
            ))
            time.sleep(args.sleep_time)
            continue

        file_parts = logs.find_file_parts(args, relevant_requests)

        logging.info("found {part} of {parts} expected".format(
            part=len(file_parts),
            parts=expected_size))

        if len(file_parts) != expected_size:
            logging.info("Didn't find all file parts, sleeping for {sleep} seconds".format(
                sleep=args.sleep_time
            ))
            time.sleep(args.sleep_time)
            continue

        logging.info("Assembling file...")
        full_file_encoded = ""
        for x in range(1, expected_size+1):
            full_file_encoded += file_parts[x]

        # data_url_prefex = r'^data\:[\w\_\-\/\*]+\;base64\,'
        # data_url_prefex_regex = re.compile(data_url_prefex)
        # full_file_encoded = re.sub(data_url_prefex_regex, '', full_file_encoded)

        file_hash = hashlib.md5(full_file_encoded.encode('utf-8')).hexdigest()

        logging.info("Expected file hash {hash}".format(hash=expected_hash))
        logging.info("Actual file hash {hash}".format(hash=file_hash))
        if expected_hash == file_hash:
            # fix padding
            if len(full_file_encoded) % 4:
                # not a multiple of 4, add padding:
                full_file_encoded += '=' * (4 - len(full_file_encoded) % 4)
            full_file = base64.urlsafe_b64decode(full_file_encoded)
            f = open(args.output_file, "wb")
            f.write(full_file)
            f.close()
            print("SUCCESS!!")
        else:
            logging.error("File hashes didn't match, exiting.")

        break
