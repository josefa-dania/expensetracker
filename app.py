from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import sqlite3
import json
import os

PORT = 8080
DB_FILE = "expenses.db"

def init_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL,
                category TEXT,
                description TEXT,
                date TEXT
            )
        ''')
        conn.commit()
        conn.close()

def get_expense_table_html():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "<p>No expenses found.</p>"

    html = "<table><tr><th>ID</th><th>Amount</th><th>Category</th><th>Description</th><th>Date</th><th>Action</th></tr>"
    for r in rows:
        html += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td>"
        html += f"<td><form action='/delete' method='post' style='display:inline'><input type='hidden' name='id' value='{r[0]}'><button type='submit'>Delete</button></form></td></tr>"
    html += "</table>"
    return html

class ExpenseHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            with open('index.html', 'r') as f:
                html = f.read()
            html = html.replace("<!-- Table rendered by Python -->", get_expense_table_html())
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())

        elif self.path == '/style.css':
            with open('style.css', 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', 'text/css')
                self.end_headers()
                self.wfile.write(f.read())

        elif self.path == '/report-data':
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
            data = cursor.fetchall()
            conn.close()

            categories = [row[0] for row in data]
            amounts = [row[1] for row in data]
            response = json.dumps({"categories": categories, "amounts": amounts})
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(response.encode())

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(length)
        data = urllib.parse.parse_qs(post_data.decode())

        if self.path == '/add':
            try:
                amount = float(data['amount'][0])
                category = data['category'][0]
                description = data['description'][0]
                date = data['date'][0]

                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
                               (amount, category, description, date))
                conn.commit()
                conn.close()

                self.send_response(303)
                self.send_header('Location', '/')
                self.end_headers()
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode())

        elif self.path == '/delete':
            try:
                expense_id = int(data['id'][0])
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
                conn.commit()
                conn.close()

                self.send_response(303)
                self.send_header('Location', '/')
                self.end_headers()
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode())

        else:
            self.send_response(405)
            self.end_headers()
            self.wfile.write(b"Method Not Allowed")

if __name__ == '__main__':
    init_db()
    print(f"Server running at http://localhost:{PORT}")
    server = HTTPServer(('localhost', PORT), ExpenseHandler)
    server.serve_forever()
