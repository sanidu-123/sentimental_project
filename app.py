from flask import Flask, request, jsonify
from transformers import pipeline
import sqlite3
from collections import Counter
import re

app = Flask(__name__, static_folder='static')
classifier = pipeline('sentiment-analysis')

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('sentiment.db')
    conn.row_factory = sqlite3.Row  # Allows fetching rows as dictionaries
    return conn

# Initialize the database. no need after create the data base
# def init_db():
 #    conn = get_db_connection()
 #    conn.execute('''CREATE TABLE IF NOT EXISTS analyses
 #                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
  #                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  #                    text TEXT,
   #                   label TEXT,
   #                   score REAL)''')
   #  conn.commit()
   #  conn.close()

#init_db()

# Serve the frontend
@app.route('/')
def index():
    return app.send_static_file('index.html')

# Endpoint to analyze sentiment
@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    text = data['text']
    result = classifier(text)[0]
    label = result['label']
    score = result['score']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO analyses (text, label, score) VALUES (?, ?, ?)',
                 (text, label, score))
    conn.commit()
    conn.close()
    
    return jsonify(result)

# Endpoint to retrieve all statistics
@app.route('/stats', methods=['GET'])
def stats():
    conn = get_db_connection()
    analyses = conn.execute('SELECT timestamp, text, label, score FROM analyses ORDER BY timestamp').fetchall()

    # 1. Sentiment Counts (Pie Chart)
    sentiment_counts = Counter(row['score'] for row in analyses)
    
    # 2. Sentiment Trend (Line Chart)
    analyses_list = [
        {'timestamp': row['timestamp'], 'sentiment': row['score'] if row['label'] == 'POSITIVE' else -row['score']}
        for row in analyses
    ]
    
    # 3. Score Distribution (Bar Chart)
    bins = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    pos_scores = [row['score'] for row in analyses if row['label'] == 'POSITIVE']
    neg_scores = [row['score'] for row in analyses if row['label'] == 'NEGATIVE']
    pos_dist = [sum(1 for s in pos_scores if b1 <= s < b2) for b1, b2 in zip(bins[:-1], bins[1:])]
    neg_dist = [sum(1 for s in neg_scores if b1 <= s < b2) for b1, b2 in zip(bins[:-1], bins[1:])]
    
    # 4. Word Frequencies (Word Cloud)
    pos_words = ' '.join(row['text'] for row in analyses if row['label'] == 'POSITIVE').lower()
    neg_words = ' '.join(row['text'] for row in analyses if row['label'] == 'NEGATIVE').lower()
    pos_freq = dict(Counter(re.findall(r'\w+', pos_words)).most_common(20))
    neg_freq = dict(Counter(re.findall(r'\w+', neg_words)).most_common(20))
    
    # 5. Time Trends (Stacked Area Chart)
    time_data = conn.execute('SELECT strftime("%Y-%m-%d %H", timestamp) as hour, label, COUNT(*) as count '
                             'FROM analyses GROUP BY hour, label ORDER BY hour').fetchall()
    #conn.close()
    hours = sorted(set(row['hour'] for row in time_data))
    pos_counts = [next((r['count'] for r in time_data if r['hour'] == h and r['label'] == 'POSITIVE'), 0) for h in hours]
    neg_counts = [next((r['count'] for r in time_data if r['hour'] == h and r['label'] == 'NEGATIVE'), 0) for h in hours]
    
    # 6. Heatmap (Sentiment by Day and Hour)
    heatmap_data = conn.execute('SELECT strftime("%w", timestamp) as day, strftime("%H", timestamp) as hour, '
                                'label, COUNT(*) as count FROM analyses GROUP BY day, hour, label').fetchall()
    
    conn.close()

    days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    hours_24 = [f'{h:02d}' for h in range(24)]
    heatmap_pos = [[0]*24 for _ in range(7)]
    heatmap_neg = [[0]*24 for _ in range(7)]
    for row in heatmap_data:
        d, h = int(row['day']), int(row['hour'])
        if row['label'] == 'POSITIVE':
            heatmap_pos[d][h] = row['count']
        else:
            heatmap_neg[d][h] = row['count']

    return jsonify({
        'sentiment_counts': dict(sentiment_counts),
        'analyses': analyses_list,
        'score_distribution': {
            'bins': [f'{b1}-{b2}' for b1, b2 in zip(bins[:-1], bins[1:])],
            'positive': pos_dist,
            'negative': neg_dist
        },
        'word_frequencies': {
            'positive': pos_freq,
            'negative': neg_freq
        },
        'time_trends': {
            'hours': hours,
            'positive': pos_counts,
            'negative': neg_counts
        },
        'heatmap': {
            'days': days,
            'hours': hours_24,
            'positive': heatmap_pos,
            'negative': heatmap_neg
        }
    })

if __name__ == '__main__':
    app.run(debug=True)