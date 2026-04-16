import os
from flask import Flask, render_template, request, redirect, session, url_for
from flask_pymongo import PyMongo
import bcrypt

# Vercel ke liye template folder ka path sahi set karein
app = Flask(__name__, template_folder='templates')
app.secret_key = "neon_vault_2026_key"

# MongoDB URI (Quotes hatane ke baad ye sahi chalega)
uri = os.environ.get("MONGO_URI")
if not uri:
    # Backup URI
    uri = "mongodb+srv://avinash08:Avinash10092009@vanx-tracker.qkqdovs.mongodb.net/VivanX_Vault?retryWrites=true&w=majority"

app.config["MONGO_URI"] = uri
mongo = PyMongo(app)

REGISTRATION_SECRET = "AVINASH_2026"

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            users = mongo.db.users
            uname = request.form.get('username')
            pw = request.form.get('password')
            s_key = request.form.get('secret_key')

            if s_key != REGISTRATION_SECRET:
                return "<h3>Invalid Secret Key!</h3>"
            
            if users.find_one({"username": uname}):
                return "<h3>User already exists!</h3>"

            hashed_pw = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
            users.insert_one({
                "username": uname,
                "password": hashed_pw,
                "vault": {"files": [], "notes": [], "contacts": []}
            })
            return redirect(url_for('login'))
        except Exception as e:
            return f"Registration Error: {str(e)}"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            users = mongo.db.users
            check_user = users.find_one({"username": request.form.get('username')})
            if check_user and bcrypt.checkpw(request.form.get('password').encode('utf-8'), check_user['password']):
                session['username'] = check_user['username']
                return redirect(url_for('dashboard'))
            return "<h3>Invalid Login!</h3>"
        except Exception as e:
            return f"Login Error: {str(e)}"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    try:
        if 'username' in session:
            return render_template('dashboard.html', username=session['username'])
        return redirect(url_for('login'))
    except Exception as e:
        # Agar template nahi mil raha toh ye error dikhayega
        return f"Dashboard Display Error: {str(e)}"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
