import sys
import codecs
import datetime as dt
import feature as ft


def writeMetadata(filename, N, reviewId, userId, prodId, dates, ratings, label, sep=' '):
    with codecs.open(filename, 'w', 'utf-8') as fw:
        for i in xrange(N):
            fw.write(sep.join(map(str,[reviewId[i],userId[i],prodId[i],dates[i],ratings[i],label[i]]))+'\n')

def writeReview(filename, N, reviewId, reviewtxt, sep=' '):
    with codecs.open(filename, 'w', 'utf-8') as fw:
        for i in xrange(N):
            print i,type(reviewtxt[i])
            fw.write(sep.join(map(str,[reviewId[i],reviewtxt[i].encode('utf-8')]))+'\n')

if __name__ == '__main__':
    file1, file2, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
    reviewId, userId, prodId, dates, ratings, recommend = ft.readMetadata('./metadata', N)
    writeMetadata(file1, N, reviewId, userId, prodId, dates, ratings, recommend)
    reviewIdr, reviewtxt = ft.readReview('./reviewContent', N)
    assert reviewId == reviewIdr
    writeReview(file2, N, reviewIdr, reviewtxt)
