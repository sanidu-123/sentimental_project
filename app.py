from flask import Flask, request, jsonify
from transformers import pipeline
import sqlite3
import torch

app = Flask(__name__, static_folder='static')

# Ensure PyTorch is used
device = 0 if torch.cuda.is_available() else -1  # Use GPU if available, else CPU
classifier = pipeline('sentiment-analysis', device=device)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('sentiment.db')
    conn.row_factory = sqlite3.Row  # Allows fetching rows as dictionaries
    return conn

# Initialize the database
def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS analyses
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                     text TEXT,
                     label TEXT,
                     score REAL)''')
    conn.commit()
    conn.close()

init_db()

# Serve the frontend
@app.route('/')
def index():
    return app.send_static_file('index.html')

# Endpoint to analyze sentiment
@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "No text provided"}), 400

    result = classifier(text)[0]  # Returns a list with one dict
    label = result['label']  # 'POSITIVE' or 'NEGATIVE'
    score = result['score']  # Confidence score
    
    # Store the result in the database
    conn = get_db_connection()
    conn.execute('INSERT INTO analyses (text, label, score) VALUES (?, ?, ?)',
                 (text, label, score))
    conn.commit()
    conn.close()
    
    return jsonify(result)

# Endpoint to retrieve statistics for the dashboard
@app.route('/stats', methods=['GET'])
def stats():
    conn = get_db_connection()
    sentiment_counts = conn.execute('SELECT label, COUNT(*) FROM analyses GROUP BY label').fetchall()
    analyses = conn.execute('SELECT timestamp, label, score FROM analyses ORDER BY timestamp').fetchall()
    conn.close()
    
    sentiment_counts_dict = {row['label']: row['COUNT(*)'] for row in sentiment_counts}
    analyses_list = [
        {'timestamp': row['timestamp'], 'sentiment': row['score'] if row['label'] == 'POSITIVE' else -row['score']}
        for row in analyses
    ]
    
    return jsonify({
        'sentiment_counts': sentiment_counts_dict,
        'analyses': analyses_list
    })

if __name__ == '__main__':
    app.run(debug=True)
