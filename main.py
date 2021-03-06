# -*- coding: utf-8 -*-
import csv
import io
import pickle
import re
import nltk
import random
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation
import numpy as np



def processTweet(tweet):
    # Convert to lower case
    tweet = tweet.lower()
    # Convert www.* or https?://* to URL
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)
    # Convert @username to AT_USER
    tweet = re.sub('@[^\s]+', 'AT_USER', tweet)
    # Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    # Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)

    # tweet = re.findall(r'[^,;\s]+',tweet)

    # try to split hashtag words
    # tweet = re.findall('#[A-Z][^A-Z]*',tweet)
    # tweet = ' '.join(tweet)

    tweet = re.sub('@[^/]+', ' ', tweet)

    # Remove numbers from string
    # tweet = re.sub(r'-?[0-9]', '', tweet)

    # trim
    tweet = tweet.strip('\'"')

    # drop text begin with '(@'
    tweet = re.sub('[(]', '', tweet)

    return tweet


def replaceTwoOrMore(s):
    # detect 2 or more repetitions of character and replace with the character itself
    pattern = re.compile(r"(.)\1+", re.DOTALL)
    return pattern.sub(r"\1\1", s)


def getStopWordList(stopWordListFileName):
    # read the stopwords
    stopWords = ['AT_USER', 'URL']

    fp = io.open(stopWordListFileName, 'r', encoding='utf-8')
    line = fp.readline()
    while line:
        word = line.strip()
        stopWords.append(word)
        line = fp.readline()
    fp.close()
    return stopWords


def getFeatureVector(tweet, stopWords):
    featureVector = []

    # remove , . from the tweets
    tweet = re.findall(r'[^,;\s]+', tweet)
    tweet = ' '.join(tweet)
    tweet = re.findall(r'[^.;\s]+', tweet)
    tweet = ' '.join(tweet)

    # remove ' from tweets
    # tweet = re.findall(r"^[^*$<,>?!']*$", tweet)
    # tweet = ' '.join(tweet)

    # split tweet into words
    words = tweet.split()
    for w in words:

        # replace two or more with two occurrences
        w = replaceTwoOrMore(w)
        # strip punctuation
        w = w.strip('\'"?,.')
        # check if the word stats with an turkish alphabet
        # val = re.search(r"^[a-zA-Z0-9ğüşöçİĞÜŞÖÇ]+$", w)

        # ignore if it is a stop word
        if w in stopWords:
            continue
        else:
            # print w
            featureVector.append(w.lower())
    return featureVector


def extract_features(tweet):
    tweet_words = set(tweet)
    features = {}
    for word in featureList:
        features['contains(%s)' % word] = (word in tweet_words)
    return features


stopWords = getStopWordList('stopWords.txt')

featureList = []
tweets = []
tempList = []
count = 0

with open('newData.csv', 'r', encoding='ISO-8859-9') as f:

    # Read the tweets one by one and process it
    reader = csv.reader(f, delimiter=';')
    for row in reader:
        tweet = row[0]  # tweet from csv file
        sentiment = row[1]  # sentiment of tweet from csv file

        processedTweet = processTweet(tweet)
        featureVector = getFeatureVector(processedTweet, stopWords)

        featureList.extend(featureVector)
        tweets.append((featureVector, sentiment))

length = int(len(tweets) * 0.90)
# random.shuffle(tweets)

training_tweets = tweets[:length]  # 90% to train
testing_tweets = tweets[length:]  # 10% to learn

del tweets

# Remove featureList duplicates
featureList = list(set(featureList))

# Extract feature vector for all tweets
training_set = nltk.classify.util.apply_features(extract_features, training_tweets)
testing_set = nltk.classify.util.apply_features(extract_features, testing_tweets)

total = 0
training_set1 = np.array(training_set)
LogisticRegression_classifier = SklearnClassifier(LogisticRegression())
cv = cross_validation.KFold(len(training_set1), n_folds=10, shuffle=True, random_state=None)
for traincv, testcv in cv:
    classifier = LogisticRegression_classifier.train(training_set1[traincv])
    print(nltk.classify.util.accuracy(classifier, training_set1[testcv]))
    total += nltk.classify.util.accuracy(classifier, training_set1[testcv])
print("CV Logistic Regression Average : ", total/10)

# Logistic Regression
LogisticRegression_classifier = SklearnClassifier(LogisticRegression())
LogisticRegression_classifier.train(training_set)


# Test the Logistic Regression classifier with one tweet
# testTweet = 'çekilmez bir adam oldum'
# processedTestTweet = processTweet(testTweet)
# print(testTweet + " ; ", (LogisticRegression_classifier.classify(extract_features(getFeatureVector(processedTestTweet, stopWords)))))

# test the classifier with tweets from the txt file
with open('testTweets.txt', encoding='ISO-8859-9') as f:
    data = f.readlines()
#
for counter in range(0, len(data)):
     a = data[counter]
     testTweet = ''.join(a)
     processedTestTweet = processTweet(testTweet)
     actualResult = LogisticRegression_classifier.classify(extract_features(getFeatureVector(processedTestTweet, stopWords)))
     with open('testResults.csv', 'a', encoding='ISO-8859-9')as csv_file:
         writer = csv.writer(csv_file, delimiter=';')

         writer.writerow([testTweet, actualResult])




# save_classifier = open("data/pickled_algos/LogisticRegressionclassifier.pickle", "wb")
# pickle.dump(LogisticRegression_classifier, save_classifier)
# save_classifier.close()

# print("Logistic Regression Accuracy Percent : ", (nltk.classify.accuracy(LogisticRegression_classifier, testing_set)) * 100)


total = 0
NBClassifier = nltk.NaiveBayesClassifier
cv = cross_validation.KFold(len(training_set1), n_folds=10, shuffle=True, random_state=None)
for traincv, testcv in cv:
    classifier = NBClassifier.train(training_set1[traincv])
    print(nltk.classify.util.accuracy(classifier, training_set1[testcv]))
    total += nltk.classify.util.accuracy(classifier, training_set1[testcv])
print("CV Naive Bayes Average : ", total/10)



total = 0
MNB_classifier = SklearnClassifier(MultinomialNB())
cv = cross_validation.KFold(len(training_set1), n_folds=10, shuffle=True, random_state=None)
for traincv, testcv in cv:
    classifier = MNB_classifier.train(training_set1[traincv])
    print(nltk.classify.util.accuracy(classifier, training_set1[testcv]))
    total += nltk.classify.util.accuracy(classifier, training_set1[testcv])
print("CV Multinomial Naive Bayes Average : ", total/10)


total = 0
BernoulliNB_classifier = SklearnClassifier(BernoulliNB())
cv = cross_validation.KFold(len(training_set1), n_folds=10, shuffle=True, random_state=None)
for traincv, testcv in cv:
    classifier = BernoulliNB_classifier.train(training_set1[traincv])
    print(nltk.classify.util.accuracy(classifier, training_set1[testcv]))
    total += nltk.classify.util.accuracy(classifier, training_set1[testcv])
print("CV Bernoulli Naive Bayes Average : ", total/10)


total = 0
LinearSVC_classifier = SklearnClassifier(LinearSVC())
cv = cross_validation.KFold(len(training_set1), n_folds=10, shuffle=True, random_state=None)
for traincv, testcv in cv:
    classifier = LinearSVC_classifier.train(training_set1[traincv])
    print(nltk.classify.util.accuracy(classifier, training_set1[testcv]))
    total += nltk.classify.util.accuracy(classifier, training_set1[testcv])
print("CV Linear SVC Average : ", total/10)


total = 0
SGDC_classifier = SklearnClassifier(SGDClassifier())
cv = cross_validation.KFold(len(training_set1), n_folds=10, shuffle=True, random_state=None)
for traincv, testcv in cv:
    classifier = SGDC_classifier.train(training_set1[traincv])
    print(nltk.classify.util.accuracy(classifier, training_set1[testcv]))
    total += nltk.classify.util.accuracy(classifier, training_set1[testcv])
print("CV SGDC Average : ", total/10)


total = 0
DecisionTree_Classifier = SklearnClassifier(DecisionTreeClassifier())
cv = cross_validation.KFold(len(training_set1), n_folds=10, shuffle=True, random_state=None)
for traincv, testcv in cv:
    classifier = DecisionTree_Classifier.train(training_set1[traincv])
    print(nltk.classify.util.accuracy(classifier, training_set1[testcv]))
    total += nltk.classify.util.accuracy(classifier, training_set1[testcv])
print("CV Decision Tree Average : ", total/10)


total = 0
RandomForest_Classifier = SklearnClassifier(RandomForestClassifier())
cv = cross_validation.KFold(len(training_set1), n_folds=10, shuffle=True, random_state=None)
for traincv, testcv in cv:
    classifier = RandomForest_Classifier.train(training_set1[traincv])
    print(nltk.classify.util.accuracy(classifier, training_set1[testcv]))
    total += nltk.classify.util.accuracy(classifier, training_set1[testcv])
print("CV Random Forest Average : ", total/10)




# # Write wrong tweets with keywords
# for counter in range(0, len(testing_tweets)):
#     a = (testing_tweets[counter][0])
#     sent = testing_tweets[counter][1]
#     testTweet = ' '.join(a)
#     processedTestTweet = processTweet(testTweet)
#     actualResult = LogisticRegression_classifier.classify(
#         extract_features(getFeatureVector(processedTestTweet, stopWords)))
#     if actualResult != sent:
#         print testTweet, "Predicted : ", actualResult, "Expected : ", sent
#         stripped = testTweet.split()
#         for word in stripped:
#             for c in range(0, 10):
#                 a = mostList[c]
#                 if a[0] == word and a[1] == True:
#                     print word, a[2], a[3]
#         print "\n"
#
#
# # to print most informative words
# mostList = []
# mostList2 = NBClassifier.show_most(100)
# for counter in range(0, 100):
#     contains = mostList2[counter][0]
#     contains = contains[contains.find("(") + 1:contains.find(")")]
#     isContain = mostList2[counter][1]
#     sent = mostList2[counter][2]
#     ratio = mostList2[counter][3]
#     mostList.append((contains, isContain, sent, ratio))



# Print all wrongly estimated tweets for Logistic Regression
# for counter in range(0,len(testing_tweets)):
#     a=testing_tweets[counter][0]
#
#     testTweet = ' '.join(a)
#     processedTestTweet = processTweet(testTweet)
#     actualResult = LogisticRegression_classifier.classify(extract_features(getFeatureVector


