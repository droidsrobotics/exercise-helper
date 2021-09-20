from http.server import *
import logging
import cv2
import numpy as np
import os
import sys

from poseDetection import *
import platform
# video = sys.argv[1]
# label = sys.argv[2]

try:
    print("trying openpose backend")
    pose = openPose()
except:
    print("trying posenet backend")
    pose = posenet()

pose.config()

def flattenList(L):
    M = []
    for entry in L:
        if type(entry) == list:
            M.extend(flattenList(entry))
        else:
            M.append(entry)
    return M



class Handler(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        # logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
        #         str(self.path), str(self.headers), post_data.decode('utf-8'))
        img = cv2.imdecode(np.fromstring(post_data, np.uint8), cv2.IMREAD_UNCHANGED)
        
        # img = cv2.rotate(img, cv2.cv2.ROTATE_90_CLOCKWISE) 

        output_image, output = pose.process(img)

        # cv2.imshow("tmp",img)
        key = cv2.waitKey(1)
        # if key==ord('q'):
        #     break
        self._set_response()
        # img = cv2.resize(img, (320, 240))
        # _, data = cv2.imencode(".jpg", img)
        # data2 = str([output, data.tobytes()])
        self.wfile.write(str(output).encode())


def run(server_class=HTTPServer, handler_class=Handler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

run()