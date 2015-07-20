"""
Pull data from Met Office Beta Data Services and push to thredds repository.

"""
from betadataservices import WCS2Requester
from paramiko.client import SSHClient
import dateutil.parser
import os

valid_req_params = ["var_name", "model_feed", "coverage_id", "components",
                    "format", "elevation", "bbox", "time", "width", "height",
                    "interpolation"]

format_dict = {"NetCDF3" : "nc",
               "GRIB2"   : "grib2"}

# Set up enviroment variables.
thrds_url      = os.environ['THREDDS_URL']
thrds_username = os.environ['THREDDS_USERNAME']
thrds_datadir  = os.environ['THREDDS_DATADIR']
api_key        = os.environ['API_KEY']

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

def to_thredds(data, filename, thredds=thrds_url, username=thrds_username,
               data_dir=thrds_datadir):
    """
    Put data in thredds directory.


    """
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(thredds, username=username)
    sftp = ssh.open_sftp()
    outfile = sftp.open(data_dir + filename, 'w')
    outfile.write(data)
    outfile.close()
    ssh.close()

def main():
    requests = read_requests()

    for model_feed in requests.keys():
        req = WCS2Requester(api_key, model_feed)

        for request_dict in requests[model_feed]:
            filename = create_filename(req, request_dict)
            request_dict.pop("var_name")
            response = req.getCoverage(stream=True, **request_dict)
            to_thredds(response.content, filename)

if __name__ == "__main__":
    main()
