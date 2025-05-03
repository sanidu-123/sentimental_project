# Sentiment Analysis and Trend Dashboard

A real-time web application for text sentiment analysis with visualization capabilities.

## Overview

This dashboard analyzes text sentiment in real-time, classifying input as positive, negative, or neutral. It provides comprehensive visualization of results through interactive charts, word clouds, and time-based analytics. The application stores all analyses in a database to track sentiment patterns over time.

## Features

- **Real-time Sentiment Analysis**: Immediate feedback on text sentiment
- **Multi-class Classification**: Positive, negative, and neutral detection with confidence scores
- **Interactive Visualizations**:
  - Sentiment distribution pie chart
  - Score distribution bar chart
  - Word clouds for each sentiment category
  - Time trend analysis
  - Day/hour heatmap
- **Responsive Design**: Mobile-friendly interface

## Technology Stack

### Backend
- **Flask**: Web framework
- **Transformers (Hugging Face)**: NLP model for sentiment analysis
- **NLTK**: Text preprocessing
- **SQLite**: Data storage
- **WordCloud**: Word cloud generation

### Frontend
- **HTML/CSS/JavaScript**: Core web technologies
- **Chart.js**: Simple charts (pie, bar)
- **ECharts**: Advanced visualizations (time series, heatmap)

## Installation

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install flask transformers nltk wordcloud torch
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Access at `http://localhost:5000`

## Usage

1. Enter text in the input area
2. Click "Analyze Sentiment"
3. View results and automatically updated visualizations

## API Endpoints

### `/analyze` (POST)
Analyzes text sentiment.
```json
Request: {"text": "Text to analyze"}
Response: {"status": "success", "data": {"result": {"label": "POSITIVE", "score": 0.95}}}
```

### `/stats` (GET)
Retrieves visualization data.

### `/wordcloud/<sentiment>` (GET)
Generates a word cloud for the specified sentiment.

### `/recent` (GET)
Lists recent analyses.

## Future Improvements

- Multi-language support
- User accounts and authentication
- Data export functionality
- Custom model training
- Aspect-based sentiment analysis
- Batch processing

## Dashboard overview
Mainly use HTML, CSS, JavaScript for building the interface. This application provides sentiment analysis of text input and displays various analytics through interactive charts and visualizations. The dashboard includes:

* Real-time sentiment analysis of user input
* Pie chart showing overall sentiment distribution
* Bar chart displaying score distributions for both positive and negative sentiments
* Time-series chart showing sentiment trends over time
* Day vs. Hour heatmap visualization of sentiment patterns
* Word clouds for both positive and negative sentiment words

The dashboard can input text and get the output, if it is a positive or negative sentiment. The procedure is simple; the user needs to enter the text that they want to analyze, and can have the output immediately with confidence level and type of sentiment
![image](https://github.com/user-attachments/assets/73a88e9d-b692-46d6-a8b7-e2dc63a597a1)

There are several charts we use to analyze the sentiments.

### Sentiment Distribution chart
![WhatsApp Image 2025-05-03 at 20 35 19_4ea8c53311](https://github.com/user-attachments/assets/b5dfe80f-b231-4a57-97d2-7c3cae5f3232)

This chart presents the overall positive, negative, and neutral sentiments. We used different colours for better understanding and user interaction. Legends are also provided for the identification of the chart.

### Score Distribution chart
![image](https://github.com/user-attachments/assets/f31e3482-39fb-445f-bfb9-55afb8bf4fbb)

This showcases the number of analyses for each sentiment score range. The ranges are 0.5-0.6,0.6-0.7,0.7-0.8,0.8-0.9,0.9-1.0. Charts also represent positive and negative scores at the same time.

### Word cloud for positive and negative sentiments
![WhatsApp Image 2025-05-03 at 20 35 44_652acdaf](https://github.com/user-attachments/assets/4e290438-6a16-435a-886b-11593f41f474)


Word cloud used to present positive, neutral, and negative words according to frequency.

### Sentiment time series chart
![image](https://github.com/user-attachments/assets/35addff0-646b-40aa-8a01-16c74964f353)

The chart shows that the positive and negative sentiment fluctuates over time. The user can observe individual positive and negative sentiment behaviour by selecting filters.

### Sentiment heatmap Day vs Hour
![image](https://github.com/user-attachments/assets/3437ae7f-62e9-43b0-b917-e815b5fd167e)

By this chart, we can identify potential user behaviour. When analyzing this chart, we can get a brief idea of which days and which hours are mostly active with sentiment entries.

* Frontend Structure

 1. html - Main dashboard UI
 2. JavaScript - for charts and interactions
 3. CSS - CSS styling files

* Contribution
  1. HSS Hewage- contribute to the front end and provide support for app.py
  2. GLS Chamaka- contribute to the app.py and provide support for the front end
  3. MSS Piyarathne- Contribution to the app.py and building the database
