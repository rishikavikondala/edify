import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def num_times_in(arr, x):
    num = 0
    for i in arr:
        if (i == x):
            num += 1

    return num

def questionTime(inputFile, outputFile, isChat):
    clean_transcript = pd.read_csv(inputFile)
    values = clean_transcript["TIME"].tolist()

    time_ints = []
    for value in values:
        split = value.split(":")
        hours = int(split[0])
        minutes = int(split[1])
        seconds = float(split[2])
        time_ints.append((hours*60) + minutes + (seconds//60))

    print(time_ints)

    x_values = np.arange(0, time_ints[len(time_ints)-1]+1)
    y_values = []

    for i in x_values:
        y_values.append(num_times_in(time_ints, i))

    print(y_values)

    plt.plot(x_values, y_values)
    plt.xlabel('Time since start of recording (minutes)')
    plt.ylabel('Number of Questions')
    if (isChat):
        plt.title("Number of Questions over Time from Chat")
    else:
        plt.title("Number of Questions over Time from Audio Transcript")

    #plt.show()
    plt.savefig(outputFile)
    plt.clf()
