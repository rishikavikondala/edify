'''
input_file: The raw vtt file from the audio call transcript
output_file: The file to store the formatted version of the transcript
'''

def clean_audio_transcript(input_file, output_file): 
    a_file = open(input_file, "r")
    lines = a_file.readlines()
    a_file.close()
    counter = 1
    new_file = open(output_file, "w+")
    number = False
    lines[0] = "QUERY\n"
    for line in lines:
        try:
            if (number):
                number = False
            elif (int(line) == counter):
                number = True
                counter = counter + 1
        except ValueError:
            if (":" in line):
                ind = line.index(':') + 2
                length = len(line)
                line = line[ind:len(line)]
            new_file.write(line)
            number = True
    new_file.close()

#clean_audio_transcript() -> identify_questions() -> generate_topics -> process_files()