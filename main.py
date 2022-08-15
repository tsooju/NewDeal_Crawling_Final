import sys
import time

import schedule

from Naver_crawling import NewsTitle, Wordcloud
from Naver_crawling_comment import NewsComment, CommentWordcloud
import os
from konlpy import jvm



def crawling_schedule():
	# newstitle = NewsTitle()
	# print(newstitle.main_function())
	#
	# newstitle_wordcloud = Wordcloud()
	# print(newstitle_wordcloud.get_title_wordcloud())

	newscomment = NewsComment()
	print(newscomment.main_function())

	newscomment_wordcloud = CommentWordcloud()
	print(newscomment_wordcloud.get_comment_wordcloud())

if __name__ == '__main__':
	jvm.init_jvm()
	try:
		os.chdir(sys._MEIPASS)
		print(sys._MEIPASS)
	except:
		os.chdir(os.getcwd())
	# schedule.every().day.at("10:00").do(crawling_schedule)
	# while True:
	# 	schedule.run_pending()
	# 	time.sleep(1)



	crawling_schedule()



