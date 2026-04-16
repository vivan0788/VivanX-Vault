import os
from flask import Flask, render_template, request, redirect, session, url_for
from flask_pymongo import PyMongo
import bcrypt

# Template folder ka raasta bilkul saaf karein Vercel ke liye
template_dir = os.path.abspath('templates')
app = Flask(__name__, template_folder=template_dir)

# 1. Secret Key (Sessions ke liye mandatory hai)
app.secret_key = "neon_vault_2026_key"

# 2. MongoDB Connectivity
uri = os.environ.get("MONGO_URI")
if not uri:
    # Backup URI agar environment variable nahi milta
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
        users = mongo.db.users
        uname = request.form.get('username')
        pw = request.form.get('password')
        s_key = request.form.get('secret_key')

        if s_key != REGISTRATION_SECRET:
            return "<h3>Invalid Secret Key!</h3>"

        if users.find_one({"username": uname}):
            return "<h3>User already exists! <a href='/register'>Try again</a></h3>"

        hashed_pw = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
        
        users.insert_one({
            "username": uname,
            "password": hashed_pw,
            "vault": {"files": [], "notes": [], "contacts": []}
        })

        return f'''
        <body style="background:#000; display:flex; justify-content:center; align-items:center; height:100vh; margin:0; font-family:sans-serif; text-align:center;">
            <div style="border:2px solid #00f3ff; padding:40px; border-radius:15px; box-shadow:0 0 20px #00f3ff; width:85%;">
                <h1 style="color:#00f3ff; text-shadow:0 0 10px #00f3ff; font-size:2.5rem;">VivanX Vault</h1>
                <h2 style="color:#fff; margin:20px 0;">✅ Account Created!</h2>
                <p style="color:#aaa; margin-bottom:30px; font-size:1.1rem;">Aapka registration safal raha, {uname}!</p>
                <a href="/login" style="background:#ff00ff; color:#fff; text-decoration:none; padding:15px 40px; border-radius:10px; font-weight:bold; box-shadow:0 0 15px #ff00ff; font-size:1.2rem;">LOGIN NOW</a>
            </div>
        </body>
        '''
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        check_user = users.find_one({"username": request.form.get('username')})

        if check_user:
            if bcrypt.checkpw(request.form.get('password').encode('utf-8'), check_user['password']):
                session['username'] = check_user['username']
                return redirect(url_for('dashboard'))
        
        return "<h3>Invalid login! <a href='/login'>Try again</a></h3>"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    try:
        if 'username' in session:
            # File existence check for debugging
            target_file = os.path.join(template_dir, 'dashboard.html')
            if not os.path.exists(target_file):
                return f"Technical Error: dashboard.html not found at {target_file}"
                
            return render_template('dashboard.html', username=session['username'])
        return redirect(url_for('login'))
    except Exception as e:
        return f"Dashboard Runtime Error: {str(e)}"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
