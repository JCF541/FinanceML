import pandas as pd
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from src.data.models.database import engine
from src.data.models.analysis_summary import AnalysisSummary
import logging

logger = logging.getLogger(__name__)

class MemoEngine:
    def __init__(self, period="daily", data=None):
        self.period = period
        self.session = sessionmaker(bind=engine)()
        if data is not None:
            self.df = pd.DataFrame(data)
        else:
            self.df = self.fetch_analysis_data()
            logger.info(f"Fetched {len(self.df)} analysis records for memo generation.")

    @staticmethod
    def get_period_start(today, period):
        if period == "daily":
            return today
        elif period == "weekly":
            return today - timedelta(days=today.weekday())
        elif period == "monthly":
            return today.replace(day=1)
        elif period == "quarterly":
            return today.replace(day=1, month=((today.month - 1) // 3) * 3 + 1)
        elif period == "yearly":
            return today.replace(day=1, month=1)
        return today

    def fetch_analysis_data(self):
        today = datetime.utcnow().date()
        period_start = self.get_period_start(today, self.period)
        try:
            query = self.session.query(AnalysisSummary).filter(
                AnalysisSummary.created_at >= period_start
            ).all()
            logger.info(f"Fetched {len(query)} analysis summaries since {period_start}.")
        except Exception as e:
            logger.error(f"Error fetching analysis data: {e}")
            query = []
        records = [
            {
                "date": record.created_at,
                "title": record.article.title,
                "url": record.article.url,
                "bullish_signal": record.sentiment == "Bullish",
                "bearish_signal": record.sentiment == "Bearish",
                "fact_check_flag": bool(record.credibility_issues),
                "key_points": record.key_points
            }
            for record in query
        ]
        return pd.DataFrame(records)

    def generate_summary(self):
        if self.df.empty:
            logger.info("No analysis data available, returning zero counts.")
            return {"bullish_count": 0, "bearish_count": 0, "fact_check_flags": 0}
        bullish_count = self.df["bullish_signal"].sum()
        bearish_count = self.df["bearish_signal"].sum()
        fact_check_flags = self.df["fact_check_flag"].sum()
        summary = {
            "bullish_count": int(bullish_count),
            "bearish_count": int(bearish_count),
            "fact_check_flags": int(fact_check_flags),
        }
        logger.info(f"Generated summary: {summary}")
        return summary

    def detect_trend(self, summary):
        if summary["bullish_count"] > summary["bearish_count"]:
            trend = "Bullish"
        elif summary["bearish_count"] > summary["bullish_count"]:
            trend = "Bearish"
        else:
            trend = "Neutral"
        logger.info(f"Detected market trend: {trend}")
        return trend

    def extract_key_articles(self):
        if self.df.empty:
            logger.info("No analysis data for key articles extraction.")
            return []
        key_articles = self.df[self.df["bullish_signal"]].head(3)[["title", "url"]].to_dict(orient="records")
        logger.info(f"Extracted key articles: {key_articles}")
        return key_articles

    def generate_memo(self):
        summary = self.generate_summary()
        trend = self.detect_trend(summary)
        key_articles = self.extract_key_articles()
        memo = {
            "period": self.period.capitalize(),
            "date_generated": datetime.utcnow().isoformat(),
            "market_trend": trend,
            "summary": summary,
            "key_articles": key_articles,
        }
        logger.info("Memo generated successfully.")
        return memo

    def save_memo(self):
        memo = self.generate_memo()
        file_path = f"memos/{self.period}_memo_{datetime.utcnow().strftime('%Y-%m-%d')}.json"
        try:
            with open(file_path, "w") as f:
                json.dump(memo, f, indent=4)
            logger.info(f"Memo saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving memo to {file_path}: {e}")

    def run(self):
        self.save_memo()
