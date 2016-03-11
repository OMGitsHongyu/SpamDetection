__author__ = 'srayana'

import nltk
import nltk.tokenize.punkt
import codecs
import re
import string
import csv
import sys

def allCapitalCount(reviewFile, outFile):
    with codecs.open(reviewFile, 'r', 'utf-8') as f:
        data1 = f.readlines()
    f.close()

    writer = csv.writer(open(outFile, 'wb'))
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    for line in data1:
        count = re.split("\s+", line, 1)[0]
        if len(re.split("\s+", line, 1)) > 1:
            text = re.split("\s+", line, 1)[1]
            words = nltk.word_tokenize(text)
            word = list()
            countWord = 0
            countAllCapital = 0

            for w in words:
                if w.isupper():
                    countAllCapital += 1
                new_token = regex.sub(u'', w)
                if not new_token == u'':
                    word.append(new_token)
                    countWord += 1
            if countWord > 0:
                percAllCapital = (float(countAllCapital)/countWord)
            else:
                percAllCapital = 0.0
            writer.writerow([count, percAllCapital])

if __name__ == "__main__":
    x = str(sys.argv[1])
    y = str(sys.argv[2])
    sys.stdout.write(str(allCapitalCount(x,y)))
