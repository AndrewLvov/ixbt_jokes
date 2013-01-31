# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

#def serialize_jokes(jokes):
	#str = ''
	#for joke in jokes:
		#str = str + joke + '\n'

class IxbtItem(Item):
	author = Field()
	text = Field()
	grats = Field()
	url = Field()

class JokeItem(Item):
	author = Field()
	text = Field()
	url = Field()
