from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import sqlite3

PORT = 8080

# Ensure DB exists
def init_db():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        amount REAL,
                        category TEXT,
                        description TEXT,
                        date TEXT)''')
    conn.commit()
    conn.close()

class ExpenseHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            with open('index.html', 'rb') as file:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(file.read())
        elif self.path == '/style.css':
            with open('style.css', 'rb') as file:
                self.send_response(200)
                self.send_header('Content-type', 'text/css')
                self.end_headers()
                self.wfile.write(file.read())

    def do_POST(self):
        if self.path == '/add':
            length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(length)
            data = urllib.parse.parse_qs(post_data.decode())

            amount = float(data['amount'][0])
            category = data['category'][0]
            description = data['description'][0]
            date = data['date'][0]

            conn = sqlite3.connect("expenses.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
                           (amount, category, description, date))
            conn.commit()
            conn.close()

            # Redirect back to homepage
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

if __name__ == '__main__':
    init_db()
    server = HTTPServer(('localhost', PORT), ExpenseHandler)
    print(f"Server running at http://localhost:{PORT}")
    server.serve_forever()
