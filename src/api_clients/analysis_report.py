from flask import Flask, jsonify, request
from src.data.models.database import get_session
from src.data.models.analysis_summary import AnalysisSummary
from src.processing.memo_engine import MemoEngine
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route("/api/analyses", methods=["GET"])
def get_analyses():
    period = request.args.get("period", "daily")

    today = datetime.utcnow().date()
    period_start = MemoEngine.get_period_start(None, today, period)

    with get_session() as session:
        analyses = session.query(AnalysisSummary).filter(AnalysisSummary.created_at >= period_start).all()

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

@app.route("/api/memos/<period>", methods=["GET"])
def get_memo(period):
    memo_engine = MemoEngine(period)
    memo = memo_engine.generate_memo()
    return jsonify(memo)

if __name__ == "__main__":
    app.run(debug=True)
