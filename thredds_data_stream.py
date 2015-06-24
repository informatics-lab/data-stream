"""
Pull data from Met Office Beta Data Services and push to thredds repository.

"""
from betadataservices import WCS2Requester
from paramiko.client import SSHClient

valid_req_params = ["coverage_id", "components", "format", "elevation", "bbox",
                    "time", "width", "height", "interpolation"]


##################### Functions for convertion if needed #####################
import iris
import os

def get_tmp_filename(id):
    return "_tmp_res_data_%s.nc" % id

def remove_tmp_file(id):
    """

    """
    tmp_filename = get_tmp_filename(id)
    os.remove(tmp_filename)

def get_cubes(response, id):
    """
    To load data into cube, currently it must be temperarily saved to file and
    loaded back in. The id used to create a unique filename when parallel
    processing.

    """
    tmp_filename = get_tmp_filename(id)
    with open(tmp_filename, "w") as outfile:
        outfile.write(response.content)
    cubes = iris.load(tmp_filename)
    return cubes
##############################################################################

def read_requests():
    """
    Read data_requests.txt file, extract the requests and return in a list as
    dictionaries.

    """
    requests = []
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
                        requests.append(request_dict)
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

def to_thredds(data, filename,
               thredds="ec2-52-16-245-62.eu-west-1.compute.amazonaws.com",
               username="ec2-user",
               data_dir="/var/lib/tomcat/content/thredds/public/lab_data/"):
    """
    Do any convertions / manipulations here (use Iris).
    What is directory structure for thredds?

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
    """

    """
    api_key = "4fc1f5e2-00f9-4ef2-a252-e5c3e9af1734"
    req = WCS2Requester(api_key)

    requests = read_requests()

    for i, request_dict in enumerate(requests):
        response = req.getCoverage(stream=True, **request_dict)
        to_thredds(response.content, "pytest.nc")

if __name__ == "__main__":
    main()
