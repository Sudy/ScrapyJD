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
                host='192.168.1.153'
                db='jddata',
                user='spider',
                passwd='spider1234',
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
        
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        query.addErrback(self.handle_error)

        return item

    def _conditional_insert(self, tx, item):
        # create record if doesn't exist. 
        # all this block run on it's own thread

        if item.has_key("pinfo"):
            tx.execute(\
                "insert into product_table (pro_id, pro_info, pro_price) "
                "values (%s, %s, %s)",
                (    item['proid'],
                     item['pinfo'],
                     item['pricejd'],
                 )
            )
        else:
            tx.execute(\
                "insert into comment_table (pro_id, user, time, score, comment) "
                "values (%s, %s, %s, %s, %s)",
                (    item['proid'],
                     item['user'],
                     item['time'],
                     item['score'],
                     item['comment'],
                 )
            )

        log.msg("Item stored in db: %s" % item["proid"], level=log.INFO)
    def handle_error(self, e):
        log.err(e)