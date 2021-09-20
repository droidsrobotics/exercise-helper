import os
import sys
from PIL import Image
from PIL import ImageDraw
import numpy as np
import cv2
import requests
import socket
import struct
import threading

dir_path = os.path.dirname(os.path.realpath(__file__))

def flattenList(L):
    M = []
    for entry in L:
        if type(entry) == list:
            M.extend(flattenList(entry))
        else:
            M.append(entry)
    return M

class openPose(object):
    def __init__(self):
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

        self.op = op

    def config(self, dir=None):
        params = dict()
        if sys.platform == "win32":
            params["model_folder"] = "../models/"
        else:
            params["model_folder"] = "../../../models/"
        # os.mkdir(label)
        if dir != None:
            params["write_json"] = dir 

        self.opWrapper = self.op.WrapperPython()
        self.opWrapper.configure(params)
        self.opWrapper.start()
    
    def process(self, img):
        try:
            img = cv2.resize(img, (640, 480))
            datum = self.op.Datum()
            imageToProcess = img
            datum.cvInputData = imageToProcess
            # datum.handRectangles = handRectangles

            self.opWrapper.emplaceAndPop(self.op.VectorDatum([datum]))
            output_image = datum.cvOutputData
        except Exception as e:
            print(e)
        try:
            output = {"version":1.3,"people":[{"person_id":[-1],"pose_keypoints_2d":flattenList(datum.poseKeypoints[0].tolist()),"face_keypoints_2d":[],"hand_left_keypoints_2d":[],"hand_right_keypoints_2d":[],"pose_keypoints_3d":[],"face_keypoints_3d":[],"hand_left_keypoints_3d":[],"hand_right_keypoints_3d":[]}]}
        except:
            output = {"version":1.3,"people":[{"person_id":[-1],"pose_keypoints_2d":[],"face_keypoints_2d":[],"hand_left_keypoints_2d":[],"hand_right_keypoints_2d":[],"pose_keypoints_3d":[],"face_keypoints_3d":[],"hand_left_keypoints_3d":[],"hand_right_keypoints_3d":[]}]}

        return output_image, output

class posenet(object):
    toBody25 = {
        "NOSE":0,
        "LEFT_EYE":15,
        "RIGHT_EYE":16,
        "LEFT_EAR":17,
        "RIGHT_EAR":18,
        "LEFT_SHOULDER":2,
        "RIGHT_SHOULDER":5,
        "LEFT_ELBOW":3,
        "RIGHT_ELBOW":6,
        "LEFT_WRIST":4,
        "RIGHT_WRIST":7,
        "LEFT_HIP":9,
        "RIGHT_HIP":12,
        "LEFT_KNEE":10,
        "RIGHT_KNEE":13,
        "LEFT_ANKLE":11,
        "RIGHT_ANKLE":14
    }
    def __init__(self):
        from posenetCoral.pose_engine import PoseEngine
        self.PoseEngine = PoseEngine
        self.engine = PoseEngine(
        'posenetCoral/models/resnet/posenet_resnet_50_416_288_16_quant_edgetpu_decoder.tflite')
        #self.engine = PoseEngine('posenetCoral/models/resnet/posenet_resnet_50_640_480_16_quant_edgetpu_decoder.tflite')

    def config(self, dir=None):
        self.dir = dir
        self.frame = 0
        if dir != None:
            try:
                os.mkdir(dir)
            except:
                pass

    def process(self, img):
        img = cv2.resize(img, (416,288))
        pil_image = Image.fromarray(img)
        poses, inference_time = self.engine.DetectPosesInImage(pil_image)
        # for pose in poses:
        # print('\nPose Score: ', pose.score)
        points = [0]*(25*3)
        try:
            # print(1/inference_time)
            pose = poses[0]
            for label, keypoint in pose.keypoints.items():
                label = label.name
                #if pose.score < 0.4: break
                # print('  %-20s x=%-4d y=%-4d score=%.1f' %
                # (label.name, keypoint.point[0], keypoint.point[1], keypoint.score))
                x, y = int(keypoint.point[0]), int(keypoint.point[1])
                if keypoint.score < 0.05:
                    x, y = 0, 0
                points[3*posenet.toBody25[label]] = int(640*x/416)
                points[3*posenet.toBody25[label]+1] = int(480*y/288)
                points[3*posenet.toBody25[label]+2] = keypoint.score
                # points.append(int(640*x/416))
                # points.append(int(480*y/288))
                # points.append(keypoint.score)
                img = cv2.circle(img, (x,y), 5, (0, 0, 255), 5)        
        except Exception as e:
            pass
            # print(e)

        output = {"version":"posenet","people":[{"person_id":[-1],"pose_keypoints_2d":points,"face_keypoints_2d":[],"hand_left_keypoints_2d":[],"hand_right_keypoints_2d":[],"pose_keypoints_3d":[],"face_keypoints_3d":[],"hand_left_keypoints_3d":[],"hand_right_keypoints_3d":[]}]}

        if self.dir != None:
            f = open(self.dir+"/"+str(self.frame)+"_keypoints.json","w")
            f.write(str(output))
            f.close()
        self.frame+=1
        img = cv2.resize(img, (640,480))

        return img, output

class http(object):
    def __init__(self, ip="192.168.1.205", port=8000):
        self.addr = "http://"+ip+":"+str(port)
    
    def config(self, dir=None):
        self.frame = 0
        self.dir = dir
        if dir != None:
            try:
                os.mkdir(dir)
            except:
                pass

    def process(self, img):
        img = cv2.resize(img.copy(), (320, 240))
        _, data = cv2.imencode(".jpg", img)
        
        output = {"version":"posenet","people":[{"person_id":[-1],"pose_keypoints_2d":[0]*(25*3),"face_keypoints_2d":[],"hand_left_keypoints_2d":[],"hand_right_keypoints_2d":[],"pose_keypoints_3d":[],"face_keypoints_3d":[],"hand_left_keypoints_3d":[],"hand_right_keypoints_3d":[]}]}
        try:
            # print(1/inference_time)
            r = requests.post(
                url=self.addr,
                data=data.tobytes(),
                headers={'Content-Type': 'application/octet-stream'})

            #print(r.content.decode())
            output = eval(r.content.decode())
            points = output["people"][0]['pose_keypoints_2d']
            img = cv2.resize(img, (640, 480))

            for i in range(0, len(points), 3):
                x = int(points[i])
                y = int(points[i+1])
                # print(x,y)
                img = cv2.circle(img, (x,y), 5, (0, 0, 255), 5)    

        except Exception as e:
            # pass
            print(e)
            return None

        if self.dir != None:
            f = open(self.dir+"/"+str(self.frame)+"_keypoints.json","w")
            f.write(str(output))
            f.close()
        self.frame+=1

        return img, output

class rpiSend(object):
    def __init__(self, ip="192.168.1.168", camport=5000, port=8000):
        self.addr = sendIP = ip
        xdim = 640
        ydim = 480
        self.recvport = port
        self.out = cv2.VideoWriter('appsrc ! videoconvert ! video/x-raw,format=I420 ! omxh264enc ! video/x-h264,profile=baseline ! rtph264pay ! udpsink host='+sendIP+' port='+str(camport),cv2.CAP_GSTREAMER,0,30,(xdim,ydim),True);
        # self.sock = sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.addr2 = "http://"+ip+":"+str(port)
        self.output = {}

    def config(self, dir=None):
        b = threading.Thread(target=self.recvPose, daemon=True)
        b.start()
        self.frame = 0
        self.dir = dir
        if dir != None:
            try:
                os.mkdir(dir)
            except:
                pass

    def recvPose(self):
        while True:
            try:
                r = requests.post(
                    url=self.addr2,
                    data="".encode(),
                    headers={'Content-Type': 'application/octet-stream'})

                self.output = eval(r.content.decode())
            except Exception as e:
                print(e)

    def process(self, img):
        output = {"version":"posenet","people":[{"person_id":[-1],"pose_keypoints_2d":[0]*(75),"face_keypoints_2d":[],"hand_left_keypoints_2d":[],"hand_right_keypoints_2d":[],"pose_keypoints_3d":[],"face_keypoints_3d":[],"hand_left_keypoints_3d":[],"hand_right_keypoints_3d":[]}]}
        try:
            self.out.write(img)
            
            # data_len_str= self.cc_sock.recv( struct.calcsize("!I") )
            # data_len = (self.struct.unpack("!I", data_len_str))[0]
            # data = ""
            # while (data_len > 0):
            #    data += self.cc_sock.recv( data_len ).decode()
            #    data_len -= len(data)
            # print(data)

            output = self.output
            # output = eval(data)
            points = output["people"][0]['pose_keypoints_2d']
            # img = cv2.resize(img, (640, 480))

            # print(points)
            for i in range(0, len(points), 6):
                x = int(points[i])
                y = int(points[i+1])
                # print(x,y)
                img = cv2.circle(img, (x,y), 5, (0, 0, 255), 5)    

        except Exception as e:
            # pass
            print(e)
            return None

        if self.dir != None:
            f = open(self.dir+"/"+str(self.frame)+"_keypoints.json","w")
            f.write(str(output))
            f.close()
        self.frame+=1

        return img, output