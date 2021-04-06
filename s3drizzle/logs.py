import re
import urllib

s3_log_pattern = r'(\S+) (\S+) \[(.*?)\] (\S+) (\S+) ' \
    r'(\S+) (\S+) (\S+) "([^"]+)" ' \
    r'(\S+) (\S+) (\S+) (\S+) (\S+) (\S+) ' \
    r'"([^"]+)" "([^"]+)"'

s3_log_regex = re.compile(s3_log_pattern)


def parse_s3_log_line(line):
    match = s3_log_regex.match(line)
    result = [match.group(1+n) for n in range(17)]
    return result


def find_start_request(args, relevant_requests):
    expected_size = 0
    expected_hash = ""
    for request in relevant_requests:
        uri_parts = urllib.parse.urlparse(request)
        if is_start_request(args, uri_parts):
            print("Found start request")
            arguments = urllib.parse.parse_qs(uri_parts.query)
            if "x-request-length" in arguments.keys():
                expected_size = int(
                    arguments['x-request-length'][0])
            if "x-request-hash" in arguments.keys():
                expected_hash = arguments['x-request-hash'][0]
            if expected_size > 0 and expected_hash != "":
                print("Start request found with size {size} and hash {hash}".format(
                    size=expected_size,
                    hash=expected_hash
                ))
                break

            print("Start request is malformed")
            return -1, expected_hash

    return expected_size, expected_hash


def find_file_parts(args, relevant_requests):
    file_parts = {}
    for request in relevant_requests:
        uri_parts = urllib.parse.urlparse(request)
        if is_session_request(args, uri_parts):
            arguments = urllib.parse.parse_qs(uri_parts.query)
            part_number = int(arguments['x-request-sequence'][0])
            part = arguments['x-request-data'][0]
            file_parts[part_number] = part

    return file_parts


def is_relevant_request(uri_parts, bucket, session, endpoint):
    return (uri_parts.path == "/{bucket}/{session}/{s3object}".format(
        bucket=bucket,
        session=session,
        s3object=endpoint) and
        uri_parts.query != "")


def is_start_request(args, uri_parts):
    return is_relevant_request(
        uri_parts,
        args.web_bucket,
        args.session,
        'start.js')


def is_session_request(args, uri_parts):
    return is_relevant_request(
        uri_parts,
        args.web_bucket,
        args.session,
        'session.js')
