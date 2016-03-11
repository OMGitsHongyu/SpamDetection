__author__ = 'srayana'

import nltk
import nltk.tokenize.punkt
import codecs
import re
import sys
import string

def uniGram(filename,outputFile):
    # print('uniGram: ')
    #
    # file = 'emoticons.txt'
    # emoticons = list()
    #
    # with open(file, 'r') as f:
    #     data = f.readlines()
    # f.close()
    #
    # for d in data:
    #     emo = d.rstrip('\n')
    #     emoticons.append(emo)
    #print(emoticons)

    with codecs.open(filename, 'r', 'utf-8') as f:
        data1 = f.readlines()
    f.close()

    output = codecs.open(outputFile, 'a', 'utf-8')
    regex = re.compile('[%s]' % re.escape(string.punctuation))

    for line in data1:
        count = re.split("\s+",line, 1)[0]

        if len(re.split("\s+",line, 1)) > 1:
            line = re.split("\s+",line, 1)[1]
            #words = line.split()
            words = nltk.word_tokenize(line)
            word = []
            temp = ""
            c = 0
            for w in words:
                c = c + 1
                if w in string.punctuation:
                    temp = temp+w
                    if c < len(words):
                        continue
                if len(temp) > 1:
                    word.append(temp)
                temp = ""
                new_token = regex.sub(u'', w)
                if not new_token == u'':
                    word.append(new_token)
            for ug in word:
                output.write(count+' '+ug.encode('ascii', 'ignore')+'\n')
                #print(str(count)+' '+bg[0]+'_'+bg[1]+'\n')
    output.close()

if __name__ == "__main__":
    x = str(sys.argv[1])
    y = str(sys.argv[2])
    sys.stdout.write(str(uniGram(x,y)))
