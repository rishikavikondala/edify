def get_message(arr):
    start = arr[3][1:]
    i = 3
    while i < len(arr)-1:
        start += arr[i]
        i += 1
    return start

def chat_to_audio(inputFile, outputFile):
    new_file = open(outputFile, "w+")
    new_file.write("WEBVTT")
    a_file = open(inputFile, "r")
    lines = a_file.readlines()

    count = 1
    firstHour = 0
    firstMinute = 0
    firstSecond = 0

    new_file.write("\n")
    for line in lines:
        new_file.write("\n")
        new_file.write(str(count) + "\n")
        if(count == 1):
            firstHour = int(line[0:2])
            firstMinute = int(line[3:5])
            firstSecond = int(line[6:8])

            print(firstHour)
            print(firstMinute)
            print(firstSecond)

        thisHour = int(line[0:2])
        thisMinute = int(line[3:5])
        thisSecond = int(line[6:8])

        hourDiff = thisHour - firstHour
        if (hourDiff < 0):
            hourDiff += 24
        minuteDiff = thisMinute - firstMinute
        if (minuteDiff < 0):
            minuteDiff += 60
        secondDiff = thisSecond - firstSecond
        if (secondDiff < 0):
            secondDiff += 60

        timeString = str(hourDiff) + ":" + str(minuteDiff) + ":" + str(secondDiff)
        new_file.write(timeString + " --> " + timeString + "\n")


        splitColon = line.split("\t")
        #print(splitColon)
        name = splitColon[1]
        message = splitColon[2]
        #print(message)

        new_file.write(name + ": " + message)
        count += 1


