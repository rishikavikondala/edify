from question_handler import questionDetector
import pandas as pd
import numpy as np
import warnings
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation as LDA
import re

'''
input_file: The file of questions we want to organize
output_file: The file where we want to store the different categories
'''
def generate_topics(input_file, output_file): 
    questions = pd.read_csv(input_file)
    #Remove Punctiation
    questions["text_processed"] = questions["QUERY"].map(lambda x : re.sub('[,\.!?]', '', x))
    #Concert to lowercase
    questions['text_processed'] = questions['text_processed'].map(lambda x: x.lower())
    # Initialise the count vectorizer with the English stop words
    count_vectorizer = CountVectorizer(stop_words='english')
    # Fit and transform the processed titles
    count_data = count_vectorizer.fit_transform(questions['text_processed'])
    #LDA
    warnings.simplefilter("ignore", DeprecationWarning)
    def print_topics(model, count_vectorizer, n_top_words):
        words = count_vectorizer.get_feature_names()
        str = ""
        for topic_idx, topic in enumerate(model.components_):
            str += ("\nTopic #%d:" % topic_idx)
            str += (" ".join([words[i]
                            for i in topic.argsort()[:-n_top_words - 1:-1]]))
        return str
    number_topics = 7
    number_words = 3
    # Create and fit the LDA model
    lda = LDA(n_components=number_topics, n_jobs=-1)
    lda.fit(count_data)
    # Print the topics found by the LDA model
    print("Topics found via LDA:")
    print(print_topics(lda, count_vectorizer, number_words))
    new_file = open(output_file, "w+")
    new_file.write("Topics found via LDA:")
    new_file.write(print_topics(lda, count_vectorizer, number_words))

