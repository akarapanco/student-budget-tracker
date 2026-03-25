import sqlite3
import os

DB_NAME = 'app_database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn

def setup_db():
    connection = sqlite3.connect('app_database.db')
    cursor = connection.cursor()

    with open("schema.sql", "r") as file:
        sql_cmds = file.read()
        
    cursor.execute(sql_cmds)

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

def add_income(user_id, source, amount):
    try:
        connection = get_db_connection()
        connection.execute("INSERT INTO incomes (user_id, source, amount) VALUES (?, ?, ?)", (user_id, source, amount))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        return False
    
def add_expense(user_id, source, amount):
    try:
        connection = get_db_connection()
        connection.execute("INSERT INTO expenses (user_id, source, amount) VALUES (?, ?, ?)", (user_id, source, amount))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        return False
    