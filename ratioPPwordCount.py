__author__ = 'srayana'

import nltk
import nltk.tokenize.punkt
import codecs
import re
import sys
import csv

def PPWordCount(filename,outputFile):

    PP_1_Word = list()
    with open('1PP-words.txt', 'r') as f:
        data = f.readlines()
    f.close()

    for d in data:
        w = d.rstrip('\n')
        PP_1_Word.append(w)
    print(PP_1_Word)

    PP_2_Word = list()
    with open('2PP-words.txt', 'r') as f:
        data = f.readlines()
    f.close()

    for d in data:
        w = d.rstrip('\n')
        PP_2_Word.append(w)
    print(PP_2_Word)

    with codecs.open(filename, 'r', 'utf-8') as f:
        data1 = f.readlines()
    f.close()

    writer = csv.writer(open(outputFile, 'wb'))

    for line in data1:
        count = re.split("\s+", line, 1)[0]
        if len(re.split("\s+", line, 1)) > 1:
            line = re.split("\s+", line, 1)[1]
            #words = text.split()
            words = nltk.word_tokenize(line)
            countPP_1 = 0
            countPP_2 = 0
            for w in words:
                if w.lower() in PP_1_Word:
                    countPP_1 += 1
                if w.lower() in PP_2_Word:
                    countPP_2 += 1
            countPro = countPP_1 + countPP_2
            if countPro > 0:
                percPP1 = (float(countPP_1)/countPro)
                percPP2 = (float(countPP_2)/countPro)
            else:
                percPP1 = 0.0
                percPP2 = 0.0
            writer.writerow([count, percPP1, percPP2])

if __name__ == "__main__":
    x = str(sys.argv[1])
    y = str(sys.argv[2])
    sys.stdout.write(str(PPWordCount(x,y)))

