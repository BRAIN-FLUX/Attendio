from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import sqlite3
from datetime import datetime, date

app = Flask(__name__)
CORS(app)

DB = "attendance.db"


# ── DB Setup ──
def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        name TEXT,
        date TEXT,
        time TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ── Mark Attendance ──
@app.route('/mark_present', methods=['POST'])
def mark_present():
    data = request.json
    sid = data.get("student_id")
    name = data.get("name")

    today = str(date.today())
    now_time = datetime.now().strftime("%H:%M:%S")

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # ❗ Prevent duplicate entries for same day
    cursor.execute("""
        SELECT * FROM attendance 
        WHERE student_id=? AND date=?
    """, (sid, today))

    exists = cursor.fetchone()

    if not exists:
        cursor.execute("""
            INSERT INTO attendance (student_id, name, date, time)
            VALUES (?, ?, ?, ?)
        """, (sid, name, today, now_time))
        conn.commit()

    conn.close()

    return jsonify({"status": "ok"})


# ── Get Today's Attendance ──
@app.route('/attendance/today')
def get_today():
    today = str(date.today())

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT student_id, name, time 
        FROM attendance 
        WHERE date=?
    """, (today,))

    rows = cursor.fetchall()
    conn.close()

    present_ids = [r[0] for r in rows]

    records = [
        {"student_id": r[0], "name": r[1], "time": r[2]}
        for r in rows
    ]

    return jsonify({
        "present_ids": present_ids,
        "records": records
    })


# ── OPTIONAL: Manual Reset (for testing) ──
@app.route('/reset_attendance', methods=['POST'])
def reset():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM attendance")
    conn.commit()
    conn.close()

    return jsonify({"status": "cleared"})


# ── Dummy Camera APIs (keep your existing ones) ──
@app.route('/camera/start', methods=['POST'])
def start_camera():
    return jsonify({"status": "started"})


@app.route('/camera/stop', methods=['POST'])
def stop_camera():
    return jsonify({"status": "stopped"})


@app.route('/video_feed')
def video_feed():
    return Response("Camera feed here", mimetype='text/plain')


@app.route('/current_face')
def current_face():
    # Replace with real face recognition output
    return jsonify({"sid": None})


if __name__ == '__main__':
    app.run(debug=True)
