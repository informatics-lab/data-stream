# data-stream

Python module to pull data from BDS and upload to the thredds server.

Download and upload use HTTPS/HTTP protocol and the requests library.

## Environment variables

All must be set, there are no default values.

 * *API_KEY*: BDS (DataPoint) API key
 * *THREDDS_UPLOAD*: URL for upload (HTTP POST of mutlipart file to here)
 * *THREDDS_USER*: Username for basic authentication
 * *THREDDS_PASS*: Password for basic authentication
 * *THREDDS_CATALOG*: Catalogue URI to which file name is added.
 * *THREDDS_QUEUE*: AQS queue name
