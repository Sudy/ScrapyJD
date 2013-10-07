# Scrapy settings for ScrapyJdAzw project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'ScrapyJdAzw'

SPIDER_MODULES = ['ScrapyJdAzw.spiders']
NEWSPIDER_MODULE = 'ScrapyJdAzw.spiders'

SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = True
SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"


ITEM_PIPELINES = [
    'ScrapyJdAzw.pipelines.ScrapyjdazwPipeline',
]

CONCURRENT_REQUESTS = 50
# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'jdspider'
#DOWNLOAD_DELAY = 2
DOWNLOAD_TIMEOUT = 10

# Specify the host and port to use when connecting to Redis (optional).
REDIS_HOST = '172.17.161.101'
REDIS_PORT = 6379