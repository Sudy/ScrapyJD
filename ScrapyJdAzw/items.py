# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class ScrapyjdazwItem(Item):
    # define the fields for your item here like:
    # name = Field()
    #username, purchase time,score given and comment given
    
    proid = Field()
    user = Field()
    time = Field()
    score = Field()
    comment = Field()


class ProductItem(Item):
    # define the fields for your item here like:
    # product id, product information
    # product market price,prodcut jd price
    proid = Field()
    pinfo = Field()
    #pricemk = Field()
    pricejd = Field()
