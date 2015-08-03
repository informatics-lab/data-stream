"""
Pull data from Met Office Beta Data Services and push to thredds repository.

"""
from betadataservices import WCS2Requester

import dateutil.parser
import os
import requests
import io

valid_req_params = ["var_name", "model_feed", "coverage_id", "components",
                    "format", "elevation", "bbox", "time", "width", "height",
                    "interpolation"]

format_dict = {"NetCDF3" : "nc",
               "GRIB2"   : "grib2"}

# Set up enviroment variables.
# For BDS
api_key        = os.environ['API_KEY']
# For the thredds (tomcat) server
# Note that upload is via HTTP POST of multipart file.
# The username and password are for this form only.
# The upload form checks for file size and type so
# security requirements are minimal.
thrds_url      = os.environ['THREDDS_URL']
thrds_username = os.environ['THREDDS_USER']
thrds_password = os.environ['THREDDS_PASS']
thrds_catalog = os.environ['THREDDS_CATALOG']
thrds_queue = os.environ['THREDDS_QUEUE']
aws_region = os.environ['AWS_REGION']


def read_requests():
    """
    Read data_requests.txt file, extract the requests and return in a list as
    dictionaries.

    """
    requests = {}
    request_dict = None

    with open("data_requests.txt", "r") as infile:
        for i, line in enumerate(infile.readlines()):
            line = line.strip()
            # Ignore blank lines and comments.
            if not line or line[0] == "#":
                continue
            else:
                # Start a new request dict.
                if line == "START REQUEST":
                    request_dict = {}
                elif line == "END REQUEST":
                    if request_dict:
                        if not request_dict.get("model_feed"):
                            raise UserWarning("No model_feed given. This "\
                                              "parameter must be specified.")
                        else:
                            # Want to group model feeds together so we don't
                            # have to have a new WCS2Requester instance every
                            # time.
                            model_feed = request_dict.pop("model_feed")
                            if requests.get(model_feed):
                                requests[model_feed].append(request_dict)
                            else:
                                requests[model_feed] = [request_dict]
                else:
                    if request_dict is not None:
                        req_params = line.split("=")
                        if len(req_params) != 2:
                            raise UserWarning("Incorrect request parameter "\
                                              "'%s', line %s."
                                              % (line, i+1))
                        if req_params[0] not in valid_req_params:
                            raise UserWarning("Invalid request parameter "\
                                              "'%s', line %s."
                                              % (req_params[0], i+1))
                        if not req_params[1]:
                            print ("Ignoring incomplete request parameter '%s'"
                                   % line)
                        else:
                            # Convert to list if appropriate.
                            req_params[1] = req_params[1].split(",")
                            if len(req_params[1]) == 1:
                                req_params[1] = req_params[1][0]
                            request_dict[req_params[0]] = req_params[1]
    return requests

def write_filename(model, variable, init, fmt):
    return "{mod}_{var}_{init}.{fmt}".format(mod=model,
                                             var=variable,
                                             init=init,
                                             fmt=fmt)

def format_date(cov_date):
    """
    Convert date to given format for filename.

    """
    dtime = dateutil.parser.parse(cov_date)
    return dtime.strftime("%Y%m%dT%H%M%S")

def create_filename(req, request_dict):
    """
    Build the filename format.

    """
    coverage = req.describeCoverage(request_dict["coverage_id"], show=False)
    init_date = format_date(coverage.dim_runs)
    return write_filename(req.model_feed, request_dict["var_name"],
                          init_date, format_dict[request_dict["format"]])

def to_thredds(content, filename, thredds=thrds_url, username=thrds_username, as_data=False):
    """
    Post data to thredds sever.


    """
    s = requests.Session()
    s.auth = ('user', 'pass')
    s.headers.update({'my-filename': filename})

    if as_data:
        try:
            with io.BytesIO( content ) as f:
                s.post(thrds_url, data=f)
        except Exception, e:
            raise UserWarning("to_thredds error: %s" % e)
    else:
        print("to_thredds uploading: %s (length %d) " % (filename,len(content)))
        # use multi-part form
        files = {filename: io.BytesIO( content )}
        try:
            r = s.post(thrds_url, files=files)
            print("to_thredds upload status code: %d" % r.status_code)
            print r.ok
        # Possible errors
        # UserWarning: to_thredds error: ('Connection aborted.', error(32, 'Broken pipe'))
        except Exception, e:
            raise UserWarning("to_thredds error: %s" % e)


def postTHREDDSJob(msg, queue_name="thredds_queue"):
    import boto.sqs
    import boto.sqs.message
    # NB. AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must
    # be set in calling environment.
    conn = boto.sqs.connect_to_region(aws_region)
    #print conn.get_all_queues()
    queue = conn.get_queue(queue_name)
    #print "Adding " + msg + " to queue[" + queue_name + "]"
    m = boto.sqs.message.Message()
    m.set_body(msg)
    queue.write(m)

def main(debug=False, upload=True):
    requests = read_requests()

    print requests

    for model_feed in requests.keys():
        req = WCS2Requester(api_key, model_feed)
        for request_dict in requests[model_feed]:

            print request_dict

            filename = create_filename(req, request_dict)
            request_dict.pop("var_name")

            desc = req.describeCoverage( request_dict['coverage_id'] )

            print desc

            response = req.getCoverage(stream=True, **request_dict)

            if upload:
                to_thredds(response.content, filename)
                postTHREDDSJob(thrds_catalog + "/" + filename)

if __name__ == "__main__":
    main(debug=True, upload=False)
