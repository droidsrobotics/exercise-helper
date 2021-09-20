import requests
import cv2
import numpy as np
import time
import threading
import sys
import statistics
from poseDetection import *
from PIL import Image, ImageTk
from pygame.locals import KEYDOWN, K_ESCAPE, K_q
import pygame
import numpy 

pose = rpiSend(ip="192.168.1.168", port=8000)
pose.config()

# if pose.process(numpy.zeros((256, 256, 1), dtype = "uint8")) == None:
#     print("switching to coral server")
#     pose = http(ip="192.168.1.205", port=8000)
#     pose.config()

url2='http://192.168.1.175:9000'

if sys.argv[1:] == []:
    camid = "0"
    xdim = 640
    ydim = 480
    stream = cv2.VideoCapture('v4l2src device=/dev/video'+camid+' ! video/x-raw,framerate=30/1,width='+str(xdim)+',height='+str(ydim)+' ! videoscale ! videoconvert ! appsink', cv2.CAP_GSTREAMER)
else:
    stream = cv2.VideoCapture(sys.argv[1])

ct = 0
t = time.time()
history = []

f = open("processed_data/lengths","r")
l = f.read().splitlines()
exercises = eval(l[1])
lookup = eval(l[2])
lengths = eval(l[0])
fileExercises = eval(l[3])
interest = eval(l[5])
print(lengths)
exercise = "situp"
eid = 0
past = [eid]
finalFrame = None


def reverseDict(d):
    f = {}
    for key in d:
        f[d[key]] = key
    return f

revLookup = reverseDict(lookup)

dataOut = {}


def runcam():
    global history, ct, t, l, exercises, eid, past, finalFrame
    while True:
        _, frame = stream.read()
        # frame = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        if sys.argv[1:] != []:
            frame = cv2.resize(frame, (640, 480))
        font = cv2.FONT_HERSHEY_SIMPLEX


        try:
            frame, output = pose.process(frame)
            
            # output = dataOut

            outputX = points = output["people"][0]['pose_keypoints_2d']

            # frame2 = frame.copy()

            # # print(outputX)
            if len(outputX) == 75:
                 normalized = []
                 for i in range(len(outputX)):
                     if (i-2)%3 != 0:
                         out = outputX[i]
                         if i%3 == 0:
                             normalized.append(str(int( (int(out))*50/(50))))
                         elif i%3 == 1:
                             normalized.append(str(int( (int(out))*50/(50) )))

                 for i in range(0, len(normalized), 4):
                     x = int(normalized[i])
                     y = int(normalized[i+1])
                     # print(x,y)
                     frame = cv2.circle(frame, (x,y), 5, (0, 0, 255), 5)

            history.append(normalized)

            history = history[-100:]

            cv2.rectangle(frame, (0, 0), (1000, 100), (255, 255, 255), -1)

            cv2.putText(frame,str(revLookup[int(eid)]), (10, 80), font, 2, (0, 0, 0), 2)

            ct += 1
            print("F: ",ct, "FPS: ", 1/(time.time()-t), "eid: ", past[-1], revLookup[past[-1]])
            t = time.time()

            cv2.imshow("cam",frame)


        except KeyboardInterrupt:
            # quit
            sys.exit()
        except Exception as e:
            print(e)
        key = cv2.waitKey(1)
        if key==ord('q'):
            break


def predict():
    global history, eid, past
    while True:
            if len(history) > 50:
                spliced = []
                lastline = []
                for line in history[-lengths[exercises.index(exercise)]:]:
                    if len(line) > 50:
                        line = lastline
                    lastline = line
                    # spliced.append(",".join(line))
                    spliced.append(line)
                    # print(len(line))
                    #     print("ERROR")
                    #     print("ERROR")
                    #     print("ERROR")
                    #     print("ERROR")
                for k in range(len(interest)):
                    set = interest[k]
                    works = True
                    for line in spliced:
                        # print("start")
                        zeroes = 0
                        for id in set:
                            # print(line[2*id], line[2*id+1])
                            if not (int(line[2*id]) != 0 and int(line[2*id+1]) != 0):
                                zeroes += 1
                                # works = False
                        # print(zeroes)
                        if zeroes >= 10:
                            works = False
                            # print("end", works)
                            break
                        else:
                            dx = int(spliced[0][0])
                            dy = int(spliced[0][1])
                            for l in range(len(spliced)):
                                line = spliced[l]
                                if not (int(line[2*id]) != 0 and int(line[2*id+1]) != 0):
                                    if l-1 < 0:
                                        line[2*id] = spliced[l+1][2*id]
                                        line[2*id+1] = spliced[l+1][2*id+1]
                                    else:
                                        line[2*id] = spliced[l-1][2*id]
                                        line[2*id+1] = spliced[l-1][2*id+1]
                                        # print("REPLACING")
                                    # works = False
                                # for m in range(0,len(line),2):
                                #     line[m] = int(line[m])-dx
                                # for m in range(1,len(line),2):
                                #     line[m] = int(line[m])-dy
                                # print(line[2*id], line[2*id+1])
                        # print("end", works)
                    if works:
                        tmp = []
                        for line in spliced:
                            tmp2 = []
                            for id in set:
                                tmp2.append(int(line[2*id])-int(spliced[0][0]))
                                tmp2.append(int(line[2*id+1])-int(spliced[0][1]))
                                # tmp2.append(line[2*id])
                                # tmp2.append(line[2*id+1])
                            tmp.append(tmp2)
                        for line in tmp:
                            for l in range(len(line)):
                                line[l] = str(line[l])
                        combined = outLine = ",".join([",".join(line) for line in tmp])

                        data = [exercise, combined, k]
                        try:
                            # print(len(tmp[0]))
                            r = requests.post(
                                url=url2,
                                data=str(data).encode(),
                                headers={'Content-Type': 'application/octet-stream'})
                            # print(r.content.decode())
                            eid = r.content.decode()
                            past.append(int(eid))
                            past = past[-15:]
                            avg = statistics.mode(past)
                            eid = str(avg)
                        except KeyboardInterrupt:
                            # quit
                            sys.exit()
                        except:
                            pass

a = threading.Thread(target=predict, daemon=True)
a.start()

runcam()


#predict()
