import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer

#nltk.download('punkt')

stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]

def normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')

def get_similarity(text1, text2):
    tfidf = vectorizer.fit_transform([text1, text2])
    return abs(((tfidf * tfidf.T).A)[0,1])

'''
Keywords file: Txt file of all the keywords, 
Questions_file: CSV file of question output format, 
output_folder: Folder to save the ouput txt file in
'''

def process_files(keywords_file, questions_file, output_file):
    matcher = {}
    with open(keywords_file, 'r') as keywords_reader:
        lines = keywords_reader.readlines()[1:]
        for line in lines:
            word = line[line.index(':') + 1 : ].strip()
            matcher[word] = []
    with open(questions_file, 'r') as questions_reader:
        lines = questions_reader.readlines()[1:]
        for line in lines:
            line = line.replace("\"", "")
            line = line.replace(".", "")
            original = line[ : line.index(',')].strip()
            sentence = original
            best_keyword = "None"
            highest_similarity = 0
            for keyword in matcher:
                score = get_similarity(sentence, keyword)
                if(score > highest_similarity):
                    highest_similarity = score
                    best_keyword = keyword
            if(highest_similarity != 0):
                matcher[best_keyword].append(original)
    with open(output_file, 'w+') as writer:
        for keyword in matcher:
            writer.write(str(keyword) + "\n")
            for sentence in matcher[keyword]:
                writer.write("\t" + str(sentence) + "\n")
