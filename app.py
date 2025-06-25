## Project: CRM Relationship Insights Analyzer
# Description: Backend API for analyzing CRM data to assess engagement strength and communication sentiment

from flask import Flask, request, jsonify
from flask import render_template
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
        "name": "Client A",
        "last_contact": "2025-05-20",
        "emails": ["Great work!", "Appreciate the update."]
    },
    {
        "name": "Client B",
        "last_contact": "2025-04-10",
        "emails": ["Need help with the issue.", "Please follow up."]
    },
    {
        "name": "Client C",
        "last_contact": "2025-03-05",
        "emails": ["This is unacceptable.", "Very disappointed."]
    },
    {
        "name": "Client D",
        "last_contact": "2025-05-22",
        "emails": ["Excellent support!", "Let's continue this."]
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

@app.route("/analyze/top", methods=["GET"])
def top_clients():
    metric = request.args.get("by", "engagement").lower()
    try:
        n = int(request.args.get("n", 5))
    except ValueError:
        return jsonify({"error": "Parameter 'n' must be an integer."}), 400

    if metric not in ["engagement", "sentiment"]:
        return jsonify({"error": "Parameter 'by' must be either 'engagement' or 'sentiment'."}), 400

    results = []
    for _, row in data.iterrows():
        engagement_score = compute_engagement_score(row["last_contact"], row["emails"])
        sentiment = compute_sentiment(row["emails"])

        results.append({
            "name": row["name"],
            "engagement_score": engagement_score,
            "sentiment": sentiment
        })

    key = "engagement_score" if metric == "engagement" else "sentiment"
    sorted_results = sorted(results, key=lambda x: x[key], reverse=True)

    return jsonify(sorted_results[:n])


@app.route("/upload", methods=["POST"])
def upload():
    global data
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    try:
        # Read CSV into DataFrame
        df = pd.read_csv(file)

        # Convert emails string to list using semicolon separator
        df["emails"] = df["emails"].apply(lambda x: x.split(";") if isinstance(x, str) else [])

        # Basic validation
        required_columns = {"name", "last_contact", "emails"}
        if not required_columns.issubset(df.columns):
            return "CSV must contain 'name', 'last_contact', and 'emails' columns", 400

        # Replace the global data
        data = df
        return "File uploaded successfully", 200

    except Exception as e:
        return f"Failed to process file: {str(e)}", 500



@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
     print("Starting Flask server...")
     app.run(debug=True, port=5050)
