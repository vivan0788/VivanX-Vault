import os
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_pymongo import PyMongo
import bcrypt

app = Flask(__name__, template_folder='templates')
app.secret_key = "neon_vault_2026_key"

# MongoDB Connectivity
uri = os.environ.get("MONGO_URI")
if not uri:
    uri = "mongodb+srv://avinash08:Avinash10092009@vanx-tracker.qkqdovs.mongodb.net/VivanX_Vault?retryWrites=true&w=majority"

app.config["MONGO_URI"] = uri
mongo = PyMongo(app)

REGISTRATION_SECRET = "AVINASH_2026"

# --- HELPER FUNCTIONS ---
def get_user_data():
    if 'username' in session:
        return mongo.db.users.find_one({"username": session['username']})
    return None

# --- BASIC ROUTES ---
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
            return "<h3>User already exists!</h3>"

        hashed_pw = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
        users.insert_one({
            "username": uname,
            "password": hashed_pw,
            "vault": {
                "passwords": [],
                "files": [], 
                "notes": [], 
                "contacts": [],
                "media": {"images": [], "videos": [], "audio": []}
            }
        })
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        check_user = users.find_one({"username": request.form.get('username')})
        if check_user and bcrypt.checkpw(request.form.get('password').encode('utf-8'), check_user['password']):
            session['username'] = check_user['username']
            return redirect(url_for('dashboard'))
        return "<h3>Invalid login!</h3>"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    user_data = get_user_data()
    if user_data:
        return render_template('dashboard.html', username=session['username'], vault=user_data.get('vault'))
    return redirect(url_for('login'))

# --- FEATURE ROUTES (DATABASE OPERATIONS) ---

@app.route('/add_contact', methods=['POST'])
def add_contact():
    if 'username' in session:
        name = request.form.get('name')
        phone = request.form.get('phone')
        mongo.db.users.update_one(
            {"username": session['username']},
            {"$push": {"vault.contacts": {"name": name, "phone": phone}}}
        )
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/add_note', methods=['POST'])
def add_note():
    if 'username' in session:
        title = request.form.get('title')
        content = request.form.get('content')
        mongo.db.users.update_one(
            {"username": session['username']},
            {"$push": {"vault.notes": {"title": title, "content": content}}}
        )
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/add_password', methods=['POST'])
def add_password():
    if 'username' in session:
        site = request.form.get('site')
        acc_pass = request.form.get('acc_pass')
        # Security ke liye aap ise yahan encrypt bhi kar sakte hain
        mongo.db.users.update_one(
            {"username": session['username']},
            {"$push": {"vault.passwords": {"site": site, "pass": acc_pass}}}
        )
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Placeholder for Media Upload (Cloudinary Integration Needed)
@app.route('/upload_media', methods=['POST'])
def upload_media():
    return "Media Upload Feature Coming Soon with Cloudinary!"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
