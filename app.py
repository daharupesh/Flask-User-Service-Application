from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import re
import mysql.connector

app = Flask(__name__)
app.secret_key = '12345'

db = {
    'host': 'localhost',
    'user': 'root',  
    'password': '',  
    'database': 'user_service'  
}

def get_users():
    """Function to fetch users from the MySQL database"""
    conn = mysql.connector.connect(**db)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, timestamp FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

def email_exists(email):
    """Check if the email already exists in the database"""
    conn = mysql.connector.connect(**db)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count > 0

@app.route('/', methods=['GET', 'POST'])
def home():
    present_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        # Validation patterns
        name_pattern = re.compile(r'^[A-Za-z\s]+$')
        email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

        # Server-side validation
        if not name_pattern.match(name):
            flash('Invalid name! Please enter a valid name.', 'danger')
        elif not email_pattern.match(email):
            flash('Invalid email! Please enter a valid email.', 'danger')
        elif email_exists(email):
            flash('Email already exists! Please use a different email.', 'danger')
        else:
            # Insert the new user into the database
            conn = mysql.connector.connect(**db)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name, email, timestamp) VALUES (%s, %s, %s)", 
                           (name, email, present_time))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Form submitted successfully!', 'success')
            return redirect(url_for('users'))

    return render_template('index.html', present_time=present_time)

@app.route('/users', methods=['GET'])
def users():
    users = get_users()
    return render_template('users.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)
