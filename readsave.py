#from tensorflow import keras
import numpy as np
import keras
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

f = open("processed_data/lengths","r")
l = f.read().splitlines()
exercises = eval(l[1])
lookup = eval(l[2])
lengths = eval(l[0])
fileExercises = eval(l[3])

# datafile = sys.argv[1]

for file in os.listdir("test_data"):
    if "X.csv" in file:
        filename = file.split("X.csv")[0]
        id = int(filename.split("test")[1])
        length = lengths[id]

        exercise = exercises[id]

        namesList = []
        for i in range(length*25):
            namesList.append("X"+str(i))
            namesList.append("Y"+str(i))
        
        datafile = filename

        x_data = pd.read_csv("test_data/"+datafile+"X.csv",names=namesList,na_values=0)
        x_data.fillna(0,inplace=True)
        y_dataR = np.genfromtxt("test_data/"+datafile+"Y.csv",delimiter=',',dtype=int)
        num_classes = np.max(y_dataR) + 1
        y_data = keras.utils.to_categorical(y_dataR, num_classes)
        #x_train, x_test, y_train, y_test = train_test_split(x_data,y_data, test_size=0.20, random_state=0)
        #x_train = x_data[:880]
        x_test = x_data
        #y_train = y_data[:880]
        y_test = y_data
        #x_train.shape,y_train.shape,x_test.shape,y_test.shape

        model = keras.models.load_model("processed_data/"+exercise+'modelSave')
        # print(model.summary())
        print(exercise)
        #print('Training Accuracy : ' , np.mean(model.history["accuracy"]))
        #print('Validation Accuracy : ' , np.mean(model.history["val_accuracy"]))
        y_pred = model.predict(x_test)
        #print(x_test)
        #y_pred = model.predict(np.array([[400,400,400,400,400]]*50))
        rounded = [np.argmax(x) for x in y_pred]
        # for y in y_pred:
        #     print(y)
        y_testComp = [np.argmax(x) for x in y_test]
        print(confusion_matrix(y_testComp,rounded))