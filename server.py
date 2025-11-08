#!/usr/bin/env python3
"""
CI-NDA Flask Backend Server
Complete backend for the filmmaker platform with authentication and CRUD operations
"""

from flask import Flask, request, jsonify, session, g, send_from_directory
from flask_cors import CORS
from functools import wraps
import mysql.connector
from mysql.connector import Error
import bcrypt
import jwt
import datetime
import os
from werkzeug.utils import secure_filename
import re
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration from environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-this-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '86400')))

# CORS configuration
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:5500').split(',')
CORS(app, supports_credentials=True, origins=CORS_ORIGINS)

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'cinda_db'),
    'port': int(os.getenv('DB_PORT', '3306'))
}

# File upload configuration from environment variables
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '104857600'))  # Default 100MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'webm', 'mp3', 'wav'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database connection helper
def get_db_connection():
    """Get database connection with proper charset handling"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        # Set charset after connection (for compatibility)
        cursor = connection.cursor()
        cursor.execute("SET NAMES utf8mb4")
        cursor.close()
        
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def init_database():
    """Initialize database connection on request"""
    if 'db' not in g:
        g.db = get_db_connection()
    return g.db

@app.before_request
def before_request():
    """Initialize database connection before each request"""
    g.db = get_db_connection()

@app.teardown_appcontext
def close_db(error):
    """Close database connection after each request"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ============ STATIC FILE SERVING ============

@app.route('/')
def index():
    """Serve main page"""
    return app.send_static_file('index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (HTML, CSS, JS, etc.)"""
    try:
        return app.send_static_file(filename)
    except:
        # If file not found in static, try serving from root
        from flask import send_from_directory
        try:
            return send_from_directory('.', filename)
        except:
            return jsonify({'error': 'File not found'}), 404

# Utility functions
def allowed_file(filename):
    """Check if uploaded file is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    """Check password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_token(user_id, user_type, email):
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'user_type': user_type,
        'email': email,
        'exp': datetime.datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES']
    }
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Authentication decorator
def auth_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401
        
        # Verify token
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Token is invalid or expired'}), 401
        
        # Get user from database
        try:
            cursor = g.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE id = %s", (payload['user_id'],))
            user = cursor.fetchone()
            cursor.close()
            
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 401
            
            g.current_user = user
            return f(*args, **kwargs)
            
        except Error as e:
            return jsonify({'success': False, 'message': 'Database error'}), 500
    
    return decorated_function

# ============ AUTHENTICATION ROUTES ============

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'userType']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'message': f'{field} is required'}), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
        
        # Validate user type
        if data['userType'] not in ['filmmaker', 'mentor', 'sponsor']:
            return jsonify({'success': False, 'message': 'Invalid user type'}), 400
        
        # Check if user already exists
        cursor = g.db.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (data['email'],))
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            return jsonify({'success': False, 'message': 'User already exists with this email'}), 409
        
        # Hash password
        hashed_password = hash_password(data['password'])
        
        # Insert new user
        insert_query = """
        INSERT INTO users (name, email, password, user_type, bio, location, website, 
                          specialization, is_verified, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        user_data = (
            data['name'],
            data['email'],
            hashed_password,
            data['userType'],
            data.get('bio', ''),
            data.get('location', ''),
            data.get('website', ''),
            json.dumps(data.get('specialization', [])),
            False,
            datetime.datetime.now()
        )
        
        cursor.execute(insert_query, user_data)
        user_id = cursor.lastrowid
        g.db.commit()
        cursor.close()
        
        # Generate token
        token = generate_token(user_id, data['userType'], data['email'])
        
        # Return user data
        user_response = {
            'id': user_id,
            'name': data['name'],
            'email': data['email'],
            'userType': data['userType'],
            'bio': data.get('bio', ''),
            'location': data.get('location', ''),
            'website': data.get('website', ''),
            'specialization': data.get('specialization', []),
            'isVerified': False,
            'stats': {
                'followers': 0,
                'following': 0,
                'projects': 0,
                'awards': 0
            }
        }
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': user_response,
            'token': token
        }), 201
        
    except Error as e:
        return jsonify({'success': False, 'message': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred during registration'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        # Get user from database
        cursor = g.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (data['email'],))
        user = cursor.fetchone()
        cursor.close()
        
        if not user or not check_password(data['password'], user['password']):
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
        # Update last login
        cursor = g.db.cursor()
        cursor.execute("UPDATE users SET last_login = %s WHERE id = %s", 
                      (datetime.datetime.now(), user['id']))
        g.db.commit()
        cursor.close()
        
        # Generate token
        token = generate_token(user['id'], user['user_type'], user['email'])
        
        # Parse specialization JSON
        specialization = []
        if user['specialization']:
            try:
                specialization = json.loads(user['specialization'])
            except:
                pass
        
        # Return user data
        user_response = {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'userType': user['user_type'],
            'bio': user['bio'] or '',
            'location': user['location'] or '',
            'website': user['website'] or '',
            'avatar': user['avatar'] or '',
            'specialization': specialization,
            'isVerified': bool(user['is_verified']),
            'stats': {
                'followers': user['followers'],
                'following': user['following'],
                'projects': user['projects'],
                'awards': user['awards']
            }
        }
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user_response,
            'token': token
        }), 200
        
    except Error as e:
        return jsonify({'success': False, 'message': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred during login'}), 500

@app.route('/api/auth/social-login', methods=['POST'])
def social_login():
    """Social media login"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['provider', 'providerId', 'email', 'name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'message': f'{field} is required'}), 400
        
        # Check if user exists with this social login
        cursor = g.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE social_provider = %s AND social_provider_id = %s", 
                      (data['provider'], data['providerId']))
        user = cursor.fetchone()
        
        if user:
            # User exists, login
            cursor.execute("UPDATE users SET last_login = %s WHERE id = %s", 
                          (datetime.datetime.now(), user['id']))
            g.db.commit()
            cursor.close()
            
            token = generate_token(user['id'], user['user_type'], user['email'])
            
            specialization = []
            if user['specialization']:
                try:
                    specialization = json.loads(user['specialization'])
                except:
                    pass
            
            user_response = {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'userType': user['user_type'],
                'bio': user['bio'] or '',
                'location': user['location'] or '',
                'website': user['website'] or '',
                'avatar': user['avatar'] or '',
                'specialization': specialization,
                'isVerified': bool(user['is_verified']),
                'stats': {
                    'followers': user['followers'],
                    'following': user['following'],
                    'projects': user['projects'],
                    'awards': user['awards']
                }
            }
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': user_response,
                'token': token
            }), 200
        else:
            # Check if user exists with this email
            cursor.execute("SELECT * FROM users WHERE email = %s", (data['email'],))
            existing_user = cursor.fetchone()
            
            if existing_user:
                cursor.close()
                return jsonify({'success': False, 'message': 'User already exists with this email'}), 409
            
            # Create new user
            insert_query = """
            INSERT INTO users (name, email, user_type, avatar, social_provider, 
                             social_provider_id, is_verified, created_at, last_login)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            user_data = (
                data['name'],
                data['email'],
                data.get('userType', 'filmmaker'),
                data.get('avatar', ''),
                data['provider'],
                data['providerId'],
                True,  # Social login users are considered verified
                datetime.datetime.now(),
                datetime.datetime.now()
            )
            
            cursor.execute(insert_query, user_data)
            user_id = cursor.lastrowid
            g.db.commit()
            cursor.close()
            
            # Generate token
            token = generate_token(user_id, data.get('userType', 'filmmaker'), data['email'])
            
            # Return user data
            user_response = {
                'id': user_id,
                'name': data['name'],
                'email': data['email'],
                'userType': data.get('userType', 'filmmaker'),
                'bio': '',
                'location': '',
                'website': '',
                'avatar': data.get('avatar', ''),
                'specialization': [],
                'isVerified': True,
                'stats': {
                    'followers': 0,
                    'following': 0,
                    'projects': 0,
                    'awards': 0
                }
            }
            
            return jsonify({
                'success': True,
                'message': 'User registered and logged in successfully',
                'user': user_response,
                'token': token
            }), 201
            
    except Error as e:
        return jsonify({'success': False, 'message': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred during social login'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@auth_required
def logout():
    """Logout user"""
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200

# ============ USER ROUTES ============

@app.route('/api/users/profile', methods=['GET'])
@auth_required
def get_profile():
    """Get user profile"""
    try:
        user = g.current_user
        
        # Parse specialization JSON
        specialization = []
        if user['specialization']:
            try:
                specialization = json.loads(user['specialization'])
            except:
                pass
        
        # Get enrolled courses count
        cursor = g.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM course_enrollments WHERE user_id = %s", (user['id'],))
        enrolled_courses_count = cursor.fetchone()[0]
        
        # Get portfolios count
        cursor.execute("SELECT COUNT(*) FROM portfolios WHERE user_id = %s", (user['id'],))
        portfolios_count = cursor.fetchone()[0]
        cursor.close()
        
        user_response = {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'userType': user['user_type'],
            'bio': user['bio'] or '',
            'location': user['location'] or '',
            'website': user['website'] or '',
            'avatar': user['avatar'] or '',
            'specialization': specialization,
            'isVerified': bool(user['is_verified']),
            'stats': {
                'followers': user['followers'],
                'following': user['following'],
                'projects': portfolios_count,
                'awards': user['awards'],
                'enrolledCourses': enrolled_courses_count
            },
            'createdAt': user['created_at'].isoformat() if user['created_at'] else None,
            'lastLogin': user['last_login'].isoformat() if user['last_login'] else None
        }
        
        return jsonify({'success': True, 'user': user_response}), 200
        
    except Error as e:
        return jsonify({'success': False, 'message': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

@app.route('/api/users/profile', methods=['PUT'])
@auth_required
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        user_id = g.current_user['id']
        
        # Prepare update fields
        update_fields = []
        update_values = []
        
        allowed_fields = ['name', 'bio', 'location', 'website', 'specialization']
        
        for field in allowed_fields:
            if field in data:
                if field == 'specialization':
                    update_fields.append('specialization = %s')
                    update_values.append(json.dumps(data[field]))
                else:
                    update_fields.append(f'{field} = %s')
                    update_values.append(data[field])
        
        if not update_fields:
            return jsonify({'success': False, 'message': 'No valid fields to update'}), 400
        
        # Update user
        update_values.append(user_id)
        update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
        
        cursor = g.db.cursor()
        cursor.execute(update_query, update_values)
        g.db.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'Profile updated successfully'}), 200
        
    except Error as e:
        return jsonify({'success': False, 'message': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

# ============ COURSE ROUTES ============

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all courses with optional filtering"""
    try:
        # Get query parameters
        category = request.args.get('category')
        level = request.args.get('level')
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        
        # Build query
        where_conditions = []
        params = []
        
        if category:
            where_conditions.append("category = %s")
            params.append(category)
        
        if level:
            where_conditions.append("level = %s")
            params.append(level)
        
        if search:
            where_conditions.append("(title LIKE %s OR description LIKE %s)")
            params.extend([f'%{search}%', f'%{search}%'])
        
        where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # Get courses
        cursor = g.db.cursor(dictionary=True)
        query = f"""
        SELECT c.*, COUNT(ce.id) as enrolled_count
        FROM courses c
        LEFT JOIN course_enrollments ce ON c.id = ce.course_id
        {where_clause}
        GROUP BY c.id
        ORDER BY c.created_at DESC
        LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        cursor.execute(query, params)
        courses = cursor.fetchall()
        
        # Get total count
        count_query = f"SELECT COUNT(DISTINCT c.id) FROM courses c {where_clause}"
        cursor.execute(count_query, params[:-2])  # Exclude limit and offset
        total_count = cursor.fetchone()['COUNT(DISTINCT c.id)']
        cursor.close()
        
        # Process courses data
        for course in courses:
            # Parse instructor JSON
            if course['instructor']:
                try:
                    course['instructor'] = json.loads(course['instructor'])
                except:
                    course['instructor'] = {'name': 'Unknown', 'avatar': '', 'bio': ''}
            
            # Parse lessons JSON
            if course['lessons']:
                try:
                    course['lessons'] = json.loads(course['lessons'])
                except:
                    course['lessons'] = []
            
            course['enrolledStudents'] = course['enrolled_count']
            del course['enrolled_count']
        
        return jsonify({
            'success': True,
            'courses': courses,
            'pagination': {
                'currentPage': page,
                'totalPages': (total_count + limit - 1) // limit,
                'totalCourses': total_count,
                'hasNext': offset + limit < total_count,
                'hasPrev': page > 1
            }
        }), 200
        
    except Error as e:
        return jsonify({'success': False, 'message': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """Get specific course by ID"""
    try:
        cursor = g.db.cursor(dictionary=True)
        
        # Get course with enrollment count
        cursor.execute("""
        SELECT c.*, COUNT(ce.id) as enrolled_count
        FROM courses c
        LEFT JOIN course_enrollments ce ON c.id = ce.course_id
        WHERE c.id = %s
        GROUP BY c.id
        """, (course_id,))
        
        course = cursor.fetchone()
        
        if not course:
            cursor.close()
            return jsonify({'success': False, 'message': 'Course not found'}), 404
        
        # Parse instructor and lessons JSON
        if course['instructor']:
            try:
                course['instructor'] = json.loads(course['instructor'])
            except:
                course['instructor'] = {'name': 'Unknown', 'avatar': '', 'bio': ''}
        
        if course['lessons']:
            try:
                course['lessons'] = json.loads(course['lessons'])
            except:
                course['lessons'] = []
        
        course['enrolledStudents'] = course['enrolled_count']
        del course['enrolled_count']
        
        # Check if current user is enrolled (if authenticated)
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            payload = verify_token(token.split(' ')[1])
            if payload:
                cursor.execute("""
                SELECT id FROM course_enrollments 
                WHERE user_id = %s AND course_id = %s
                """, (payload['user_id'], course_id))
                
                enrollment = cursor.fetchone()
                course['isEnrolled'] = enrollment is not None
        
        cursor.close()
        
        return jsonify({'success': True, 'course': course}), 200
        
    except Error as e:
        return jsonify({'success': False, 'message': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

@app.route('/api/courses/<int:course_id>/enroll', methods=['POST'])
@auth_required
def enroll_in_course(course_id):
    """Enroll user in a course"""
    try:
        user_id = g.current_user['id']
        
        # Check if course exists
        cursor = g.db.cursor()
        cursor.execute("SELECT id FROM courses WHERE id = %s", (course_id,))
        course = cursor.fetchone()
        
        if not course:
            cursor.close()
            return jsonify({'success': False, 'message': 'Course not found'}), 404
        
        # Check if already enrolled
        cursor.execute("SELECT id FROM course_enrollments WHERE user_id = %s AND course_id = %s", 
                      (user_id, course_id))
        existing_enrollment = cursor.fetchone()
        
        if existing_enrollment:
            cursor.close()
            return jsonify({'success': False, 'message': 'Already enrolled in this course'}), 409
        
        # Enroll user
        cursor.execute("""
        INSERT INTO course_enrollments (user_id, course_id, enrolled_at, progress)
        VALUES (%s, %s, %s, %s)
        """, (user_id, course_id, datetime.datetime.now(), 0))
        
        g.db.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'Successfully enrolled in course'}), 201
        
    except Error as e:
        return jsonify({'success': False, 'message': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

# ============ OPPORTUNITY ROUTES ============

@app.route('/api/opportunities', methods=['GET'])
def get_opportunities():
    """Get all opportunities with optional filtering"""
    try:
        # Get query parameters
        type_filter = request.args.get('type')
        category = request.args.get('category')
        location = request.args.get('location')
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        
        # Build query
        where_conditions = ["is_active = TRUE", "deadline > %s"]
        params = [datetime.datetime.now()]
        
        if type_filter:
            where_conditions.append("type = %s")
            params.append(type_filter)
        
        if category:
            where_conditions.append("category = %s")
            params.append(category)
        
        if location:
            where_conditions.append("location LIKE %s")
            params.append(f'%{location}%')
        
        if search:
            where_conditions.append("(title LIKE %s OR description LIKE %s OR company LIKE %s)")
            params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
        
        where_clause = " WHERE " + " AND ".join(where_conditions)
        
        # Get opportunities
        cursor = g.db.cursor(dictionary=True)
        query = f"""
        SELECT o.*, COUNT(oa.id) as applications_count
        FROM opportunities o
        LEFT JOIN opportunity_applications oa ON o.id = oa.opportunity_id
        {where_clause}
        GROUP BY o.id
        ORDER BY o.deadline ASC
        LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        cursor.execute(query, params)
        opportunities = cursor.fetchall()
        
        # Get total count
        count_query = f"SELECT COUNT(DISTINCT o.id) FROM opportunities o {where_clause}"
        cursor.execute(count_query, params[:-2])  # Exclude limit and offset
        total_count = cursor.fetchone()['COUNT(DISTINCT o.id)']
        cursor.close()
        
        # Process opportunities data
        for opportunity in opportunities:
            # Parse details JSON
            if opportunity['details']:
                try:
                    opportunity['details'] = json.loads(opportunity['details'])
                except:
                    opportunity['details'] = {}
            
            opportunity['applicationsCount'] = opportunity['applications_count']
            del opportunity['applications_count']
            
            # Format deadline
            if opportunity['deadline']:
                opportunity['deadline'] = opportunity['deadline'].isoformat()
        
        return jsonify({
            'success': True,
            'opportunities': opportunities,
            'pagination': {
                'currentPage': page,
                'totalPages': (total_count + limit - 1) // limit,
                'totalOpportunities': total_count,
                'hasNext': offset + limit < total_count,
                'hasPrev': page > 1
            }
        }), 200
        
    except Error as e:
        return jsonify({'success': False, 'message': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

@app.route('/api/opportunities/<int:opportunity_id>/apply', methods=['POST'])
@auth_required
def apply_to_opportunity(opportunity_id):
    """Apply to an opportunity"""
    try:
        data = request.get_json()
        user_id = g.current_user['id']
        
        # Validate cover letter
        if not data.get('coverLetter'):
            return jsonify({'success': False, 'message': 'Cover letter is required'}), 400
        
        # Check if opportunity exists and is active
        cursor = g.db.cursor(dictionary=True)
        cursor.execute("""
        SELECT id, deadline FROM opportunities 
        WHERE id = %s AND is_active = TRUE
        """, (opportunity_id,))
        
        opportunity = cursor.fetchone()
        
        if not opportunity:
            cursor.close()
            return jsonify({'success': False, 'message': 'Opportunity not found or inactive'}), 404
        
        # Check if deadline has passed
        if opportunity['deadline'] < datetime.datetime.now():
            cursor.close()
            return jsonify({'success': False, 'message': 'Application deadline has passed'}), 400
        
        # Check if already applied
        cursor.execute("""
        SELECT id FROM opportunity_applications 
        WHERE user_id = %s AND opportunity_id = %s
        """, (user_id, opportunity_id))
        
        existing_application = cursor.fetchone()
        
        if existing_application:
            cursor.close()
            return jsonify({'success': False, 'message': 'Already applied to this opportunity'}), 409
        
        # Create application
        cursor.execute("""
        INSERT INTO opportunity_applications (user_id, opportunity_id, cover_letter, status, applied_at)
        VALUES (%s, %s, %s, %s, %s)
        """, (user_id, opportunity_id, data['coverLetter'], 'pending', datetime.datetime.now()))
        
        g.db.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'Application submitted successfully'}), 201
        
    except Error as e:
        return jsonify({'success': False, 'message': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

# ============ PORTFOLIO ROUTES ============

@app.route('/api/portfolios', methods=['GET'])
def get_portfolios():
    """Get all portfolios with optional filtering"""
    try:
        # Get query parameters
        category = request.args.get('category')
        user_id = request.args.get('userId')
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        
        # Build query
        where_conditions = []
        params = []
        
        if category:
            where_conditions.append("category = %s")
            params.append(category)
        
        if user_id:
            where_conditions.append("user_id = %s")
            params.append(user_id)
        
        if search:
            where_conditions.append("(title LIKE %s OR description LIKE %s)")
            params.extend([f'%{search}%', f'%{search}%'])
        
        where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # Get portfolios
        cursor = g.db.cursor(dictionary=True)
        query = f"""
        SELECT p.*, u.name as user_name, u.avatar as user_avatar,
               COUNT(DISTINCT pl.id) as likes_count,
               COUNT(DISTINCT pc.id) as comments_count
        FROM portfolios p
        LEFT JOIN users u ON p.user_id = u.id
        LEFT JOIN portfolio_likes pl ON p.id = pl.portfolio_id
        LEFT JOIN portfolio_comments pc ON p.id = pc.portfolio_id
        {where_clause}
        GROUP BY p.id
        ORDER BY p.created_at DESC
        LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        cursor.execute(query, params)
        portfolios = cursor.fetchall()
        
        # Get total count
        count_query = f"SELECT COUNT(DISTINCT p.id) FROM portfolios p {where_clause}"
        cursor.execute(count_query, params[:-2])  # Exclude limit and offset
        total_count = cursor.fetchone()['COUNT(DISTINCT p.id)']
        cursor.close()
        
        # Process portfolios data
        for portfolio in portfolios:
            # Parse tags JSON
            if portfolio['tags']:
                try:
                    portfolio['tags'] = json.loads(portfolio['tags'])
                except:
                    portfolio['tags'] = []
            
            portfolio['likesCount'] = portfolio['likes_count']
            portfolio['commentsCount'] = portfolio['comments_count']
            portfolio['user'] = {
                'name': portfolio['user_name'],
                'avatar': portfolio['user_avatar']
            }
            
            # Remove redundant fields
            del portfolio['likes_count']
            del portfolio['comments_count']
            del portfolio['user_name']
            del portfolio['user_avatar']
            
            # Format dates
            if portfolio['created_at']:
                portfolio['created_at'] = portfolio['created_at'].isoformat()
        
        return jsonify({
            'success': True,
            'portfolios': portfolios,
            'pagination': {
                'currentPage': page,
                'totalPages': (total_count + limit - 1) // limit,
                'totalPortfolios': total_count,
                'hasNext': offset + limit < total_count,
                'hasPrev': page > 1
            }
        }), 200
        
    except Error as e:
        return jsonify({'success': False, 'message': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

@app.route('/api/portfolios', methods=['POST'])
@auth_required
def create_portfolio():
    """Create new portfolio"""
    try:
        data = request.get_json()
        user_id = g.current_user['id']
        
        # Validate required fields
        required_fields = ['title', 'description', 'category']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'message': f'{field} is required'}), 400
        
        # Validate category
        valid_categories = ['Short Films', 'Documentaries', 'Music Videos', 'Commercials', 'Experimental']
        if data['category'] not in valid_categories:
            return jsonify({'success': False, 'message': 'Invalid category'}), 400
        
        # Create portfolio
        cursor = g.db.cursor()
        cursor.execute("""
        INSERT INTO portfolios (user_id, title, description, thumbnail, video_url, 
                              tags, category, views, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            data['title'],
            data['description'],
            data.get('thumbnail', ''),
            data.get('videoUrl', ''),
            json.dumps(data.get('tags', [])),
            data['category'],
            0,
            datetime.datetime.now()
        ))
        
        portfolio_id = cursor.lastrowid
        g.db.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Portfolio created successfully',
            'portfolioId': portfolio_id
        }), 201
        
    except Error as e:
        return jsonify({'success': False, 'message': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

# ============ MENTORSHIP ROUTES ============

@app.route('/api/mentorships', methods=['GET'])
@auth_required
def get_mentorships():
    """Get user's mentorships"""
    try:
        user_id = g.current_user['id']
        user_type = g.current_user['user_type']
        
        cursor = g.db.cursor(dictionary=True)
        
        if user_type == 'mentor':
            # Get mentorships where user is mentor
            cursor.execute("""
            SELECT m.*, u.name as mentee_name, u.email as mentee_email, u.avatar as mentee_avatar
            FROM mentorships m
            LEFT JOIN users u ON m.mentee_id = u.id
            WHERE m.mentor_id = %s
            ORDER BY m.created_at DESC
            """, (user_id,))
        else:
            # Get mentorships where user is mentee
            cursor.execute("""
            SELECT m.*, u.name as mentor_name, u.email as mentor_email, u.avatar as mentor_avatar
            FROM mentorships m
            LEFT JOIN users u ON m.mentor_id = u.id
            WHERE m.mentee_id = %s
            ORDER BY m.created_at DESC
            """, (user_id,))
        
        mentorships = cursor.fetchall()
        cursor.close()
        
        # Process mentorships data
        for mentorship in mentorships:
            # Parse specialties and sessions JSON
            if mentorship['specialties']:
                try:
                    mentorship['specialties'] = json.loads(mentorship['specialties'])
                except:
                    mentorship['specialties'] = []
            
            if mentorship['sessions']:
                try:
                    mentorship['sessions'] = json.loads(mentorship['sessions'])
                except:
                    mentorship['sessions'] = []
            
            # Add user info based on relationship
            if user_type == 'mentor':
                mentorship['mentee'] = {
                    'name': mentorship['mentee_name'],
                    'email': mentorship['mentee_email'],
                    'avatar': mentorship['mentee_avatar']
                }
                del mentorship['mentee_name']
                del mentorship['mentee_email']
                del mentorship['mentee_avatar']
            else:
                mentorship['mentor'] = {
                    'name': mentorship['mentor_name'],
                    'email': mentorship['mentor_email'],
                    'avatar': mentorship['mentor_avatar']
                }
                del mentorship['mentor_name']
                del mentorship['mentor_email']
                del mentorship['mentor_avatar']
            
            # Format dates
            if mentorship['created_at']:
                mentorship['created_at'] = mentorship['created_at'].isoformat()
        
        return jsonify({
            'success': True,
            'mentorships': mentorships
        }), 200
        
    except Error as e:
        return jsonify({'success': False, 'message': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

# ============ FILE UPLOAD ROUTES ============

@app.route('/api/upload', methods=['POST'])
@auth_required
def upload_file():
    """Upload file"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to filename to avoid conflicts
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_")
            filename = f"{timestamp}{filename}"
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Return file URL
            file_url = f"/uploads/{filename}"
            
            return jsonify({
                'success': True,
                'message': 'File uploaded successfully',
                'fileUrl': file_url,
                'filename': filename
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': 'File upload failed'}), 500

# ============ SEARCH ROUTES ============

@app.route('/api/search', methods=['GET'])
def search():
    """Global search across all content"""
    try:
        query = request.args.get('q', '').strip()
        category = request.args.get('category', 'all')  # all, courses, opportunities, portfolios, users
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit
        
        if not query:
            return jsonify({'success': False, 'message': 'Search query is required'}), 400
        
        search_pattern = f'%{query}%'
        results = {}
        
        cursor = g.db.cursor(dictionary=True)
        
        # Search courses
        if category in ['all', 'courses']:
            cursor.execute("""
            SELECT 'course' as type, id, title, description, category, level, price, image,
                   created_at
            FROM courses 
            WHERE title LIKE %s OR description LIKE %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """, (search_pattern, search_pattern, limit if category == 'courses' else limit//4, 
                  offset if category == 'courses' else 0))
            results['courses'] = cursor.fetchall()
        
        # Search opportunities
        if category in ['all', 'opportunities']:
            cursor.execute("""
            SELECT 'opportunity' as type, id, title, description, type, company, deadline,
                   created_at
            FROM opportunities 
            WHERE (title LIKE %s OR description LIKE %s OR company LIKE %s) 
                  AND is_active = TRUE AND deadline > %s
            ORDER BY deadline ASC
            LIMIT %s OFFSET %s
            """, (search_pattern, search_pattern, search_pattern, datetime.datetime.now(),
                  limit if category == 'opportunities' else limit//4, 
                  offset if category == 'opportunities' else 0))
            results['opportunities'] = cursor.fetchall()
        
        # Search portfolios
        if category in ['all', 'portfolios']:
            cursor.execute("""
            SELECT 'portfolio' as type, p.id, p.title, p.description, p.category, 
                   p.thumbnail, p.views, p.created_at, u.name as user_name
            FROM portfolios p
            LEFT JOIN users u ON p.user_id = u.id
            WHERE p.title LIKE %s OR p.description LIKE %s
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
            """, (search_pattern, search_pattern, 
                  limit if category == 'portfolios' else limit//4,
                  offset if category == 'portfolios' else 0))
            results['portfolios'] = cursor.fetchall()
        
        # Search users
        if category in ['all', 'users']:
            cursor.execute("""
            SELECT 'user' as type, id, name, email, user_type, bio, location, avatar,
                   followers, created_at
            FROM users 
            WHERE name LIKE %s OR bio LIKE %s OR location LIKE %s
            ORDER BY followers DESC, created_at DESC
            LIMIT %s OFFSET %s
            """, (search_pattern, search_pattern, search_pattern,
                  limit if category == 'users' else limit//4,
                  offset if category == 'users' else 0))
            results['users'] = cursor.fetchall()
        
        cursor.close()
        
        # Format results
        total_results = sum(len(category_results) for category_results in results.values())
        
        return jsonify({
            'success': True,
            'query': query,
            'category': category,
            'results': results,
            'totalResults': total_results,
            'pagination': {
                'currentPage': page,
                'hasNext': total_results == limit,
                'hasPrev': page > 1
            }
        }), 200
        
    except Error as e:
        return jsonify({'success': False, 'message': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': 'Search failed'}), 500

# ============ STATIC FILE SERVING ============

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return app.send_static_file(f'uploads/{filename}')

# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'success': False, 'message': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

# ============ HEALTH CHECK ============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db = get_db_connection()
        if db:
            db.close()
            return jsonify({
                'success': True,
                'message': 'Server is healthy',
                'timestamp': datetime.datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Database connection failed'
            }), 503
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Health check failed'
        }), 503

# ============ MAIN ============

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("Starting CI-NDA Flask Backend Server...")
    print(f"Server will run on http://{host}:{port}")
    print("API endpoints available at: http://localhost:5000/api")
    print("Database configuration:")
    print(f"  Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"  Database: {DB_CONFIG['database']}")
    print(f"  User: {DB_CONFIG['user']}")
    print("Make sure to:")
    print("  1. Import database_schema.sql into phpMyAdmin")
    print("  2. Update .env file with your database credentials")
    print("  3. Ensure MySQL server is running")
    print()
    
    app.run(debug=debug, host=host, port=port)