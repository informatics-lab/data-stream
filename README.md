# data-stream

Python module to pull data from BDS and upload to the thredds server.

Download and upload use HTTPS/HTTP protocol and the requests library.

## Environment variables

All must be set, there are no default values.

 * *THREDDS_CATALOG*: Catalogue URI to which file name is added.
 * *AWS_REGION*: AWS server region
 * *AWS_KEY*: Key to access AWS
 * *AWS_SECRET_KEY*: Secret key to access AWS
 * *SNS_TOPIC*: Topic name for AWS SNS
 * *FTP_HOST*: Server to pull data from
 * *FTP_USER*: User for FTP login
 * *FTP_PASS*: Password for FTP login
 * *DATA_DIR*: Directory where data is stored on FTP host
