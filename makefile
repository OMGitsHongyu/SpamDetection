##################
# Author: Hongyu Zhu and Shayan Doroudi
# Date: March 2016
##################


precvs:
	python prefiles.py $(file1) $(file2) 608598
	python WordCount_reviews.py $(file2) output_wordcount.txt
	python allCapitalCount.py $(file2) output_AllCapital.csv
	python countCapital.py $(file2) output_PC.csv
	python ratioPPwordCount.py $(file2) output_PP1.csv
	python excSentenceCount.py $(file2) output_RES.csv
	python sentimentAnalysis.py $(file2) output_SW+OW.csv
	python uniGram.py $(file2) output_uniGram.txt
	python codeTable.py output_uniGram.txt output_DL_u.csv dict_uniGram.csv
	python codeTable.py output_biGram.txt output_DL_b.csv dict_biGram.csv
