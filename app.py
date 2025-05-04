from flask import Flask, request, jsonify, abort
from transformers import pipeline
import sqlite3
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import datetime
import os
import logging
from wordcloud import WordCloud
import io
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download necessary NLTK data
try:
    nltk.download("stopwords", quiet=True)
    nltk.download("punkt", quiet=True)
except Exception as e:
    logger.warning(f"NLTK download failed: {e}")

app = Flask(__name__, static_folder="static")


# Initialize sentiment analysis model
def initialize_model():
    try:
        logger.info("Initializing sentiment analysis model...")
        # Use a model that supports neutral sentiment
        classifier = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment",
            device=-1,
        )  # Force CPU usage
        logger.info("Model initialized successfully")
        print("Classifier initialized:", classifier)
        return classifier
    except Exception as e:
        logger.error(f"Failed to initialize model: {str(e)}")
        print(f"Model initialization error: {str(e)}")
        raise


classifier = initialize_model()

# Database configuration
DATABASE_PATH = os.path.join(os.getcwd(), "sentiment.db")


def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise


def init_db():
    try:
        with get_db_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    text TEXT NOT NULL,
                    label TEXT CHECK(label IN ('POSITIVE', 'NEGATIVE', 'NEUTRAL')) NOT NULL,
                    score REAL CHECK(score >= 0 AND score <= 1) NOT NULL
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_timestamp ON analyses (timestamp)"
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_label ON analyses (label)")
            conn.commit()
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


init_db()


def preprocess_text(text):
    try:
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words("english"))
        return [w for w in tokens if w.isalnum() and w not in stop_words]
    except Exception as e:
        logger.warning(f"Text preprocessing failed, using fallback: {e}")
        return re.findall(
            r"\w+", text.lower()
        )  # using regex based extractions and preprocessing


# root route
@app.route("/")
def index():
    try:
        return app.send_static_file("index.html")
    except Exception as e:
        logger.error(f"Failed to serve index.html: {e}")
        abort(404, description="Frontend not found")


# analyse route
@app.route("/analyze", methods=["POST"])
def analyze():
    if not request.is_json:
        logger.error("Request is not JSON")
        abort(400, description="Request must be JSON")

    try:
        # Debug print request data
        print("Request data:", request.get_data())

        data = request.get_json()
        if not data or "text" not in data:
            logger.error("Missing text field in request")
            abort(400, description="Missing text field in request")

        text = data.get("text", "").strip()

        if not text:
            logger.error("Empty text received")
            abort(400, description="Text cannot be empty")

        # Debug print
        print(f"Processing text: {text[:100]}...")

        # Verify classifier is initialized
        if not classifier:
            logger.error("Classifier not initialized")
            abort(500, description="Sentiment analyzer not initialized")

        # Get sentiment analysis with error handling
        try:
            result = classifier(text)[0]
            print(f"Raw classifier result: {result}")  # Debug print

            # Map the model's labels to our format
            label_mapping = {
                "LABEL_0": "NEGATIVE",
                "LABEL_1": "NEUTRAL",
                "LABEL_2": "POSITIVE",
            }

            label = label_mapping.get(result["label"], "NEUTRAL")
            score = result["score"]

            # Debug print
            print(f"Analysis complete - Label: {label}, Score: {score}")

        except Exception as e:
            logger.error(f"Classifier failed: {str(e)}")
            raise Exception(f"Sentiment analysis failed: {str(e)}")

        # Store in database
        try:
            with get_db_connection() as conn:
                conn.execute(
                    "INSERT INTO analyses (text, label, score) VALUES (?, ?, ?)",
                    (text, label, score),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Database operation failed: {str(e)}")
            raise Exception(f"Failed to store analysis: {str(e)}")

        response = {
            "status": "success",
            "data": {
                "result": {"label": label, "score": score},
                "processed_text": text[:1000],  # Limit response text length
            },
        }
        return jsonify(response)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Analysis failed: {error_msg}")
        print(f"Error in /analyze endpoint: {error_msg}")  # Debug print
        return jsonify(
            {"status": "error", "message": "Analysis failed", "error": error_msg}
        ), 500


# stats endpoint to get the data from the DB and
@app.route("/stats", methods=["GET"])
def stats():
    try:
        with get_db_connection() as conn:
            analyses = conn.execute(
                "SELECT timestamp, text, label, score FROM analyses ORDER BY timestamp"
            ).fetchall()

        analyses_list = [dict(row) for row in analyses] if analyses else []

        # Initialize default empty values
        response_data = {
            "sentiment_counts": {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0},
            "score_distribution": {
                "bins": ["0.5-0.6", "0.6-0.7", "0.7-0.8", "0.8-0.9", "0.9-1.0"],
                "positive": [0, 0, 0, 0, 0],
                "negative": [0, 0, 0, 0, 0],
                "neutral": [0, 0, 0, 0, 0],
            },
            "word_frequencies": {"positive": {}, "negative": {}},
            "time_trends": {"hours": [], "positive": [], "negative": []},
            "heatmap": {
                "days": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
                "hours": [f"{h:02d}" for h in range(24)],
                "positive": [[0] * 24 for _ in range(7)],
                "negative": [[0] * 24 for _ in range(7)],
                "neutral": [[0] * 24 for _ in range(7)],
            },
        }

        if analyses_list:
            # 1. Sentiment Counts
            response_data["sentiment_counts"] = dict(
                Counter(row["label"] for row in analyses_list)
            )

            # 2. Score Distribution
            bins = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            pos_scores = [
                row["score"] for row in analyses_list if row["label"] == "POSITIVE"
            ]
            neg_scores = [
                row["score"] for row in analyses_list if row["label"] == "NEGATIVE"
            ]
            neu_scores = [
                row["score"] for row in analyses_list if row["label"] == "NEUTRAL"
            ]

            response_data["score_distribution"]["positive"] = [
                sum(1 for s in pos_scores if b1 <= s < b2)
                for b1, b2 in zip(bins[:-1], bins[1:])
            ]
            response_data["score_distribution"]["negative"] = [
                sum(1 for s in neg_scores if b1 <= s < b2)
                for b1, b2 in zip(bins[:-1], bins[1:])
            ]
            response_data["score_distribution"]["neutral"] = [
                sum(1 for s in neu_scores if b1 <= s < b2)
                for b1, b2 in zip(bins[:-1], bins[1:])
            ]

            # 3. Word Frequencies
            all_pos_text = " ".join(
                row["text"] for row in analyses_list if row["label"] == "POSITIVE"
            ).lower()
            all_neg_text = " ".join(
                row["text"] for row in analyses_list if row["label"] == "NEGATIVE"
            ).lower()

            try:
                pos_tokens = preprocess_text(all_pos_text)
                neg_tokens = preprocess_text(all_neg_text)

                response_data["word_frequencies"]["positive"] = dict(
                    Counter(pos_tokens).most_common(30)
                )
                response_data["word_frequencies"]["negative"] = dict(
                    Counter(neg_tokens).most_common(30)
                )
            except:
                response_data["word_frequencies"]["positive"] = dict(
                    Counter(re.findall(r"\w+", all_pos_text)).most_common(30)
                )
                response_data["word_frequencies"]["negative"] = dict(
                    Counter(re.findall(r"\w+", all_neg_text)).most_common(30)
                )

            # 4. Time Trends
            hour_data = {}
            for row in analyses_list:
                try:
                    hour = row["timestamp"][:13]  # Extract YYYY-MM-DD HH
                    if hour not in hour_data:
                        hour_data[hour] = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
                    hour_data[hour][row["label"]] += 1
                except:
                    continue

            response_data["time_trends"]["hours"] = sorted(hour_data.keys())
            response_data["time_trends"]["positive"] = [
                hour_data[h]["POSITIVE"] for h in response_data["time_trends"]["hours"]
            ]
            response_data["time_trends"]["negative"] = [
                hour_data[h]["NEGATIVE"] for h in response_data["time_trends"]["hours"]
            ]
            response_data["time_trends"]["neutral"] = [
                hour_data[h]["NEUTRAL"] for h in response_data["time_trends"]["hours"]
            ]

            # 5. Heatmap
            for row in analyses_list:
                try:
                    timestamp = row["timestamp"]
                    date_obj = datetime.datetime.strptime(
                        timestamp, "%Y-%m-%d %H:%M:%S"
                    )
                    day_of_week = date_obj.weekday()
                    hour = date_obj.hour

                    if row["label"] == "POSITIVE":
                        response_data["heatmap"]["positive"][day_of_week][hour] += 1
                    elif row["label"] == "NEGATIVE":
                        response_data["heatmap"]["negative"][day_of_week][hour] += 1
                    else:
                        response_data["heatmap"]["neutral"][day_of_week][hour] += 1
                except:
                    continue

        return jsonify({"status": "success", "data": response_data})
    except Exception as e:
        logger.error(f"Stats generation failed: {e}")
        abort(500, description="Could not generate statistics")


@app.route("/wordcloud/<sentiment>")
def wordcloud(sentiment):
    if sentiment not in ["positive", "negative", "neutral"]:
        abort(400, description="Invalid sentiment type")

    try:
        with get_db_connection() as conn:
            texts = conn.execute(
                "SELECT text FROM analyses WHERE label = ?", (sentiment.upper(),)
            ).fetchall()

        if not texts:
            return jsonify(
                {
                    "status": "success",
                    "data": {
                        "image": None,
                        "message": "No data available for word cloud",
                    },
                }
            )

        all_text = " ".join([t["text"] for t in texts])
        tokens = preprocess_text(all_text)
        processed_text = " ".join(tokens)

        # Update colormap to include neutral
        colormap = {"positive": "viridis", "negative": "Reds", "neutral": "Greys"}

        wc = WordCloud(
            width=800,
            height=400,
            background_color="white",
            colormap=colormap.get(sentiment, "viridis"),
            max_words=100,
        ).generate(processed_text)

        # Convert to base64 for web display
        img = io.BytesIO()
        wc.to_image().save(img, "PNG")
        img.seek(0)
        img_b64 = base64.b64encode(img.getvalue()).decode("utf-8")

        return jsonify(
            {"status": "success", "data": {"image": f"data:image/png;base64,{img_b64}"}}
        )
    except Exception as e:
        logger.error(f"Word cloud generation failed: {e}")
        abort(500, description="Could not generate word cloud")


@app.route("/recent", methods=["GET"])
def recent_analyses():
    try:
        limit = min(int(request.args.get("limit", 10)), 100)  # Cap at 100

        with get_db_connection() as conn:
            analyses = conn.execute(
                "SELECT timestamp, text, label, score FROM analyses ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()

        return jsonify(
            {
                "status": "success",
                "data": [dict(row) for row in analyses] if analyses else [],
            }
        )
    except Exception as e:
        logger.error(f"Failed to fetch recent analyses: {e}")
        abort(500, description="Could not fetch recent analyses")


@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(500)
def handle_error(e):
    return jsonify({"status": "error", "message": e.description}), e.code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
