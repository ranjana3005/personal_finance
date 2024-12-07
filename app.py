from flask import Flask, render_template, request, redirect, session
import mysql.connector
from passlib.hash import sha256_crypt
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database connection settings
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'pass',
    'database': 'personal_finance'
}

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = sha256_crypt.encrypt(request.form['password'])
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, password)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and sha256_crypt.verify(password, user[3]):
            session['user_id'] = user[0]
            return redirect('/dashboard')
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transactions WHERE user_id = %s", (session['user_id'],))
    transactions = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('dashboard.html', transactions=transactions)

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    if 'user_id' not in session:
        return redirect('/login')
    transaction_type = request.form['type']
    category = request.form['category']
    amount = request.form['amount']
    date = request.form['date']
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (user_id, type, category, amount, date) VALUES (%s, %s, %s, %s, %s)",
        (session['user_id'], transaction_type, category, amount, date)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
