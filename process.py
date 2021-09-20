import os
import sys
import shutil

exercises = ["pushup","pushup-bad","pushup-bad2","situp","situp-bad","situp-bad2","situp-bad3","squat","squat-bad"]
lookup = {"other":0,"pushup":1,"pushup-bad":2,"pushup-bad2":3,"situp":4,"situp-bad":5,"situp-bad2":6,"situp-bad3":7,"squat":8,"squat-bad":9}
typeLookup = {"pushup":["pushup","pushup-bad", "pushup-bad2"],"situp":["situp","situp-bad","situp-bad2","situp-bad3"],"squat":["squat","squat-bad"]}

# from body_25 https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/02_output.md
interest = [
            [i for i in range(25)],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 13, 14],
            [0, 2, 3, 5, 6],
            [0, 1, 2, 3, 5, 6],
            [0, 1, 2, 3, 5, 6, 8, 10, 13],
            [0, 2, 3, 5, 6, 9, 10, 13],
            [0, 2, 3, 5, 4, 7, 8],
            [0, 2, 3, 5, 4, 7, 9],
            [0, 2, 3, 5, 4, 7, 12]
            # [0]
            ]

models = [[] for _ in interest]



for dir in os.listdir("to_process/"):
    if not ".csv" in dir:
        outFile = "to_process/"+dir
        fA = open(outFile+"raw.csv", "w")
        fN = open(outFile+"normalized.csv", "w")
        # fX = open(outFile+"Xraw.csv", "w")
        # fY = open(outFile+"Yraw.csv", "w")
        # exercises = {"pushup":1, "situp":2}
        # exercises = {"pushup":1, "situp":2, "camera":-1}
        files = os.listdir("to_process/"+dir+"/")
        if 'ben-pushup' in files:
            print(files, dir)
        #for x in files:
        #    print(x)
        #    print(int(x.split("_")[0]))
        fileInts = [int(x.split("_")[0]) for x in files]
        fileInts.sort()
        files = [str(x)+"_keypoints.json" for x in fileInts]
        # print(files)
        last = ""
        last2 = ""
        outputY = open("videos/"+dir+".info", "r").read()
        for fileName in files:
            with open("to_process/"+dir+"/"+fileName, "r") as f:
                data = eval(f.read())
                if (len(data["people"]) == 1):
                    last = ""
                    last2 = ""
                    lastStart = [0, 0]
                    lastScale = [1, 1]
                    outputX = data["people"][0]["pose_keypoints_2d"]
                    for i in range(len(outputX)):
                        if (i-2)%3 != 0:
                            # if outputX[0] == outputX[1] == 0:
                            #     outputX[0], outputX[1] = lastStart[0], lastStart[1]
                            # if outputX[24] == outputX[25] == 0:
                            #     outputX[24], outputX[25] = lastScale[0], lastScale[1]
                            # if outputX[24] == outputX[0]:
                            #     outputX[24], outputX[0] = outputX[24], outputX[0]+1
                            # if outputX[25] == outputX[1]:
                            #     outputX[25], outputX[1] = outputX[25], outputX[1]+1
                            out = outputX[i]
                            fA.write(str(int(out)))
                            if i%3 == 0:
                                fN.write(str(int( (int(out))*50/(50))))
                                last2 += str(int( (int(out))*50/(50)))
                                # fN.write(str(int( (int(out)-int(outputX[0]))*50/(50))))
                                # last2 += str(int( (int(out)-int(outputX[0]))*50/(50)))
                                # fN.write(str(int( (int(out)-int(outputX[0]))*50/(outputX[24]-outputX[0]))))
                                # last2 += str(int( (int(out)-int(outputX[0]))*50/(outputX[24]-outputX[0])))
                            elif i%3 == 1:
                                fN.write(str(int( (int(out))*50/(50) )))
                                last2 += str(int( (int(out))*50/(50) ))
                                # fN.write(str(int( (int(out)-int(outputX[1]))*50/(50) )))
                                # last2 += str(int( (int(out)-int(outputX[1]))*50/(50) ))
                                # fN.write(str(int( (int(out)-int(outputX[1]))*50/(outputX[25]-outputX[1]) )))
                                # last2 += str(int( (int(out)-int(outputX[1]))*50/(outputX[25]-outputX[1]) ))
                            last += str(int(out))
                            # fX.write(str(int(out)))
                            # print(str(int(out))+",", end="")
                            fA.write(",")
                            # fA.write(",")
                            if i != len(outputX)-2:
                                fN.write(",")
                                last2+=","
                            lastStart[0], lastStart[1] = outputX[0], outputX[1]
                            lastScale[0], lastScale[1] = outputX[24], outputX[25]

                    fA.write(str(outputY)+"\n")
                    fN.write("\n")
                    # fY.write(str(exercises[outputY])+"\n")
                    # fX.write("\n")
                    # print(outputY)
                else:
                    fA.write(str(last)+","+outputY+"\n")
                    fN.write(str(last2)+"\n")


fileExercises = [[] for _ in range(len(exercises))]


for filename in os.listdir("videos/"):
    if ".info" in filename:
        with open("videos/"+filename, "r") as f:
            fileExercises[exercises.index(f.read().strip())].append(filename.split(".info")[0])

fullDiff = []
for elist in fileExercises:
    first = []
    last = []
    for file in elist:
        with open("videos/"+file+".label") as f:
            data = f.read().splitlines()
            for i in range(0,len(data)-1,2):
                line = data[i]
                line2 = data[i+1]
                first.append(int(line))
                last.append(int(line2))
    diff = []
    for i in range(len(first)):
        diff.append(last[i]-first[i])
    fullDiff.append(round(sum(diff)/len(diff)))

fullFirsts = [[] for _ in range(len(exercises))]
for i in range(len(fileExercises)):
    elist = fileExercises[i]
    for j in range(len(elist)):
        file = elist[j]
        first = []
        with open("videos/"+file+".label") as f:
            data = f.read().splitlines()
            # print(data)
            for k in range(0,len(data)-1,2):
                line = data[k]
                first.append(int(line))
        # print(fullFirsts, i)
        fullFirsts[i].append(first)



# for i in range(0,len(fullDiff),2):
#     fullDiff[i+1] = fullDiff[i] = round((fullDiff[i]+fullDiff[i+1])/2)
# print(fullDiff)

for key in typeLookup:
    sum = 0
    num = len(typeLookup[key])
    for entry in typeLookup[key]:
        sum += fullDiff[exercises.index(entry)]
    for entry in typeLookup[key]:
        fullDiff[exercises.index(entry)] = round(sum/num)

print(fullDiff)

def step2():
    # print(fullDiff, fullFirsts)
    # for i in fullFirsts:
    #     print(i)
    f = open("processed_data/lengths","w")
    f.write(str(fullDiff)+"\n")
    f.write(str(exercises)+"\n")
    f.write(str(lookup)+"\n")
    f.write(str(fileExercises)+"\n")
    f.write(str(typeLookup)+"\n")
    f.write(str(interest))
    f.close()
    # print(fileExercises)
    for key in typeLookup:
        fX = []
        fY = []
        for i in range(len(interest)):
            fX.append(open("processed_data/"+key+str(i)+"TrainX.csv", "w"))
            fY.append(open("processed_data/"+key+str(i)+"TrainY.csv", "w"))
        for exercise in typeLookup[key]:
            i = exercises.index(exercise)
            exercise = exercises[i]
            # exerciseBad = exercises[i+1]
            for j in range(len(fileExercises[i])):
                file = fileExercises[i][j]
                spliced = []
                with open("to_process/"+file+"normalized.csv","r") as f:
                    data = f.read().splitlines()
                    for k in range(len(data)):
                        data[k] = data[k].split(",")
                    print(file, fullFirsts[i][j],fullDiff[i], i, j)
                    for k in range(0,len(fullFirsts[i][j])):
                        first = fullFirsts[i][j][k]
                        spliced.append(data[first:first+fullDiff[i]])
                splicedLines = spliced
                for spliced in splicedLines:
                    for k in range(len(interest)):
                        set = interest[k]
                        works = True
                        for line in spliced:
                            # print("start")
                            zeroes = 0
                            for id in set:
                                # print(line[2*id], line[2*id+1])
                                if not (line[2*id] != '0' and line[2*id+1] != '0'):
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
                                    if (line[2*id] == '0' and line[2*id+1] == '0'):
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
                            models[k].append(tmp)
                            # print(exercise, tmp)
                            for line in tmp:
                                for l in range(len(line)):
                                    line[l] = str(line[l])
                            # print("LEN",len(spliced),len(tmp), len(tmp[0]), set)
                            outLine = ",".join([",".join(line) for line in tmp])
                            # print(exercise,outLine)
                            fX[k].write(outLine+"\n")
                            fY[k].write(str(lookup[exercise])+"\n")
        for file in fX+fY:
            file.close()


    for i in range(len(models)):
        if models[i] == []:
            interest[i] = []

    while [] in interest:
        interest.remove([])
        step2()

step2()


                # print(len(data))
                    # print(data[first:fullDiff[i]], fullFirsts[i][j], k)
        # print(spliced)
        # for j in range(len(spliced)):
        #     data = spliced[j]
        #     strline = ",".join(data)
        #     fX.write(strline+"\n")  
        #     fY.write(str(lookup[exercise])+"\n")    
        
# for model in models:
#     print(model)


    # spliced = []
    # for j in range(len(fileExercises[i+1])):
    #     file = fileExercises[i+1][j]
    #     with open("to_process/"+file+"normalized.csv","r") as f:
    #         data = f.read().splitlines()
    #         # print(len(data))
    #         print(file, fullFirsts[i+1][j],fullDiff[i], i+1, j)
    #         for k in range(0,len(fullFirsts[i+1][j])):
    #             first = fullFirsts[i+1][j][k]
    #             spliced.append(data[first:first+fullDiff[i+1]])
    #             # print(data[first:fullDiff[i]], fullFirsts[i][j], k)
    # # print(spliced)
    # for j in range(len(spliced)):
    #     data = spliced[j]
    #     strline = ",".join(data)
    #     fX.write(strline+"\n")  
    #     fY.write(str(lookup[exerciseBad])+"\n")   

    # for exercise1 in exercises:
    #     if exercise1 != exercise and exercise1 != exerciseBad:
    #         spliced = []
    #         for j in range(len(fileExercises[exercises.index(exercise1)])):
    #             file = fileExercises[exercises.index(exercise1)][j]
    #             with open("to_process/"+file+"normalized.csv","r") as f:
    #                 data = f.read().splitlines()
    #                 # print(len(data))
    #                 # print(file, j, fullFirsts[exercises.index(exercise1)])
    #                 print(file, fullFirsts[exercises.index(exercise1)][j],fullDiff[i], i, j)
    #                 for k in range(0,len(fullFirsts[exercises.index(exercise1)][j])):
    #                     first = fullFirsts[exercises.index(exercise1)][j][k]
    #                     spliced.append(data[first:first+fullDiff[i]])
    #                     # print(data[first:fullDiff[i]], fullFirsts[i][j], k)
    #         # print(spliced)
    #         for j in range(len(spliced)):
    #             data = spliced[j]
    #             strline = ",".join(data)
    #             fX.write(strline+"\n")  
    #             fY.write(str(lookup["other"])+"\n")    
