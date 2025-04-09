from flask import Flask, jsonify, request
from src.data.models.database import get_session
from src.data.models.analysis_summary import AnalysisSummary
from src.processing.memo_engine import MemoEngine
from datetime import datetime, timedelta
import logging

app = Flask(__name__)

# Configure logging for the API
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.route("/api/analyses", methods=["GET"])
def get_analyses():
    period = request.args.get("period", "daily")
    logger.info(f"Received request for analyses with period: {period}")
    today = datetime.utcnow().date()
    period_start = MemoEngine.get_period_start(today, period)
    try:
        with get_session() as session:
            analyses = session.query(AnalysisSummary).filter(AnalysisSummary.created_at >= period_start).all()
            logger.info(f"Fetched {len(analyses)} analysis summaries from the database.")
            results = [
                {
                    "article_id": a.article_id,
                    "sentiment": a.sentiment,
                    "key_points": a.key_points,
                    "potential_impact": a.potential_impact,
                    "credibility_issues": a.credibility_issues,
                    "created_at": a.created_at.isoformat()
                } for a in analyses
            ]
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error fetching analyses: {e}")
        return jsonify({"error": "An error occurred fetching analyses"}), 500

@app.route("/api/memos/<period>", methods=["GET"])
def get_memo(period):
    logger.info(f"Received request for memo with period: {period}")
    try:
        memo_engine = MemoEngine(period)
        memo = memo_engine.generate_memo()
        logger.info("Memo generated successfully.")
        return jsonify(memo)
    except Exception as e:
        logger.error(f"Error generating memo: {e}")
        return jsonify({"error": "An error occurred generating memo"}), 500

if __name__ == "__main__":
    app.run(debug=True)
