"""


"""

import dateutil.parser
import os
import os.path
import io
import iris
import boto
import boto.sns
import time
import ftplib
import sys

from boto.sns import SNSConnection

sys.path.append(".")
from config import manifest

def connect():
    ftp_server = os.getenv('FTP_HOST')
    print "Connecting to FTP server " + ftp_server
    ftp = ftplib.FTP(ftp_server)
    ftp.login(os.getenv('FTP_USER'), os.getenv('FTP_PASS'))
    return ftp

def nofiles(ftp):
    print "No files found"
    disconnect(ftp)
    print "Sleeping for 15 minutes..."
    time.sleep(60*15)
    print "Maybe there are new files now, exiting to restart service."
    sys.exit(1)

def getfile(ftp):
    files = []

    try:
        files = [f for f in ftp.nlst() if f.endswith("grib2")]
        file = files[0]
    except Exception, resp:
        nofiles(ftp)

    ourfile = file+"~" 
    ftp.rename(file, ourfile) 
    print "Found file"

    localfile = os.path.join(os.getenv('DATA_DIR'), file)
    print "Downloading " + file + " to " + localfile
    ftp.retrbinary('RETR ' + ourfile, open(localfile, 'wb').write)
    ftp.rename(ourfile, ourfile+"~")
    # ftp.delete(ourfile)

    return localfile


def getJobs(file):
    info = manifest.runnames[file.slice("_")[-2]]

    newfiles = []
    for variable in info["variables"]:
        print "Ingesting " + variable
        thisdata = iris.load_cube(file, variable)
        stem, fname = os.path.split(file)
        newname = info["model"] + "_" + variable + "_" + fname.split("_")[0] + "_" + fname.split("_")[-1].replace("grib2", "nc")
        iris.save(thisdata, os.path.join(stem, newname))
        postJob(newname) 
    os.remove(file)


def postJob(file):
    print "File saved, posting to SNS"
    conn = boto.sns.connect_to_region(os.getenv("AWS_REGION"),
                            aws_access_key_id=os.getenv("AWS_KEY"),
                            aws_secret_access_key=os.getenv("AWS_SECRET_KEY"))
    conn.publish(os.getenv('SNS_TOPIC'),
                os.path.join(os.getenv('THREDDS_CATALOG'), file))


def disconnect(ftp):
    print "Disconnecting from FTP server"
    ftp.quit()


def main():
    ftp = connect()
    filein = getfile(ftp)
    getJobs(filein)
    disconnect(ftp)

if __name__ == "__main__":
    main()
