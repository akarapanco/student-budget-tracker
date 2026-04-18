import calendar
from datetime import datetime
import sqlite3

DB_NAME = 'app_database.db'

def is_valid_txn(amount):
    try:
        float_amount = float(amount)
        return float_amount > 0
    except ValueError:
        return False

def get_db_connection():
    return sqlite3.connect(DB_NAME)

def setup_db():
    connection = sqlite3.connect('app_database.db')
    cursor = connection.cursor()
    with open("schema.sql", "r") as file:
        sql_cmds = file.read()
    cursor.executescript(sql_cmds)
    connection.commit()
    connection.close()

def add_user(username, password):
    try:
        connection = get_db_connection()
        connection.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        connection.commit()
        connection.close()
        return True
    except Exception:
        return False

def verify_user(username, password):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    connection.close()
    return user

def add_income(user_id, source, amount):
    if not is_valid_txn(amount):
        return False
    try:
        connection = get_db_connection()
        connection.execute("INSERT INTO incomes (user_id, source, amount) VALUES (?, ?, ?)", (user_id, source, amount))
        connection.commit()
        connection.close()
        return True
    except Exception:
        return False

def add_expense(user_id, category, amount, description=""):
    if not is_valid_txn(amount):
        return False
    try:
        connection = get_db_connection()
        connection.execute("INSERT INTO expenses (user_id, category, amount, description) VALUES (?, ?, ?, ?)", (user_id, category, amount, description))
        connection.commit()
        connection.close()
        return True
    except Exception:
        return False

def delete_expense(expense_id, user_id):
    try:
        connection = get_db_connection()
        connection.execute("DELETE FROM expenses WHERE expense_id = ? AND user_id = ?", (expense_id, user_id))
        connection.commit()
        connection.close()
        return True
    except Exception:
        return False

def edit_expense(expense_id, user_id, new_category, new_amount):
    if not is_valid_txn(new_amount):
        return False
    try:
        connection = get_db_connection()
        connection.execute("UPDATE expenses SET category = ?, amount = ? WHERE expense_id = ? AND user_id = ?",
                           (new_category, new_amount, expense_id, user_id))
        connection.commit()
        connection.close()
        return True
    except Exception:
        return False

def get_expenses(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM expenses WHERE user_id = ?", (user_id,))
    expenses = cursor.fetchall()
    connection.close()
    return expenses

def get_expense(expense_id, user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM expenses WHERE expense_id = ? AND user_id = ?", (expense_id, user_id))
    expense = cursor.fetchone()
    connection.close()
    return expense

def get_category_totals(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE user_id = ? GROUP BY category", (user_id,))
    rows = cursor.fetchall()
    connection.close()
    return rows

def get_financial_overview(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT SUM(amount) FROM incomes WHERE user_id = ?", (user_id,))
    total_income = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id = ?", (user_id,))
    total_expenses = cursor.fetchone()[0] or 0
    connection.close()
    remaining = round(total_income - total_expenses, 2)
    return {
        'total_income': round(total_income, 2),
        'total_expenses': round(total_expenses, 2),
        'remaining': remaining
    }

def save_budget(user_id, month, amount):
    if not is_valid_txn(amount):
        return False
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM budgets WHERE user_id = ? AND month = ?", (user_id, month))
        if cursor.fetchone():
            connection.execute("UPDATE budgets SET amount = ? WHERE user_id = ? AND month = ?", (amount, user_id, month))
        else:
            connection.execute("INSERT INTO budgets (user_id, month, amount) VALUES (?, ?, ?)", (user_id, month, amount))
        connection.commit()
        return True
    except Exception:
        return False
    finally:
        connection.close()

def get_budget(user_id, month):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT amount FROM budgets WHERE user_id = ? AND month = ?", (user_id, month))
    row = cursor.fetchone()
    connection.close()
    return row[0] if row else 0

def get_incomes(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM incomes WHERE user_id = ?", (user_id,))
    incomes = cursor.fetchall()
    connection.close()
    return incomes

def save_category_budget(user_id, category, amount):
    try:
        connection = get_db_connection()
        connection.execute("""
            INSERT INTO category_budgets (user_id, category, amount)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, category) DO UPDATE SET amount = ?
        """, (user_id, category, amount, amount))
        connection.commit()
        connection.close()
        return True
    except Exception:
        return False

def get_category_budgets(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT category, amount FROM category_budgets WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    connection.close()
    return {row[0]: row[1] for row in rows}

def budget_alert(user_id):
    now = datetime.now()
    month = now.strftime('%Y-%m')
    current_day = now.day
    total_days = calendar.monthrange(now.year, now.month)[1]
    budget = get_budget(user_id, month)
    if budget <= 0:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id = ? AND strftime('%Y-%m', date) = ?", (user_id, month))
    total_spent = cursor.fetchone()[0] or 0
    conn.close()
    spending_percentage = (total_spent / budget) * 100
    time_percentage = (current_day / total_days) * 100
    if spending_percentage > time_percentage + 20:
        return {
            "level": "warning",
            "message": f"You have spent {spending_percentage:.2f}% of your budget.",
            "spending": round(total_spent, 2),
            "budget": budget
        }
    return None
