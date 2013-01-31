# Scrapy settings for ixbt project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'ixbt'

SPIDER_MODULES = ['ixbt.spiders']
NEWSPIDER_MODULE = 'ixbt.spiders'

ITEM_PIPELINES = [
	'ixbt.pipelines.DupesPipeline',
	'ixbt.pipelines.JsonExportPipeline',
]

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ixbt (+http://www.yourdomain.com)'
