# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class WaifuCrawlerPipeline:
    def __init__(self):
        self.merged_results = []


    def process_item(self, item, spider):
        self.merged_results.append(ItemAdapter(item).asdict())
        return item

    def close_spider(self, spider):
        print("test")
        return None