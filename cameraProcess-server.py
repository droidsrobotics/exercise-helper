from http.server import *
import logging
import cv2
import numpy as np
import os
import sys

from tensorflow import keras
from sklearn.metrics import confusion_matrix, precision_score
import pandas as pd
import numpy as np
import sys
import os
import tensorflow as tf


gpus = tf.compat.v1.config.experimental.list_physical_devices('GPU')
if gpus:
  try:
    tf.config.experimental.set_virtual_device_configuration(gpus[0], [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=1024)])
  except RuntimeError as e:
    print(e)
    

# model0 = keras.models.load_model("processed_data/pushupmodelSave")
# model1 = keras.models.load_model("processed_data/situpmodelSave")

# models = [model0, model0, model1, model1]

f = open("processed_data/lengths","r")
l = f.read().splitlines()
exercises = eval(l[1])
lookup = eval(l[2])
lengths = eval(l[0])
fileExercises = eval(l[3])
typeLookup = eval(l[4])
interest = eval(l[5])

models = {}
for key in typeLookup:
    models[key] = []
    for i in range(len(interest)):
        models[key].append(keras.models.load_model("processed_data/"+key+str(i)+"modelSave")) 

# exercise = "situp"

# nameLists = []
# for length in lengths:
#     namesList = []
#     print(length*25*2)
#     for i in range(length*25):
#         namesList.append("X"+str(i))
#         namesList.append("Y"+str(i))
#     nameLists.append(namesList)
# length = lengths[2]
# nameList = nameLists[2]


def predict(data, modelid, dir="http_raw", exercise="situp"):
    # try:
        prob = [0]*(len(exercises)+5)
        modelset = models[exercise]
        
        # for i in range(0,len(lengths),2):
        # print("I:",i, len(nameLists[i]))
        # x_data = pd.read_csv("http_process/"+dir+str(i)+"X.csv",names=nameLists[i],na_values=0)
        L = data.split(",")
        M = []
        for n in L:
            try:
                M.append(int(n))
            except:
                M.append(0)
        namesList = []
        for i in range(len(L)//2):
            namesList.append("X"+str(i))
            namesList.append("Y"+str(i))

        x_data = pd.DataFrame([M], columns=namesList)
        x_data.fillna(0,inplace=True)
        x_data.replace(np.nan,0)
        x_test = x_data
        # print(x_data)
        # return random.randint(0,10)
        y_pred = modelset[modelid].predict(x_test)
        #print(x_test)
        #y_pred = model.predict(np.array([[400,400,400,400,400]]*50))
        #rounded = [np.argmax(x) for x in y_pred]
        #print(rounded[-1])
        #return rounded[-1]
        # if y_pred[-1][0] > 0.85:
        #     return 3
        # elif y_pred[-1][1] > 0.85:
        #     return 4
        # else: return 0
        
        # prob[np.argmax(y_pred[-1])] = y_pred[-1][np.argmax(y_pred[-1])]
        # print(np.argmax(y_pred[-1]), y_pred[-1][np.argmax(y_pred[-1])], "  ", end="")
        # print(prob)
        print(y_pred[-1])
        return np.argmax(y_pred[-1]) if (y_pred[-1][np.argmax(y_pred[-1])] > 0.5) else 0
    # except Exception as e:
    #     # print(data)
    #     # print(e)
    #     return 0

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
   
        data = eval(post_data.decode())
        spliced = data[1]
        exercise = data[0]
        modelid = data[2]
        output = predict(spliced, modelid, exercise=exercise)
        print(output)

        self._set_response()
   
        self.wfile.write(str(output).encode())


def run(server_class=HTTPServer, handler_class=Handler):
    server_address = ('', 9000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

run()