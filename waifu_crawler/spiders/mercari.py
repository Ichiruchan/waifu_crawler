import scrapy
from seleniumwire import webdriver
from seleniumwire.utils import decode
from py_utils import db_utils
import pandas as pd
from urllib.parse import quote_plus
import os
import json
from waifu_crawler.items import WaifuCrawlerItem

seleniumwire_options = {
            'proxy': {
                'http': 'http://127.0.0.1:7890',
                'https': 'http://127.0.0.1:7890',
                'no_proxy': 'localhost,127.0.0.1'
            }
        }
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-gpu")


class MercariSpider(scrapy.Spider):
    name = "mercari"
    allowed_domains = ["jp.mercari.com"]
    db_conn = db_utils.DbConnection()
    mercari_data_df = pd.read_sql_table(
        table_name=os.getenv("mercari_table", "mercari"),
        con=db_conn.conn_engine,
        schema=os.getenv("mercari_schema", "public")
    )
    kw_list = mercari_data_df["keyword"].to_list()
    mercari_start_urls = [
        ("https://jp.mercari.com/search?keyword={kw}&order=desc&sort=created_time&status=on_sale".format(
            kw=quote_plus(item)), item) for item in kw_list]

    start_urls = mercari_start_urls

    def __init__(self):
        self.browser = webdriver.Chrome(options=chrome_options,
                                        seleniumwire_options=seleniumwire_options)
        super().__init__()

    def start_requests(self):
        for url, kw in self.start_urls:
            print(f"从煤炉开始查询关键词{kw}")
            yield scrapy.Request(url=url, callback=self.parse, meta={"original_url": url, "kw": kw, "index": 0})

    def parse(self, response):
        response_body = decode(response.body, response.headers.get("Content-Encoding", "identity").decode("utf-8"))
        res_dict = dict(json.loads(response_body.decode("utf-8")))
        id_list = [item["id"] for item in res_dict["items"]]
        next_page_token = res_dict["meta"]["nextPageToken"]

        scrapy_item = WaifuCrawlerItem()
        scrapy_item["id"] = str(response.meta["kw"])
        scrapy_item["item_list"] = id_list
        yield scrapy_item

            # if next_page_token:
            #
            #     print(f"查询下一页{next_page_token}，关键词为{response.meta['kw']}")
            #     next_url = str(response.meta["original_url"]) + "&page_token=" + str(quote_plus(next_page_token))
            #     yield scrapy.Request(url=next_url, callback=self.parse, meta={"original_url": response.meta["original_url"],
            #                                                                   "kw": response.meta["kw"],
            #                                                                   "index": response.meta["index"] + 1})


        # filename = "test.html"
        # with open(filename, "wb") as f:
        #     f.write(response.body)

    def close(self, spider):
        print('爬虫结束，关闭浏览器')
        self.browser.quit()
