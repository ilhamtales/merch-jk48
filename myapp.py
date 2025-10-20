from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)
app.secret_key = 'rahasia'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def generate_id():
    return uuid.uuid4().hex[:10]

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            flash('Password tidak cocok!')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        user_id = generate_id()
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO tugas_2 (id, username, email, password) VALUES (%s, %s, %s, %s)',
                    (user_id, username, email, hashed_pw))
        mysql.connection.commit()
        cur.close()
        flash('Registrasi berhasil! Silakan login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM tugas_2 WHERE username = %s', (username,))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            flash('Login berhasil!')
            return redirect(url_for('home'))
        flash('Username atau password salah!')
    return render_template('login.html')

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute('SELECT id, username, email FROM tugas_2')
    data = cur.fetchall()
    cur.close()
    return render_template('home.html', tugas_2=data, username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    flash('Berhasil logout!')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)