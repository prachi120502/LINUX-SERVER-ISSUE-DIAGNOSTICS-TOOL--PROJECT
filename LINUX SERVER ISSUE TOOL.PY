from flask import Flask, jsonify, request
import psutil
import sqlite3
import os

# Initialize Flask application
app = Flask(__name__)

# Database setup
DATABASE = 'diagnostics.db'

def init_db():
    """Initialize the SQLite database."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpu_usage REAL,
                memory_usage REAL,
                disk_usage REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def gather_system_metrics():
    """Gather system metrics: CPU, memory, and disk usage."""
    metrics = {
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
    }
    return metrics

def store_metrics(metrics):
    """Store the gathered metrics in the SQLite database."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO metrics (cpu_usage, memory_usage, disk_usage)
            VALUES (?, ?, ?)
        ''', (metrics['cpu_usage'], metrics['memory_usage'], metrics['disk_usage']))
        conn.commit()

@app.route('/diagnostics', methods=['GET'])
def diagnostics():
    """API endpoint to get system diagnostics."""
    metrics = gather_system_metrics()
    store_metrics(metrics)
    return jsonify(metrics)

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """API endpoint to retrieve stored metrics."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM metrics ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        return jsonify([{"id": row[0], "cpu_usage": row[1], "memory_usage": row[2], "disk_usage": row[3], "timestamp": row[4]} for row in rows])

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(host='0.0.0.0', port=5000)  # Run the Flask app