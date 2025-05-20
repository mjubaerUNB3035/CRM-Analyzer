## Project: CRM Relationship Insights Analyzer
# Description: Backend API for analyzing CRM data to assess engagement strength and communication sentiment

from flask import Flask, request, jsonify
from textblob import TextBlob
import pandas as pd
import datetime
import io

app = Flask(__name__)

## Initialize global data as empty DataFrame
data = pd.DataFrame([])

# Temporary sample data for testing
sample_data = pd.DataFrame([
    {
        "name": "MD",
        "last_contact": "2025-04-10",
        "emails": ["Appreciate your effort.", "Let's connect again soon."]
    },
    {
        "name": "ABC",
        "last_contact": "2025-5-12",
        "emails": ["This is unacceptable.", "I need a response now."]
    }
])

data = sample_data.copy()

# compute engagement score
def compute_engagement_score(last_contact_str, emails):
    today = datetime.date.today()
    last_contact = datetime.datetime.strptime(last_contact_str, "%Y-%m-%d").date()
    days_since_contact = (today - last_contact).days

    # Base Score (100- Last date of Contact)
    base_score = max(0, 100 - days_since_contact)  

    # Email Boost (Number of emails * 5)
    email_boost = min(len(emails)*5, 50)

    # Total Score
    total_score = base_score + email_boost

    return total_score

# compute sentiment
def compute_sentiment(emails):
    sentiments = [TextBlob(email).sentiment.polarity for email in emails]
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    return avg_sentiment

# Compute sentiment trend: compare first half average vs second half average
def compute_sentiment_trend(emails):
    n = len(emails)
    if n < 2:
        return 0  # Less Number
    first_half = emails[:n//2]
    second_half = emails[n//2:]
    first_avg = sum(TextBlob(email).sentiment.polarity for email in first_half) / len(first_half)
    second_avg = sum(TextBlob(email).sentiment.polarity for email in second_half) / len(second_half)
    trend = second_avg - first_avg
    return trend

@app.route("/analyze", methods=["GET"])
def analyze():
    results = []
    for _, row in data.iterrows():
        score = compute_engagement_score(row["last_contact"], row["emails"])
        sentiment = compute_sentiment(row["emails"])
        trend = compute_sentiment_trend(row["emails"])

        # Score Flag Logic
        if score<40 or score<0:
            flag= "At Risk"
        elif score < 60 or sentiment < 0.2:
            flag = "Needs Attention"
        else:
            flag = "Healthy"

        results.append({
            "name": row["name"],
            "engagement_score": score,
            "sentiment": sentiment,
            "trend": trend,
            "flag": flag
        })
    return jsonify(results)

@app.route("/upload", methods=["POST"])
def upload():
    global data
    if 'file' not in request.files:
        return "No file uploaded", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    try:
        content = file.read()
        decoded = content.decode("utf-8")
        df = pd.read_csv(io.StringIO(decoded))
        df["emails"] = df["emails"].apply(eval)  # Convert string to list
        data = df
        return "File uploaded and data loaded successfully. Access /analyze to see results."
    except Exception as e:
        return f"Error processing file: {e}", 500


@app.route("/")
def home():
    return "Smart Relationship Dashboard API is running. Visit /analyze to view results."


if __name__ == "__main__":
     print("Starting Flask server...")
     app.run(debug=True, port=5050)
