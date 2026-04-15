from flask import Flask, render_template, request, redirect, session, url_for
from flask_pymongo import PyMongo
import bcrypt

app = Flask(__name__)
app.secret_key = "neon_vault_2026_key"

# MongoDB Connectivity (Change with your Atlas Link)
app.config["MONGO_URI"] = "mongodb+srv://avinash08:Avinash10092009@vanx-tracker.qkqdovs.mongodb.net/VivanX_Vault?retryWrites=true&w=majority"
mongo = PyMongo(app)

# MASTER KEY for Registration
REGISTRATION_SECRET = "AVINASH_2026"

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('register_page'))

@app.route('/register_page')
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    users = mongo.db.users
    uname = request.form.get('username')
    pw = request.form.get('password')
    s_key = request.form.get('secret_key')

    if s_key != REGISTRATION_SECRET:
        return "<h3>Invalid Secret Key! Contact Admin.</h3>"

    if users.find_one({"username": uname}):
        return "<h3>User already exists!</h3>"

    # Encrypt Password
    hashed_pw = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
    
    users.insert_one({
        "username": uname,
        "password": hashed_pw,
        "vault": {"files": [], "notes": [], "contacts": []}
    })
    return '''
    <div style="background:#000; height:100vh; display:flex; flex-direction:column; justify-content:center; align-items:center; font-family:sans-serif;">
        <h1 style="color:#00f3ff; text-shadow:0 0 15px #00f3ff;">✅ Registration Successful!</h1>
        <p style="color:#fff; font-size:1.2rem;">Aapka account ban gaya hai.</p>
        <a href="/login" style="color:#ff00ff; text-decoration:none; border:1px solid #ff00ff; padding:10px 20px; border-radius:5px; box-shadow:0 0 10px #ff00ff; margin-top:20px;">LOGIN NOW</a>
    </div>
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        check_user = users.find_one({"username": request.form.get('username')})

        if check_user and bcrypt.checkpw(request.form.get('password').encode('utf-8'), check_user['password']):
            session['username'] = check_user['username']
            return redirect(url_for('dashboard'))
        return "Invalid Username or Password!"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        # User-specific data fetch
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
