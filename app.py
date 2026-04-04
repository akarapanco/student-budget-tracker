from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import data_manager

app = Flask(__name__)
# random key just so it works. can change later
app.secret_key = '12345'

data_manager.setup_db()

# homepage route: dashboard
@app.route('/')
def index():
    return redirect('/dashboard')

# register tab
@app.route('/register', methods=['GET', 'POST'])
def register():
    # if the client sent data, go through these steps (using sql db)
    if request.method == 'POST':
        # username and password forms submitted
        username = request.form['username']
        password = request.form['password']
        
        if data_manager.add_user(username, password):
            return redirect('/login')
        
        else:
            return "Username already exists! <a href='/register'>Try again</a>"
        
    return render_template('register.html')

# login tab
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = data_manager.verify_user(username, password)

        # user exists
        if user is not None:
            # save id in session
            session['user_id'] = user[0] 
            return redirect('/dashboard') # go to dashboard after login
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
        
        if data_manager.add_income(session['user_id'], source, amount):
            return "Income saved! <a href='/add_income'>Click here to add another</a>"
        
        else:
            return "Error saving income. <a href='/add_income'>Try again</a>"
        
    return render_template('add_income.html')



@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        amount = request.form['amount']
        category_id = request.form.get('category_id', 1) 
        
        if data_manager.add_expense(session['user_id'], category_id, amount):
            return "Expense logged! <a href='/add_expense'>Add more</a>"
        else:
            return "Error: Invalid amount. <a href='/add_expense'>Try again</a>"

    return render_template('add_expense.html')


@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    if 'user_id' not in session:
        return redirect('/login')

    if data_manager.delete_expense(expense_id, session['user_id']):
        return "Expense deleted! <a href='/add_expense'>Back to expenses</a>"
    else:
        return "Error deleting expense. <a href='/add_expense'>Try again</a>"

@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        new_source = request.form['source']
        new_amount = request.form['amount']

        if data_manager.edit_expense(expense_id, session['user_id'], new_source, new_amount):
            return "Expense updated! <a href='/add_expense'>Back to expenses</a>"
        else:
            return "Error updating expense. <a href='/add_expense'>Try again</a>"

    expense = data_manager.get_expense(expense_id, session['user_id'])
    if not expense:
        return redirect('/view_expenses')
    return render_template('edit_expense.html', expense=expense)

@app.route('/spending_summary')
def spending_summary():
    if 'user_id' not in session:
        return redirect('/login')

    totals = data_manager.get_category_totals(session['user_id'])
    return render_template('spending_summary.html', totals=totals)
    
@app.route('/financial_overview')
def financial_overview():
    if 'user_id' not in session:
        return redirect('/login')

    overview = data_manager.get_financial_overview(session['user_id'])
    totals = data_manager.get_category_totals(session['user_id'])
    
    return render_template('financial_overview.html', overview=overview, totals=totals)   
    
@app.route('/view_expenses')
def view_expenses():
    if 'user_id' not in session:
        return redirect('/login')

    expenses = data_manager.get_expenses(session['user_id'])
    return render_template('view_expenses.html', expenses=expenses)

@app.route('/set_budget', methods=['GET', 'POST'])
def set_budget():
    if 'user_id' not in session:
        return redirect('/login')
    current_month = datetime.now().strftime('%Y-%m')  # Use current month
    if request.method == 'POST':
        amount = request.form['amount']
        if data_manager.save_budget(session['user_id'], current_month, amount):
            return redirect('/set_budget')
        else:
            return "Error: Invalid budget amount."
    overview = data_manager.get_financial_overview(session['user_id'])
    totals = data_manager.get_category_totals(session['user_id'])
    current_budget = data_manager.get_budget(session['user_id'], current_month)
    return render_template('set_budget.html', overview=overview, totals=totals, current_budget=current_budget, current_month=current_month)

# dashboard tab
@app.route('/dashboard')
def dashboard():
    # have to be logged in
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    current_month = datetime.now().strftime('%Y-%m')

    # stats for dashboard
    overview = data_manager.get_financial_overview(user_id)
    totals = data_manager.get_category_totals(user_id)
    current_budget = data_manager.get_budget(user_id, current_month)

    return render_template('dashboard.html', overview=overview, totals=totals, current_budget=current_budget)

if __name__ == '__main__':
    app.run(debug=True)
