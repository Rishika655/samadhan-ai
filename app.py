from flask import Flask, render_template, request, jsonify
from modules.llm_parser import parse_complaint
import sqlite3
from datetime import datetime, timedelta
from modules.duplicate import check_duplicate
from modules.hotspot import generate_map
from modules.escalation import get_escalation_status
from flask import redirect



app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database/complaints.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        complaint TEXT,
        category TEXT,
        location TEXT,
        latitude REAL,
        longitude REAL,
        priority_score INTEGER,
        status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    conn = sqlite3.connect('database/complaints.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM complaints")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM complaints WHERE status='Resolved'")
    resolved = c.fetchone()[0]
    conn.close()
    return render_template('home.html', total=total, resolved=resolved)

@app.route('/submit-complaint')
def submit_complaint():
    return render_template('dashboard.html')

## form creation

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    location = request.form['location']
    complaint = request.form['complaint']

    # check duplicate first
    dup_result = check_duplicate(complaint)
    if dup_result['is_duplicate']:
        return f"""
        <h2>⚠️ Duplicate Complaint Detected!</h2>
        <p>Your complaint is <b>{dup_result['similarity_score']}% similar</b> to an existing one.</p>
        <p><b>Existing complaint:</b> {dup_result['matched_complaint']}</p>
        <p>Your complaint has been linked to complaint ID #{dup_result['duplicate_of_id']}</p>
        <a href='/complaints'>View Dashboard</a> | <a href='/'>Submit another</a>
        """

    # Groq AI analysis
    ai_result = parse_complaint(complaint, location)

    conn = sqlite3.connect('database/complaints.db')
    c = conn.cursor()
    c.execute("""INSERT INTO complaints 
                (name, complaint, location, category, priority_score) 
                VALUES (?, ?, ?, ?, ?)""",
              (name, complaint, location,
               ai_result['category'], ai_result['priority_score']))
    conn.commit()
    conn.close()

    return f"""
    <h2>Complaint Analyzed by AI!</h2>
    <p><b>Name:</b> {name}</p>
    <p><b>Category:</b> {ai_result['category']}</p>
    <p><b>Severity:</b> {ai_result['severity']}</p>
    <p><b>Priority Score:</b> {ai_result['priority_score']}/100</p>
    <p><b>Summary:</b> {ai_result['summary']}</p>
    <p><b>Est. Resolution:</b> {ai_result['estimated_resolution_days']} days</p>
    <a href='/complaints'>View Dashboard</a> | <a href='/'>Submit another</a>
    """
    

## time convert
def convert_to_ist(utc_time_str):
    utc_time = datetime.strptime(utc_time_str, '%Y-%m-%d %H:%M:%S')
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time.strftime('%d-%m-%Y %I:%M %p')


##map(geocoding)
@app.route('/map')
def show_map():
    generate_map()
    return render_template('map.html')


## resolve option
@app.route('/resolve/<int:complaint_id>')
def resolve(complaint_id):
    conn = sqlite3.connect('database/complaints.db')
    c = conn.cursor()
    c.execute("UPDATE complaints SET status='Resolved' WHERE id=?", (complaint_id,))
    conn.commit()
    conn.close()
    return redirect('/complaints')


## update complaint routes to add escalation
@app.route('/complaints')
def complaints():
    conn = sqlite3.connect('database/complaints.db')
    c = conn.cursor()
    c.execute("SELECT * FROM complaints ORDER BY priority_score DESC")
    rows = c.fetchall()
    conn.close()

    converted = []
    for row in rows:
        row = list(row)
        ist_time = convert_to_ist(row[9])
        row[9] = ist_time

        # get escalation status
        escalation = get_escalation_status(
            row[4],   # category
            row[7],   # priority_score
            ist_time, # created_at in IST
            row[8]    # status
        )
        row.append(escalation)
        converted.append(row)

    return render_template('complaints.html', complaints=converted)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)





    