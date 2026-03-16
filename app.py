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
# Safety checker page
@app.route('/safety')
def safety_checker():
    return render_template('safety.html')
# Relief coordination dashboard
@app.route('/relief')
def relief():
    return render_template('relief.html')

# API - submit relief supply
@app.route('/submit_relief', methods=['POST'])
def submit_relief():
    data = request.form
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS relief (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            org_name TEXT,
            contact TEXT,
            supply_type TEXT,
            quantity TEXT,
            going_to TEXT,
            latitude REAL,
            longitude REAL,
            status TEXT DEFAULT 'active',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        INSERT INTO relief (org_name, contact, supply_type, quantity, going_to, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('org_name'),
        data.get('contact'),
        data.get('supply_type'),
        data.get('quantity'),
        data.get('going_to'),
        data.get('latitude'),
        data.get('longitude')
    ))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# API - get all relief supplies
@app.route('/relief_data')
def relief_data():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS relief (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            org_name TEXT,
            contact TEXT,
            supply_type TEXT,
            quantity TEXT,
            going_to TEXT,
            latitude REAL,
            longitude REAL,
            status TEXT DEFAULT 'active',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('SELECT * FROM relief')
    rows = c.fetchall()
    conn.close()
    supplies = []
    for row in rows:
        supplies.append({
            'id': row[0],
            'org_name': row[1],
            'contact': row[2],
            'supply_type': row[3],
            'quantity': row[4],
            'going_to': row[5],
            'latitude': row[6],
            'longitude': row[7],
            'status': row[8],
            'timestamp': row[9]
        })
    return jsonify(supplies)

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
# Serve service worker from root so PWA offline works
@app.route('/sw.js')
def service_worker():
    return app.send_static_file('sw.js'), 200, {'Content-Type': 'application/javascript'}
if __name__ == '__main__':
    init_db()
    app.run(debug=True)