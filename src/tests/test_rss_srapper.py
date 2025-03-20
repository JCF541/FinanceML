import pytest
import json
from unittest.mock import patch, MagicMock
from scrapy.http import Request, HtmlResponse
from src.scraping.scrape_news import RSSSpider
from src.data.models.article import Article
from src.data.models.analysis_summary import AnalysisSummary

@pytest.fixture
def spider():
    return RSSSpider()

@patch("src.scraping.scrape_news.client.chat.completions.create")
def test_rss_spider_parse_article(mock_openai_api, spider, db_session):
    mock_analysis = {
        "sentiment": "Bullish",
        "key_points": ["Institutional interest increasing", "New market ATH"],
        "potential_impact": "Positive short-term momentum",
        "credibility_issues": None
    }
    mock_openai_api.return_value.choices = [MagicMock()]
    mock_openai_api.return_value.choices[0].message.content = json.dumps(mock_analysis)

    request = Request(
        url="https://example.com/bitcoin-new-high",
        meta={
            "source_name": "MockSource",
            "title": "Bitcoin Hits New High",
            "url": "https://example.com/bitcoin-new-high",
            "content": "Bitcoin has reached a new all-time high."
        }
    )
    response = HtmlResponse(
        url=request.url,
        body="<html></html>".encode("utf-8"),
        encoding='utf-8',
        request=request
    )

    original_get_session = spider.parse_article.__globals__['get_session']
    spider.parse_article.__globals__['get_session'] = lambda: db_session

    result = next(spider.parse_article(response))

    assert result['source'] == 'MockSource'
    assert result['analysis']['sentiment'] == 'Bullish'
