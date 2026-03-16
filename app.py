from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Always ensure tables exist
    c.execute('''CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, phone TEXT, damage_type TEXT, description TEXT,
        latitude REAL, longitude REAL, photo TEXT,
        verified INTEGER DEFAULT 0,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS relief (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        org_name TEXT, contact TEXT, supply_type TEXT, quantity TEXT,
        going_to TEXT, latitude REAL, longitude REAL,
        status TEXT DEFAULT 'active',
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    return conn

# Landing page
@app.route('/')
def landing():
    return render_template('landing.html')

# Report damage form
@app.route('/report')
def index():
    return render_template('index.html')

# Map page
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

# War Room government dashboard
@app.route('/warroom')
def warroom():
    return render_template('warroom.html')

# Serve service worker from root
@app.route('/sw.js')
def service_worker():
    return app.send_static_file('sw.js'), 200, {'Content-Type': 'application/javascript'}

# API - submit damage report
@app.route('/submit', methods=['POST'])
def submit_report():
    data = request.form
    photo = request.files.get('photo')
    photo_filename = None
    if photo and photo.filename:
        photo_filename = photo.filename
        os.makedirs('static', exist_ok=True)
        photo.save(os.path.join('static', photo_filename))
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO reports (name, phone, damage_type, description, latitude, longitude, photo)
        VALUES (?, ?, ?, ?, ?, ?, ?)''', (
        data.get('name'), data.get('phone'), data.get('damage_type'),
        data.get('description'), data.get('latitude'), data.get('longitude'),
        photo_filename
    ))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Report submitted successfully'})

# API - get all reports
@app.route('/reports')
def get_reports():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM reports')
    rows = c.fetchall()
    conn.close()
    reports = []
    for row in rows:
        reports.append({
            'id': row[0], 'name': row[1], 'phone': row[2],
            'damage_type': row[3], 'description': row[4],
            'latitude': row[5], 'longitude': row[6],
            'photo': row[7], 'verified': row[8], 'timestamp': row[9]
        })
    return jsonify(reports)

# API - verify a report
@app.route('/verify/<int:report_id>', methods=['POST'])
def verify_report(report_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE reports SET verified = 1 WHERE id = ?', (report_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# API - submit relief supply
@app.route('/submit_relief', methods=['POST'])
def submit_relief():
    data = request.form
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO relief (org_name, contact, supply_type, quantity, going_to, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?)''', (
        data.get('org_name'), data.get('contact'), data.get('supply_type'),
        data.get('quantity'), data.get('going_to'),
        data.get('latitude'), data.get('longitude')
    ))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# API - get all relief supplies
@app.route('/relief_data')
def relief_data():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM relief')
    rows = c.fetchall()
    conn.close()
    supplies = []
    for row in rows:
        supplies.append({
            'id': row[0], 'org_name': row[1], 'contact': row[2],
            'supply_type': row[3], 'quantity': row[4],
            'going_to': row[5], 'latitude': row[6],
            'longitude': row[7], 'status': row[8], 'timestamp': row[9]
        })
    return jsonify(supplies)

if __name__ == '__main__':
    get_db()
    app.run(debug=True)
