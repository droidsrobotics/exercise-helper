import os
import sys
import cv2
import numpy as np

import pandas as pd
import numpy as np
import sys
import os
import threading
import shutil
import time


# model = keras.models.load_model("processed_data/situpmodelSave")

# Import Openpose (Windows/Ubuntu/OSX)
dir_path = os.path.dirname(os.path.realpath(__file__))
try:
    # Windows Import
    if sys.platform == "win32":
        # Change these variables to point to the correct folder (Release/x64 etc.)
        sys.path.append(dir_path + '/../bin/python/openpose/Release');
        os.environ['PATH']  = os.environ['PATH'] + ';' + dir_path + '/../x64/Release;' +  dir_path + '/../bin;'
        import pyopenpose as op
    else:
        # Change these variables to point to the correct folder (Release/x64 etc.)
        sys.path.append('../../python');
        # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
        # sys.path.append('/usr/local/python')
        from openpose import pyopenpose as op
except ImportError as e:
    print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
    raise e
# #Setting OpenPose parameters

#Constructing OpenPose object allocates GPU memory
params = dict()
if sys.platform == "win32":
    params["model_folder"] = "../models/"
else:
    params["model_folder"] = "../../../models/"
# params["face"] = True
# params["hand"] = True
# params["face_detector"] = 2
# params["hand_detector"] = 2
# os.rmdir("camera_process/camera_raw")
shutil.rmtree("camera_process/camera_raw", ignore_errors=True)

params["write_json"] = "camera_process/camera_raw/" 

opWrapper = op.WrapperPython()
opWrapper.configure(params)
opWrapper.start()
#Opening OpenCV stream
stream = cv2.VideoCapture(0)
# stream = cv2.VideoCapture("videos/ben-situp.mp4")

f = open("processed_data/lengths","r")
l = f.read().splitlines()
exercises = eval(l[1])
lookup = eval(l[2])
lengths = eval(l[0])
fileExercises = eval(l[3])


length = lengths[2]
namesList = []
for i in range(length*25):
    namesList.append("X"+str(i))
    namesList.append("Y"+str(i))

font = cv2.FONT_HERSHEY_SIMPLEX
frame = 0
out = 4

def pose():
    global frame, out, font
    t = time.time()
    while True:
        ret,img = stream.read()
        img = cv2.resize(img, (640, 480))
        print("FPS:", 1/(time.time()-t))
        t = time.time()
        # handRectangles = [
        #     # Left/Right hands person 0
        #     [
        #     op.Rectangle(320.035889, 377.675049, 69.300949, 69.300949),
        #     op.Rectangle(0., 0., 0., 0.),
        #     ],
        #     # Left/Right hands person 1
        #     [
        #     op.Rectangle(80.155792, 407.673492, 80.812706, 80.812706),
        #     op.Rectangle(46.449715, 404.559753, 98.898178, 98.898178),
        #     ],
        #     # Left/Right hands person 2
        #     [
        #     op.Rectangle(185.692673, 303.112244, 157.587555, 157.587555),
        #     op.Rectangle(88.984360, 268.866547, 117.818230, 117.818230),
        #     ]
        # ]
        datum = op.Datum()
        imageToProcess = img
        datum.cvInputData = imageToProcess
        # datum.handRectangles = handRectangles

        opWrapper.emplaceAndPop(op.VectorDatum([datum]))
        output_image = datum.cvOutputData
        # Display Image
        # print("Body keypoints: " + str(datum.poseKeypoints))
        # print(datum)
        
        # print("Left hand keypoints: " + str(datum.handKeypoints[0]))
        # print("Right hand keypoints: " + str(datum.handKeypoints[1]))
        # Display the stream
        font=cv2.FONT_HERSHEY_PLAIN
        cv2.putText(output_image,"Frame: "+str(frame), (10, 50), font, 2, (0, 0, 0), 2)
        

        try:
            output = open("camera_process/prediction","r")
            label = out = int(output.read())
            output.close()
        except:
            print("prediction not avaliable")


        # label = cameraProcess.predictFrame(frame)

        # if out == 3:
        #     cv2.putText(output_image,"Good situp", (10, 80), font, 2, (0, 0, 0), 2)
        # elif out == 4:
        #     cv2.putText(output_image,"Bad situp", (10, 80), font, 2, (0, 0, 0), 2)
        # else:
        #     cv2.putText(output_image,"None", (10, 80), font, 2, (0, 0, 0), 2)

        cv2.putText(output_image,str(label), (10, 80), font, 2, (0, 0, 0), 2)


        cv2.imshow('Human Pose Estimation',output_image)

        frame+=1
        key = cv2.waitKey(1)
        if key==ord('q'):
                break

    stream.release()
    cv2.destroyAllWindows()

# import cameraProcess

if __name__ == '__main__':
    pose()
