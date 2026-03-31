import sqlite3
import os

DB_NAME = 'app_database.db'


# def get_user_categories(user_id):
#     conn = get_db_connection()
#     categories = conn.execute(
#         "SELECT * FROM expense_categories WHERE user_id = ?", 
#         (user_id,)
#     ).fetchall()
#     conn.close()
#     return categories

# def add_custom_category(user_id, name):
#     try:
#         conn = get_db_connection()
#         conn.execute(
#             "INSERT INTO expense_categories (user_id, name) VALUES (?, ?)", 
#             (user_id, name.strip())
#         )
#         conn.commit()
#         conn.close()
#         return True
#     except sqlite3.IntegrityError:
#         return False
    

def is_valid_txn(amount):
    try:
        float_amount = float(amount)
        if float_amount <= 0:
            return False
        else:
            return True
    except ValueError:
        return False

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn

def setup_db():
    connection = sqlite3.connect('app_database.db')
    cursor = connection.cursor()

    with open("schema.sql", "r") as file:
        sql_cmds = file.read()
        
    cursor.executescript(sql_cmds)

    # save (w/ commit) and close
    connection.commit()
    connection.close()


def add_user(username, password):
    try:
        connection = get_db_connection()
        connection.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        return False
    
def verify_user(username, password):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone() 
    connection.close()
    return user

def add_income(user_id, course, amount):
    if not is_valid_txn(amount):
        return False
    
    try:
        connection = get_db_connection()
        connection.execute("INSERT INTO incomes (user_id, source, amount) VALUES (?, ?, ?)", (user_id, category_id, amount))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        return False
    
def add_expense(user_id, category_id, amount):
    if not is_valid_txn(amount):
        return False

    try:
        connection = get_db_connection()
        connection.execute("INSERT INTO expenses (user_id, category_id, amount) VALUES (?, ?, ?)", (user_id, category_id, amount))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        return False
    
def delete_expense(expense_id, user_id):
    try:
        connection = get_db_connection()
        connection.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        return False
    

def edit_expense(expense_id, user_id, new_category_id, new_amount):
    if not is_valid_txn(new_amount):
        return False
    
    try:
        connection = get_db_connection()
        connection.execute("UPDATE expenses SET category_id = ?, amount = ? WHERE id = ? AND user_id = ?", (new_source, new_amount, expense_id, user_id))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        return False
    
def get_expenses(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM expenses WHERE user_id = ?", (user_id,))
    expenses = cursor.fetchall() 
    connection.close()
    return expenses


def get_category_totals(user_id):
    category_names = {
        1: 'Food & Dining',
        2: 'Transport',
        3: 'Entertainment',
        4: 'Rent/Utilities',
        5: 'Health & Fitness',
        6: 'Education',
        7: 'Shopping',
        8: 'Travel',
        9: 'Other'
    }
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT category_id, SUM(amount) FROM expenses WHERE user_id = ? GROUP BY category_id",
        (user_id,)
    )
    rows = cursor.fetchall()
    connection.close()

    totals = []
    for category_id, total in rows:
        name = category_names.get(category_id, 'Other')
        totals.append((name, round(total, 2)))

    return totals

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

