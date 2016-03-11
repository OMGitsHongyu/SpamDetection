__author__ = 'srayana'

import nltk
import nltk.tokenize.punkt
import codecs
import re
import string
from nltk.tokenize import word_tokenize
import csv
import sys
from sentiwordnet import SentiWordNetCorpusReader, SentiSynset

def sentimentAnalysis(filename, outputFile):
    swn_filename = 'SentiWordNet_3.0.0_20100705.txt'
    swn = SentiWordNetCorpusReader(swn_filename)

    regex = re.compile('[%s]' % re.escape(string.punctuation))

    with codecs.open(filename, 'r', 'utf-8') as f:
        data1 = f.readlines()
    f.close()

    writer = csv.writer(open(outputFile, 'wb'))

    tag = ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'TO', 'UH', 'PDT', 'SYM', 'RP']
    noun = ['NN', 'NNS', 'NP', 'NPS']
    adj = ['JJ', 'JJR', 'JJS']
    pronoun = ['PP', 'PP$', 'WP', 'WP$']
    verb = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    adverb = ['RB', 'RBR', 'RBS', 'WRB']
    for text in data1:
        count = re.split("\s+",text, 1)[0]
        if len(re.split("\s+",text, 1)) > 1:
            text = re.split("\s+",text, 1)[1]
            Tex = regex.sub(u'', text)
            words = word_tokenize(Tex.lower())
            word = nltk.pos_tag(words)
            objCount = 0
            subCount = 0
            for w in word:
                if not w[1] in tag:
                    #print(w)
                    if w[1] in noun:
                        pos_Char = 'n'
                    elif w[1] in adj:
                        pos_Char = 'a'
                    elif w[1] in pronoun:
                        pos_Char = 'p'
                    elif w[1] in verb:
                        pos_Char = 'v'
                    elif w[1] in adverb:
                        pos_Char = 'r'
                    else:
                        pos_Char = 'none'

                    if pos_Char == 'none':
                        try:
                            s = swn.senti_synsets(w[0])
                            scores = list(s)[0]
                            if scores.obj_score > 0.5:
                                objCount += 1
                            elif scores.pos_score + scores.neg_score > 0.5:
                                subCount += 1
                        except:
                            print('Unexpected word')
                    else:
                        try:
                            s = swn.senti_synsets(w[0], pos_Char)
                            scores=list(s)[0]
                            if scores.obj_score > 0.5:
                                objCount += 1
                            elif scores.pos_score + scores.neg_score > 0.5:
                                subCount += 1
                        except:
                            print('Unexpected word')

            if objCount+subCount > 0:
                ratioObj = float(objCount)/(objCount+subCount)
                ratioSub = float(subCount)/(objCount+subCount)
            else:
                ratioObj = 0.0
                ratioSub = 0.0
            writer.writerow([count, ratioObj, ratioSub])


if __name__ == "__main__":
    x = str(sys.argv[1])
    y = str(sys.argv[2])
    sys.stdout.write(str(sentimentAnalysis(x,y)))

