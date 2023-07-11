import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# proxy_url = "socks5://127.0.0.1:7890"
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument(f"--proxy-server={proxy_url}")

class MercariSpider(scrapy.Spider):
    name = "mercari"
    allowed_domains = ["jp.mercari.com"]
    start_urls = ["https://jp.mercari.com/search?keyword=%E3%82%A2%E3%83%89%E3%83%9E%E3%82%A4%E3%83%A4%E3%83%99%E3%82%AC%20%E3%83%90%E3%83%83%E3%82%B8"]

    def __init__(self):
        self.browser = webdriver.Chrome(options=chrome_options)
        super().__init__()

    def parse(self, response):
        print("ok1")
        # filename = "test.html"
        # with open(filename, "wb") as f:
        #     f.write(response.body)

    def close(self, spider):
        print('爬虫结束，关闭浏览器')
        self.browser.quit()

