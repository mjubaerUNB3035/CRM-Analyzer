# CRM Relationship Insights Analyzer

This is a backend API built with Flask that analyzes CRM data to help understand how engaged clients are and the overall tone of your communication with them. It calculates an engagement score based on how recently you contacted them and how often you’ve emailed, plus a sentiment score from the messages.

## What it does

- Calculates how strong your client engagement is
- Analyzes the tone (positive or negative) of emails using TextBlob
- Tracks changes in sentiment over time
- Lets you upload a CSV file with client interaction data
- Offers an API to get a full analysis or just the top-performing clients

## Sample CSV format

File should include these columns:
- name (e.g., Client A)
- last_contact (in YYYY-MM-DD format)
- emails (emails separated by semicolons)

Example row: Beta Corp	52	0.93	-0.11	At Risk



## API Endpoints

### GET `/analyze`

Returns all clients with:
- engagement_score
- sentiment (average)
- trend (sentiment trend)
- flag (`Healthy`, `Needs Attention`, or `At Risk`)

Example:
GET http://localhost:5050/analyze

---

### GET `/analyze/top?by=<metric>&n=<number>`

Returns top `n` clients sorted by a metric.

Query parameters:
- by: `engagement` (default) or `sentiment`
- n: number of clients (default: 5)

Example:
GET http://localhost:5050/analyze/top?by=sentiment&n=3

---

### POST `/upload`

Uploads a CSV file to replace current CRM data.

Form field: `file`  
Expected columns: `name`, `last_contact`, `emails` (semicolon-separated)

Example (with curl):
curl -X POST -F "file=@sample.csv" http://localhost:5050/upload

---

### GET `/`

Loads the index page (`index.html`), used for frontend overview.

Example:
GET http://localhost:5050/


## How to run it

1. Clone the repo  
2. Install the required packages  
3. Run the app with Python  

The app runs at:  
http://localhost:5050/


## Tech used

- Python
- Flask
- Pandas
- TextBlob

## Contact

Made by Md Hafijur Rahman Jubaer  
Email: jubaer.ca@gmail.com
