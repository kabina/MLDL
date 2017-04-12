#-*- encoding: utf-8 -*-
import pymysql as mdb
import sys
import requests
import datetime, time
import imp
import re
import urllib3
from multiprocessing import Process, Queue

from bs4 import BeautifulSoup

def crawl(date, counter):
	newslist = []
	pages_per_day = 0
	page = 1

	http = urllib3.PoolManager()
	while True :
		url='http://news.naver.com/main/election/president2017/news/realtime.nhn?mode=LSD&date='+date+'&page='+str(page)
		r = http.request('GET', url)
		plain_text = r.data

		soup = BeautifulSoup(plain_text, 'lxml')
		if pages_per_day ==0:
			pagediv=  soup.find('div', {'class':'paging',})
			pages = pagediv.findAll('a')
			for pagecnt in pages :
				pages_per_day +=1
		for links in soup.findAll('div', {'class':'tmp small2 ',}):
			link = links.find('a')
			href = link.get('href')
			urldetail = 'http://news.naver.com'+str(href)
			title = link.get('title')

			r = http.request('GET', urldetail)
			plain_text = r.data

			soup_detail = BeautifulSoup(plain_text, 'lxml')
			detail_link = soup_detail.find('div', {'id':'articleBodyContents',})
			if detail_link is None:
				body = ''
			else:
				body = detail_link.get_text()
			news = {}

			#news['title'] = re.sub('[^가-힝\\s]', '', str(title).strip())
			#news['href'] = re.sub('[^가-힝\\s]', '', str(href).strip())
			#news['body'] = re.sub('[^가-힝\\s]', '', str(body).strip())

			#news['title'] = re.sub('[ ^ \.\, \?\!a - zA - Z0 - 9\u3131 -\u3163\uac00 -\ud7a3]+', '', str(title).strip())
			#news['href'] = re.sub('[ ^ \.\, \?\!a - zA - Z0 - 9\u3131 -\u3163\uac00 -\ud7a3]+', '', str(href).strip())
			#news['body'] = re.sub('[ ^ \.\, \?\!a - zA - Z0 - 9가-힝]+', '', str(body).strip())
			news['title'] = re.sub('[ ^\.\,\?\!a-zA-Z0-9가-힝]+', '', str(title).strip())
			news['href'] = re.sub('[ ^\.\,\?\!a-zA-Z0-9가-힝]+', '', str(href).strip())
			news['body'] = re.sub('[ ^\.\,\?\!a-zA-Z0-9가-힝]+', '', str(body).strip())


			newslist.append(news)

		print("process #",counter, "page:",page)
		page += 1
		if page > pages_per_day:
			break

	filename = "./crawl_output_%d.txt"%counter
	f = open(filename, 'w', encoding='utf-8')
	for data in newslist:
		o_data = "%s\n %s\n" % (data['title'], data['body'])
		f.write(str(o_data))
	f.flush()
	f.close()

def word_count():
	wordcount = {}
	i_file=open("./crawl_output_merged.txt","r+", encoding='utf-8')
	o_file=open("./word_count.txt","w", encoding='utf-8')
	for word in i_file.read().split():
		if word not in wordcount:
			wordcount[word] = 1
		else:
			wordcount[word] += 1
	i_file.close()

	keys = list(wordcount.keys())

	for key in keys:
		o_data = "%s | %d\n"%(key, wordcount[key])
		o_file.write(o_data)
	o_file.close()
	return wordcount

def merge_files(file_count):
	w_file=open("./crawl_output_merged.txt","w", encoding='utf-8')
	idx = 1
	while idx <= file_count:
		filename ="./crawl_output_%d.txt"%idx
		r_file=open(filename,"r+", encoding='utf-8')
		for lines in r_file.read():
			w_file.write(lines)
		r_file.close()
		idx += 1
	w_file.close()
		
def write_wordcnt_db(wordcount):
	try:
		con = mdb.connect(host='localhost', port=3306, user='kabina', password='ah64jj3!', db='crawl', charset='utf8', autocommit=True)
	
		cursor = con.cursor()

		keys = list(wordcount.keys())
	
		add_word_cnt = ("INSERT INTO word_count "
					"(word, count) "
					"VALUES (%s, %s)")
	
		commit_idx = 0
		for key in keys:
			news_data = (key, int(wordcount[key]))
			cursor.execute(add_word_cnt, news_data)
			commit_idx += 1
			if commit_idx%500 == 0:
				con.commit()
		
		print("Total Insert Count : %d "% commit_idx)
		con.commit()
		cursor.close()
		con.close()
	
	except mdb.Error as  e:
		print("Error %d: %s" % (e.args[0], e.args[1]))
		sys.exit(1)

def log(message):
	ts = time.time()
	sts = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	print ("%s : %s"% (sts, message))

log("start crawl..")

if __name__ == '__main__':
	result = Queue()

	jobs = []
	for i in range(3):
		p = Process(target=crawl, args=((datetime.datetime.now() - datetime.timedelta(days = i)).strftime('%Y%m%d'),i))
		jobs.append(p)
	for p in  jobs:
		p.start()
	for p in  jobs:
		p.join()

	log("data crawling completed.")
	'''
	result.put('STOP')

	while True:
		tmp = result.get()
		if tmp == 'STOP' : 
			break
	'''

	log("merge..ing..")
	merge_files(3)
	log("counting words and saving that to mysql..")
	word_count()
	log("complete!")

