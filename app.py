from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
import io
import base64
from utils.image_processing import process_image_bytes
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime


app = Flask(__name__)
# In production, use a secure secret key from environment variables
app.config['SECRET_KEY'] = 'dev-secret-key-12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    history = db.relationship('History', backref='author', lazy=True)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    style = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    # If the request is processing an image (AJAX), return JSON error
    if request.path == '/process':
        return jsonify({'error': 'Authentication required. Please log in.', 'redirect': '/login'}), 401
    return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template('index.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'error')
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('signup'))
        
        user_exists = User.query.filter((User.username==username) | (User.email==email)).first()
        if user_exists:
            flash('Username or Email already exists.', 'error')
            return redirect(url_for('signup'))
        
        # Create new user
        new_user = User(username=username, email=email, password=generate_password_hash(password, method='scrypt'))
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        flash('Account created successfully!', 'success')
        return redirect(url_for('index'))
        
    return render_template('signup.html')

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    try:
        # Delete user's history files
        user_history = History.query.filter_by(user_id=current_user.id).all()
        upload_folder = os.path.join(app.root_path, 'static', 'uploads')
        
        for item in user_history:
            filepath = os.path.join(upload_folder, item.filename)
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"Error deleting file {filepath}: {e}")
        
        # Delete history records
        History.query.filter_by(user_id=current_user.id).delete()
        
        # Get user object to delete
        user = User.query.get(current_user.id)
        
        # Delete user and commit
        db.session.delete(user)
        db.session.commit()
        
        # Logout to clear session
        logout_user()
        
        flash('Your account has been deleted.', 'info')
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        print(f"Delete account error: {e}")
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('profile'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    user_history = History.query.filter_by(user_id=current_user.id).order_by(History.timestamp.desc()).all()
    return render_template('profile.html', history=user_history)


@app.route('/process', methods=['POST'])
@login_required
def process():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    style = request.form.get('style', 'original')
    
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400

    try:
        image_bytes = file.read()
        processed_bytes = process_image_bytes(image_bytes, style)
        
        # Convert to base64 for easy frontend display
        img_base64 = base64.b64encode(processed_bytes).decode('utf-8')
        
        # Save to history
        upload_folder = os.path.join('static', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{current_user.id}_{timestamp}_{style}.jpg"
        filepath = os.path.join(upload_folder, filename)
        
        with open(filepath, 'wb') as f:
            f.write(processed_bytes)
            
        new_history = History(filename=filename, style=style, author=current_user)
        db.session.add(new_history)
        db.session.commit()

        
        return jsonify({
            'image': f'data:image/jpeg;base64,{img_base64}',
            'style': style
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create DB if not exists
    with app.app_context():
        db.create_all()
    app.run(debug=True)
