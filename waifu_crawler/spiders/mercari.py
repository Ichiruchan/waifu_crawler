import scrapy
from seleniumwire import webdriver
from seleniumwire.utils import decode
from py_utils import db_utils
import pandas as pd
from urllib.parse import quote_plus
import os
import json

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
    mercari_start_urls = [
        "https://jp.mercari.com/search?keyword={kw}&order=desc&sort=created_time&status=on_sale".format(
            kw=quote_plus(item)) for item in (mercari_data_df["keyword"].to_list())]

    start_urls = mercari_start_urls

    def __init__(self):
        self.browser = webdriver.Chrome(options=chrome_options,
                                        seleniumwire_options=seleniumwire_options)
        super().__init__()

    def parse(self, response):
        response_body = decode(response.body, response.headers.get("Content-Encoding", "identity").decode("utf-8"))
        print("Get response body")
        res_dict = dict(json.loads(response_body.decode("utf-8")))
        pass
        # filename = "test.html"
        # with open(filename, "wb") as f:
        #     f.write(response.body)

    def close(self, spider):
        print('爬虫结束，关闭浏览器')
        self.browser.quit()
