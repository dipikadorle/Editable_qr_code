from flask import Flask, render_template, request, redirect, url_for, session, flash
import qrcode
import os
import uuid
from database.db import get_db_connection, hash_password, verify_password

# ✅ Correct Flask Initialization
app = Flask(__name__)
app.secret_key = 'dipika123'  # Secret key for session

# ✅ Directory to Store QR Codes
QR_FOLDER = "static/qrcodes/"
os.makedirs(QR_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = hash_password(password)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Signup successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.fetchall()  # ✅ Fix for unread result error
        cursor.close()
        conn.close()

        if user and verify_password(password, user['password']):
            session['user_id'] = user['id']
            flash("Login Successful", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid Email or Password 🚫", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM qr_codes WHERE user_id = %s", (session['user_id'],))
    qr_codes = cursor.fetchall()
    conn.close()

    return render_template('dashboard.html', qr_codes=qr_codes)

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    url = request.form['url']
    short_url = str(uuid.uuid4())[:8]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO qr_codes (user_id, short_url, target_url) VALUES (%s, %s, %s)", (session['user_id'], short_url, url))
    conn.commit()

    # ✅ Store real URL in QR code
    qr_code = qrcode.make(url)
    qr_path = os.path.join(QR_FOLDER, f"{short_url}.png")
    qr_code.save(qr_path)

    flash("QR Code Generated Successfully ✅", "success")
    return redirect('/dashboard')

@app.route('/qr/<short_url>')
def redirect_qr(short_url):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT target_url FROM qr_codes WHERE short_url = %s", (short_url,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return redirect(result['target_url'])
    else:
        return "Invalid QR Code"

@app.route('/update_qr', methods=['POST'])
def update_qr():
    short_url = request.form['short_url']
    new_url = request.form['new_url']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE qr_codes SET target_url = %s WHERE short_url = %s", (new_url, short_url))
    conn.commit()

    # ✅ Update QR Code image as well
    qr_code = qrcode.make(new_url)
    qr_path = os.path.join(QR_FOLDER, f"{short_url}.png")
    qr_code.save(qr_path)

    conn.close()
    flash("QR Code Link Updated Successfully 🔥", "success")
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ✅ Final Port Binding Fix for Render Deployment
if __name__ == '__main__':
    from os import environ
    port = int(environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
