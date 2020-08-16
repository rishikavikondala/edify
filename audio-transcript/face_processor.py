import cv2
import numpy as np
import glob
from scipy.spatial import distance
from imutils import face_utils
from keras.models import load_model 
import tensorflow as tf
import time
from fr_utils import *
from inception_blocks_v2 import *
import os
from imutils.face_utils import FaceAligner
import shutil
from threading import Thread
import matplotlib.pyplot as plt

refresh = False
FR_model = load_model('nn4.small2.v1.h5')
face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')

def get_previous(data, index):
	return data[max(0, index - 1)]

def write_range_file(tracker, acceptable, frames_processed, folder_to_write): 
	lines = []
	for name in tracker: 
		data = tracker[name]
		percentage = int((100.0 * len(data))/frames_processed)
		intro = str(name) + "(" + str(percentage) + ")"
		lines.append(intro)
		index = 0
		while(index < len(data)): 
			range_start = data[index]
			index += 1
			while(index < len(data) and (data[index] - get_previous(data, index)) <= acceptable):
				index += 1
			range_end = get_previous(data, index)
			sentence = "\t" + str(range_start) + "," + str(range_end)
			lines.append(sentence)
	file_path = os.path.join(folder_to_write, 'focus_ranges.txt')
	with open(file_path, 'w+') as writer: 
		writer.write('\n'.join(lines) + '\n')
	return file_path


def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print('\n' * 2)

'''File_path: The location of the video file to process
folder_to_read_from: The location of the images file
folder_to_write: Folder to write the output graph and file too'''

def process_video(file_path, folder_to_read_from, folder_to_write, start_time = 0.5, gap_time = 0.25, debug = False, save = True):
	if not os.path.exists(folder_to_write): 
		os.mkdir(folder_to_write)

	threshold = 0.5
	face_database = {}
	return_value = -1
	pause = False
	tracker = {}

	for image in os.listdir(folder_to_read_from):
			identity = os.path.splitext(os.path.basename(image))[0]
			face_database[identity] = img_path_to_encoding(os.path.join(folder_to_read_from,image), FR_model)
			tracker[identity] = [0.0]

	video_capture = cv2.VideoCapture(file_path) 
	current_time = start_time
	total_frames = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
	fps = video_capture.get(cv2.CAP_PROP_FPS)
	complete_video_length = total_frames/(60.0 * fps)
	frames_processed = 0

	while (current_time <= complete_video_length):
		current_time_ms = int(current_time * 1000 * 60)
		video_capture.set(cv2.CAP_PROP_POS_MSEC, current_time_ms)
		ret, frame = video_capture.read()
		if not ret:
			print("Reached end of file")
			break

		selected = []

		faces = face_cascade.detectMultiScale(frame, 1.3, 5)
		for(x,y,w,h) in faces:
			roi = frame[y:y+h, x:x+w]
			encoding = img_to_encoding(roi, FR_model) #Run image through neural networks
			min_dist = 100
			identity = None

			for(name, encoded_image_name) in face_database.items():
				dist = np.linalg.norm(encoding - encoded_image_name) #Get euclidean distance between face in frame and known people
				if(dist < min_dist):
					min_dist = dist
					identity = name

			if (min_dist < threshold and identity not in selected): 
				cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
				cv2.putText(frame, str(identity), (int(x - 25), int(y - 10)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0), 1)
				selected.append(identity)
				tracker[identity].append(current_time)

		if(debug):
			printProgressBar(current_time, complete_video_length)
			cv2.imshow('Face Recognition System', frame) 
			actual_reading = cv2.waitKey(1) & 0xFF
			if(actual_reading == ord('q')):
				print("User Requested quit")
				break
		
		current_time += gap_time
		frames_processed += 1
		
	video_capture.release()
	range_file = "None"
	if(save):
		range_file = write_range_file(tracker, 2 * gap_time, frames_processed, folder_to_write)
		print("Wrote ranges file")
		draw_graph(range_file, folder_to_write, start_time, gap_time, complete_video_length, debug)
		print("Saved Attention Graph")

	cv2.destroyAllWindows() 

	return tracker

def in_range(data, timestamp): 
	index = 0
	while(index < len(data)): 
		cover = data[index]
		if(timestamp >= cover[0] and timestamp <= cover[1]): 
			return True
		if(timestamp < cover[1]): 
			break
		index += 1
	return False

def draw_graph(file_name, folder_to_write, current_time, gap_time, end_time, debug): 
	values = {}
	with open(file_name, 'r') as reader: 
		lines = reader.readlines()
		index = 0
		while(index < len(lines)): 
			intro = lines[index] 
			if '(' not in intro: 
				index += 1
				continue
			name = intro[:intro.index('(')].strip()
			values[name] = []
			index += 1
			while(index < len(lines) and '\t' in lines[index]): 
				line = lines[index]
				line = line[line.index('\t') + 1 : ].strip()
				parts = line.split(',')
				start_range, end_range = float(parts[0]), float(parts[1])
				values[name].append((start_range, end_range))
				index += 1
	x_values = []
	y_values = []
	while(current_time <= end_time): 
		x_values.append(current_time)
		count = 0 
		for name in values: 
			if(in_range(values[name], current_time)): 
				count += 1
		percentage = int((100.0 * count)/len(values))
		y_values.append(percentage)
		current_time += gap_time
	plt.plot(x_values, y_values, color = 'blue')
	plt.scatter(x_values, y_values, color = 'red', s = 20)
	plt.xlabel('Time since start of recording (minutes)')
	plt.ylabel('Percentage paying attention')
	plt.title("Class Attentivenes over time")
	plt.savefig(os.path.join(folder_to_write, "Attention.png"))
	if(debug):
		plt.show()
	plt.clf()

if __name__ == "__main__":
	gap_time = 0.25
	current_time = 0.5
	#Path to file, Path to images, output folder
	process_video("GMT20200812-040149_Rishi-Kavi_gallery_1280x720.mp4", 'People', 'output')
	