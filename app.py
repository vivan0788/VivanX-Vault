import os
from flask import Flask, render_template, request, redirect, session, url_for
from flask_pymongo import PyMongo
import bcrypt
import cloudinary
import cloudinary.uploader

app = Flask(__name__, template_folder='templates')
app.secret_key = "vivanx_ultra_secure_2026"

# MongoDB Config
uri = os.environ.get("MONGO_URI")
if not uri:
    uri = "mongodb+srv://avinash08:Avinash10092009@vanx-tracker.qkqdovs.mongodb.net/VivanX_Vault?retryWrites=true&w=majority"
app.config["MONGO_URI"] = uri
mongo = PyMongo(app)

# Cloudinary Config (secure=True added for SSL fix)
cloudinary.config(
  cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME"),
  api_key = os.environ.get("CLOUDINARY_API_KEY"),
  api_secret = os.environ.get("CLOUDINARY_API_SECRET"),
  secure = True 
)

REGISTRATION_SECRET = "AVINASH_2026"

@app.route('/')
def home():
    if 'username' in session: return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        uname, pwd, u_sec = request.form.get('username'), request.form.get('password'), request.form.get('secret_key')
        if u_sec != REGISTRATION_SECRET: return "❌ Invalid Secret Key!"
        if users.find_one({"username": uname}): return "❌ User exists!"
        
        hashed_pw = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
        users.insert_one({"username": uname, "password": hashed_pw, "vault": {"passwords":[], "notes":[], "contacts":[], "media":{"images":[], "videos":[], "audio":[]}}})
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
    vault = user_data.get('vault', {"contacts":[], "notes":[], "passwords":[], "media":{"images":[], "videos":[], "audio":[]}})
    return render_template('dashboard.html', username=session['username'], vault=vault)

# --- Action Routes ---
@app.route('/add/<type>', methods=['POST'])
def add_data(type):
    data = {}
    if type == 'contact': data = {"name": request.form.get('name'), "phone": request.form.get('phone')}
    elif type == 'note': data = {"title": request.form.get('title'), "content": request.form.get('content')}
    elif type == 'pass': data = {"site": request.form.get('site'), "pass": request.form.get('acc_pass')}
    
    mongo.db.users.update_one({"username": session['username']}, {"$push": {f"vault.{type}s": data}})
    return redirect(url_for('dashboard'))

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if file:
        res = cloudinary.uploader.upload(file, resource_type="auto")
        cat = "images" if "image" in res['resource_type'] else "videos" if "video" in res['resource_type'] else "audio"
        mongo.db.users.update_one({"username": session['username']}, {"$push": {f"vault.media.{cat}": {"url": res['url']}}})
    return redirect(url_for('dashboard'))

# --- Delete Routes ---
@app.route('/delete/<type>/<int:idx>')
@app.route('/delete_media/<cat>/<int:idx>')
def delete_item(type=None, cat=None, idx=None):
    field = f"vault.{type}s" if type else f"vault.media.{cat}"
    user = mongo.db.users.find_one({"username": session['username']})
    # Nested navigation to get the list
    path = field.split('.')
    target_list = user
    for p in path: target_list = target_list[p]
    
    if 0 <= idx < len(target_list):
        target_list.pop(idx)
        mongo.db.users.update_one({"username": session['username']}, {"$set": {field: target_list}})
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__": app.run(debug=True)
