# SamadhanAI — Smart Complaint Prioritization Platform

An AI-powered civic complaint management system built with Flask and Groq LLaMA AI.

## Features
- 🤖 AI complaint analysis using Groq LLaMA
- 🔍 Duplicate complaint detection using cosine similarity
- 🗺️ Geo-spatial hotspot map using Folium
- 📈 Escalation prediction based on pending days
- 📋 Priority-ranked complaints dashboard

## Tech Stack
- Python, Flask
- Groq LLaMA AI API
- SQLite
- Scikit-learn
- Folium + OpenStreetMap
- HTML, CSS

## Setup
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Add your Groq API key in `config.py`
4. Run: `python app.py`

## Project Structure
complaint-platform/
├── app.py
├── modules/
│ ├── llm_parser.py
│ ├── duplicate.py
│ ├── escalation.py
│ └── hotspot.py
├── templates/
│ ├── home.html
│ ├── dashboard.html
│ ├── complaints.html
└── database/