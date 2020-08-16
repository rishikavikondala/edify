import re
import nltk.corpus
nltk.download('punkt')
nltk.download('nps_chat')
from nltk.corpus import nps_chat
import pandas as pand

class questionDetector():

    # Init constructor
    def __init__(self):
        posts = nltk.corpus.nps_chat.xml_posts()
        featureSet = self.getFeatureSet(posts)
        self.classifier = self.questionClassification(featureSet)

    def getFeatureSet(self, posts):
        featureList = []
        for post in posts:
            postText = post.text
            features = {}
            words = nltk.word_tokenize(postText)
            for word in words:
                features['contains({})'.format(word.lower())] = True
            featureList.append((features, post.get('class')))
        return featureList

    # Use NLTK's Multinomial Naive Bayes to perform classifcation
    # Print the Accuracy of the model
    # Return: Classifier object
    def questionClassification(self, featureSet):
        trainingSize = int(len(featureSet) * 0.1)
        trainSet, testSet = featureSet[trainingSize:], featureSet[:trainingSize]
        classifier = nltk.NaiveBayesClassifier.train(trainSet)
        print('Accuracy is : ', nltk.classify.accuracy(classifier, testSet))
        return classifier

    # Set of commonly occuring words in questions
    def questionFirstWord(self):
        questionWordList = ['what', 'where', 'when','how','why','which','did','do','is','can','have','will']
        return set(questionWordList)

    # Set of commonly occuring words in questions
    def questionWords(self):
        questionWordList = ['what', 'where', 'when','how','why','did','do','does','have','has','am','is','are','can','could','may','would','will','should'
"didn't","doesn't","haven't","isn't","aren't","can't","couldn't","wouldn't","won't","shouldn't",'?']
        return set(questionWordList)

    # Input: Sentence to be predicted
    # Return: 1 - If sentence is question | 0 - If sentence is not question
    def predictQuestion(self, sentence):
        lowerSentence = nltk.word_tokenize(sentence.lower())
        if (len(lowerSentence) > 3):
            firstWord = lowerSentence[0]
            if (firstWord in self.questionFirstWord()):
                return 1
        if self.questionWords().intersection(lowerSentence) == False:
            return 0
        if '?' in sentence:
            return 1

        features = {}
        for word in lowerSentence:
            features['contains({})'.format(word.lower())] = True

        predictionResult = self.classifier.classify(features)
        if predictionResult == 'whQuestion' or predictionResult == 'ynQuestion':
            return 1
        return 0

    # Input: Sentence to be predicted
    # 'WH' - If question is WH question
    # 'YN' - If sentence is Yes/NO question
    # 'unknown' - If unknown question type
    def predictQuestionType(self, sentence):
        lowerSentence = nltk.word_tokenize(sentence.lower())
        features = {}
        for word in lowerSentence:
            features['contains({})'.format(word.lower())] = True

        predictionResult = self.classifier.classify(features)
        if predictionResult == 'whQuestion':
            return 'WH'
        elif predictionResult == 'ynQuestion':
            return 'YN'
        else:
            return 'unknown'

'''
input_transcript: The VTT file representing the call transcript (call plus chat or just call)
output_file_advanced: The file to store the questions along with type of questions 
output_file_simple: The file to store just the questions wihtout information on the type 
'''
def identify_questions(input_transcript, time_data, output_file_advanced, output_file_simple):
    qDetector = questionDetector()
    clean_transcript = pand.read_csv(input_transcript, sep='\t')
    clean_time = pand.read_csv(time_data, sep='\t')
    d = {'QUERY': clean_transcript.loc[:, "QUERY"], 'TIME': clean_time.loc[:, "TIME"]}
    df1 = pand.DataFrame(data=d)
    df1['is_question'] = df1['QUERY'].apply(qDetector.predictQuestion)
    df1['question_type'] = df1[df1['is_question'] == 1]['QUERY'].apply(qDetector.predictQuestionType)
    df1.to_csv(output_file_advanced, index=False)
    df1 = df1[df1['is_question'] == 1]
    del df1['is_question']
    df1.to_csv(output_file_simple, index=False)