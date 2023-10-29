from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors
import re
import hashlib
import json

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = '!python_database'
mysql = MySQL(app)

app.secret_key = 'flukkiez-secretkey'

with open('my_project.json', 'r') as json_file:
    items = json.load(json_file)


@app.route('/')
def first_page():
    return render_template('html/index.html', items=items)


@app.route('/home')
def home():
    # Check if the user is logged in
    if 'loggedin' in session:
        # User is loggedin show them the home page

        return render_template('html/index.html',
                               username=session['username'],
                               email=session['email'],
                               items=items
                               )
    else:
        return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']  # รับรหัสผ่านแบบเปล่าๆ
        email = request.form['email']
        if len(password) < 8:
            msg = 'Password ต้องมากกว่า 8 ตัว'
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT * FROM accounts WHERE username = %s', (username,))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            elif not username or not password or not email:
                msg = 'Please fill out the form!'
            else:
                # เข้ารหัสรหัสผ่านและบันทึกลงฐานข้อมูล
                hashed_password = hashlib.md5(
                    password.encode()).hexdigest()  # เข้ารหัสรหัสผ่าน
                cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)',
                               (username, hashed_password, email))
                mysql.connection.commit()
                msg = 'สมัครสำเร็จ'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('html/register.html', msg=msg)


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']  # รับรหัสผ่านแบบเปล่าๆ
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM accounts WHERE username = %s AND password = %s', (username, hashlib.md5(password.encode()).hexdigest()))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in our database
        if account:
            # Create session data
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['email'] = account['email']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesn't exist or username/password incorrect
            msg = 'Username หรือ Password ผิด'
    # Show the login form with message (if any)
    return render_template('html/login.html', msg=msg)


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
