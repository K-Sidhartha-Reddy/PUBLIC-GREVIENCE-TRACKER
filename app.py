from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grievance_portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aadhaar_number = db.Column(db.String(12), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    state = db.Column(db.String(50))  # User's state
    district = db.Column(db.String(50))  # User's district
    role = db.Column(db.String(20), nullable=False)  # 'citizen', 'admin', or 'ngo'
    assigned_area = db.Column(db.String(100))  # For admin users
    
    # NGO-specific fields
    organization_name = db.Column(db.String(200))  # For NGO users
    registration_number = db.Column(db.String(50))  # NGO registration number
    ngo_type = db.Column(db.String(100))  # Type of NGO (social welfare, environment, etc.)
    
    # Points system
    points_balance = db.Column(db.Integer, default=0)
    total_points_earned = db.Column(db.Integer, default=0)
    total_points_redeemed = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    village = db.Column(db.String(100), nullable=False)
    area_type = db.Column(db.String(20), nullable=False)  # 'rural' or 'urban'
    authority = db.Column(db.String(100), nullable=False)  # Panchayat or Municipal name

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    subcategory = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='Submitted')  # Submitted, NGO Review, Verified, Forwarded to Admin, In Progress, Resolved, Rejected
    progress = db.Column(db.Integer, default=0)  # Progress percentage (0-100)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Made optional for anonymous complaints
    complainant_name = db.Column(db.String(100))  # For anonymous complaints
    complainant_email = db.Column(db.String(120))  # For anonymous complaints
    complainant_phone = db.Column(db.String(10))  # For anonymous complaints
    image_path = db.Column(db.String(200))
    priority = db.Column(db.String(20), default='Medium')  # Low, Medium, High, Critical
    
    # NGO workflow fields
    assigned_ngo_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # NGO assigned to verify
    ngo_verified = db.Column(db.Boolean, default=False)
    ngo_verification_notes = db.Column(db.Text)  # NGO's verification comments
    ngo_verified_at = db.Column(db.DateTime)
    forwarded_to_admin = db.Column(db.Boolean, default=False)
    
    # Points awarded
    points_awarded_to_ngo = db.Column(db.Integer, default=0)
    points_awarded_to_citizen = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    location = db.relationship('Location', backref='complaints')
    user = db.relationship('User', foreign_keys=[user_id], backref='submitted_complaints')
    assigned_ngo = db.relationship('User', foreign_keys=[assigned_ngo_id], backref='assigned_complaints')

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    announcement_type = db.Column(db.String(50), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    location = db.relationship('Location', backref='announcements')
    author = db.relationship('User', backref='announcements')

class PointsTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=True)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'earned' or 'redeemed'
    points = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='points_transactions')
    complaint = db.relationship('Complaint', backref='points_transactions')

class Redemption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points_redeemed = db.Column(db.Integer, nullable=False)
    redemption_type = db.Column(db.String(50), nullable=False)  # 'bank_transfer', 'gift_voucher', etc.
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Completed
    details = db.Column(db.Text)  # Bank details or voucher info
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    user = db.relationship('User', backref='redemptions')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Aadhaar validation function
def validate_aadhaar(aadhaar_number):
    """Validate Aadhaar number format"""
    # Remove any spaces or dashes
    aadhaar_clean = re.sub(r'[\s-]', '', aadhaar_number)
    
    # Check if it's exactly 12 digits
    if not re.match(r'^\d{12}$', aadhaar_clean):
        return False, "Aadhaar number must be exactly 12 digits"
    
    # Basic checksum validation (simplified)
    # In real implementation, you would use proper Aadhaar validation API
    return True, "Valid Aadhaar number"

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        aadhaar_number = request.form['aadhaar_number']
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        role = request.form['role']
        
        # Validate Aadhaar number
        is_valid, message = validate_aadhaar(aadhaar_number)
        if not is_valid:
            flash(message)
            return redirect(url_for('register'))
        
        # Check if Aadhaar already exists
        if User.query.filter_by(aadhaar_number=aadhaar_number).first():
            flash('Aadhaar number already registered')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))
        
        # Create user with role-specific fields
        user = User(
            aadhaar_number=aadhaar_number,
            full_name=full_name,
            email=email,
            phone=phone,
            state=request.form.get('state'),
            district=request.form.get('district'),
            role=role
        )
        
        # Add NGO-specific fields if role is NGO
        if role == 'ngo':
            user.organization_name = request.form.get('organization_name')
            user.registration_number = request.form.get('registration_number')
            user.ngo_type = request.form.get('ngo_type')
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now login with your Aadhaar number.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        aadhaar_number = request.form['aadhaar_number']
        user = User.query.filter_by(aadhaar_number=aadhaar_number).first()
        
        if user:
            login_user(user)
            flash('Logged in successfully!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'ngo':
                return redirect(url_for('ngo_dashboard'))
            else:
                return redirect(url_for('citizen_dashboard'))
        else:
            flash('Aadhaar number not found. Please register first.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/citizen-dashboard')
@login_required
def citizen_dashboard():
    if current_user.role != 'citizen':
        flash('Access denied')
        return redirect(url_for('index'))
    
    complaints = Complaint.query.filter_by(user_id=current_user.id).order_by(Complaint.created_at.desc()).all()
    total = len(complaints)
    resolved = len([c for c in complaints if c.status == 'Resolved'])
    pending = len([c for c in complaints if c.status == 'Pending'])
    in_progress = len([c for c in complaints if c.status == 'In Progress'])
    submitted = len([c for c in complaints if c.status == 'Submitted'])
    stats = {
        'total': total,
        'resolved': resolved,
        'pending': pending,
        'in_progress': in_progress,
        'submitted': submitted
    }
    return render_template('citizen_dashboard.html', complaints=complaints, stats=stats)

@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get complaints for admin's assigned area
    complaints = Complaint.query.join(Location).filter(
        Location.authority == current_user.assigned_area
    ).order_by(Complaint.created_at.desc()).all()
    
    # Dashboard statistics
    total_complaints = len(complaints)
    resolved_complaints = len([c for c in complaints if c.status == 'Resolved'])
    pending_complaints = len([c for c in complaints if c.status == 'Pending'])
    in_progress_complaints = len([c for c in complaints if c.status == 'In Progress'])
    
    stats = {
        'total': total_complaints,
        'resolved': resolved_complaints,
        'pending': pending_complaints,
        'in_progress': in_progress_complaints
    }
    
    return render_template('admin_dashboard.html', complaints=complaints, stats=stats)

@app.route('/ngo-dashboard')
@login_required
def ngo_dashboard():
    if current_user.role != 'ngo':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get complaints assigned to this NGO or pending assignment
    assigned_complaints = Complaint.query.filter_by(assigned_ngo_id=current_user.id).order_by(Complaint.created_at.desc()).all()
    pending_complaints = Complaint.query.filter_by(status='Submitted', assigned_ngo_id=None).order_by(Complaint.created_at.desc()).limit(20).all()
    
    # Dashboard statistics
    total_assigned = len(assigned_complaints)
    verified = len([c for c in assigned_complaints if c.ngo_verified])
    pending_verification = len([c for c in assigned_complaints if not c.ngo_verified])
    forwarded = len([c for c in assigned_complaints if c.forwarded_to_admin])
    
    stats = {
        'total_assigned': total_assigned,
        'verified': verified,
        'pending_verification': pending_verification,
        'forwarded': forwarded,
        'points_balance': current_user.points_balance,
        'total_points_earned': current_user.total_points_earned
    }
    
    return render_template('ngo_dashboard.html', 
                         assigned_complaints=assigned_complaints,
                         pending_complaints=pending_complaints,
                         stats=stats)

@app.route('/ngo/claim-complaint/<int:complaint_id>', methods=['POST'])
@login_required
def claim_complaint(complaint_id):
    if current_user.role != 'ngo':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    complaint = Complaint.query.get_or_404(complaint_id)
    
    if complaint.assigned_ngo_id is not None:
        flash('This complaint has already been claimed by another NGO', 'error')
        return redirect(url_for('ngo_dashboard'))
    
    complaint.assigned_ngo_id = current_user.id
    complaint.status = 'NGO Review'
    complaint.progress = 10
    db.session.commit()
    
    flash('Complaint claimed successfully! Please verify and forward to authorities.', 'success')
    return redirect(url_for('ngo_dashboard'))

@app.route('/ngo/verify-complaint/<int:complaint_id>', methods=['POST'])
@login_required
def verify_complaint(complaint_id):
    if current_user.role != 'ngo':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    complaint = Complaint.query.get_or_404(complaint_id)
    
    if complaint.assigned_ngo_id != current_user.id:
        flash('You can only verify complaints assigned to you', 'error')
        return redirect(url_for('ngo_dashboard'))
    
    verification_notes = request.form.get('verification_notes', '')
    action = request.form.get('action')  # 'verify' or 'reject'
    
    if action == 'verify':
        complaint.ngo_verified = True
        complaint.ngo_verification_notes = verification_notes
        complaint.ngo_verified_at = datetime.utcnow()
        complaint.status = 'Verified'
        complaint.progress = 25
        
        # Award points to NGO (100 points per verification)
        ngo_points = 100
        complaint.points_awarded_to_ngo = ngo_points
        current_user.points_balance += ngo_points
        current_user.total_points_earned += ngo_points
        
        # Create points transaction
        transaction = PointsTransaction(
            user_id=current_user.id,
            complaint_id=complaint.id,
            transaction_type='earned',
            points=ngo_points,
            description=f'Verified complaint #{complaint.id}'
        )
        db.session.add(transaction)
        
        flash(f'Complaint verified successfully! You earned {ngo_points} points.', 'success')
    elif action == 'reject':
        complaint.status = 'Rejected'
        complaint.ngo_verification_notes = verification_notes
        complaint.progress = 0
        flash('Complaint rejected.', 'info')
    
    db.session.commit()
    return redirect(url_for('ngo_dashboard'))

@app.route('/ngo/forward-complaint/<int:complaint_id>', methods=['POST'])
@login_required
def forward_complaint(complaint_id):
    if current_user.role != 'ngo':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    complaint = Complaint.query.get_or_404(complaint_id)
    
    if complaint.assigned_ngo_id != current_user.id:
        flash('You can only forward complaints assigned to you', 'error')
        return redirect(url_for('ngo_dashboard'))
    
    if not complaint.ngo_verified:
        flash('Please verify the complaint before forwarding', 'error')
        return redirect(url_for('ngo_dashboard'))
    
    complaint.forwarded_to_admin = True
    complaint.status = 'Forwarded to Admin'
    complaint.progress = 35
    
    # Award points to citizen (percentage of NGO points)
    if complaint.user_id:
        citizen_points = int(complaint.points_awarded_to_ngo * 0.3)  # 30% of NGO points
        complaint.points_awarded_to_citizen = citizen_points
        
        citizen = User.query.get(complaint.user_id)
        if citizen:
            citizen.points_balance += citizen_points
            citizen.total_points_earned += citizen_points
            
            # Create points transaction for citizen
            transaction = PointsTransaction(
                user_id=citizen.id,
                complaint_id=complaint.id,
                transaction_type='earned',
                points=citizen_points,
                description=f'Complaint #{complaint.id} verified and forwarded'
            )
            db.session.add(transaction)
    
    db.session.commit()
    flash('Complaint forwarded to government authorities successfully!', 'success')
    return redirect(url_for('ngo_dashboard'))

@app.route('/redeem-points', methods=['GET', 'POST'])
@login_required
def redeem_points():
    if request.method == 'POST':
        points_to_redeem = int(request.form['points'])
        redemption_type = request.form['redemption_type']
        details = request.form.get('details', '')
        
        if points_to_redeem > current_user.points_balance:
            flash('Insufficient points balance', 'error')
            return redirect(url_for('redeem_points'))
        
        if points_to_redeem < 100:
            flash('Minimum redemption is 100 points', 'error')
            return redirect(url_for('redeem_points'))
        
        # Create redemption request
        redemption = Redemption(
            user_id=current_user.id,
            points_redeemed=points_to_redeem,
            redemption_type=redemption_type,
            details=details
        )
        
        # Deduct points
        current_user.points_balance -= points_to_redeem
        current_user.total_points_redeemed += points_to_redeem
        
        # Create transaction
        transaction = PointsTransaction(
            user_id=current_user.id,
            transaction_type='redeemed',
            points=points_to_redeem,
            description=f'Redeemed for {redemption_type}'
        )
        
        db.session.add(redemption)
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Redemption request submitted! {points_to_redeem} points will be processed.', 'success')
        return redirect(url_for('citizen_dashboard') if current_user.role == 'citizen' else url_for('ngo_dashboard'))
    
    return render_template('redeem_points.html')

@app.route('/submit-complaint', methods=['GET', 'POST'])
def submit_complaint():
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        subcategory = request.form['subcategory']
        state = request.form['state']
        district = request.form['district']
        village = request.form['village']
        
        # Get complainant details (for anonymous complaints)
        complainant_name = request.form.get('complainant_name', '')
        complainant_email = request.form.get('complainant_email', '')
        complainant_phone = request.form.get('complainant_phone', '')
        
        # Validate subcategory
        if not subcategory or subcategory.strip() == '':
            flash('Please select a specific issue type for the chosen category.')
            return redirect(url_for('submit_complaint'))
        
        # Validate category and subcategory combination
        valid_categories = {
            'Roads & Transportation': [
                'Potholes or damaged roads', 'Broken or missing streetlights', 'Traffic signal not working',
                'Lack of pedestrian crossings', 'Damaged or missing road signs', 'Poor drainage on roads',
                'Illegal parking issues', 'Unmaintained public bus stops'
            ],
            'Water Supply & Drainage': [
                'Water leakage or pipeline burst', 'Irregular water supply', 'Contaminated or muddy water',
                'Drainage blockage / overflow', 'Open or damaged manholes', 'Sewer smell in residential areas'
            ],
            'Sanitation & Waste Management': [
                'Garbage not collected regularly', 'Overflowing dustbins', 'Illegal dumping of waste',
                'Lack of public dustbins', 'Mosquito breeding spots / stagnant water'
            ],
            'Electricity & Power': [
                'Frequent power cuts', 'Damaged electric poles or wires', 'Streetlight not functioning',
                'Transformer failure or sparks', 'Low voltage issues'
            ],
            'Environment & Public Spaces': [
                'Tree cutting without permission', 'Lack of greenery / need for plantation drive',
                'Encroachment on public parks', 'Polluted lakes or ponds', 'Noise pollution or burning of waste'
            ],
            'Education & Public Facilities': [
                'Poor maintenance of government schools', 'Lack of clean drinking water in schools',
                'Broken classroom infrastructure', 'Playground maintenance issues', 'Public library or community hall upkeep'
            ],
            'Health & Hygiene': [
                'Poor sanitation near hospitals', 'Mosquito or vector-borne disease risk',
                'Lack of medical waste disposal', 'Overflowing sewage near residential areas'
            ],
            'Government & Administrative Services': [
                'Delay in document processing (ration, birth/death certificate, etc.)',
                'Non-functional government service centers', 'Issues with pensions or welfare schemes',
                'Corruption or negligence in local office'
            ],
            'Housing & Infrastructure': [
                'Unsafe or illegal construction', 'Water stagnation near houses',
                'Lack of drainage connections', 'Encroachment of government land'
            ],
            'Emergency & Safety': [
                'Fire hazards (unattended garbage, chemical waste)', 'Open borewells or pits',
                'Stray animal issues', 'Public safety concerns in dark or isolated areas'
            ],
            'Panchayat & Digital Governance': [
                'Panchayat meeting schedule updates missing', 'Issues with panchayat fund transparency',
                'Request for new digital service in village', 'Need for online access to meeting resolutions',
                'Maintenance of panchayat website or information board'
            ],
            'Urban Municipal Issues': [
                'Delay in building permissions', 'Encroachment on footpaths', 'Overflowing public drains',
                'Lack of public toilets', 'Poor street cleaning services'
            ]
        }
        
        if category not in valid_categories or subcategory not in valid_categories.get(category, []):
            flash('Invalid category and subcategory combination.')
            return redirect(url_for('submit_complaint'))
        
        # Find location
        location = Location.query.filter_by(
            state=state, district=district, village=village
        ).first()
        
        if not location:
            flash('Location not found')
            return redirect(url_for('submit_complaint'))
        
        # Handle file upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = filename
        
        # Determine user_id and complainant details
        user_id = None
        if current_user.is_authenticated and current_user.role == 'citizen':
            user_id = current_user.id
            complainant_name = None
            complainant_email = None
            complainant_phone = None
        else:
            # For anonymous complaints, validate required fields
            if not complainant_name or not complainant_email:
                flash('Name and email are required for anonymous complaints.')
                return redirect(url_for('submit_complaint'))
        
        complaint = Complaint(
            title=title,
            description=description,
            category=category,
            subcategory=subcategory,
            location_id=location.id,
            user_id=user_id,
            complainant_name=complainant_name,
            complainant_email=complainant_email,
            complainant_phone=complainant_phone,
            image_path=image_path
        )
        
        db.session.add(complaint)
        db.session.commit()
        
        flash('Complaint submitted successfully!')
        if current_user.is_authenticated and current_user.role == 'citizen':
            return redirect(url_for('citizen_dashboard'))
        else:
            return redirect(url_for('index'))
    
    return render_template('submit_complaint.html')

@app.route('/update-complaint-status/<int:complaint_id>', methods=['POST'])
@login_required
def update_complaint_status(complaint_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    complaint = Complaint.query.get_or_404(complaint_id)
    new_status = request.form['status']
    new_progress = int(request.form.get('progress', 0))
    
    complaint.status = new_status
    complaint.progress = new_progress
    complaint.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash('Complaint status and progress updated successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/announcements')
def announcements():
    location_id = request.args.get('location_id')
    if location_id:
        announcements = Announcement.query.filter_by(location_id=location_id).order_by(Announcement.created_at.desc()).all()
    else:
        announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    
    return render_template('announcements.html', announcements=announcements)

@app.route('/create-announcement', methods=['GET', 'POST'])
@login_required
def create_announcement():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        announcement_type = request.form['type']
        location_id = request.form['location_id']
        
        announcement = Announcement(
            title=title,
            content=content,
            announcement_type=announcement_type,
            location_id=location_id,
            created_by=current_user.id
        )
        
        db.session.add(announcement)
        db.session.commit()
        
        flash('Announcement created successfully!')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('create_announcement.html')

@app.route('/api/locations')
def api_locations():
    state = request.args.get('state')
    district = request.args.get('district')
    
    if state and district:
        locations = Location.query.filter_by(state=state, district=district).all()
    elif state:
        locations = Location.query.filter_by(state=state).all()
    else:
        locations = Location.query.all()
    
    return jsonify([{
        'id': loc.id,
        'state': loc.state,
        'district': loc.district,
        'village': loc.village,
        'area_type': loc.area_type,
        'authority': loc.authority
    } for loc in locations])

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create sample data if not exists
        if not Location.query.first():
            sample_locations = [
                Location(state='Telangana', district='Hyderabad', village='Amberpet', area_type='urban', authority='Greater Hyderabad Municipal Corporation'),
                Location(state='Telangana', district='Hyderabad', village='Tirumalagiri', area_type='rural', authority='Tirumalagiri Gram Panchayat'),
                Location(state='Telangana', district='Hyderabad', village='Bandlaguda', area_type='rural', authority='Bandlaguda Gram Panchayat'),
                Location(state='Telangana', district='Hyderabad', village='Maredpalle', area_type='rural', authority='Maredpalle Gram Panchayat'),
                Location(state='Telangana', district='Hyderabad', village='Secunderabad', area_type='urban', authority='Greater Hyderabad Municipal Corporation'),
                Location(state='Telangana', district='Hyderabad', village='Charminar', area_type='urban', authority='Greater Hyderabad Municipal Corporation'),
                Location(state='Telangana', district='Hyderabad', village='Banjara Hills', area_type='urban', authority='Greater Hyderabad Municipal Corporation'),
                Location(state='Telangana', district='Hyderabad', village='Jubilee Hills', area_type='urban', authority='Greater Hyderabad Municipal Corporation'),
            ]
            
            for loc in sample_locations:
                db.session.add(loc)
            
            # Create sample admin user
            admin_user = User(
                aadhaar_number='123456789012',
                full_name='Admin User',
                email='admin@grievance.gov.in',
                phone='9876543210',
                state='Telangana',
                district='Hyderabad',
                role='admin',
                assigned_area='Greater Hyderabad Municipal Corporation'
            )
            db.session.add(admin_user)
            
            # Create sample citizen user
            citizen_user = User(
                aadhaar_number='987654321098',
                full_name='John Doe',
                email='john@example.com',
                phone='9876543211',
                state='Telangana',
                district='Hyderabad',
                role='citizen'
            )
            db.session.add(citizen_user)
            
            # Create sample NGO user
            ngo_user = User(
                aadhaar_number='555566667777',
                full_name='NGO Representative',
                email='contact@helpingngo.org',
                phone='9876543212',
                state='Telangana',
                district='Hyderabad',
                role='ngo',
                organization_name='Helping Hands NGO',
                registration_number='NGO/2020/12345',
                ngo_type='Social Welfare'
            )
            db.session.add(ngo_user)
            
            # Create sample announcements
            sample_announcements = [
                # Meeting Schedule announcements
                Announcement(
                    title='Monthly Gram Sabha Meeting - January 2024',
                    content='All residents are invited to attend the monthly Gram Sabha meeting scheduled for January 15, 2024, at 10:00 AM in the village community hall. Agenda includes discussion on village development projects, budget allocation, and public grievances.',
                    announcement_type='Meeting Schedule',
                    location_id=2,  # Tirumalagiri
                    created_by=1  # Admin user
                ),
                Announcement(
                    title='Municipal Council Meeting - Development Projects',
                    content='The Municipal Council meeting will be held on January 20, 2024, at 2:00 PM in the Municipal Office. Key topics include road construction projects, water supply improvements, and waste management initiatives.',
                    announcement_type='Meeting Schedule',
                    location_id=1,  # Amberpet
                    created_by=1  # Admin user
                ),
                
                # Public Notice announcements
                Announcement(
                    title='Water Supply Maintenance Notice',
                    content='Water supply will be temporarily suspended on January 18, 2024, from 8:00 AM to 4:00 PM for maintenance work. Residents are advised to store water in advance. We apologize for any inconvenience caused.',
                    announcement_type='Public Notice',
                    location_id=1,  # Amberpet
                    created_by=1  # Admin user
                ),
                Announcement(
                    title='Road Construction - Traffic Diversion',
                    content='Road construction work will begin on Main Street from January 22 to February 5, 2024. Traffic will be diverted through alternative routes. Please plan your travel accordingly.',
                    announcement_type='Public Notice',
                    location_id=3,  # Bandlaguda
                    created_by=1  # Admin user
                ),
                
                # Welfare Scheme announcements
                Announcement(
                    title='Pradhan Mantri Awas Yojana - Application Open',
                    content='Applications for Pradhan Mantri Awas Yojana (PMAY) are now open for eligible families. Last date for submission: February 15, 2024. Contact the Gram Panchayat office for application forms and eligibility criteria.',
                    announcement_type='Welfare Scheme',
                    location_id=2,  # Tirumalagiri
                    created_by=1  # Admin user
                ),
                Announcement(
                    title='Ayushman Bharat Health Card Registration',
                    content='Free health card registration under Ayushman Bharat scheme is available at the Municipal Health Center. Bring Aadhaar card and family details. Registration timings: 9 AM to 5 PM, Monday to Friday.',
                    announcement_type='Welfare Scheme',
                    location_id=5,  # Secunderabad
                    created_by=1  # Admin user
                ),
                
                # Fund Usage announcements
                Announcement(
                    title='14th Finance Commission Fund Utilization Report',
                    content='The Gram Panchayat has utilized ₹2,50,000 from the 14th Finance Commission funds for village infrastructure development including street lighting, drainage system, and community center renovation.',
                    announcement_type='Fund Usage',
                    location_id=4,  # Maredpalle
                    created_by=1  # Admin user
                ),
                Announcement(
                    title='Municipal Budget Allocation - Q4 2023',
                    content='Municipal budget allocation for Q4 2023: Road maintenance (₹5,00,000), Water supply (₹3,00,000), Waste management (₹2,00,000), Public health (₹1,50,000). Detailed report available at Municipal Office.',
                    announcement_type='Fund Usage',
                    location_id=6,  # Charminar
                    created_by=1  # Admin user
                ),
                
                # Development Work announcements
                Announcement(
                    title='New Primary Health Center Construction',
                    content='Construction of a new Primary Health Center has commenced in our village. The facility will include outpatient services, emergency care, and maternal health services. Expected completion: June 2024.',
                    announcement_type='Development Work',
                    location_id=2,  # Tirumalagiri
                    created_by=1  # Admin user
                ),
                Announcement(
                    title='Smart City Initiative - Digital Infrastructure',
                    content='Smart City project implementation includes installation of smart street lights, Wi-Fi hotspots, and digital payment systems. Phase 1 completion expected by March 2024.',
                    announcement_type='Development Work',
                    location_id=7,  # Banjara Hills
                    created_by=1  # Admin user
                ),
                
                # Emergency Notice announcements
                Announcement(
                    title='Cyclone Warning - Precautionary Measures',
                    content='IMD has issued a cyclone warning for our region. All residents are advised to stay indoors, secure loose objects, and avoid unnecessary travel. Emergency helpline: 108. Stay safe!',
                    announcement_type='Emergency Notice',
                    location_id=1,  # Amberpet
                    created_by=1  # Admin user
                ),
                Announcement(
                    title='Power Outage - Emergency Repair',
                    content='Emergency power outage due to transformer failure. Repair work in progress. Power restoration expected within 4-6 hours. Emergency services will continue to operate on backup power.',
                    announcement_type='Emergency Notice',
                    location_id=8,  # Jubilee Hills
                    created_by=1  # Admin user
                ),
                
                # General Information announcements
                Announcement(
                    title='Digital India Week - Awareness Program',
                    content='Digital India Week celebration from January 25-31, 2024. Free digital literacy training, online service demonstrations, and awareness sessions on government digital services. All residents welcome!',
                    announcement_type='General Information',
                    location_id=3,  # Bandlaguda
                    created_by=1  # Admin user
                ),
                Announcement(
                    title='Voter Registration Drive - Electoral Roll Update',
                    content='Special voter registration drive from January 20-30, 2024. New voters can register and existing voters can update their details. Bring valid ID proof and address documents.',
                    announcement_type='General Information',
                    location_id=4,  # Maredpalle
                    created_by=1  # Admin user
                )
            ]
            
            for announcement in sample_announcements:
                db.session.add(announcement)
            
            # Create sample grievances
            sample_grievances = [
                Complaint(
                    title='Broken Street Light on Main Road',
                    description='Street light near the community center has been broken for the past week. It creates safety issues for pedestrians and vehicles during night time. Please repair it at the earliest.',
                    category='Electricity & Power',
                    subcategory='Streetlight not functioning',
                    status='In Progress',
                    progress=65,
                    priority='Medium',
                    location_id=1,  # Amberpet
                    user_id=2,  # John Doe
                    created_at=datetime(2024, 1, 10)
                ),
                Complaint(
                    title='Water Leakage in Residential Area',
                    description='There is a major water leakage from the main pipeline near house number 45. Water is being wasted and causing inconvenience to residents. Urgent repair required.',
                    category='Water Supply & Drainage',
                    subcategory='Water leakage or pipeline burst',
                    status='Submitted',
                    progress=25,
                    priority='High',
                    location_id=2,  # Tirumalagiri
                    user_id=2,  # John Doe
                    created_at=datetime(2024, 1, 12)
                ),
                Complaint(
                    title='Potholes on Village Road',
                    description='Multiple potholes have developed on the main village road leading to the school. It is dangerous for vehicles and school children. Request immediate road repair.',
                    category='Roads & Transportation',
                    subcategory='Potholes or damaged roads',
                    status='Resolved',
                    progress=100,
                    priority='High',
                    location_id=3,  # Bandlaguda
                    user_id=2,  # John Doe
                    created_at=datetime(2024, 1, 5)
                ),
                Complaint(
                    title='Garbage Collection Irregular',
                    description='Garbage collection has become irregular in our locality. Garbage is piling up and causing health hazards. Please ensure regular collection schedule.',
                    category='Sanitation & Waste Management',
                    subcategory='Garbage not collected regularly',
                    status='In Progress',
                    progress=40,
                    priority='Medium',
                    location_id=4,  # Maredpalle
                    user_id=2,  # John Doe
                    created_at=datetime(2024, 1, 8)
                ),
                Complaint(
                    title='Drainage Blockage in Market Area',
                    description='Drainage system is blocked in the market area causing water stagnation and foul smell. It affects business and public health. Immediate cleaning required.',
                    category='Water Supply & Drainage',
                    subcategory='Drainage blockage / overflow',
                    status='Submitted',
                    progress=15,
                    priority='High',
                    location_id=5,  # Secunderabad
                    user_id=2,  # John Doe
                    created_at=datetime(2024, 1, 14)
                )
            ]
            
            for grievance in sample_grievances:
                db.session.add(grievance)
            
            db.session.commit()
    
    app.run(debug=True)
