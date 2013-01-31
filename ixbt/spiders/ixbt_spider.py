# coding=utf-8

from scrapy import log
from scrapy.http import Request
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from ixbt.items import IxbtItem
import re
import string
from urlparse import urlparse,urljoin

class IxbtSpider(BaseSpider):
	name = "ixbt"
	allowed_domains = ['forum.ixbt.com']
	#start_urls = []
	start_urls = [
	'http://forum.ixbt.com/topic.cgi?id=77:3849',	 #2
	'http://forum.ixbt.com/topic.cgi?id=77:8543',	 #3
	'http://forum.ixbt.com/topic.cgi?id=77:12313',	#4
	'http://forum.ixbt.com/topic.cgi?id=77:14830',	#5
	]

	def __init__(self, category = None):
		filename = 'anek_ixbt.txt'
		self.file = open(filename, "wb")

	def parse(self, response):
		hxs = HtmlXPathSelector(response)
		comments = hxs.select('//script[contains(text(),"t_post")]')
		#filename = response.url.split("/")[-2]
		self.file.write('comments: ' + str(len(comments)) + '\n\n')
		#items = []
		for comment in comments:
			#pattern = re.compile(r"'?([^(,]+)'?,")
			pattern = re.compile(r"('(.*?)'|(\d+),)", re.S)
			results = pattern.findall(comment.extract())
			comment_items = list((x[2] if x[2] else x[1]) for x in results)

			item = IxbtItem()
			if len(comment_items) > 5:
				text = comment_items[5]
				item['grats'] = len(text.split(';'))
			else:
				item['grats'] = 0

			item['text'] = []
			text = ''
			if len(comment_items) > 4:
				text = comment_items[4];
				text = re.sub(r'<br>', '\n', text)
				text = re.sub(r'<p>.*<p>', '\n', text)
				text = re.sub(r'\\n', '\n', text)
				#text = re.sub(r'\<.*', '', text)
				#text = re.sub(r'\<[^>]*\>', '', text)
				text = re.sub(r'(\n|^).{1,20}(\n)+', '\n', text)
				#text = re.sub(r'(\n){3,}', '\n\n', text)
				#text = re.sub(r'\s+$', '', text)
				#text = re.sub(r'^\s+', '', text)
				pattern = re.compile(r'(.+?)(\n\n|$)', re.S)
				tuples = pattern.findall(text)
				item['text'] = list(x[0].strip() for x in tuples if len(x[0].strip()) > 12)

			item['author'] = comment_items[1]

			item['url'] = response.url + u'#' + comment_items[0]
				
			if item['grats'] > 2:
				self.file.write('Автор: ' + item['author'].encode('UTF-8') + '\n')
				self.file.write(str(item['grats']) + ' человек сказали спасибо\n')
				self.file.write(item['url'] + '\n')
				s = '\n'.join(item['text'])
				self.file.write('кол-во анекдотов: ' + str(len(item['text'])) + '\n')
				#self.file.write(comment_items[4].encode('UTF-8'))
				for joke in item['text']:
					self.file.write(joke.encode('UTF-8') + '\n\n')

			#items.append(item)
			yield item

		next_url = hxs.select('//script[contains(text(),"t_assign")]').re(u'href=([^ ]*?)>далее')
		if len(next_url) > 0:
			next_url = next_url[0]
			parsed_url = urlparse(next_url)
			next_url = urljoin(response.url, next_url)
			yield Request(next_url, callback=self.parse)
			self.file.write("Следующая страница: " + next_url.encode('UTF-8') + '\n')

		#return items
