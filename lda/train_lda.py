# Trains and saves an LDA model with the given text files.

from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
import glob
import string
import numpy as np


whitelist = string.letters + string.digits + ' '
instagram_text_data_path = '../../../datasets/SocialMedia/captions_resized_1M/cities_instagram/'
model_path = '../../../datasets/SocialMedia/models/LDA/lda_model_cities_instagram_1M_500_5000chunck.model'
words2filter = ['rt','http','t','gt','co','s','https','http','tweet','markars_','photo','pictur','picture','say','photo','much','tweet','now','blog']

cities = ['london','newyork','sydney','losangeles','chicago','melbourne','miami','toronto','singapore','sanfrancisco']

num_topics = 400
threads = 8
passes = 1 #Passes over the whole corpus
chunksize = 5000 #Update the model every 10000 documents
# See https://radimrehurek.com/gensim/wiki.html
update_every = 1

repetition_threshold = 20

#Initialize Tokenizer
tokenizer = RegexpTokenizer(r'\w+')
# create English stop words list
en_stop = get_stop_words('en')
# add own stop words
for w in words2filter:
    en_stop.append(w)
# Create p_stemmer of class PorterStemmer
p_stemmer = PorterStemmer()

posts_text = []
texts = [] #List of lists of tokens

# -- LOAD DATA FROM INSTAGRAM --
for city in cities:
    print "Loading data from " + city
    for file_name in glob.glob(instagram_text_data_path + city + "/*.txt"):
        caption = ""
        filtered_caption = ""
        file = open(file_name, "r")
        for line in file:
            caption =  caption + line

        # Replace hashtags with spaces
        caption = caption.replace('#', ' ')
        # Keep only letters and numbers
        for char in caption:
            if char in whitelist:
                filtered_caption += char

        posts_text.append(filtered_caption.decode('utf-8').lower())


print "Number of posts: " + str(len(posts_text))

print "Creating tokens"
c= 0

for t in posts_text:

    c += 1
    if c % 10000 == 0:
        print c

    try:
        t = t.lower()
        tokens = tokenizer.tokenize(t)
        # remove stop words from tokens
        stopped_tokens = [i for i in tokens if not i in en_stop]
        # stem token
        text = [p_stemmer.stem(i) for i in stopped_tokens]
        # add proceced text to list of lists
        texts.append(text)
    except:
        continue
    #Remove element from list if memory limitation TODO
    #del tweets_text[0]
posts_text = []

# Remove words that appear less than N times
print "Removing words appearing less than: " + str(repetition_threshold)
from collections import defaultdict
frequency = defaultdict(int)
for text in texts:
    for token in text:
        frequency[token] += 1
texts = [[token for token in text if frequency[token] > repetition_threshold] for text in texts]

# Construct a document-term matrix to understand how frewuently each term occurs within each document
# The Dictionary() function traverses texts, assigning a unique integer id to each unique token while also collecting word counts and relevant statistics.
# To see each token unique integer id, try print(dictionary.token2id)
dictionary = corpora.Dictionary(texts)
print(dictionary)
corpus = [dictionary.doc2bow(text) for text in texts]

texts = []

#Randomize training elements
corpus = np.random.permutation(corpus)


# Generate an LDA model
print "Creating LDA model"
 # the minimum_probability=0 argument is necessary in order for
# gensim to return the full document-topic-distribution matrix.  If
# this argument is omitted and left to the gensim default of 0.01,
# then all document-topic weights below that threshold will be
# returned as NaN, violating the subsequent LDAvis assumption that
# all rows (documents) in the document-topic-distribution matrix sum
# to 1.

#ldamodel = models.ldamodel.LdaModel(corpus, num_topics=num_topics, id2word = dictionary, passes=passes, minimum_probability=0)
ldamodel = models.LdaMulticore(corpus, num_topics=num_topics, id2word = dictionary, chunksize=chunksize, passes=passes, workers=threads, minimum_probability=0)
ldamodel.save(model_path)
# Our LDA model is now stored as ldamodel

print(ldamodel.print_topics(num_topics=8, num_words=10))

print "DONE"








