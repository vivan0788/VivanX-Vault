import os
from flask import Flask, render_template, request, redirect, session, url_for
from flask_pymongo import PyMongo
import bcrypt
import cloudinary
import cloudinary.uploader

app = Flask(__name__, template_folder='templates')
app.secret_key = "neon_vault_vivanx_2026"

# MongoDB Config
uri = os.environ.get("MONGO_URI")
if not uri:
    uri = "mongodb+srv://avinash08:Avinash10092009@vanx-tracker.qkqdovs.mongodb.net/VivanX_Vault?retryWrites=true&w=majority"
app.config["MONGO_URI"] = uri
mongo = PyMongo(app)

# Cloudinary Config
cloudinary.config(
  cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME"),
  api_key = os.environ.get("CLOUDINARY_API_KEY"),
  api_secret = os.environ.get("CLOUDINARY_API_SECRET")
)

# Registration Secret Key
REGISTRATION_SECRET = "AVINASH_2026"

@app.route('/')
def home():
    if 'username' in session: return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        uname = request.form.get('username')
        pwd = request.form.get('password')
        u_secret = request.form.get('secret_key')

        if u_secret != REGISTRATION_SECRET:
            return "❌ Invalid Secret Key! Registration Failed."

        if users.find_one({"username": uname}): 
            return "❌ User already exists!"
        
        hashed_pw = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
        users.insert_one({
            "username": uname, 
            "password": hashed_pw,
            "vault": {
                "passwords":[], "notes":[], "contacts":[], 
                "media":{"images":[], "videos":[], "audio":[]}
            }
        })
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = mongo.db.users.find_one({"username": request.form.get('username')})
        if user and bcrypt.checkpw(request.form.get('password').encode('utf-8'), user['password']):
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session: return redirect(url_for('login'))
    user_data = mongo.db.users.find_one({"username": session['username']})
    
    vault = user_data.get('vault', {})
    if 'media' not in vault:
        vault['media'] = {"images": [], "videos": [], "audio": []}
        
    return render_template('dashboard.html', username=session['username'], vault=vault)

# --- Add Data Routes ---
@app.route('/add_contact', methods=['POST'])
def add_contact():
    mongo.db.users.update_one({"username": session['username']}, 
        {"$push": {"vault.contacts": {"name": request.form.get('name'), "phone": request.form.get('phone')}}})
    return redirect(url_for('dashboard'))

@app.route('/add_note', methods=['POST'])
def add_note():
    mongo.db.users.update_one({"username": session['username']}, 
        {"$push": {"vault.notes": {"title": request.form.get('title'), "content": request.form.get('content')}}})
    return redirect(url_for('dashboard'))

@app.route('/add_password', methods=['POST'])
def add_password():
    mongo.db.users.update_one({"username": session['username']}, 
        {"$push": {"vault.passwords": {"site": request.form.get('site'), "pass": request.form.get('acc_pass')}}})
    return redirect(url_for('dashboard'))

@app.route('/upload_media', methods=['POST'])
def upload_media():
    file = request.files.get('file')
    if file:
        res = cloudinary.uploader.upload(file, resource_type="auto")
        url, r_type = res.get('url'), res.get('resource_type')
        cat = "images" if "image" in r_type else "videos" if "video" in r_type else "audio"
        mongo.db.users.update_one({"username": session['username']}, 
            {"$push": {f"vault.media.{cat}": {"name": file.filename, "url": url}}})
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__": app.run(debug=True)
