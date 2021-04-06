# Introduction

THIS TOOLS IS FOR EDUCATIONAL USE ONLY. YOU ARE RESPONSIBLE FOR YOUR ACTIONS WHEN USING THIS TOOL!

S3Drizzle is a data exfiltration tool that uses HEAD requests to transfer a file out of a network.
Many organizations block paste sites, file hosting services, etc.  One thing that is rarely blocked
is S3.  This tool takes advantage of [Path Style S3 Virtual Hosting](https://docs.aws.amazon.com/AmazonS3/latest/dev/VirtualHosting.html#path-style-access) 
to send a file out of a network.

# :exclamation: IMPORTANT NOTES

* YOU NEED TO PROVISION FOR EACH FILE YOU WANT TO TRANSFER (SAME BUCKET NAMES DIFFERENT SESSION PARAMETER)
* DON'T DEPROVISION AND REPROVISION THE SAME BUCKETS AS OLD LOG ENTRIES MAY STILL SHOW UP
* THIS TOOL IS SLOW - LOGS CAN TAKE HOURS TO SHOW UP
* THIS TOOL DOES NOT DO ENCRYPTION OF THE PAYLOAD
* I HAVE SEEN BROWSER PLUGINS BLOCK SOME OF THE EXFIL REQUEST SO DISABLE THOSE
  * You can see if this occurs by looking at network requests in browser developer tools

https://docs.aws.amazon.com/AmazonS3/latest/dev/ServerLogs.html#LogDeliveryBestEffort

> The completeness and timeliness of server logging is not guaranteed. The 
> log record for a particular request might be delivered long after the 
> request was actually processed, or it might not be delivered at all.

# Disclaimer

THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

# Usage

## Prerequisite
Setup your AWS account credentials as normal in ~/.aws/credentials

## Setup
Setup environment
```
python3 -m venv ./venv && source venv/bin/activate
pip3 install -r requirements.txt
```

## Provision Environment for Data Exfil 
* Note don't use a . in your bucket name to avoid certificate errors.
Run:
```
bin/s3drizzle --web-bucket <bucket to exfil to> --log-bucket <bucket for logs> --verbose provision
```

## Exfil Data
The previous command will output a url to visit to use in order to exfil the data.  As soon as you
select a file it will be exfilled.

## Materialize the Exfiled Data
Run:
```
bin/s3drizzle --web-bucket <bucket to exfil to> --log-bucket <bucket for logs> --output-file <output file name> --verbose materialize
```

## Deprovision Environment
Run:
```
bin/s3drizzle --web-bucket <bucket to exfil to> --log-bucket <bucket for logs> --verbose deprovision
```

# Why AWS/S3?

It is very unlikely to be blocked for HTTP HEAD requests even from security concious organizations.
Also by using path style requests the bucket name and request parameters used to exfil the file will
be hidden from proxies unless full TLS inspection is happening.

Yes other AWS services could give faster logs but they reveal more to general proxies in the in the
hostname of the request.


# Ideas
* Add some kind of check bit functionality to recover lost log entries
* Add encryption
* Add random delay to exfil requests to hide them better
* load other sites (e.g. youtube) to hide requests among the noise