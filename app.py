## Project: CRM Relationship Insights Analyzer
# Description: Backend API for analyzing CRM data to assess engagement strength and communication sentiment

from flask import Flask, request, jsonify
from textblob import TextBlob
import pandas as pd
import datetime

app = Flask(__name__)

# Simulated data loading
data = pd.DataFrame([
    {"name": "Alice Johnson", "last_contact": "2024-12-15", "emails": ["Let's catch up soon!", "Great work on the project."]},
    {"name": "Bob Smith", "last_contact": "2024-08-01", "emails": ["Not happy with the results.", "Please fix the issue immediately."]},
    {"name": "Carol Lee", "last_contact": "2025-01-10", "emails": ["Thanks for the update.", "Looking forward to next steps."]},
])

# compute engagement score
def compute_engagement_score(last_contact_str):
    today = datetime.date.today()
    last_contact = datetime.datetime.strptime(last_contact_str, "%Y-%m-%d").date()
    days_since_contact = (today - last_contact).days
    score = max(0, 100 - days_since_contact)  # Simple decay model
    return score

# compute sentiment
def compute_sentiment(emails):
    sentiments = [TextBlob(email).sentiment.polarity for email in emails]
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    return avg_sentiment

@app.route("/analyze", methods=["GET"])
def analyze():
    results = []
    for _, row in data.iterrows():
        score = compute_engagement_score(row["last_contact"])
        sentiment = compute_sentiment(row["emails"])
        results.append({
            "name": row["name"],
            "engagement_score": score,
            "sentiment": sentiment
        })
    return jsonify(results)

if __name__ == "__main__":
     print("Starting Flask server...")
     app.run(debug=True, port=5050)
