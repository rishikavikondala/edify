import numpy as np

def clean_time_data(input_file, output_file):
    a_file = open(input_file, "r")
    lines = a_file.readlines()
    a_file.close()
    new_file = open(output_file, "w+")
    new_file.write("TIME\n")
    for line in lines:
        if ("-->" in line):
            arr = line.split(" ")
            new_file.write(arr[0]+"\n")

    new_file.close()
