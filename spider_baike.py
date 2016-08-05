#!/usr/bin/env python
#coding:utf-8

import urllib2
import re
from bs4 import BeautifulSoup

class URLManager(object):
	def __init__(self):
		self.new_urls = set()
		self.old_urls = set()

	def add_url(self, url):
		if url not in self.new_urls and url not in self.old_urls:
			self.new_urls.add(url)

	def add_urls(self, urls):
		for url in urls:
			self.add_url(url)
	
	def has_new_url(self):
		return len(self.new_urls) != 0

	def get_url(self):
		new_url = self.new_urls.pop()
		self.old_urls.add(new_url)
		return new_url


class HTMLDownloader(object):
	def download(self, url):
		res = urllib2.urlopen(url)
		if res.getcode() != 200:
			return None
		return res.read()


class HTMLParser(object):
	def parse(self, url, html):
		soup = BeautifulSoup(html, 'html.parser', from_encoding='utf8')
		urls = self._get_urls(soup)
		data = self._get_data(url, soup)
		return urls, data

	def _get_urls(self, soup):
		urls = soup.find_all('a', href=re.compile(r'/view/\d+\.htm'))
		return map(lambda s: 'http://baike.baidu.com'+s['href'], urls)

	def _get_data(self, url, soup):
		data = {'url': url,
			'title': soup.find('dd', class_='lemmaWgt-lemmaTitle-title').find('h1').get_text(),
			'content': soup.find('div', class_='lemma-summary').get_text()}
		return data


class HTMLOutputer(object):
	def __init__(self):
		self.datas = []

	def collect_data(self, data):
		self.datas.append(data)

	def output_html(self):
		f = open('output.html', 'w')
		f.write('<table>')
		for data in self.datas:
			f.write('<tr>')
			f.write('<td>%s</td>' % data['url'])
			f.write('<td>%s</td>' % data['title'].encode('utf-8'))
			f.write('<td>%s</td>' % data['content'].encode('utf-8'))
			f.write('</tr>')
		f.write('</table>')
		

		

class SpiderMain(object):
	def __init__(self):
		self.urls = URLManager()
		self.downloader = HTMLDownloader()
		self.parser = HTMLParser()
		self.outputer = HTMLOutputer()

	def craw(self, root_url):
		count = 1
		self.urls.add_url(root_url)
		while self.urls.has_new_url():
			try:
				url = self.urls.get_url()			
				html = self.downloader.download(url)
				new_urls, data = self.parser.parse(url, html)
				print 'craw [%d]: %s' % (count, url)
				self.urls.add_urls(new_urls)
				self.outputer.collect_data(data)
				if count == 1000:
					break
				count += 1
			except:
				print 'craw [Failed]'
		self.outputer.output_html()

		

if __name__ == '__main__':
	root_url = 'http://baike.baidu.com/view/21087.htm'
	spider = SpiderMain()
	spider.craw(root_url)