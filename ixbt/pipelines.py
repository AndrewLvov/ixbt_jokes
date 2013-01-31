# coding=utf-8
#
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
#

from scrapy import log
from scrapy import signals
from scrapy.contrib.exporter import JsonItemExporter
from ixbt.items import JokeItem
import re

def ixbt_url_less(url1, url2):
	pattern = re.compile(r'77:(\d+)(-\d+)?#(\d+)')
	res1 = pattern.search(url1)
	res2 = pattern.search(url2)
	if res1.group(0) < res2.group(0):
		return True
	elif res1.group(0) > res2.group(0):
		return False

	if res1.group(2) < res2.group(2):
		return True
	elif res1.group(2) > res2.group(2):
		return False

	return False	# equal

class IxbtPipeline(object):
		def process_item(self, item, spider):
				return item

class DupesPipeline(object):
	def __init__(self):
		#log.msg('hahaha\n\n\n\n\n\n\n\n')
		self.jokes = dict()
		self.dupe_authors = dict()
		#self.jokes_file = open('jokes.txt', 'wb')

	@classmethod
	def from_crawler(cls, crawler):
		pipeline = cls()
		crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
		crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
		return pipeline


	def spider_opened(self, spider):
		#self.f = open('dupe.txt', 'wb')
		pass

	def add_dupe_author(self, item):
		log.msg('add_dupe_author\n\n\n\n\n\n')
		#self.f.write('added ' + item['author'].encode('UTF-8') + '\n')
		if item['author'] in self.dupe_authors:
			self.dupe_authors[item['author']].append(item)
		else:
			self.dupe_authors[item['author']] = [item]
	
	def get_original_url(self, joke_item):
		#self.f.write('get original for: ' + joke_item['url'] + '\n')
		if joke_item['text'] in self.jokes:
			items = self.jokes[joke_item['text']]
			for item in items:
				#for it in items:
					#self.f.write('orig candidate: ' + it['url'] + '\n')
				#self.f.write('\n')
				return items[0]['url']

	def spider_closed(self, spider):
		dupe_auth = open('bayanists.txt', 'wb')
		for author in self.dupe_authors:
			items = self.dupe_authors[author]
			item_count = len(items)
			if item_count == 1:
				item_count = '1 баян'
			elif (item_count%10 == 2 or item_count%10 == 3 or item_count%10 == 4)\
					and (item_count < 10 or 20 < item_count):
				item_count = str(item_count) + ' баяна'
			else:
				item_count = str(item_count) + ' баянов'
			dupe_auth.write(item_count + ' у пользователя ' + author.encode('UTF-8') + '\n')
			for item in items:
				text = item['text'].split('\n')
				if len(text) > 1:
					text = text[0] + '...'
				else:
					text = text[0]
				#dupe_auth.write(text.encode('UTF-8') + '\n')
				dupe_auth.write(item['url'])
				original_url = self.get_original_url(item)
				dupe_auth.write(' (оригинал: ' + original_url.encode('UTF-8') + ')')
				dupe_auth.write('\n')
			dupe_auth.write('\n')

		dupes_file = open('boyan.txt', 'wb')
		for joke in self.jokes:
			items = self.jokes[joke] 
			if len(items) > 1:
				dupes_file.write(str(len(items)) + '-кратный баян:\n'\
						+ joke.encode('UTF-8') + '\n')
				for item in items:
					dupes_file.write(item['url'].encode('UTF-8') + '\n')
				dupes_file.write('\n')

	def process_item(self, item, spider):
		new_jokes = set(it for it in item['text'])
		for joke in new_jokes:
			itm = JokeItem()
			itm['author'] = item['author']
			itm['text'] = joke
			itm['url'] = item['url']
			if joke in self.jokes:
				joke_items = self.jokes[joke]
				#self.f.write('adding duplicate joke:\n ' + joke.encode('UTF-8') + '\n')
				# original
				if ixbt_url_less(item['url'], joke_items[0]['url']):
					self.add_dupe_author(self.jokes[joke][0])
					self.jokes[joke].insert(0, itm)
				else:
					# find place to insert
					i = 1
					while i < len(joke_items)\
							and not ixbt_url_less(item['url'], joke_items[i]['url']):
						i += 1
					self.jokes[joke].insert(i, itm)
					self.add_dupe_author(itm)
			else:
				self.jokes[joke] = [itm]

		return item

class JsonExportPipeline(object):
	def __init__(self):
		self.files = {}

	@classmethod
	def from_crawler(cls, crawler):
		pipeline = cls()
		crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
		crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
		return pipeline

	def spider_opened(self, spider):
		#file = open('%_ixbt_jokes.json' % spider.name, 'w+b')
		file = open('ixbt_jokes.json', 'w+b')
		self.files[spider] = file
		self.exporter = JsonItemExporter(file)
		self.exporter.start_exporting()

	def spider_closed(self, spider):
		self.exporter.finish_exporting()
		file = self.files.pop(spider)
		file.close()

	def process_item(self, item, spider):
		self.exporter.export_item(item)
		return item
