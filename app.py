
import sqlite3
import csv
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from models import save_user, login_user, get_data_from_db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        save_user(username, email, password)
        session['username'] = username
        return redirect(url_for('dashboard'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = login_user(username, password)
        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    buy_data = get_data_from_db('buy')
    sell_data = get_data_from_db('sell')
    return render_template('dashboard.html',
                            username=session['username'],
                            buy_data=buy_data, 
                            sell_data=sell_data)
@app.route('/download/<table_name>')
def download_csv(table_name):
    filename = f"{table_name}.csv"
    conn = sqlite3.connect('swing.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(column_names)  
        writer.writerows(rows)    

    conn.close()
    
    return send_file(filename, as_attachment=True)

@app.route('/toggle_mode', methods=['POST'])
def toggle_mode():
    if 'username' not in session:
        return redirect(url_for('register'))
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
