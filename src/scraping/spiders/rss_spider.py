
import scrapy
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import openai
import json
from src.data.models.database import get_session
from src.data.models.article import Article
from src.data.models.analysis_summary import AnalysisSummary
from datetime import datetime
import scrapy

# RSS feeds configuration
rss_feeds = [
    {"url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "name": "CoinDesk"},
    {"url": "https://cointelegraph.com/rss", "name": "CoinTelegraph"},
    {"url": "https://bitcoinmagazine.com/.rss/full/", "name": "Bitcoin Magazine"},
    {"url": "https://cryptoslate.com/feed/", "name": "CryptoSlate"},
    {"url": "https://www.newsbtc.com/feed/", "name": "NewsBTC"}
]

class RSSSpider(scrapy.Spider):
    name = "rss_spider"

    def start_requests(self):
        for feed in rss_feeds:
            yield scrapy.Request(feed["url"], callback=self.parse_rss, meta={"source_name": feed["name"]})

    def parse_rss(self, response):
        source_name = response.meta["source_name"]
        root = ET.fromstring(response.body)

        for item in root.findall(".//item")[:5]:
            title = item.findtext("title")
            link = item.findtext("link")
            content_encoded = item.find("{http://purl.org/rss/1.0/modules/content/}encoded")
            description = item.findtext("description")

            if content_encoded is not None:
                content = BeautifulSoup(content_encoded.text, "html.parser").get_text(strip=True)
            else:
                content = description or ""

            yield scrapy.Request(link, callback=self.parse_article, meta={
                "source_name": source_name,
                "title": title,
                "url": link,
                "content": content
            })