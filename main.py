import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt

# DB setup
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

# Create table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        amount REAL,
        note TEXT,
        date TEXT
    )
''')
conn.commit()

# Add date column if not exists
cursor.execute("PRAGMA table_info(expenses)")
columns = [col[1] for col in cursor.fetchall()]
if 'date' not in columns:
    cursor.execute("ALTER TABLE expenses ADD COLUMN date TEXT")
    conn.commit()

# Main GUI app
app = tk.Tk()
app.title("Personal Finance Manager")
app.geometry("400x450")

# Add Expense
def add_expense():
    category = category_entry.get()
    amount = amount_entry.get()
    note = note_entry.get()

    if not category or not amount:
        messagebox.showerror("Error", "Please enter both category and amount.")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number.")
        return

    date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("INSERT INTO expenses (category, amount, note, date) VALUES (?, ?, ?, ?)",
                   (category, amount, note, date))
    conn.commit()
    messagebox.showinfo("Success", "Expense added successfully.")
    category_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    note_entry.delete(0, tk.END)

# Visualize Expenses
def visualize_expenses():
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()

    if not data:
        messagebox.showinfo("No Data", "No expenses to visualize.")
        return

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    plt.figure(figsize=(6, 6))
    plt.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=140)
    plt.title("Expenses by Category")
    plt.axis("equal")
    plt.show()

# Set Budgets
budgets = {}

def set_budget():
    cat = budget_category.get()
    amt = budget_amount.get()
    if not cat or not amt:
        messagebox.showerror("Error", "Please enter both category and budget amount.")
        return
    try:
        amt = float(amt)
        budgets[cat] = amt
        messagebox.showinfo("Success", f"Budget set for {cat}: ₹{amt}")
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number.")

def show_budget_summary():
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    spending = dict(cursor.fetchall())

    win = tk.Toplevel(app)
    win.title("Budget Summary")
    win.geometry("400x300")

    tree = ttk.Treeview(win, columns=("Category", "Spent", "Budget", "Status"), show="headings")
    tree.heading("Category", text="Category")
    tree.heading("Spent", text="Spent")
    tree.heading("Budget", text="Budget")
    tree.heading("Status", text="Status")
    tree.pack(fill=tk.BOTH, expand=True)

    for cat in budgets:
        spent = spending.get(cat, 0)
        budget = budgets[cat]
        status = "OK" if spent <= budget else "Over"
        tree.insert("", tk.END, values=(cat, round(spent, 2), budget, status))

# Monthly Summary
def show_monthly_summary():
    cursor.execute("SELECT date, amount FROM expenses")
    rows = cursor.fetchall()

    if not rows:
        messagebox.showinfo("No Data", "No expenses to summarize.")
        return

    monthly_totals = {}
    for date_str, amount in rows:
        if date_str:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                key = dt.strftime("%B %Y")
                monthly_totals[key] = monthly_totals.get(key, 0) + amount
            except:
                continue

    win = tk.Toplevel(app)
    win.title("Monthly Summary")
    win.geometry("400x300")

    tree = ttk.Treeview(win, columns=("Month", "Total Spent"), show="headings")
    tree.heading("Month", text="Month")
    tree.heading("Total Spent", text="Total Spent")
    tree.pack(fill=tk.BOTH, expand=True)

    for month, total in sorted(monthly_totals.items()):
        tree.insert("", tk.END, values=(month, round(total, 2)))

# UI Elements
tk.Label(app, text="Category").pack()
category_entry = tk.Entry(app)
category_entry.pack()

tk.Label(app, text="Amount").pack()
amount_entry = tk.Entry(app)
amount_entry.pack()

tk.Label(app, text="Note").pack()
note_entry = tk.Entry(app)
note_entry.pack()

tk.Button(app, text="Add Expense", command=add_expense).pack(pady=5)
tk.Button(app, text="Visualize Expenses", command=visualize_expenses).pack(pady=5)

tk.Label(app, text="Set Budget").pack(pady=10)
budget_category = tk.Entry(app)
budget_category.pack()
budget_amount = tk.Entry(app)
budget_amount.pack()
tk.Button(app, text="Set Budget", command=set_budget).pack(pady=2)
tk.Button(app, text="Show Budget Summary", command=show_budget_summary).pack(pady=5)

tk.Button(app, text="Monthly Summary", command=show_monthly_summary).pack(pady=10)

app.mainloop()


