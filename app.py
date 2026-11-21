from flask import Flask, jsonify, request, g, render_template
from pathlib import Path
import sqlite3
from modules.booking import validate_booking, has_overlap
from modules.maintenance import calculate_sla_deadline, valid_transition
from modules.sensors import threshold_exceeded
from modules.approval import can_approve
from modules.synchronization import should_retry

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        DATABASE=str(Path(app.instance_path) / "campus.db"),
        MIN_BOOKING_MINUTES=30,
        MAX_BOOKING_MINUTES=240,
        SENSOR_THRESHOLD=75,
        TESTING=False,
    )
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    def db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("""CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT, room TEXT NOT NULL,
                start TEXT NOT NULL, end TEXT NOT NULL, user TEXT NOT NULL)""")
            g.db.execute("""CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open', request_key TEXT UNIQUE)""")
            g.db.commit()
        return g.db

    @app.teardown_appcontext
    def close_db(error=None):
        connection = g.pop("db", None)
        if connection is not None:
            connection.close()

    @app.get("/")
    def dashboard():
        return render_template("dashboard.html")

    @app.get("/api/bookings")
    def list_bookings():
        rows = db().execute("SELECT * FROM bookings ORDER BY id").fetchall()
        return jsonify([dict(row) for row in rows])

    @app.post("/api/bookings")
    def create_booking():
        data = request.get_json(silent=True) or {}
        required = ("room", "start", "end", "user")
        if any(not data.get(k) for k in required):
            return jsonify(error="Missing booking details"), 400
        valid, message = validate_booking(
            data["start"], data["end"],
            app.config["MIN_BOOKING_MINUTES"], app.config["MAX_BOOKING_MINUTES"])
        if not valid:
            return jsonify(error=message), 400
        connection = db()
        existing = connection.execute(
            "SELECT start, end FROM bookings WHERE room=?", (data["room"],)
        ).fetchall()
        if has_overlap(data["start"], data["end"], [(r["start"], r["end"]) for r in existing]):
            return jsonify(error="Booking overlaps an existing reservation"), 409
        cursor = connection.execute(
            "INSERT INTO bookings(room,start,end,user) VALUES(?,?,?,?)",
            (data["room"], data["start"], data["end"], data["user"]))
        connection.commit()
        return jsonify(id=cursor.lastrowid, message="Booking created"), 201

    @app.post("/api/tickets")
    def create_ticket():
        data = request.get_json(silent=True) or {}
        if not data.get("title") or not data.get("request_key"):
            return jsonify(error="title and request_key are required"), 400
        try:
            cursor = db().execute(
                "INSERT INTO tickets(title,status,request_key) VALUES(?, 'open', ?)",
                (data["title"], data["request_key"]))
            db().commit()
            return jsonify(id=cursor.lastrowid, status="open"), 201
        except sqlite3.IntegrityError:
            row = db().execute("SELECT id,status FROM tickets WHERE request_key=?",
                               (data["request_key"],)).fetchone()
            return jsonify(id=row["id"], status=row["status"], duplicate=True), 200

    @app.patch("/api/tickets/<int:ticket_id>")
    def update_ticket(ticket_id):
        data = request.get_json(silent=True) or {}
        row = db().execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()
        if row is None:
            return jsonify(error="Ticket not found"), 404
        if not valid_transition(row["status"], data.get("status", "")):
            return jsonify(error="Invalid ticket status transition"), 400
        db().execute("UPDATE tickets SET status=? WHERE id=?", (data["status"], ticket_id))
        db().commit()
        return jsonify(id=ticket_id, status=data["status"])

    @app.post("/api/approvals")
    def approve():
        role = request.headers.get("X-Role", "student")
        data = request.get_json(silent=True) or {}
        if not can_approve(role, bool(data.get("restricted"))):
            return jsonify(error="Forbidden"), 403
        return jsonify(message="Approval accepted"), 200

    @app.post("/api/sensors/check")
    def sensor_check():
        data = request.get_json(silent=True) or {}
        if not isinstance(data.get("value"), (int, float)):
            return jsonify(error="Numeric sensor value required"), 400
        return jsonify(alert=threshold_exceeded(data["value"], app.config["SENSOR_THRESHOLD"]))

    @app.get("/health")
    def health():
        db().execute("SELECT 1").fetchone()
        return jsonify(status="healthy")

    @app.post("/api/sync/retry-policy")
    def retry_policy():
        data = request.get_json(silent=True) or {}
        return jsonify(retry=should_retry(data.get("status_code")))

    return app

app = create_app()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
