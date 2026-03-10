from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
# random key just so it works. can change later
app.secret_key = '12345'

def setup_db():
    connection = sqlite3.connect('app_database.db')
    cursor = connection.cursor()

    with open("schema.sql", "r") as file:
        sql_cmds = file.read()
        
    cursor.execute(sql_cmds)

    # save (w/ commit) and close
    connection.commit()
    connection.close()

# register tab
@app.route('/register', methods=['GET', 'POST'])
def register():
    # if the client sent data, go through these steps (using sql db)
    if request.method == 'POST':
        # username and password forms submitted
        username = request.form['username']
        password = request.form['password']
        
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        
        # save user
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        
        connection.commit()
        connection.close()
        
        # Send them to the login page
        return redirect('/login')
        
    return render_template('register.html')

# login tab
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        
        # look for user in the database. ? = the inputs on the right
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone() 
        connection.close()
        
        # user exists
        if user is not None:
            # save id in session
            session['user_id'] = user[0] 
            return redirect('/add_income')
        # user doesnt exist
        else:
            return "Wrong username or password!"
            
    return render_template('login.html')

# add income tab
@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    # if not logged in, goto login
    if 'user_id' not in session:
        return redirect('/login')
        
    if request.method == 'POST':
        source = request.form['source']
        amount = request.form['amount']
        
        # get curr user id
        curr_user_id = session['user_id']
        
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        
        # save income, link user id, use vars inputted
        cursor.execute("INSERT INTO incomes (user_id, source, amount) VALUES (?, ?, ?)", (curr_user_id, source, amount))
        
        # Save and close
        connection.commit()
        connection.close()
        
        return "Income saved! <a href='/add_income'>Click here to add another</a>"
        
    return render_template('add_income.html')

if __name__ == '__main__':
    # setup db before starting server
    setup_db()
    app.run(debug=True)