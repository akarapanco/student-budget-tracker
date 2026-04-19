from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import data_manager

app = Flask(__name__)
app.secret_key = '12345'
app.config['SESSION_TYPE'] = timedelta(minutes = 30)

data_manager.setup_db()
data_manager.migrate_db()

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('add_income'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if data_manager.add_user(username, password):
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error_message="Username already exists!")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = data_manager.verify_user(username, password)
        if user is not None:
            session.permanent = True
            session['user_id'] = user[0]
            return redirect(url_for('add_income'))
        else:
            return render_template('login.html', error_message="Incorrect username or password!")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    current_budget = data_manager.get_budget(user_id, datetime.now().strftime('%Y-%m'))
    overview = data_manager.get_financial_overview(user_id)
    totals = data_manager.get_category_totals(user_id)
    alert = data_manager.budget_alert(user_id)
    success_message = session.pop('success_message', None)
    budgets = data_manager.get_category_budgets(user_id)
    incomes = data_manager.get_incomes(user_id)
    return render_template('dashboard.html', current_budget=current_budget, overview=overview, totals=totals, alert=alert, success_message=success_message, budgets=budgets, incomes=incomes)

@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        source = request.form['source']
        amount = request.form['amount']
        if data_manager.add_income(session['user_id'], source, amount):
            incomes = data_manager.get_incomes(session['user_id'])
            return render_template('add_income.html', incomes=incomes, success_message="Income saved!")
        else:
            return render_template('add_income.html', error_message="Error saving income. Please try again.")
    return render_template('add_income.html')

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form.get('category', 'Other')
        description = request.form.get('description', '')
        if data_manager.add_expense(session['user_id'], category, amount, description):
            session['success_message'] = "Expense logged!"
            return redirect(url_for('add_income'))
        else:
            return render_template('add_expense.html', error_message="Error logging expense. Please try again.")
    return render_template('add_expense.html')

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if data_manager.delete_expense(expense_id, session['user_id']):
        session['success_message'] = "Expense deleted successfully."
    else:
        session['error_message'] = "Error deleting expense. Please try again."
    return redirect(url_for('add_income'))

@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_category = request.form['category']
        new_amount = request.form['amount']
        if data_manager.edit_expense(expense_id, session['user_id'], new_category, new_amount):
            session['success_message'] = "Expense updated."
            return redirect(url_for('add_income'))
        else:
            expense = data_manager.get_expense(expense_id, session['user_id'])
            return render_template('edit_expense.html', expense=expense, error_message="Error updating expense. Please try again.")
    expense = data_manager.get_expense(expense_id, session['user_id'])
    if not expense:
        return redirect(url_for('add_income'))
    return render_template('edit_expense.html', expense=expense)

@app.route('/spending_summary')
def spending_summary():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    totals = data_manager.get_category_totals(session['user_id'])
    alert = data_manager.budget_alert(session['user_id'])
    budgets = data_manager.get_category_budgets(session['user_id'])
    return render_template('spending_summary.html', totals=totals, alert=alert, budgets=budgets)

@app.route('/financial_overview')
def financial_overview():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    overview = data_manager.get_financial_overview(session['user_id'])
    totals = data_manager.get_category_totals(session['user_id'])
    return render_template('financial_overview.html', overview=overview, totals=totals)

@app.route('/view_expenses')
def view_expenses():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    expenses = data_manager.get_expenses(session['user_id'])
    success_message = session.pop('success_message', None)
    error_message = session.pop('error_message', None)
    return render_template('view_expenses.html', expenses=expenses, success_message=success_message, error_message=error_message)

@app.route('/set_budget', methods=['GET', 'POST'])
def set_budget():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    current_month = datetime.now().strftime('%Y-%m')
    categories = ['Food & Dining', 'Transport', 'Entertainment', 'Rent/Utilities', 'Health & Fitness', 'Education', 'Shopping', 'Travel', 'Other']
    if request.method == 'POST':
        selected = request.form.getlist('selected_categories')
        for category in selected:
            amount = request.form.get('amount_' + category, 0)
            if amount:
                data_manager.save_category_budget(session['user_id'], category, amount)
        amount = request.form.get('amount', 0)
        if amount:
            data_manager.save_budget(session['user_id'], current_month, amount)
        session['success_message'] = "Budget saved!"
        return redirect(url_for('add_income'))
    existing = data_manager.get_category_budgets(session['user_id'])
    current_budget = data_manager.get_budget(session['user_id'], current_month)
    return render_template('set_budget.html', categories=categories, existing=existing, current_budget=current_budget)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
