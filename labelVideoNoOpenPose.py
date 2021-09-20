import os
import sys
import cv2
import time

# #Setting OpenPose parameters

# video = sys.argv[1]
# label = sys.argv[2]


#Opening OpenCV stream
def increase_brightness(img, value=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img

for file in os.listdir("videos"):
    if not os.path.exists("videos/"+file.split(".mp4")[0]+".label") and ".mp4" in file:
        f = open("videos/"+file.split(".mp4")[0]+".label", "w")
        stream = cv2.VideoCapture("videos/"+file)
        font = cv2.FONT_HERSHEY_SIMPLEX
        frames = []
        label = True
        try:
            frame = 0
            paused = True
            while True:
                try:
                    ret,tmp = stream.read()
                    frames.append(tmp)
                except:
                    pass
                img = frames[frame]
                img = cv2.resize(img, (640, 480))
                # img = increase_brightness(img, value=40)

                # datum = op.Datum()
                imageToProcess = img
                output_image = img
                # datum.cvInputData = imageToProcess
                # datum.handRectangles = handRectangles

                # opWrapper.emplaceAndPop(op.VectorDatum([datum]))
                # output_image = datum.cvOutputData
                # Display Image
                # Display the stream
                font=cv2.FONT_HERSHEY_PLAIN

                cv2.putText(output_image,"Frame: "+str(frame), (10, 50), font, 2, (0, 0, 0), 2)
                cv2.putText(output_image,"Label: "+("start" if label else "end"), (10, 90), font, 2, (0, 0, 0), 2)

                # cv2.putText(img, str("CLICK ON " + thiscol), (10, 50), font, 2, (0, 0, 0), 2)
                cv2.imshow('Labeller',output_image)
                if not paused:
                    frame+=1
                key = cv2.waitKey(33)
                # print(key)
                if key==ord('q'):
                        break
                elif key==ord("d"):
                    frame+=1
                elif key==ord("a"):
                    frame-=1
                elif key==ord(" "):
                    paused = not paused
                elif key==ord("s"):
                    f.write(str(frame)+"\n")
                    label = not label


                # time.sleep(0.1)
        except Exception as e:
            print(e)
        f.close()
        stream.release()
    cv2.destroyAllWindows()