"""


"""

import dateutil.parser
import os
import os.path
import requests
import io
import boto
import boto.sns
import time
from pyftpdlib import servers

from boto.sns import SNSConnection

from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.servers import DummyAuthorizer
    

class MyHandler(FTPHandler):

    def on_connect(self):
        print "%s:%s connected" % (self.remote_ip, self.remote_port)

    def on_file_received(self, file):
        print "File saved, posting to SNS"
        conn = boto.sns.connect_to_region(os.getenv("AWS_REGION"),
                                          aws_access_key_id=os.getenv("AWS_KEY"),
                                          aws_secret_access_key=os.getenv("AWS_SECRET_KEY"))
        conn.publish(os.getenv('SNS_TOPIC'),
                     os.getenv('THREDDS_CATALOG') + "/" + filename)

    def on_incomplete_file_received(self, file):
        # remove partially uploaded files
        import os
        os.remove(file)

def main():
    authorizer = DummyAuthorizer()
    authorizer.add_user(os.getenv('FTP_USER'),
                        os.getenv('FTP_PASS'),
                        homedir=os.getenv('DATA_DIR'),
                        perm='elradfmw')

    handler = MyHandler
    handler.authorizer = authorizer
    server = FTPServer((os.getenv('FTP_ADDRESS'), os.getenv('FTP_PORT'), handler)
    server.serve_forever()

if __name__ == "__main__":
    main()
