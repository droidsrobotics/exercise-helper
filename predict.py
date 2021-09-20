import numpy as np
from tensorflow import keras
# from keras.datasets import imdb
from tensorflow.keras.models import Sequential
# from keras.layers import LSTM
# from keras.layers.embeddings import Embedding
# from keras.preprocessing import sequence
from sklearn.metrics import confusion_matrix, precision_score
from sklearn.model_selection import train_test_split
# from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Dense,Dropout
from tensorflow.keras.regularizers import l2
# import matplotlib.pyplot as plt
import pandas as pd
import sys

# datafile = sys.argv[1]

f = open("processed_data/lengths","r")
l = f.read().splitlines()
exercises = eval(l[1])
lookup = eval(l[2])
lengths = eval(l[0])
typeLookup = eval(l[4])
interest = eval(l[5])

for key in typeLookup:
    i = exercises.index(key)
    exercise = exercises[i]
    length = lengths[i]
    
    for n in range(len(interest)):
        ids = interest[n]
        namesList = []
        print(ids, length)
        for i in range(length*len(ids)):
            namesList.append("X"+str(i))
            namesList.append("Y"+str(i))

        datafile = exercise+str(n)+"Train"

        x_data = pd.read_csv("processed_data/"+datafile+"X.csv",names=namesList,na_values=0)
        x_data.fillna(0,inplace=True)

        x_data.replace(np.nan,0)
        # y_dataR = pd.read_csv(datafile+"Y.csv",names=["id"])

        y_dataR = np.genfromtxt("processed_data/"+datafile+"Y.csv",delimiter=',',dtype=int)
        num_classes = np.max(y_dataR) + 1
        y_data = keras.utils.to_categorical(y_dataR, num_classes)
        #x_train, x_test, y_train, y_test = train_test_split(x_data,y_data, test_size=0.20, random_state=0)
        # x_train = x_data
        # x_test = x_data
        # y_train = y_data
        # y_test = y_data
        x_train, x_test, y_train, y_test = train_test_split(x_data, y_data, test_size = 0.4)
        # x_train.shape,y_train.shape,x_test.shape,y_test.shape

        #define a sequential Model
        model = Sequential()
        #Hidden Layer-1
        model.add(Dense(100,activation='relu',input_dim=length*len(ids)*2,kernel_regularizer=l2(0.01)))
        model.add(Dropout(0.3, noise_shape=None, seed=None))

        #Hidden Layer-2
        model.add(Dense(100,activation = 'relu',kernel_regularizer=l2(0.01)))
        model.add(Dropout(0.3, noise_shape=None, seed=None))

        #Output layer
        model.add(Dense(num_classes,activation='sigmoid'))
        model.compile(loss='binary_crossentropy',optimizer='adam',metrics=['accuracy'])
        # print(x_train)
        model_output = model.fit(x_train,y_train,epochs=300,batch_size=20,verbose=1,validation_data=(x_test,y_test),)
        model.save("processed_data/"+exercise+str(n)+'modelSave')

        print(model.summary())
        y_pred = model.predict(x_test)
        # for y in y_pred:
        #     print(y)
        #print(x_test)
        #y_pred = model.predict(np.array([[400,400,400,400,400]]*50))
        rounded = [np.argmax(x) for x in y_pred]

        y_testComp = [np.argmax(x) for x in y_test]
        print(confusion_matrix(y_testComp,rounded))
