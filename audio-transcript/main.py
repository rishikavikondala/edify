import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import requests
from requests.auth import HTTPBasicAuth
import matplotlib.pyplot as plt
from clean import clean_audio_transcript
from question_handler import identify_questions
from topic_model_questions import generate_topics
from text_similarity import process_files
from clean_time import clean_time_data
from questions_time import questionTime
from sentiment import sentimentMain
from convert_chat_to_audio_file import chat_to_audio
from face_processor import process_video
from em import send_email
from google.cloud import storage
import traceback

def download_file(input_folder, file_to_find, bucket_to_consider = 'zoom-files'): 
    input_folder += '/'
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_to_consider)
    to_read = None
    to_save = ""
    for blob in bucket.list_blobs(delimiter='/', prefix= input_folder):
        file_path = str(blob.name)
        last_index = file_path.rindex('/')
        file_name = file_path[last_index + 1 : ].strip()
        if(file_to_find in file_name): 
            to_read = blob
            to_save = file_name
            break
    lines = []
    if(to_read != None): 
        base_folder = '/tmp/' + input_folder 
        if not os.path.exists(base_folder): 
            os.mkdir(base_folder)
        dest_file = base_folder + to_save
        blob.download_to_filename(dest_file)
        return dest_file
    return 'None'

def download_pictures(input_folder, bucket_to_consider = 'zoom-files'): 
    input_folder += '/'
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_to_consider)
    base_folder = '/tmp/' + input_folder 
    if not os.path.exists(base_folder): 
        os.mkdir(base_folder)
    for blob in bucket.list_blobs(delimiter='/', prefix= input_folder):
        file_path = str(blob.name)
        last_index = file_path.rindex('/')
        file_name = file_path[last_index + 1 : ].strip()
        dest_file = base_folder + file_name
        blob.download_to_filename(dest_file)
    return base_folder

def get_sentence(path): 
    return str(path) + "," + str(os.path.exists(path)) + "\n"

def get_data(request):
    try:
        request_json = request.get_json(silent=True)
        if(request_json and 'folder_name' in request_json and 'email' in request_json):
            input_data = str(request_json['folder_name'])
            receiver = str(request_json['email'])
            people_folder = download_pictures('People')
            chat_path = download_file(input_data, 'chat')
            transcript_path = download_file(input_data, 'transcript')
            video_path = download_file(input_data, 'video')
            output_folder = '/tmp/output/'
            if not os.path.exists(output_folder): 
                os.mkdir(output_folder)
            formatted_chat_path = '/tmp/chat_as_audio.vtt'

            chat_to_audio(chat_path, formatted_chat_path)
            processing_chat_data(formatted_chat_path, output_folder)
            processing_transcript_data(transcript_path, output_folder)
            process_video(video_path, people_folder, output_folder)

            output_senti = os.path.join(output_folder, 'sentiment.png')
            sentimentMain(chat_path, output_senti)
            send_email(output_folder, receiver)
            return "200"
        return "404"
    except Exception as e:
        return str(traceback.format_exc())

def processing_transcript_data(input_file, output_folder): 
    transcript = input_file
    if not os.path.exists(transcript): 
        raise Exception(str(transcript) + " doesn't exist ")
    #clean transcript
    cleaned_transcript = "/tmp/cleaned_transcript.vtt"
    clean_audio_transcript(transcript, cleaned_transcript)
    cleaned_time_file = "/tmp/clean_time.vtt"
    clean_time_data(transcript, cleaned_time_file)
    #question classification
    output_file_advanced = os.path.join(output_folder, 'questionsAdvanced.csv')
    output_file_simple = os.path.join(output_folder, 'questionsSimple.csv')
    identify_questions(cleaned_transcript, cleaned_time_file, output_file_advanced, output_file_simple)
    #lda
    lda_file = os.path.join(output_folder, 'lda_transcript.txt')
    generate_topics(output_file_simple, lda_file)
    questionTimeInput = os.path.join(output_folder, 'questionsSimple.csv')
    questionTimeOutput = os.path.join(output_folder, 'questions_over_time_transcript.png')
    questionTime(questionTimeInput, questionTimeOutput, False)
    #questionTopicMatching
    combined_file = os.path.join(output_folder, 'questions_organized_transcript.txt')
    process_files(lda_file, output_file_simple, combined_file)

def processing_chat_data(input_file, output_folder): 
    if not os.path.exists(output_folder): 
        os.mkdir(output_folder)
    chat = input_file
    if not os.path.exists(chat): 
        raise Exception(str(chat) + " doesn't exist ")
    #clean transcript
    cleaned_transcript = "/tmp/cleaned_chat.vtt"
    clean_audio_transcript(chat, cleaned_transcript)
    cleaned_time_file = "/tmp/clean_chat_time.vtt"
    clean_time_data(chat, cleaned_time_file)
    #question classification
    output_file_advanced = os.path.join(output_folder, 'questionsAdvancedChat.csv')
    output_file_simple = os.path.join(output_folder, 'questionsSimpleChat.csv')
    identify_questions(cleaned_transcript, cleaned_time_file, output_file_advanced, output_file_simple)
    #lda
    lda_file = os.path.join(output_folder, 'lda_chat.txt')
    generate_topics(output_file_simple, lda_file)
    questionTimeInput = os.path.join(output_folder, 'questionsSimpleChat.csv')
    questionTimeOutput = os.path.join(output_folder, 'questions_over_time_chat.png')
    questionTime(questionTimeInput, questionTimeOutput, True)
    #questionTopicMatching
    combined_file = os.path.join(output_folder, 'questions_organized_chat.txt')
    process_files(lda_file, output_file_simple, combined_file)