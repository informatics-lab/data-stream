"""
Pull data from Met Office Beta Data Services and push to thredds repository.


import from list of required coverages, through warning if not found
save local for testing



"""
from betadataservices import WCS2Requester
import iris

valid_req_params = ["coverage_id", "components", "format", "elevation", "bbox",
                    "time", "width", "height", "interpolation"]

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

def main():
    """

    """
    api_key = "4fc1f5e2-00f9-4ef2-a252-e5c3e9af1734"
    req = WCS2Requester(api_key)

    requests = read_requests()

    for request_dict in requests:
        response = req.getCoverage(**request_dict)
        with open("test.nc", "w") as outfile:
            outfile.write(response.content)


if __name__ == "__main__":
    main()
