import os
import sys
import cv2
import numpy as np
import sys
import os

import time
from pymouse import PyMouse

m = PyMouse()

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
params["hand"] = True
# params["face_detector"] = 2
# params["hand_detector"] = 2
params["net_resolution"] = "-1x64"
# params["hand_net_resolution"] = "128x128"
# params["model_pose"] = "MPI_4_layers"
# params["disable_blending"] = True

# os.rmdir("camera_process/camera_raw")
# shutil.rmtree("camera_process/camera_raw", ignore_errors=True)

# params["write_json"] = "camera_process/camera_raw/" 

opWrapper = op.WrapperPython()
opWrapper.configure(params)
opWrapper.start()
#Opening OpenCV stream
stream = cv2.VideoCapture(0)
# stream = cv2.VideoCapture("videos/ben-situp.mp4")
stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
font = cv2.FONT_HERSHEY_SIMPLEX


def pose():
    frame = 0
    out = 4
    t = time.time()
    handPos = []
    while True:
        ret,img = stream.read()

        # img = cv2.resize(img, (640, 480))
        print("FPS:", 1/(time.time()-t))
        t = time.time()

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
        try:
            hand = datum.handKeypoints[1][0][8]
            handL = datum.handKeypoints[0][0][8]
            x = int(hand[0])
            y = int(hand[1])
            handPos.append((x,y))
            scale = 6
            m.move(scale*(640-x),scale*(480-y))
            xL = int(handL[0])
            yL = int(handL[1])
            print(xL, yL)
            if xL > 500 and yL > 400:
                print("click")
                m.press(scale*(640-x),scale*(480-y))
            else:
                m.release(scale*(640-x),scale*(480-y))
            print("Right hand keypoints: " , x, y)
            # for i in range(0,len(handPos)-1,2):
            #     (x,y) = handPos[i]
            #     (x2,y2) = handPos[i+1]
            #     output_image = cv2.line(output_image, (x,y), (x2,y2), (0, 0, 255), 1) 
        except:
            pass
        # Display the stream    

        # label = cameraProcess.predictFrame(frame)

        # if out == 3:
        #     cv2.putText(output_image,"Good situp", (10, 80), font, 2, (0, 0, 0), 2)
        # elif out == 4:
        #     cv2.putText(output_image,"Bad situp", (10, 80), font, 2, (0, 0, 0), 2)
        # else:
        #     cv2.putText(output_image,"None", (10, 80), font, 2, (0, 0, 0), 2)

        output_image=cv2.rotate(output_image, cv2.ROTATE_90_CLOCKWISE)
        output_image=cv2.rotate(output_image, cv2.ROTATE_90_CLOCKWISE)

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
