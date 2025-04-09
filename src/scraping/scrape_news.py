import scrapy
import openai
import json
import time
import yaml
import os
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime
from src.data.models.database import get_session
from src.data.models.article import Article
from src.data.models.analysis_summary import AnalysisSummary

def get_config():
    current_dir = os.path.dirname(__file__)
    config_path = os.path.abspath(os.path.join(current_dir, '../config/config.yml'))
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

config = get_config()
client = openai.OpenAI(api_key=config["openai"]["api_key"])

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
            self.logger.info(f"Requesting RSS feed: {feed['url']} for source {feed['name']}")
            yield scrapy.Request(feed["url"], callback=self.parse_rss, meta={"source_name": feed["name"]})
 
    def parse_rss(self, response):
        source_name = response.meta["source_name"]
        try:
            root = ET.fromstring(response.body)
        except Exception as e:
            self.logger.error(f"Error parsing XML from {response.url}: {e}")
            return
        for item in root.findall(".//item")[:5]:
            title = item.findtext("title")
            link = item.findtext("link")
            content_encoded = item.find("{http://purl.org/rss/1.0/modules/content/}encoded")
            description = item.findtext("description")
            content = BeautifulSoup(content_encoded.text, "html.parser").get_text(strip=True) if content_encoded else description or ""
            self.logger.info(f"Found article: {title} from {source_name}")
            yield scrapy.Request(link, callback=self.parse_article, meta={
                "source_name": source_name,
                "title": title,
                "url": link,
                "content": content
            })

    def parse_article(self, response):
        title = response.meta["title"]
        url = response.meta["url"]
        content = response.meta["content"]
        source_name = response.meta["source_name"]

        with get_session() as session:
            existing_article = session.query(Article).filter_by(url=url).first()
            if existing_article:
                self.logger.info(f"Skipping duplicate article: {title} ({url})")
                return

            article = Article(
                source=source_name,
                title=title,
                url=url,
                content=content,
                published_at=datetime.utcnow()
            )
            session.add(article)
            session.flush()
            self.logger.info(f"Article saved: {title}")

            analysis = self.analyze_article_with_gpt(title, content)

            analysis_summary = AnalysisSummary(
                article_id=article.id,
                sentiment=analysis["sentiment"],
                key_points=analysis["key_points"],
                potential_impact=analysis["potential_impact"],
                credibility_issues=analysis["credibility_issues"]
            )
            session.add(analysis_summary)
            session.commit()
            self.logger.info(f"Analysis summary saved for article: {title}")

        yield {
            "source": source_name,
            "title": title,
            "url": url,
            "analysis": analysis
        }

    def analyze_article_with_gpt(self, title, content):
        max_retries = 3
        retry_delay = 5  # seconds
        for attempt in range(max_retries):
            try:
                prompt = (
                    f"Analyze this Bitcoin (BTC) article. Respond only in JSON:\n\n"
                    f"Title: {title}\nContent: {content}\n\n"
                    f"Keys: sentiment, key_points (max 5), potential_impact, credibility_issues."
                )
                response = client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.2,
                )
                if response.choices:
                    raw_text = response.choices[0].message.content.strip()
                    raw_text = raw_text.replace("```json", "").replace("```", "").strip()
                    analysis_json = json.loads(raw_text)
                    sentiment = analysis_json["sentiment"].capitalize()
                    if sentiment not in ["Neutral", "Bullish", "Bearish"]:
                        sentiment = "Neutral"
                    analysis_json["sentiment"] = sentiment
                    self.logger.info(f"GPT analysis successful for article: {title}")
                    return analysis_json
            except Exception as e:
                self.logger.error(f"Error during GPT analysis (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
        self.logger.warning(f"Using default analysis for article: {title} after {max_retries} attempts")
        return {"sentiment": "Neutral", "key_points": [], "potential_impact": "N/A", "credibility_issues": None}
