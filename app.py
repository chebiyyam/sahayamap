from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# This creates our database and table if it doesn't exist yet
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            damage_type TEXT,
            description TEXT,
            latitude REAL,
            longitude REAL,
            photo TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Home page - shows the damage report form
@app.route('/')
def index():
    return render_template('index.html')

# Map page - shows all damage pins
@app.route('/map')
def map_view():
    return render_template('map.html')

# API endpoint - receives damage report from form and saves to database
@app.route('/submit', methods=['POST'])
def submit_report():
    data = request.form
    photo = request.files.get('photo')
    
    photo_filename = None
    if photo:
        photo_filename = photo.filename
        photo.save(os.path.join('static', photo_filename))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO reports (name, phone, damage_type, description, latitude, longitude, photo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'),
        data.get('phone'),
        data.get('damage_type'),
        data.get('description'),
        data.get('latitude'),
        data.get('longitude'),
        photo_filename
    ))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Report submitted successfully'})

# API endpoint - sends all reports to the map as JSON
@app.route('/reports')
def get_reports():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM reports')
    rows = c.fetchall()
    conn.close()
    
    reports = []
    for row in rows:
        reports.append({
            'id': row[0],
            'name': row[1],
            'phone': row[2],
            'damage_type': row[3],
            'description': row[4],
            'latitude': row[5],
            'longitude': row[6],
            'photo': row[7],
            'timestamp': row[8]
        })
    
    return jsonify(reports)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)