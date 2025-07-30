from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime
from functools import wraps
import csv
import io

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# --- DATABASE INITIALIZATION ---
# This function creates the database and tables.
def init_db():
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_admin BOOLEAN DEFAULT 0
        )
    ''')
    
    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
            amount DECIMAL(10,2) NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Budget table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            monthly_limit DECIMAL(10,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # User sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

#
# IMPORTANT: Call init_db() here to ensure tables exist when the app starts.
#
init_db()


# --- DECORATORS ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        conn = sqlite3.connect('finance_tracker.db')
        cursor = conn.cursor()
        cursor.execute('SELECT is_admin FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        conn.close()
        
        if not user or not user[0]:
            flash('Admin access required', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'warning')
            return render_template('register.html')
        
        password_hash = generate_password_hash(password)
        
        try:
            conn = sqlite3.connect('finance_tracker.db')
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            conn.commit()
            conn.close()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
            
        except sqlite3.IntegrityError:
            flash('Username or email already exists', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')

# (The rest of your routes: /login, /dashboard, etc. go here)
# For brevity, I'm omitting the rest of the routes as they are unchanged.
# Just make sure this top part of your file is correct.
# You can copy-paste the other routes from your existing file below this point.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('finance_tracker.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, password_hash, is_admin FROM users WHERE username = ?',
            (username,)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            session['is_admin'] = user[2]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT type, amount, category, description, date 
        FROM transactions 
        WHERE user_id = ? 
        ORDER BY date DESC, created_at DESC 
        LIMIT 10
    ''', (session['user_id'],))
    transactions = cursor.fetchall()
    
    current_month = datetime.now().strftime('%Y-%m')
    cursor.execute('''
        SELECT type, SUM(amount) 
        FROM transactions 
        WHERE user_id = ? AND date LIKE ? 
        GROUP BY type
    ''', (session['user_id'], f'{current_month}%'))
    
    monthly_summary = {'income': 0, 'expense': 0}
    for row in cursor.fetchall():
        monthly_summary[row[0]] = row[1]
    
    conn.close()
    
    return render_template('dashboard.html', 
                           transactions=transactions, 
                           monthly_summary=monthly_summary)

@app.route('/add_transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        transaction_type = request.form['type']
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form['description']
        date = request.form['date']
        
        conn = sqlite3.connect('finance_tracker.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (user_id, type, amount, category, description, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], transaction_type, amount, category, description, date))
        conn.commit()
        conn.close()
        
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_transaction.html')

@app.route('/api/transactions')
@login_required
def api_transactions():
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, type, amount, category, description, date 
        FROM transactions 
        WHERE user_id = ? 
        ORDER BY date DESC
    ''', (session['user_id'],))
    
    transactions = [{'id': r[0], 'type': r[1], 'amount': r[2], 'category': r[3], 'description': r[4], 'date': r[5]} for r in cursor.fetchall()]
    conn.close()
    return jsonify(transactions)

@app.route('/api/budget_status')
@login_required
def api_budget_status():
    user_id = request.args.get('user_id', session['user_id'])
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT b.category, b.monthly_limit, 
               COALESCE(SUM(t.amount), 0) as spent
        FROM budgets b
        LEFT JOIN transactions t ON b.category = t.category 
            AND b.user_id = t.user_id 
            AND t.type = 'expense'
            AND strftime('%Y-%m', t.date) = strftime('%Y-%m', 'now')
        WHERE b.user_id = ?
        GROUP BY b.category, b.monthly_limit
    ''', (user_id,))
    
    budget_data = [{'category': r[0], 'limit': r[1], 'spent': r[2], 'remaining': r[1] - r[2]} for r in cursor.fetchall()]
    conn.close()
    return jsonify(budget_data)

@app.route('/admin')
@admin_required
def admin_panel():
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email, created_at FROM users')
    users = cursor.fetchall()
    cursor.execute('SELECT COUNT(*) FROM transactions')
    total_transactions = cursor.fetchone()[0]
    conn.close()
    return render_template('admin.html', users=users, total_transactions=total_transactions)

@app.route('/export_data')
@login_required
def export_data():
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions WHERE user_id = ?', (session['user_id'],))
    data = cursor.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'UserID', 'Type', 'Amount', 'Category', 'Description', 'Date', 'CreatedAt'])
    writer.writerows(data)
    
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=transactions.csv'
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
