from __future__ import division
import time
import codecs
import unicodedata
import datetime as dt
import numpy as np
from numpy import linalg as LA
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer


def readMetadata(filename, N, sep='\t'):
    """Read metadata (format: userId prodId rating recommend date).
    """
    reviewId, userId, prodId, date, rating, recommend = [],[],[],[],[],[]
    reviewId0 = 1
    with codecs.open(filename, 'r', 'utf-8') as fr:
        for line in fr:
            if reviewId0 <= N:
                userId0, prodId0, rating0, recommend0, date0 = line.rstrip().split(sep)
                reviewId.append(reviewId0)
                userId.append(userId0)
                prodId.append(prodId0)
                date.append(date0)
                rating.append(rating0)
                recommend.append(recommend0)
                reviewId0 += 1
    return reviewId, userId, prodId, date, rating, recommend


def readReview(filename, N, sep='\t'):
    """Read reviews (format: userId prodId date reviewtxt).
    """
    reviewIdr, reviewtxt = [],[]
    reviewIdr0 = 1
    with codecs.open(filename, 'r', 'utf-8') as fr:
        for line in fr:
            if reviewIdr0 <= N:
                reviewtxt0 = ' '.join(line.rstrip().split(sep)[3:])
                reviewtxt0 = unicodedata.normalize('NFKD', reviewtxt0)
                reviewIdr.append(reviewIdr0)
                reviewtxt.append(reviewtxt0)
                reviewIdr0 += 1
    return reviewIdr, reviewtxt


def MNR(upId, dates):
    """Max. number of reviews written in a day.
    Parameters
    ----------
    upId : (R,) array of int
            user/product Ids.
    dates : (R,) list of datetime.datetime
            date of reviews.
    Returns
    -------
    MNR : (U/P,) array of float
            max. number of reviews of user/product in a day.
    """
    int_dates = [date.toordinal() for date in dates]
    udates, ind_dates = np.unique(int_dates, return_inverse=True)
    uup, ind_up = np.unique(upId, return_inverse=True)
    D, U = len(udates), len(uup)
    mnr_up = sparse.csr_matrix((np.ones((len(ind_dates))),(ind_dates,ind_up)),shape=(D,U)).toarray()
    return mnr_up.max(axis=0)/mnr_up.max()


def PR(upId, ratings):
    """Ratio of positive reviews (4-5 star).
    Parameters
    ----------
    upId : (R,) array of int
            user/product Ids.
    ratings : (R,) array of float
            ratings of reviews.
    Returns
    -------
    PR : (U/P,) array of float
            ratios of positive reviews.
    """
    uup, ind_up = np.unique(upId, return_inverse=True)
    nupbins = np.arange(len(uup)+1)
    tot_up, edges = np.histogram(ind_up, bins=nupbins)
    p_up, edges = np.histogram(ind_up[ratings>3], bins=nupbins)
    return p_up/tot_up


def NR(upId, ratings):
    """Ratio of negative reviews (1-2 star).
    Parameters
    ----------
    upId : (R,) array of int
            user/product Ids.
    ratings : (R,) array of float
            ratings of reviews.
    Returns
    -------
    NR : (U/P,) array of float
            ratios of negative reviews.
    """
    uup, ind_up = np.unique(upId, return_inverse=True)
    nupbins = np.arange(len(uup)+1)
    tot_up, edges = np.histogram(ind_up, bins=nupbins)
    n_up, edges = np.histogram(ind_up[ratings<3], bins=nupbins)
    return n_up/tot_up


def RD_prod(prodId, ratings):
    """Rating deviation of products.
    Parameters
    ----------
    prodId : (R,) array of int
            product Ids.
    ratings : (R,) array of float
            ratings of reviews.
    Returns
    -------
    RD : (P,) array of float
            Rating deviation of products.
    """
    uprod, ind_prods = np.unique(prodId, return_inverse=True)
    avgRating = np.zeros((len(ratings),))
    for i in xrange(len(uprod)):
        ind = ind_prods==i
        if any(ind):
            r = ratings[ind]
            avgRating[ind_prods==i] = np.sum(r)/len(r)
    return np.fabs(ratings - avgRating)


def avgRD(userId, prodId, ratings):
    """Avg. rating deviation of users/products.
    Parameters
    ----------
    userId : (R,) array of int
            user Ids.
    prodId : (R,) array of int
            product Ids.
    ratings : (R,) array of float
            ratings of reviews.
    Returns
    -------
    avgRD_user : (U,) array of float
            Avg. rating deviation of users.
    avgRD_prod : (P,) array of float
            Avg. rating deviation of products.
    """
    uuser, ind_users = np.unique(userId, return_inverse=True)
    uprod, ind_prods = np.unique(prodId, return_inverse=True)
    RD = RD_prod(prodId, ratings)
    avgRD_user = np.zeros((len(uuser),))
    for i in xrange(len((uuser))):
        ind = ind_users==i
        if any(ind):
            r = RD[ind]
            avgRD_user[i] = np.sum(r)/len(r)
    avgRD_prod = np.zeros((len(uprod),))
    for i in xrange(len((uprod))):
        ind = ind_prods==i
        if any(ind):
            r = RD[ind]
            avgRD_prod[i] = np.sum(r)/len(r)
    return avgRD_user, avgRD_prod


def WRD(userId, prodId, ratings, dates, alpha=1.5):
    """Weighted rating deviation of users/products.
    Parameters
    ----------
    userId : (R,) array of int
            user Ids.
    prodId : (R,) array of int
            product Ids.
    ratings : (R,) array of float
            ratings of reviews.
    dates : (R,) list of datetime.datetime
            date of reviews.
    alpha : float, optional
            decay rate.
    Returns
    -------
    WRD_user : (U,) array of float
            weighted rating deviation of users.
    WRD_prod : (U,) array of float
            weighted rating deviation of products.
    """
    int_dates = [date.toordinal() for date in dates]
    uuser, ind_users = np.unique(userId, return_inverse=True)
    uprod, ind_prods = np.unique(prodId, return_inverse=True)
    udates, ind_dates = np.unique(int_dates, return_inverse=True)
    RD = RD_prod(prodId, ratings)
    W = np.zeros((len(ratings),))
    for i in xrange(len(uprod)):
        ind = ind_prods==i
        if any(ind):
            d = ind_dates[ind]
            if len(d)>1:
                ud = np.unique(d)
                f, edges = np.histogram(d, bins=np.append(ud,ud.max()+1))
                m, r = 0, np.zeros((len(d),))
                for j in xrange(len(ud)):
                    r[d==ud[j]] = m + 1
                    m += f[j]
                W[ind] = 1 / (r ** alpha)
            else:
                r = 1
                W[ind] = 1 / (r ** alpha)
    WRD_user = np.zeros((len(uuser),))
    for i in xrange(len((uuser))):
        ind = ind_users==i
        if any(ind):
            r, w = RD[ind], W[ind]
            WRD_user[i] = np.sum(r*w)/np.sum(w)
    WRD_prod = np.zeros((len(uprod),))
    for i in xrange(len((uprod))):
        ind = ind_prods==i
        if any(ind):
            r, w = RD[ind], W[ind]
            WRD_prod[i] = np.sum(r*w)/np.sum(w)
    return WRD_user, WRD_prod


def ERD(upId, ratings):
    """Entropy of rating distribution of users/products' reviews.
    Parameters
    ----------
    upId : (R,) array of int
            user/product Ids.
    ratings : (R,) array of float
            ratings of reviews.
    Returns
    -------
    ERD_up : (U/P,) array of float
            entropy of rating distribution of users/products' reviews
    """

    uup, ind_up = np.unique(upId, return_inverse=True)
    rate = np.arange(1,7)
    ERD_up = np.zeros((len(uup),))
    for i in xrange(len(uup)):
        ind = ind_up==i
        if any(ind):
            s = ratings[ind]
            f, edges = np.histogram(s, bins=rate)
            f = f[f>0]
            if any(f):
                p = f / len(s)
                ERD_up[i] = np.sum(-p*np.log2(p))
    return ERD_up


def BST_user(userId, dates):
    """Burstiness of users.
    Parameters
    ----------
    userId : (R,) array of int
            user Ids.
    dates : (R,) list of datetime.datetime
            date of reviews.
    Returns
    -------
    BST_user : (U,) array of float
            burstiness of users.
    """
    uuser, ind_users = np.unique(userId, return_inverse=True)
    int_dates = np.array([date.toordinal() for date in dates])
    tau = 28
    BST_user = np.ones((len(uuser),))
    for i in xrange(len(uuser)):
        ind = ind_users==i
        if np.sum(ind)>1:
            d = int_dates[ind]
            ndays = d.max() - d.min()
            if ndays>tau:
                BST_user[i] = 0
            else:
                BST_user[i] = 1 - ndays/tau
    return BST_user


def ETG(upId, dates):
    """Entropy of temporal gaps.
    Parameters
    ----------
    upId : (R,) array of int
            user/prod Ids.
    dates : (R,) list of datetime.datetime
            date of reviews.
    Returns
    -------
    ETG_up: (U/P,) array of float
            entropy of temporal gaps.
    """
    uup, ind_up = np.unique(upId, return_inverse=True)
    int_dates = np.array([date.toordinal() for date in dates])

    ETG_up = np.zeros((len(uup),))
    for i in xrange(len(uup)):
        ind = ind_up==i
        if np.sum(ind)>1:
            d = int_dates[ind]
            deltaT = np.diff(np.sort(d))
#         %distribution
#     %     1- 0 days
#     %     2- [1-2] days
#     %     3- [3-4] days
#     %     4- [5-8] days
#     %     5- [9-16] days
#     %     6- [17-32] days
#     %     Throw away any gaps for >=33 days
            deltaT = deltaT[deltaT < 33]
            edges = [0,1,3,5,9,17,33]
            f = np.histogram(deltaT, bins=edges)[0]
            f = f[f>0]
            if len(f)>0:
                p = f / len(deltaT)
                ETG_up[i] = np.sum(-p*np.log2(p))
    return ETG_up


def RL(upId, wordcount_reviews):
    """Avg. review length in number of words.
    Parameters
    ----------
    upId : (R,) array of int
            user/prod Ids.
    wordcount_reviews : (R,2) array of int
            reviewId, wordcount of reviews.
    Returns
    -------
    RL_up : (U/P,) array of float
            Avg. review length in number of words.
    """
    uup, ind_up = np.unique(upId, return_inverse=True)
    RL_up = np.zeros((len(uup),))
    for i in xrange((len(uup))):
        ind = ind_up==i
        if any(ind):
            r = wordcount_reviews[ind,1]
            RL_up[i] = np.sum(r)/len(r)
    return RL_up


def ACS_MCS(upId, TFIDF):
    """Avg./Max. content similarity.
    Parameters
    ----------
    upId : (R,) array of int
            user/prod Ids.
    TFIDF : (R, nfeatures) scipy.sparse.csr.csr_matrix of float
            TFIDF of each review.
    Returns
    -------
    ACS_up : (U/P,) array of float
            Avg. content similarity.
    MCS_up : (U/P,) array of float
            Max. content similarity.
    """
    uup, ind_up = np.unique(upId, return_inverse=True)
    ACS_up = -np.ones((len(uup),))
    MCS_up = -np.ones((len(uup),))
    for i in xrange((len(uup))):
        ind = ind_up==i
        nreview = np.sum(ind)
        if nreview>1:
            upT = TFIDF[ind,:]
            npair = nreview*(nreview-1)/2
            sim_score = np.zeros((npair,))
            count = 0
            for j in xrange(nreview-1):
                for k in xrange(j+1,nreview):
                    x, y = upT[j,:].toarray()[0], upT[k,:].toarray()[0]
                    xdoty = np.dot(x,y)
                    if xdoty == 0:
                        sim_score[count] = xdoty
                    else:
                        sim_score[count] = xdoty/(LA.norm(x)*LA.norm(y))
                    count += 1
            ACS_up[i] = np.mean(sim_score)
            MCS_up[i] = np.max(sim_score)
    return ACS_up, MCS_up


def Rank_prod(prodId, dates):
    """Rank order among all the reviews of products.
    Parameters
    ----------
    prodId : (R,) array of int
            product Ids.
    dates : (R,) list of datetime.datetime
            date of reviews.
    Returns
    -------
    rank : (P,) array of float
            rank order among all the reviews of products.
    """
    int_dates = [date.toordinal() for date in dates]
    udates, ind_dates = np.unique(int_dates, return_inverse=True)
    uprod, ind_prod = np.unique(prodId, return_inverse=True)
    rank = np.zeros((len(prodId),))
    for i in xrange(len(uprod)):
        ind = ind_prod==i
        if any(ind):
            d = ind_dates[ind]
            if len(d)>1:
                ud = np.unique(d)
                f, edges = np.histogram(d, bins=np.append(ud,ud.max()+1))
                m, r = 0, np.zeros((len(d),))
                for j in xrange(len(ud)):
                    r[d==ud[j]] = m + 1
                    m += f[j]
                rank[ind] = r
            else:
                r = 1
                rank[ind] = r
    return rank


def EXT(ratings):
    """Extremity of rating: 1 for ratings {1, 5}, 0 otherwise.
    Parameters
    ----------
    ratings : (R,) array of float
            ratings of reviews.
    Returns
    -------
    EXT_review : (R,) array of int
            extreme rating scores of ratings.
    """
    EXT_review = np.zeros((len(ratings),))
    EXT_review[np.logical_or(ratings == 5,ratings == 1)] = 1
    return EXT_review


def DEV(prodId, ratings):
    """Thresholded rating deviation of review.
    Parameters
    ----------
    prodId : (R,) array of int
            product Ids.
    ratings : (R,) array of float
            ratings of reviews.
    Returns
    -------
    DEV_reviews : (R,) array of int
            thresholded rating deviation of review.
    """
    RD_reviews = RD_prod(prodId, ratings)
    beta1 = 0.63
    DEV_reviews = np.zeros((len(ratings),))
    normRD = RD_reviews/4
    DEV_reviews[normRD > beta1] = 1
    return DEV_reviews


def ETF(userId, prodId, ratings, dates):
    """Early time frame.
    Parameters
    ----------
    userId : (R,) array of int
            user Ids.
    prodId : (R,) array of int
            product Ids.
    ratings : (R,) array of float
            ratings of reviews.
    dates : (R,) list of datetime.datetime
            date of reviews.
    Returns
    -------
    ETF_reviews : (R,) array of float
            early time frame scores of reviews.
    """
    int_dates = np.array([date.toordinal() for date in dates])
    uuser, ind_users = np.unique(userId, return_inverse=True)
    uprod, ind_prods = np.unique(prodId, return_inverse=True)
    udates, ind_dates = np.unique(int_dates, return_inverse=True)
    P, U = len(uprod), len(uuser)
    HRMat = sparse.csr_matrix((np.ones((len(ind_prods))),(ind_prods,ind_users)),shape=(P,U))
    x, y = HRMat.nonzero()
    firstReviewDate = []
    for i in xrange(P):
        ind = ind_prods==i
        d = int_dates[ind]
        firstReviewDate.append(d.min())
    delta, beta2 = 7*30, 0.69
    F, ETF_reviews = np.zeros((len(ind_prods),)), np.zeros((len(ind_prods),))
    for i in xrange(len(x)):
        ind = np.logical_and(ind_prods==x[i],ind_users==y[i])
        d = int_dates[ind]
        deltaD = d.max() - firstReviewDate[x[i]]
        if deltaD <= delta:
            F[ind] = 1 - deltaD/delta
    ETF_reviews[F>beta2] = 1
    return ETF_reviews


def ISR(userId):
    """Is singleton?
    Parameters
    ----------
    userId : (R,) array of int
            user Ids.
    Returns
    -------
    ISR_reviews : (R,) array of int
            is singleton or not.
    """
    uuser, ind_users = np.unique(userId, return_inverse=True)
    ISR_reviews = np.zeros((len(userId),))
    for i in xrange(len(userId)):
        ind = ind_users==i
        if np.sum(ind)==1:
            ISR_reviews[ind] = 1
    return ISR_reviews


if __name__ == '__main__':
    file1, file2 = 'metadata', 'reviewContent'
    N = 100
    reviewId, userId, prodId, dates, ratings, recommend = readMetadata(file1, N)
    ratings = np.array(ratings, dtype=np.float32)
    recommend = np.array(recommend, dtype=np.float32)
    print recommend
    dateformat='%Y-%m-%d'
    date = [dt.datetime.strptime(d, dateformat) for d in dates]

    t0 = time.time()
    print "feature pipeling...."

    MNR_user = MNR(userId, date)
    MNR_prod = MNR(prodId, date)
    t1 = time.time()
    print "MNR done, time used:", t1 - t0

    PR_user = PR(userId, ratings)
    PR_prod = PR(prodId, ratings)
    t2 = time.time()
    print "PR done, time used:", t2 - t1

    NR_user = NR(userId, ratings)
    NR_prod = NR(prodId, ratings)
    t3 = time.time()
    print "NR done, time used:", t3 - t2

    RD_reviews = RD_prod(prodId, ratings)
    t4 = time.time()
    print "RD_prod done, time used:", t4 - t3

    avgRD_user, avgRD_prod = avgRD(userId, prodId, ratings)
    t5 = time.time()
    print "avgRD done, time used:", t5 - t4

    WRD_user, WRD_prod = WRD(userId, prodId, ratings, date)
    t6 = time.time()
    print "WRD done, time used:", t6 - t5

    ERD_user = ERD(userId, ratings)
    ERD_prod = ERD(prodId, ratings)
    t7 = time.time()
    print "ERD done, time used:", t7 - t6

    BST_user = BST_user(userId, date)
    t8 = time.time()
    print "BST_user done, time used:", t8 - t7

    ETG_user = ETG(userId, date)
    ETG_prod = ETG(prodId, date)
    t9 = time.time()
    print "ETG done, time used:", t9 - t8

    wc = np.loadtxt('output_wordcount.txt')
    print wc
    RL_user, RL_prod = RL(userId, wc), RL(prodId, wc)
    t10 = time.time()
    print "RL done, time used:", t10 - t9

    reviewIdr, reviewtxt = readReview(file2, N)

    vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=2000, stop_words='english')
    TFIDF = vectorizer.fit_transform(reviewtxt)
    t11 = time.time()
    print "TFIDF done, time used:", t11 - t10

    ACS_prod, MCS_prod = ACS_MCS(prodId, TFIDF)
    ACS_user, MCS_user = ACS_MCS(userId, TFIDF)
    t12 = time.time()
    print "ACS/MCS done, time used:", t12 - t11

    rank = Rank_prod(prodId, date)
    t13 = time.time()
    print "rank done, time used:", t13 - t12

    EXT_review = EXT(ratings)
    t14 = time.time()
    print "EXT done, time used:", t14 - t13

    DEV_reviews = DEV(prodId, ratings)
    t15 = time.time()
    print "DEV done, time used:", t15 - t14

    ETF_reviews = ETF(userId, prodId, ratings, date)
    t16 = time.time()
    print "ETF done, time used:", t16 - t15

    ISR_reviews = ISR(userId)
    t17 = time.time()
    print "ISR done, time used:", t17 - t16
