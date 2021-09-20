import os
import sys
import cv2
import numpy as np
from tensorflow import keras
#from keras.datasets import imdb
#from keras.models import Sequential
#from keras.layers import LSTM
#from keras.layers.embeddings import Embedding
#from keras.preprocessing import sequence
from sklearn.metrics import confusion_matrix, precision_score
#from sklearn.model_selection import train_test_split
#from keras.layers import Dense,Dropout
#from keras.regularizers import l2
#import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import os
import threading
import tensorflow as tf

gpus = tf.compat.v1.config.experimental.list_physical_devices('GPU')
if gpus:
  try:
    tf.config.experimental.set_virtual_device_configuration(gpus[0], [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=2048)])
  except RuntimeError as e:
    print(e)
    

model0 = keras.models.load_model("processed_data/pushupmodelSave")
model1 = keras.models.load_model("processed_data/situpmodelSave")

models = [model0, model0, model1, model1]

f = open("processed_data/lengths","r")
l = f.read().splitlines()
exercises = eval(l[1])
lookup = eval(l[2])
lengths = eval(l[0])
fileExercises = eval(l[3])

exercise = "situp"

nameLists = []
for length in lengths:
    namesList = []
    print(length*25*2)
    for i in range(length*25):
        namesList.append("X"+str(i))
        namesList.append("Y"+str(i))
    nameLists.append(namesList)
length = lengths[2]
nameList = nameLists[2]

def processRange(start, end, dir="camera_raw"):
    outFile = "camera_process/"+dir
    # fA = open(outFile+"raw.csv", "w")
    fN = open(outFile+"normalized.csv", "w")
    # fX = open(outFile+"Xraw.csv", "w")
    # fY = open(outFile+"Yraw.csv", "w")
    # exercises = {"pushup":1, "situp":2}
    # exercises = {"pushup":1, "situp":2, "camera":-1}
    # files = os.listdir("camera_process/"+dir)
    # fileInts = [int(x.split("_")[0]) for x in files]
    # fileInts.sort()
    fileInts = [i for i in range(start, end)]
    files = [str(x)+"_keypoints.json" for x in fileInts]
    # print(files)
    last = ""
    last2 = ""
    # outputY = open("videos/"+dir+".info", "r").read()
    for fileName in files:
        with open("camera_process/"+dir+"/"+fileName, "r") as f:
            data = eval(f.read())
            if (len(data["people"]) == 1):
                last = ""
                last2 = ""
                outputX = data["people"][0]["pose_keypoints_2d"]
                for i in range(len(outputX)):
                    if (i-2)%3 != 0:
                        out = outputX[i]
                        # fA.write(str(int(out)))
                        if i%3 == 0:
                            fN.write(str(int(int(out)-int(outputX[0]))))
                            last2 += str(int(int(out)-int(outputX[0])))
                        elif i%3 == 1:
                            fN.write(str(int(int(out)-int(outputX[1]))))
                            last2 += str(int(int(out)-int(outputX[1])))
                        last += str(int(out))
                        # fX.write(str(int(out)))
                        # print(str(int(out))+",", end="")
                        # fA.write(",")
                        # fA.write(",")
                        if i != len(outputX)-2:
                            fN.write(",")
                            last2+=","
                # fA.write(str(outputY)+"\n")
                fN.write("\n")
                # fY.write(str(exercises[outputY])+"\n")
                # fX.write("\n")
                # print(outputY)
            else:
                # fA.write(str(last)+","+outputY+"\n")
                fN.write(str(last2)+"\n")
    fN.close()

    f = open("camera_process/"+dir+"normalized.csv","r")
    data = f.read().splitlines()
    f.close()

    # for i in range(0,len(lengths),2):
    i = exercises.index(exercise)

    fX = open("camera_process/"+dir+str(i)+"X.csv", "w")
    # i = 2
    spliced = data[-lengths[i]:]
    # print(spliced)
    data = spliced
    # print(data)
    strline = ",".join(data)
    fX.write(strline+"\n")  
    fX.close()

def predict(dir="camera_raw"):
    try:
        prob = [0]*5
        i = exercises.index(exercise)
        # for i in range(0,len(lengths),2):
        # print("I:",i, len(nameLists[i]))
        x_data = pd.read_csv("camera_process/"+dir+str(i)+"X.csv",names=nameLists[i],na_values=0)
        x_data.fillna(0,inplace=True)
        x_data.replace(np.nan,0)
        x_test = x_data
        # print(x_data)
        # return random.randint(0,10)
        y_pred = models[i].predict(x_test)
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
        
        prob[np.argmax(y_pred[-1])] = y_pred[-1][np.argmax(y_pred[-1])]
        print(np.argmax(y_pred[-1]), y_pred[-1][np.argmax(y_pred[-1])], "  ", end="")
        # print(prob)
        print(prob)
        return np.argmax(prob[1:])+1 if (prob[np.argmax(prob[1:])+1 ] > 0.8) else 0
    except Exception as e:
        print(e)
        return 0

def predictor():
    global frame, out, font
    while True:
        files = os.listdir("camera_process/camera_raw/")
        fileInts = [int(x.split("_")[0]) for x in files]
        frame = max(fileInts)
        if frame > 50:
            processRange(frame-40, frame, dir="camera_raw")
        out = predict()
        output = open("camera_process/prediction","w")
        output.write(str(out))
        output.close()
        print("F:",frame, "P:",out)

def predictFrame(frame):
    if frame > 50:
        processRange(frame-40, frame, dir="camera_raw")
        out = predict()
        print("F:",frame, "P:",out)
        return out
    else:
        return 0

# pose()
# a = threading.Thread(target=pose, daemon=True)
# b = threading.Thread(target=predictor, daemon=True)
# a.start()
# b.start()
if __name__ == '__main__':
    predictor()
