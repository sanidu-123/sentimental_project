# Sentiment Analysis and Trend Dashboard

## Overview
This Flask-based web application performs sentiment analysis on text inputs using Hugging Face's Transformers library. The application stores analysis results in SQLite, generates statistics, and visualizes data through charts and word clouds.

## Features
* Sentiment Analysis: Analyzes text and classifies it as positive or negative with a confidence score
* Interactive Dashboard: Visualizes sentiment distribution, score ranges, and time-based patterns
* Word Clouds: Generates visual representations of word frequency for positive and negative sentiments
* Recent Activity: Displays the latest sentiment analysis entries

## Technical Architecture

### Backend Components
* Flask: Handles HTTP requests, routing, and serves the frontend
* Transformers: Uses pre-trained NLP models for sentiment analysis
* SQLite: Stores analysis results with timestamp, text, label, and score
* NLTK: Processes text for word frequency analysis and tokenization
* WordCloud: Generates visual word frequency representations
* Logging: Captures operational events and errors

### Database Schema
![image](https://github.com/user-attachments/assets/d02e0aa6-e65b-4709-aa57-1ddff2219a00)

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
  2. GLS Chamaka-
  3. MSS Piyarathne- 
