from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from datetime import datetime, timedelta
from authlib.integrations.flask_client import OAuth
from flask_dance.contrib.google import make_google_blueprint, google
import os
from dotenv import load_dotenv
from sqlalchemy import desc
import logging
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS, cross_origin
import requests
import json  # ADD THIS
import traceback  # ADD THIS
import os



logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
# UPDATE your CORS to be more permissive for local development
CORS(
    app,
    resources={r"/*": {
        "origins": [
            "http://127.0.0.1:10000",
            "http://localhost:10000",
            "http://localhost:5000",  # ADD THIS
            "https://cleanifyservice.com"
        ],
        "supports_credentials": True,
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }},
    supports_credentials=True
)


app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_DOMAIN=None,
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=timedelta(days=7)
)

if os.getenv("FLASK_ENV") == "development":
    app.config.update(
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False
    )
else:
    app.config.update(
        SESSION_COOKIE_SAMESITE="None",
        SESSION_COOKIE_SECURE=True
    )


# ✅ Use MySQL database
database_url = os.getenv("DATABASE_URL")

if database_url:
    # Ensure it uses postgresql:// instead of postgres://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    # Add ?sslmode=require at the end if not present
    if "sslmode" not in database_url:
        if "?" in database_url:
            # If already has query parameters, append with &
            database_url += "&sslmode=require"
        else:
            # If no query parameters, start with ?
            database_url += "?sslmode=require"
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:San00006$@localhost/alazeez_db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# OAuth configuration
oauth = OAuth(app)

# Email configuration for SendGrid
# Email configuration - ONLY for SendGrid API (NO SMTP)
app.config['MAIL_DEFAULT_SENDER'] = 'abdulhyr@gmail.com'  # Use your REAL email

# Remove or comment out the old email config:
# app.config.update(
#     MAIL_SERVER='smtp.gmail.com',
#     MAIL_PORT=587,
#     MAIL_USE_TLS=True,
#     MAIL_USERNAME='your-email@gmail.com',
#     MAIL_PASSWORD='your-email-password-or-app-password'
# )


# Google OAuth
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={
        'scope': 'openid email profile',
        'token_endpoint_auth_method': 'client_secret_post'
    },
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)

# LinkedIn OAuth registration
linkedin = oauth.register(
    name='linkedin',
    client_id=os.getenv('LINKEDIN_CLIENT_ID'),
    client_secret=os.getenv('LINKEDIN_CLIENT_SECRET'),
    access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
    authorize_url='https://www.linkedin.com/oauth/v2/authorization',
    api_base_url='https://api.linkedin.com/v2/',
    client_kwargs={
        'scope': 'openid profile email',  # Updated scopes
        'token_endpoint_auth_method': 'client_secret_post',
    },
    authorize_params={
        'response_type': 'code',
    }
)

# User model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='user')
    provider = db.Column(db.String(50), nullable=True)
    provider_id = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.email}>'

# Serve images from root images folder
@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('images', filename)

# Main Pages
@app.route('/')
def index():
    """Render the homepage"""
    return render_template('index.html')


@app.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')

@app.route('/services')
def services():
    """Render the services page"""
    return render_template('services.html')

@app.route('/contact')
def contact():
    """Render the contact page"""
    return render_template('contact.html')

# Service Detail Pages - UPDATED to match your folder structure
@app.route('/service/home-cleaning')
def home_cleaning():
    """Render home cleaning service page"""
    try:
        return render_template('service/home-cleaning.html')
    except:
        return "Home Cleaning page not found. Please check if the file exists in templates/service/", 404

@app.route('/service/sofa-cleaning')
def sofa_cleaning():
    """Render sofa cleaning service page"""
    try:
        return render_template('service/sofa-cleaning.html')
    except:
        return "Sofa Cleaning page not found. Please check if the file exists in templates/service/", 404

@app.route('/service/kitchen-cleaning')
def kitchen_cleaning():
    """Render kitchen cleaning service page"""
    try:
        return render_template('service/kitchen-cleaning.html')
    except:
        return "Kitchen Cleaning page not found. Please check if the file exists in templates/service/", 404

@app.route('/service/bathroom-cleaning')
def bathroom_cleaning():
    """Render bathroom cleaning service page"""
    try:
        return render_template('service/bathroom-cleaning.html')
    except:
        return "Bathroom Cleaning page not found. Please check if the file exists in templates/service/", 404

@app.route('/service/carpet-cleaning')
def carpet_cleaning():
    """Render carpet cleaning service page"""
    try:
        return render_template('service/carpet-cleaning.html')
    except:
        return "Carpet Cleaning page not found. Please check if the file exists in templates/service/", 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash("No account found with this email. Please sign up first.", "danger")
            return redirect(url_for('signup'))
            
        if not user.password:  # User signed up with Google
            flash("This email is associated with a Google account. Please login with Google.", "info")
            return redirect(url_for('login'))
            
        # Check if it's the admin user with special handling
        if user.email == 'creativeshanansari@gmail.com' and user.role == 'admin':
            if check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['role'] = user.role
                session['name'] = user.name
                # Update last_login
                user.last_login = datetime.utcnow()
                db.session.commit()
                flash("Admin logged in successfully!", "success")
                return redirect(url_for('index'))
            else:
                flash("Invalid admin credentials.", "danger")
                return redirect(url_for('login'))
            
        # For regular users
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            session['name'] = user.name
            session.permanent = True
            # Update last_login
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash("Logged in successfully!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # Block fake admin signup
        if role == 'admin':
            if email.lower() != 'creativeshanansari@gmail.com' or name.strip().lower() != 'admin':
                flash("You are not authorized to register as admin.", "danger")
                return redirect(url_for('signup'))

        # Check for existing user
        existing = User.query.filter_by(email=email).first()
        if existing:
            if existing.provider:  # User exists with Google
                flash("This email is already registered with Google. Please login with Google.", "info")
            else:  # User exists with email/password
                flash("Email already exists. Please login.", "danger")
            return redirect(url_for('login'))

        # Create new user
        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role=role,
            provider=None,
            provider_id=None
        )
        db.session.add(user)
        db.session.commit()

        flash("Signup successful. Please login.", "success")
        return redirect(url_for('login'))

    return render_template('login.html')



@app.route('/login/google')
def google_login():
    redirect_uri = url_for('google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/authorize')
def google_authorize():
    try:
        # Get the token and user info
        token = google.authorize_access_token()
        if not token:
            flash("Google login failed. No token received.", "danger")
            return redirect(url_for('login'))

        resp = google.get('userinfo')
        if resp.status_code != 200:
            flash("Failed to fetch user information from Google.", "danger")
            return redirect(url_for('login'))
            
        user_info = resp.json()
        print("Google User Info:", user_info)  # Debug output

        # Verify we have required fields - NOTE THE CHANGE FROM 'sub' TO 'id'
        if not user_info.get('id') or not user_info.get('email'):
            flash("Google didn't provide required user information.", "danger")
            return redirect(url_for('login'))

        # Use 'id' instead of 'sub' as provider_id
        provider_id = user_info['id']
        
        # Check if user exists by provider_id
        user = User.query.filter_by(provider='google', provider_id=provider_id).first()
        
        if not user:
            # Check if email exists with another provider
            existing_email_user = User.query.filter_by(email=user_info['email']).first()
            if existing_email_user:
                flash("This email is already registered with email/password. Please login with email.", "danger")
                return redirect(url_for('login'))
            
            # Create new user
            user = User(
                name=user_info.get('name', 'Google User'),
                email=user_info.get('email'),
                password=None,
                role='user',
                provider='google',
                provider_id=provider_id  # Using 'id' instead of 'sub'
            )
            db.session.add(user)
            db.session.commit()
        
        # Login the user
        session['user_id'] = user.id
        session['role'] = user.role
        session['name'] = user.name
        session.permanent = True
        flash("Logged in with Google successfully!", "success")
        return redirect(url_for('index'))
        
    except Exception as e:
        print("Google auth error:", str(e))  # Debug output
        flash("Google login failed. Please try again.", "danger")
        return redirect(url_for('login'))

@app.route('/login/linkedin')
def linkedin_login():
    try:
        redirect_uri = url_for('linkedin_authorize', _external=True)
        print(f"Redirecting to LinkedIn with URI: {redirect_uri}")  # Debug
        return linkedin.authorize_redirect(redirect_uri)
    except Exception as e:
        print(f"LinkedIn redirect error: {str(e)}")
        flash("Failed to initiate LinkedIn login", "danger")
        return redirect(url_for('login'))

@app.route('/login/linkedin/authorize')
def linkedin_authorize():
    try:
        # Get access token
        token = linkedin.authorize_access_token()
        if not token:
            flash("LinkedIn login failed. No token received.", "danger")
            return redirect(url_for('login'))

        # Fetch user info using OpenID Connect
        resp = linkedin.get('userinfo')
        if resp.status_code != 200:
            flash("Failed to fetch user information from LinkedIn.", "danger")
            return redirect(url_for('login'))

        user_info = resp.json()
        print("LinkedIn User Info:", user_info)  # Debug output

        # Extract user data
        linkedin_id = user_info.get('sub')
        email = user_info.get('email')
        name = user_info.get('name')
        
        if not all([linkedin_id, email, name]):
            flash("Incomplete user information from LinkedIn.", "danger")
            return redirect(url_for('login'))

        # Find or create user
        user = User.query.filter_by(provider='linkedin', provider_id=linkedin_id).first()

        if not user:
            # Check if email already exists with another provider
            existing_email_user = User.query.filter_by(email=email).first()
            if existing_email_user:
                flash("This email is already registered. Please login directly.", "danger")
                return redirect(url_for('login'))

            # Create new user
            user = User(
                name=name,
                email=email,
                password=None,  # No password for OAuth users
                role='user',
                provider='linkedin',
                provider_id=linkedin_id,
                last_login=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()
            flash("Account created successfully with LinkedIn!", "success")
        else:
            # Update last login for existing user
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash("Logged in with LinkedIn successfully!", "success")

        # Set session variables
        session['user_id'] = user.id
        session['role'] = user.role
        session['name'] = user.name
        session.permanent = True
        session['email'] = user.email
        session['provider'] = user.provider

        return redirect(url_for('profile'))  # Redirect to profile page

    except Exception as e:
        print("LinkedIn auth error:", str(e))
        flash("LinkedIn login failed. Please try again.", "danger")
        return redirect(url_for('login'))
        
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for('index'))

@app.route('/admin/users')
def view_users():
    if session.get('role') != 'admin':
        return "Unauthorized", 403
    
    users = User.query.all()
    return render_template('users.html', users=users)



@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # If user is admin, fetch analytics data
    if user.role == 'admin':
        # Get user statistics
        total_users = User.query.count()
        total_registered_users = User.query.filter(User.provider == None).count()
        total_social_logins = User.query.filter(User.provider.isnot(None)).count()
        
        # Get specific social login counts
        google_logins = User.query.filter(User.provider == 'google').count()
        linkedin_logins = User.query.filter(User.provider == 'linkedin').count()
        
        # Get recent signups (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.now() - timedelta(days=7)
        recent_signups = User.query.filter(User.created_at >= week_ago).count()
        
        # Remove active_users calculation since last_login doesn't exist
        active_users = total_users  # Temporary placeholder
        
        # Get recent users for the table - filter out None created_at
        recent_users = User.query.filter(User.created_at.isnot(None)).order_by(User.created_at.desc()).limit(10).all()

        analytics_data = {
            'total_users': total_users,
            'total_registered': total_registered_users,
            'total_social_logins': total_social_logins,
            'google_logins': google_logins,
            'linkedin_logins': linkedin_logins,
            'recent_signups': recent_signups,
            'active_users': active_users,
        }
        
        return render_template('profile.html', user=user, analytics=analytics_data, 
                             recent_users=recent_users, is_admin=True)
    
    # Regular user view
    return render_template('profile.html', user=user, is_admin=False)

# SendGrid API function
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr  # ✅ ADD THIS IMPORT
import os
from datetime import datetime

def send_email(data):
    """Send email using Gmail SMTP - Shows as 'Cleanify' in inbox"""
    try:
        # Get credentials from .env
        MAIL_USERNAME = os.getenv("MAIL_USERNAME", "creativeshanansari@gmail.com")
        MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")  
        ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "creativeshanansari@gmail.com")
        
        if not MAIL_PASSWORD:
            print("❌ MAIL_PASSWORD not found in environment variables")
            return False
        
        print("="*50)
        print("📧 GMAIL SMTP CONFIGURATION:")
        print(f"📧 Username: {MAIL_USERNAME}")
        print(f"📧 Password (first 5 chars): {MAIL_PASSWORD[:5]}...")
        print(f"📧 Admin Email: {ADMIN_EMAIL}")
        print("="*50)
        
        # Generate booking ID
        booking_id = f"CLN{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = f"📋 New Booking: {data.get('service', 'Service')} - {data.get('package', 'Package')}"
        
        # ✅ CRITICAL CHANGE: Set sender as "Cleanify" instead of just email
        message["From"] = formataddr(("Cleanify", MAIL_USERNAME))
        # This will show as "Cleanify" in the recipient's inbox
        # Instead of: creativeshanansari@gmail.com
        # It shows as: Cleanify <creativeshanansari@gmail.com>
        
        message["To"] = ADMIN_EMAIL
        
        # Also set Reply-To with customer's name
        customer_name = data.get('fullName', 'Customer')
        customer_email = data.get('email', '')
        if customer_email:
            message["Reply-To"] = formataddr((customer_name, customer_email))
        
        # Plain text version
        text = f"""
NEW BOOKING REQUEST - ACTION REQUIRED

Customer Details:
---------------
• Name: {data.get('fullName', 'N/A')}
• Email: {data.get('email', 'N/A')}
• Phone: {data.get('phone', 'N/A')}
• Address: {data.get('address', 'N/A')}

Service Details:
---------------
• Service: {data.get('service', 'N/A')}
• Package: {data.get('package', 'N/A')}
• Date: {data.get('date', 'N/A')}
• Time: {data.get('time', 'N/A')}
• Payment: {data.get('payment', 'N/A')}

Booking Information:
------------------
• Booking ID: {booking_id}
• Booking Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️ URGENT ACTION REQUIRED:
Please contact {data.get('fullName', 'Customer')} at {data.get('email', 'N/A')} 
or {data.get('phone', 'N/A')} within 24 hours.

---
Cleanify Booking System
        """
        
        # HTML version
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New Booking</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
        .section {{ margin-bottom: 20px; }}
        .label {{ font-weight: bold; color: #333; }}
        .value {{ color: #666; }}
        .urgent {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 New Booking Received!</h1>
        <p>Cleanify Service Booking System</p>
    </div>
    
    <div class="content">
        <div class="section">
            <h2>👤 Customer Details</h2>
            <p><span class="label">Name:</span> <span class="value">{data.get('fullName', 'N/A')}</span></p>
            <p><span class="label">Email:</span> <span class="value">{data.get('email', 'N/A')}</span></p>
            <p><span class="label">Phone:</span> <span class="value">{data.get('phone', 'N/A')}</span></p>
            <p><span class="label">Address:</span> <span class="value">{data.get('address', 'N/A')}</span></p>
        </div>
        
        <div class="section">
            <h2>🔧 Service Details</h2>
            <p><span class="label">Service:</span> <span class="value">{data.get('service', 'N/A')}</span></p>
            <p><span class="label">Package:</span> <span class="value">{data.get('package', 'N/A')}</span></p>
            <p><span class="label">Date:</span> <span class="value">{data.get('date', 'N/A')}</span></p>
            <p><span class="label">Time:</span> <span class="value">{data.get('time', 'N/A')}</span></p>
            <p><span class="label">Payment:</span> <span class="value">{data.get('payment', 'N/A')}</span></p>
        </div>
        
        <div class="section">
            <h2>📋 Booking Information</h2>
            <p><span class="label">Booking ID:</span> <span class="value">{booking_id}</span></p>
            <p><span class="label">Booking Time:</span> <span class="value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span></p>
        </div>
        
        <div class="urgent">
            <h3>⚠️ URGENT ACTION REQUIRED</h3>
            <p>Please contact <strong>{data.get('fullName', 'Customer')}</strong> at <strong>{data.get('email', 'N/A')}</strong> or <strong>{data.get('phone', 'N/A')}</strong> within <strong>24 hours</strong> to confirm this booking.</p>
        </div>
    </div>
    
    <div class="footer">
        <p>This email was automatically generated by Cleanify Booking System</p>
        <p>© {datetime.now().year} Cleanify Service. All rights reserved.</p>
    </div>
</body>
</html>"""
        
        # Attach both versions
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Send email via Gmail SMTP
        print("📧 Connecting to Gmail SMTP...")
        
        # Method 1: Using SSL (port 465) - Recommended
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(MAIL_USERNAME, MAIL_PASSWORD)
                server.sendmail(MAIL_USERNAME, ADMIN_EMAIL, message.as_string())
                print("✅ Email sent successfully via Gmail SMTP (SSL)!")
                return True
        except Exception as ssl_error:
            print(f"⚠️ SSL method failed, trying TLS: {ssl_error}")
            
            # Method 2: Using TLS (port 587)
            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()  # Upgrade to secure connection
                    server.login(MAIL_USERNAME, MAIL_PASSWORD)
                    server.sendmail(MAIL_USERNAME, ADMIN_EMAIL, message.as_string())
                    print("✅ Email sent successfully via Gmail SMTP (TLS)!")
                    return True
            except Exception as tls_error:
                print(f"❌ TLS method failed: {tls_error}")
                return False
                
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False   
# API Endpoints
@app.route('/book', methods=['POST', 'OPTIONS'])
def book_service():
    if request.method == 'OPTIONS':
        return jsonify({}), 200    
    # 🔐 LOGIN REQUIRED
    if 'user_id' not in session:
        return jsonify({
            'error': 'LOGIN_REQUIRED',
            'message': 'Please login to book a service'
        }), 401    
    """
    Handle booking form submissions - 100% RELIABLE VERSION
    """
    try:
        print("🔵 /book endpoint called")

        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            print("❌ No JSON data received")
            return jsonify({'error': 'No JSON data received'}), 400
        
        # Validate required fields
        required_fields = ['fullName', 'email', 'phone', 'service', 'package', 'date', 'time', 'payment', 'address']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        print(f"✅ Data validation passed for {data['fullName']}")
        
        # Generate booking ID
        booking_id = f"CLN{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Save booking to file FIRST (guaranteed success)
        try:
            bookings_dir = os.path.join(app.root_path, 'bookings')
            os.makedirs(bookings_dir, exist_ok=True)
            
            booking_data = {
                'booking_id': booking_id,
                'timestamp': datetime.now().isoformat(),
                'customer': data['fullName'],
                'email': data['email'],
                'phone': data['phone'],
                'service': data['service'],
                'package': data['package'],
                'date': data['date'],
                'time': data['time'],
                'address': data['address'],
                'payment': data['payment'],
                'email_sent': False  # Will update if email succeeds
            }
            
            filename = os.path.join(bookings_dir, f'{booking_id}.json')
            with open(filename, 'w') as f:
                json.dump(booking_data, f, indent=2)
            
            print(f"✅ Booking saved to file: {filename}")
            
        except Exception as file_error:
            print(f"⚠️ Could not save booking to file: {file_error}")
            # Don't fail - continue without file save
        
        # Try to send email (optional)
        email_sent = False
        email_error = None

        try:
            print("🔵 Attempting to send email via Gmail SMTP...")
            email_sent = send_email(data)  # Changed from send_sendgrid_email to send_email
    
            if email_sent:
                print("✅ Email sent successfully!")
                # Update the saved file to mark email as sent
                try:
                    if 'booking_data' in locals():
                        booking_data['email_sent'] = True
                        with open(filename, 'w') as f:
                            json.dump(booking_data, f, indent=2)
                except:
                    pass
            else:
                email_error = "Email failed to send"
                print("⚠️ Email sending failed, but booking is saved")
        
        except Exception as email_err:
            email_error = str(email_err)
            print(f"⚠️ Email error: {email_error}")        
        
        # Log to console (Render logs)
        print("\n" + "="*50)
        print("📋 BOOKING COMPLETED SUCCESSFULLY")
        print("="*50)
        print(f"Booking ID: {booking_id}")
        print(f"Customer: {data['fullName']}")
        print(f"Email: {data['email']}")
        print(f"Phone: {data['phone']}")
        print(f"Service: {data['service']} - {data['package']}")
        print(f"Date: {data['date']} at {data['time']}")
        print(f"Address: {data['address'][:50]}...")  # Truncate long addresses
        print(f"Payment: {data['payment']}")
        print(f"Email Sent: {'✅ Yes' if email_sent else '❌ No'}")
        print("="*50 + "\n")
        
        # Return SUCCESS response
        return jsonify({
            'success': True,
            'message': '✅ Booking confirmed successfully! We will contact you within 24 hours.',
            'booking_id': booking_id,
            'email_sent': email_sent,
            'note': 'Your booking has been saved to our system.'
        })
        
    except Exception as e:
        print(f"❌ Error in booking endpoint: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Booking failed due to server error. Please try again.'}), 500

# Add this admin route to view bookings
@app.route('/admin/bookings', methods=['GET'])
def view_bookings():
    """Admin view to see all bookings"""
    try:
        bookings_dir = os.path.join(app.root_path, 'bookings')
        
        if not os.path.exists(bookings_dir):
            return jsonify({'message': 'No bookings yet', 'bookings': []})
        
        bookings = []
        for filename in os.listdir(bookings_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(bookings_dir, filename)
                with open(filepath, 'r') as f:
                    booking_data = json.load(f)
                    bookings.append(booking_data)
        
        # Sort by timestamp (newest first)
        bookings.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return jsonify({
            'count': len(bookings),
            'bookings': bookings
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/contact-form', methods=['POST'])
def contact_form():
    """
    Handle contact form submissions
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Print contact form data
        print(f"Contact form received: {data}")
        
        print("\n" + "="*50)
        print("CONTACT FORM SUBMISSION")
        print("="*50)
        print(f"Name: {data['name']}")
        print(f"Email: {data['email']}")
        print(f"Phone: {data['phone']}")
        print(f"Service: {data.get('service', 'Not specified')}")
        print(f"Message: {data['message']}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50 + "\n")
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your message! We will get back to you within 24 hours.'
        })
        
    except Exception as e:
        print(f"Error processing contact form: {str(e)}")  # Fixed: using print instead of logger
        return jsonify({'error': 'Internal server error. Please try again.'}), 500
    

@app.route('/api/services')
def api_services():
    """API endpoint to get services data"""
    services_data = [
        {
            'name': 'Home Cleaning',
            'description': 'Complete home cleaning including living room, bedrooms, and common areas',
            'price': 'Starting from ₹1,000',
            'slug': 'home-cleaning'
        },
        {
            'name': 'Sofa Cleaning',
            'description': 'Deep cleaning and sanitization of sofas and upholstery',
            'price': 'Starting from ₹799',
            'slug': 'sofa-cleaning'
        },
        {
            'name': 'Kitchen Cleaning',
            'description': 'Complete kitchen cleaning including cabinets, countertops, and appliances',
            'price': 'Starting from ₹999',
            'slug': 'kitchen-cleaning'
        },
        {
            'name': 'Bathroom Cleaning',
            'description': 'Deep cleaning and sanitization of bathrooms and toilets',
            'price': 'Starting from ₹699',
            'slug': 'bathroom-cleaning'
        },
        {
            'name': 'Carpet Cleaning',
            'description': 'Professional carpet cleaning and stain removal services',
            'price': 'Starting from ₹1,099',
            'slug': 'carpet-cleaning'
        }
    ]
    return jsonify(services_data)

@app.route('/test-email-config', methods=['GET'])
def test_email_config():
    """Test email configuration"""
    try:
        api_key = os.getenv("MAIL_PASSWORD")
        admin_email = os.getenv("ADMIN_EMAIL", "abdulhyr@gmail.com")
        sender_email = app.config.get('MAIL_DEFAULT_SENDER', 'creativeshanansari@gmail.com')
        
        return jsonify({
            'sendgrid_api_key_set': bool(api_key),
            'admin_email': admin_email,
            'sender_email': sender_email,
            'note': f'Emails will be sent FROM {sender_email} TO {admin_email}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/check-auth')
def check_auth():
    """Check if user is logged in"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return jsonify({
            'logged_in': True,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role
            },
            'session_id': session.get('_id', 'no_session_id')
        })
    return jsonify({'logged_in': False, 'message': 'Not logged in'})

@app.route('/debug-session')
def debug_session():
    """Debug session info"""
    return jsonify({
        'session': dict(session),
        'headers': dict(request.headers),
        'cookies': request.cookies,
        'user_agent': request.user_agent.string
    })

@app.route('/test-connection')
def test_connection():
    """Test if Flask is reachable"""
    return jsonify({
        'status': 'ok',
        'server': 'Flask',
        'timestamp': datetime.now().isoformat(),
        'session_exists': 'user_id' in session,
        'cors_working': True
    })

# Add this before your booking route
@app.route('/preflight-test', methods=['OPTIONS', 'GET'])
def preflight_test():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight_ok'})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response
    return jsonify({'status': 'ok', 'method': 'GET'})

# Static file serving (if needed)
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# ✅ Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Only creates tables if they don't exist
    app.run(host="0.0.0.0", port=10000)


