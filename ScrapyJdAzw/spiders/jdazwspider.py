from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from ScrapyJdAzw.items import ScrapyjdazwItem,ProductItem
from scrapy.http import Request
import re
import math

class JdAzwSpider(CrawlSpider):
    name = 'jdazw'
    allowed_domains = ['m.jd.com',]
    
    #start_urls = [#'http://m.jd.com/category/1319.html']
    #                'http://m.jd.com/ware/comments.action?wareId=1021960473&score=5&page=15']


    #rules = (
        #Rule(SgmlLinkExtractor(allow=("http://m\.jd\.com/category/*"),restrict_xpaths='//div[@class="mc"]')),
        #Rule(SgmlLinkExtractor(allow=("http://m\.jd\.com/products/*",)),callback='parse_products'),
        #Rule(SgmlLinkExtractor(allow=("http://m\.jd\.com/product/*",)),callback='parse_product'),        
        #Rule(SgmlLinkExtractor(allow=("http://m\.jd\.com/comments/*",)),callback='parse_comment'),
    #   Rule(SgmlLinkExtractor(allow=("http://m\.jd\.com/ware/comments\.action\?wareId=*",)),callback='parse_ware'),
    #)

    def start_requests(self):
        yield Request(url='http://m.jd.com/ware/comments.action?wareId=1021960473&score=5&page=15',callback=self.parse_ware)
    
    def parse_products(self,response):
        hxs = HtmlXPathSelector(response)
        try:
            product_urls = hxs.select('//div[@class="pmc"]/div[@class="title"]/a/@href').extract()

            #go to product url
            for url in product_urls:
                self.log("http://m.jd.com" + url)
                yield Request(url="http://m.jd.com" + url,callback=self.parse_product)

            #get the next page
            next_page_url = hxs.select('//div[@class="page"]/a/@href').extract()[0]
            self.log("http://m.jd.com" + next_page_url)

            yield Request(url="http://m.jd.com" + next_page_url,callback=self.parse_products)
        
        except:
            pass

    def parse_product(self,response):

        hxs = HtmlXPathSelector(response)
        
        try:
            #product item information 
            pro_item = ProductItem()

            pro_item['pinfo'] = hxs.select('//div[@class="pro"]//text()[not(parent::font)]').extract()
            
            item =  hxs.select('//div[@class="content content2"]')
            #pro_item['pricemk'] = item.select('div[@class="p-price"]/del/font/text()').extract()[0].strip()
            pro_item['pricejd'] = item.select('div[@class="p-price"]/font[@color="red"]/text()').extract()[0].strip()
            pro_item['proid'] = item.select('div[@style="padding-bottom:5px;"]/text()').extract()[0].split(" ",1)[1].strip()

            yield pro_item

            comment_url = hxs.select('//div[@class="content content2"]//a[3]/@href').extract()[0]
            redirect_url = "http://m.jd.com" + comment_url
            self.log(redirect_url)
            yield Request(url = redirect_url,callback=self.parse_comment)
        except:
            pass
        

    def get_page(self,total):
        return int(math.ceil(1.0*int(total)/15))


    def parse_comment(self,response):

        hxs = HtmlXPathSelector(response)
        try:
            proid_pattern =  re.compile('/([0-9]+)')
            proid_match = proid_pattern.search(response.url)
            if None == proid_match:
                return

            wareid = proid_match.group(1)

            marks = hxs.select('//div[@class="content"]//font[@color="orange"]/text()').extract()
            #http://m.jd.com/ware/comments.action?wareId=244923&score=5
            if len(marks) == 3:
                good_page = self.get_page(marks[0])
                middle_page  =  self.get_page(marks[1])
                bad_page = self.get_page(marks[2])

                for page in range(0,good_page):
                    url = "http://m.jd.com/ware/comments.action?wareId="+ wareid + "&score=5&page=" + str(page+1)
                    #self.log(url)
                    yield Request(url = url,callback=self.parse_ware)
                
                for page in range(0,middle_page):
                    url = "http://m.jd.com/ware/comments.action?wareId="+ wareid + "&score=3&page=" + str(page+1)
                    #self.log(url)
                    yield Request(url = url,callback=self.parse_ware)
                
                for page in range(0,bad_page):
                    url = "http://m.jd.com/ware/comments.action?wareId="+ wareid + "&score=1&page=" + str(page+1)
                    #self.log(url)
                    yield Request(url = url,callback=self.parse_ware)
        except:
            pass

    def parse_ware(self,response):
        hxs = HtmlXPathSelector(response)
        try:
            #product id pattern
            proid_pattern = re.compile("wareId=([0-9]+)")


            productid = 0
            proid_match = proid_pattern.search(response.url)
            if None != proid_match:
                productid =  int(proid_match.group(1))

            #comments
            comments = hxs.select('//div[@class="eval"]') 

            for comment in comments:

                product_item = ScrapyjdazwItem()
                product_item['proid'] =  productid
                #get user and time
                user_time = comment.select('div[@class="u-info"][2]//text()').extract()[0]
                result = user_time.split(" ",1)
     
                product_item['user'] =  result[0].strip()
                product_item['time'] =  result[1].strip()
                product_item['score'] = comment.select('div[@class="u-score"]/span/text()').extract()[0]
                product_item['comment'] = comment.select('div[@class="u-summ"]/text()').extract()[0]
                
                yield product_item
        except:
            pass