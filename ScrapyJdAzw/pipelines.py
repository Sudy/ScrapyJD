# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import log
#from scrapy.core.exceptions import DropItem
from twisted.enterprise import adbapi

import time
import MySQLdb.cursors

class ScrapyjdazwPipeline(object):

    def __init__(self):
        # @@@ hardcoded db settings
        # TODO: make settings configurable through settings
        self.dbpool = adbapi.ConnectionPool('MySQLdb',
                db='jddata',
                user='root',
                passwd='123456',
                cursorclass=MySQLdb.cursors.DictCursor,
                charset='utf8',
                use_unicode=True
            )

    def process_item(self, item, spider):
        # run db query in thread pool
        if item.has_key("pinfo"):
            result = ""
            for it in item["pinfo"]:
                result += it.strip()
            item["pinfo"] = result
        


        #query = self.dbpool.runInteraction(self._conditional_insert, item)
        #query.addErrback(self.handle_error)

        return item

    def _conditional_insert(self, tx, item):
        # create record if doesn't exist. 
        # all this block run on it's own thread
        tx.execute("select * from sites where url = %s", (item['url'][0], ))
        result = tx.fetchone()
        if result:
            log.msg("Item already stored in db: %s" % item, level=log.DEBUG)
        else:
            tx.execute(\
                "insert into sites (name, url, description, created) "
                "values (%s, %s, %s, %s)",
                (item['name'][0],
                 item['url'][0],
                 item['description'][0],
                 time.time())
            )
            log.msg("Item stored in db: %s" % item, level=log.DEBUG)

    def handle_error(self, e):
        log.err(e)