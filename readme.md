myenv/scripts/activate

# End-to-End Data Pipeline for T20 Cricket Data

## Overview
This Flask-based web application performs sentiment analysis on text inputs using Hugging Face's Transformers library. The application stores analysis results in SQLite, generates statistics, and visualizes data through charts and word clouds.

## Features
* Sentiment Analysis: Analyzes text and classifies it as positive or negative with a confidence score
* Interactive Dashboard: Visualizes sentiment distribution, score ranges, and time-based patterns
* Word Clouds: Generates visual representations of word frequency for positive and negative sentiments
* Recent Activity: Displays the latest sentiment analysis entries

# Technical Architecture

## Backend Components
* Flask: Handles HTTP requests, routing, and serves the frontend
* Transformers: Uses pre-trained NLP models for sentiment analysis
* SQLite: Stores analysis results with timestamp, text, label, and score
* NLTK: Processes text for word frequency analysis and tokenization
* WordCloud: Generates visual word frequency representations
* Logging: Captures operational events and errors

# Database Schema
CREATE TABLE analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    text TEXT NOT NULL,
    label TEXT CHECK(label IN ('POSITIVE', 'NEGATIVE')) NOT NULL,
    score REAL CHECK(score >= 0 AND score <= 1) NOT NULL
)

## Dashboard overview
The dashboard can input text and get the output, if it is a positive or negative sentiment. The procedure is simple; the user needs to enter the text that they want to analyze, and can have the output immediately with confidence level and type of sentiment
![image](https://github.com/user-attachments/assets/73a88e9d-b692-46d6-a8b7-e2dc63a597a1)

There are several charts we use to analyze the sentiments.

### Sentiment Distribution chart
![image](https://github.com/user-attachments/assets/f3d4bdd9-d7b5-4183-a406-ef37bd370afe)

This chart presents the overall positive and negative sentiments. We used green and red colours for better understanding and user interaction. Legends are also provided for the identification of the chart.

### Score Distribution chart
![image](https://github.com/user-attachments/assets/f31e3482-39fb-445f-bfb9-55afb8bf4fbb)

This showcases the number of analyses for each sentiment score range. The ranges are 0.5-0.6,0.6-0.7,0.7-0.8,0.8-0.9,0.9-1.0. Charts also represent positive and negative scores at the same time.

