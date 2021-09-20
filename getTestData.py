f = open("processed_data/lengths","r")
l = f.read().splitlines()
exercises = eval(l[1])
lookup = eval(l[2])
lengths = eval(l[0])
fileExercises = eval(l[3])

for i in range(0,len(lengths),2):
    fX = open("test_data/test"+str(i)+"X.csv", "w")
    fY = open("test_data/test"+str(i)+"Y.csv", "w")
    for j in range(len(fileExercises)):
        fileSet = fileExercises[j]
        for filename in fileSet:
            f = open("to_process/"+filename+"normalized.csv","r")
            data = f.read().splitlines()
            for k in range(len(data)-lengths[i]):
                spliced = data[k:k+lengths[i]]
                # print(spliced)
                for l in range(len(spliced)):
                    data = spliced
                    # print(data)
                    strline = ",".join(data)
                    fX.write(strline+"\n")  
                    val = lookup[exercises[j]]
                    if i == 0 and val >= 3:
                        val = 0
                    if i == 2 and val <= 2:
                        val = 0
                    fY.write(str(val)+"\n")   

