from flask import Flask, render_template, request, redirect, url_for, jsonify
import json

app = Flask(__name__)

# Load expenses from JSON file
def load_expenses():
    try:
        with open('expenses.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Save expenses to JSON file
def save_expenses(expenses):
    with open('expenses.json', 'w') as file:
        json.dump(expenses, file, indent=4)

# Home Page (View Expenses)
@app.route('/')
def index():
    expenses = load_expenses()
    return render_template("index.html", expenses=expenses)

# Add Expense
@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        description = request.form['description']
        date = request.form['date']

        expenses = load_expenses()
        expenses.append({
            "id": len(expenses) + 1,
            "amount": float(amount),
            "category": category,
            "description": description,
            "date": date
        })

        save_expenses(expenses)
        return redirect(url_for('index'))

    return render_template("add_expense.html")

# Delete Expense
@app.route('/delete/<int:id>')
def delete_expense(id):
    expenses = load_expenses()
    updated_expenses = [expense for expense in expenses if expense['id'] != id]
    save_expenses(updated_expenses)
    return redirect(url_for('index'))

# Generate Report
@app.route('/report')
def generate_report():
    expenses = load_expenses()
    total_spent = sum(expense['amount'] for expense in expenses)
    return render_template("report.html", expenses=expenses, total_spent=total_spent)

if __name__ == '__main__':
    app.run(debug=True)
