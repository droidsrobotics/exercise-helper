import os
import sys
import cv2
from poseDetection import *
import platform
import shutil


for filename in os.listdir("videos/"):
    if ".mp4" in filename and not "hflip" in filename and not os.path.exists("videos/"+filename.split(".mp4")[0]+"hflip.mp4"):
        name = filename.split(".mp4")[0]
        shutil.copyfile("videos/"+name+".info", "videos/"+name+"hflip.info")
        shutil.copyfile("videos/"+name+".label", "videos/"+name+"hflip.label")
        os.system("ffmpeg -i videos/"+name+".mp4 -vf hflip -c:a copy videos/"+name+"hflip.mp4")



# video = sys.argv[1]
# label = sys.argv[2]

if platform.uname()[4] == "aarch64":
    pose = posenet()
elif platform.uname()[4] == "x86_64":
    pose = openPose()
else:
    pose = None

#Constructing OpenPose object allocates GPU memory

#Opening OpenCV stream

for file in os.listdir("videos"):
    if ".mp4" in file:
        # and not os.path.exists("to_process/"+file.split(".mp4")[0]):
        stream = cv2.VideoCapture("videos/"+file)
        label = file.split(".mp4")[0]

        pose.config(dir="to_process/"+label)

        frame = 0
        try:
            while True:
                font = cv2.FONT_HERSHEY_SIMPLEX

                ret,img = stream.read()
                img = cv2.resize(img, (640, 480))


                output_image, _ = pose.process(img)

                # Display Image
                # print("Body keypoints: " + str(datum.poseKeypoints))
                # print(datum)
                font=cv2.FONT_HERSHEY_PLAIN

                cv2.putText(output_image,"Frame: "+str(frame), (10, 50), font, 2, (0, 0, 0), 2)
                # print("Left hand keypoints: " + str(datum.handKeypoints[0]))
                # print("Right hand keypoints: " + str(datum.handKeypoints[1]))
                # Display the stream
                cv2.imshow('Human Pose Estimation',output_image)
                frame+=1
                key = cv2.waitKey(1)
                if key==ord('q'):
                        break
        except Exception as e:
            print(e)
        stream.release()
        #cv2.destroyAllWindows()
