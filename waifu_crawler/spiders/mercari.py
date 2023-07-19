import scrapy

from seleniumwire.utils import decode
from py_utils import db_utils
import pandas as pd
from urllib.parse import quote_plus
import os
import json
from waifu_crawler.items import WaifuCrawlerItem
from loguru import logger

df_col_dict = {
    "id": int,
    "keyword": str,
    'fuzzy_result': object,
    'exact_result': object,
    'last_fr': object,
    'last_er': object
}
array_2_list_keys = ["fuzzy_result", "exact_result", "last_fr", "last_er"]


class MercariSpider(scrapy.Spider):
    name = "mercari"
    allowed_domains = ["jp.mercari.com"]
    db_conn = db_utils.DbConnection()
    mercari_data_df = pd.read_sql_table(
        table_name=os.getenv("mercari_table", "mercari"),
        con=db_conn.conn_engine,
        schema=os.getenv("mercari_schema", "public"),
        columns=list(df_col_dict.keys())
    )
    mercari_data_df = mercari_data_df.astype(
        df_col_dict
    )
    for array_2_list_key in array_2_list_keys:
        mercari_data_df[array_2_list_key] = mercari_data_df[array_2_list_key].apply(
            lambda cell: cell.strip("{}").split(",") if cell else None)
    mercari_start_urls = [
        ("https://jp.mercari.com/search?keyword={kw}&order=desc&sort=created_time&status=on_sale".format(
            kw=quote_plus(item)), item) for item in mercari_data_df["keyword"].to_list()]
    start_urls = mercari_start_urls

    def __init__(self):
        # self.browser = webdriver.Chrome(options=chrome_options,
        #                                 seleniumwire_options=seleniumwire_options)
        super().__init__()

    def start_requests(self):
        for url, kw in self.start_urls:
            print(f"从煤炉开始查询关键词{kw}")
            yield scrapy.Request(url=url, callback=self.parse, meta={"original_url": url, "kw": kw, "index": 0})

    def parse(self, response):
        response_body = decode(response.body, response.headers.get("Content-Encoding", "identity").decode("utf-8"))
        try:
            res_dict = dict(json.loads(response_body.decode("utf-8")))
        except Exception as e:
            logger.exception(f"请求{response.url}失败 , 报错信息为{e}")
        else:
            id_list = sorted([item["id"] for item in res_dict["items"]])
            logger.info(f"关键词: {response.meta['kw']} - 当前页面token: {response.meta['index']}: {id_list}")
            res_item = WaifuCrawlerItem()
            res_item["id"] = str(response.meta["kw"])
            res_item["item_list"] = id_list
            yield res_item
            next_page_token = res_dict["meta"]["nextPageToken"]
            if next_page_token:
                print(f"查询下一页{next_page_token}，关键词为{response.meta['kw']}")
                next_url = str(response.meta["original_url"]) + "&page_token=" + str(quote_plus(next_page_token))
                yield scrapy.Request(url=next_url, callback=self.parse,
                                     meta={"original_url": response.meta["original_url"],
                                           "kw": response.meta["kw"],
                                           "index": next_page_token})

    def close(self, spider):
        print('爬虫结束，关闭浏览器')
