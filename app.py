from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret'

# Folder para sa image uploads
upload_folder = 'static/uploads'
os.makedirs(upload_folder, exist_ok=True)

def make_db():
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            name TEXT,
            birthday TEXT,
            address TEXT,
            image TEXT
        )
    ''')
    con.commit()
    con.close()

make_db()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        con = sqlite3.connect('users.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (uname, pwd))
        user = cur.fetchone()
        con.close()
        if user:
            session['user'] = uname
            return redirect('/profile')
        else:
            return render_template('login.html', error="Wrong username or password")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        name = request.form['name']
        birthday = request.form['birthday']
        addr = request.form['address']
        img = request.files['image']
        img_name = img.filename if img.filename else None
        if img_name:
            img.save(os.path.join(upload_folder, img_name))

        con = sqlite3.connect('users.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (uname,))
        if cur.fetchone():
            con.close()
            return render_template('register.html', error="Username already exists")
        cur.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", (uname, pwd, name, birthday, addr, img_name))
        con.commit()
        con.close()
        return redirect('/')
    return render_template('register.html')

@app.route('/profile')
def profile():
    if 'user' in session:
        uname = session['user']
        con = sqlite3.connect('users.db')
        cur = con.cursor()
        cur.execute("SELECT name, birthday, address, image FROM users WHERE username=?", (uname,))
        user = cur.fetchone()
        con.close()
        age = ''
        if user:
            birthday_str = user[1]
            if birthday_str and len(birthday_str) == 10 and '-' in birthday_str:
                parts = birthday_str.split('-')
                if len(parts) == 3:
                    year = int(parts[0])
                    month = int(parts[1])
                    day = int(parts[2])
                    today = datetime.today()
                    age = today.year - year
                    if (today.month, today.day) < (month, day):
                        age = age - 1
            return render_template('profile.html', user={
                'name': user[0],
                'age': age,
                'address': user[2],
                'image': user[3]
            })
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
