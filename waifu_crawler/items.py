# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WaifuCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    item_list = scrapy.Field()


