from flask import Flask, request, redirect, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ---------------- DATABASE SETUP ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS zones (
        zone_id INTEGER PRIMARY KEY AUTOINCREMENT,
        zone_name TEXT,
        brand_id INTEGER,
        is_active BOOLEAN,
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    conn.commit()
    conn.close()

def get_db():
    return sqlite3.connect("database.db")

# ---------------- HOME (DASHBOARD) ----------------
@app.route('/')
def index():
    conn = get_db()
    zones = conn.execute("SELECT * FROM zones").fetchall()

    total_zones = conn.execute("SELECT COUNT(*) FROM zones").fetchone()[0]
    total_active = conn.execute("SELECT COUNT(*) FROM zones WHERE is_active=1").fetchone()[0]

    conn.close()

    return render_template_string('''
    <h1>Zone Dashboard</h1>

    <h3>Total Zones: {{total_zones}}</h3>
    <h3>Active Zones: {{total_active}}</h3>

    <a href="/add">Add Zone</a>

    <table border="1" cellpadding="10">
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Brand</th>
            <th>Status</th>
            <th>Action</th>
        </tr>

        {% for z in zones %}
        <tr>
            <td>{{z[0]}}</td>
            <td>{{z[1]}}</td>
            <td>{{z[2]}}</td>
            <td>{{"Active" if z[3] else "Inactive"}}</td>
            <td>
                <a href="/edit/{{z[0]}}">Edit</a> |
                <a href="/delete/{{z[0]}}">Delete</a>
            </td>
        </tr>
        {% endfor %}
    </table>
    ''', zones=zones, total_zones=total_zones, total_active=total_active)

# ---------------- ADD ZONE ----------------
@app.route('/add', methods=['GET', 'POST'])
def add_zone():
    if request.method == 'POST':
        name = request.form['zone_name']
        brand = request.form['brand_id']

        conn = get_db()
        conn.execute(
            "INSERT INTO zones (zone_name, brand_id, is_active, created_at) VALUES (?, ?, ?, ?)",
            (name, brand, True, datetime.now())
        )
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template_string('''
    <h2>Add Zone</h2>
    <form method="POST">
        Zone Name: <input type="text" name="zone_name" required><br><br>
        Brand ID: <input type="number" name="brand_id" required><br><br>
        <button type="submit">Add</button>
    </form>
    <br>
    <a href="/">Back</a>
    ''')

# ---------------- EDIT ZONE ----------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_zone(id):
    conn = get_db()

    if request.method == 'POST':
        name = request.form['zone_name']
        brand = request.form['brand_id']
        status = 1 if request.form.get('is_active') == 'on' else 0

        conn.execute(
            "UPDATE zones SET zone_name=?, brand_id=?, is_active=?, updated_at=? WHERE zone_id=?",
            (name, brand, status, datetime.now(), id)
        )
        conn.commit()
        conn.close()

        return redirect('/')

    zone = conn.execute("SELECT * FROM zones WHERE zone_id=?", (id,)).fetchone()
    conn.close()

    return render_template_string('''
    <h2>Edit Zone</h2>
    <form method="POST">
        Zone Name: <input type="text" name="zone_name" value="{{zone[1]}}"><br><br>
        Brand ID: <input type="number" name="brand_id" value="{{zone[2]}}"><br><br>
        Active: <input type="checkbox" name="is_active" {% if zone[3] %}checked{% endif %}><br><br>
        <button type="submit">Update</button>
    </form>
    <br>
    <a href="/">Back</a>
    ''', zone=zone)

# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete_zone(id):
    conn = get_db()
    conn.execute("DELETE FROM zones WHERE zone_id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

# ---------------- RUN ----------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)