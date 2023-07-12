import scrapy
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
sw_options = {
    "proxy":
        {
            "http": "socks5://127.0.0.1:7890",
            "https": "socks5://127.0.0.1:7890",
            "no_proxy": "localhost,127.0.0.1"
        }
}


class MercariSpider(scrapy.Spider):
    name = "mercari"
    allowed_domains = ["jp.mercari.com"]
    start_urls = ["https://jp.mercari.com/search?keyword=%E3%82%A2%E3%83%89%E3%83%9E%E3%82%A4%E3%83%A4%E3%83%99%E3%82%AC%20%E3%83%90%E3%83%83%E3%82%B8"]

    def __init__(self):
        self.browser = webdriver.Chrome(options=chrome_options,
                                        seleniumwire_options=sw_options)
        super().__init__()

    def parse(self, response):
        print("test")
        pass
        # filename = "test.html"
        # with open(filename, "wb") as f:
        #     f.write(response.body)

    def close(self, spider):
        print('爬虫结束，关闭浏览器')
        self.browser.quit()

