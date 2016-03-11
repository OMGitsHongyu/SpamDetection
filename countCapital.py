__author__ = 'srayana'

import codecs
import string
import csv
import sys
import re

def countCapital(filename, outputFile):

    with codecs.open(filename, 'r', 'utf-8') as f:
        data1 = f.readlines()
    f.close()

    writer = csv.writer(open(outputFile, 'wb'))

    for line in data1:
        count = re.split("\s+",line, 1)[0]
        if len(re.split("\s+",line, 1)) > 1:
            line = re.split("\s+",line, 1)[1]
            countCapital = sum(1 for c in line if c.isupper())
            line = filter(lambda x: x in string.letters, line.lower())
            countCharacter = len(line)
            if countCharacter > 0:
                percCap = (float(countCapital)/countCharacter)
            else:
                percCap = 0.0
            writer.writerow([count, percCap])

if __name__ == "__main__":
    x = str(sys.argv[1])
    y = str(sys.argv[2])
    sys.stdout.write(str(countCapital(x,y)))

