# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pandas as pd
from itemadapter import ItemAdapter
import os
from loguru import logger


class WaifuCrawlerPipeline:
    def __init__(self):
        self.result_list = []

    def process_item(self, item, spider):
        self.result_list.append(ItemAdapter(item).asdict())
        return item

    def close_spider(self, spider):  # next_page_token = res_dict["meta"]["nextPageToken"]
        merged_result_dict = {}
        for result in self.result_list:
            item_name = result["id"]
            item_list = result["item_list"]
            if item_name in (merged_result_dict.keys()):
                merged_result_dict[item_name].extend(item_list)
            else:
                merged_result_dict[item_name] = item_list
        updated_df = spider.mercari_data_df.copy()
        for k, v in merged_result_dict.items():
            last_fr = updated_df.loc[updated_df["keyword"] == k].iloc[0]["last_fr"]
            fuzzy_result = updated_df.loc[updated_df["keyword"] == k].iloc[0]["fuzzy_result"]
            replace_index = updated_df.loc[updated_df["keyword"] == k].index[0]
            if last_fr is None and fuzzy_result is None:
                updated_df.at[replace_index, "last_fr"] = v
                updated_df.at[replace_index, "fuzzy_result"] = v
            elif sorted(v) != sorted(fuzzy_result):
                updated_df.at[replace_index, "last_fr"] = fuzzy_result
                updated_df.at[replace_index, "fuzzy_result"] = v
        if (updated_df.sort_values(by=["id"])).equals(
                spider.mercari_data_df.sort_values(by=["id"])):
            logger.info("无更新")
        else:
            updated_df.to_sql(name=os.getenv("mercari_table", "mercari"),
                              con=spider.db_conn.conn_engine,
                              schema=os.getenv("mercari_schema", "public"),
                              if_exists="replace",
                              index=False
                              )
        return None
