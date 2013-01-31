# coding=utf-8

from scrapy.http import Request
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from ixbt.items import IxbtItem
import re
from urlparse import urlparse,urljoin

class IxbtSpider(BaseSpider):
	name = "ixbt"
	allowed_domains = ['forum.ixbt.com']
	start_urls = ['http://forum.ixbt.com/topic.cgi?id=77:14830']

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
			pattern = re.compile(r"'(.*?)'")
			comment_items = pattern.findall(comment.extract())

			item = IxbtItem()
			if len(comment_items) > 3:
				text = comment_items[3]
				item['grats'] = len(text.split(';'))
			else:
				item['grats'] = 0

			if len(comment_items) > 2:
				text = comment_items[2];
				text = re.sub(r'<br>', '\n', text)
				text = re.sub(r'<p>.*<p>', '\n', text)
				text = re.sub(r'\\n', '\n', text)
				item['text'] = text
				item['author'] = comment_items[0]
				
			if item['grats'] > 2:
				self.file.write('Автор: ' + comment_items[0].encode('UTF-8') + '\n')
				self.file.write('Спасибо сказали: ' + str(item['grats']) + ' человек\n')
				self.file.write(item['text'].encode('UTF-8') + '\n')

			#items.append(item)
			yield item
			#file.write(text)
			#print text

		next_url = hxs.select('//script[contains(text(),"t_assign")]').re(u'href=([^ ]*?)>далее')
		if len(next_url) > 0:
			next_url = next_url[0]
			parsed_url = urlparse(next_url)
			next_url = urljoin(response.url, next_url)
			yield Request(next_url, callback=self.parse)
			self.file.write("Следующая страница: " + next_url.encode('UTF-8') + '\n')

		#return items


