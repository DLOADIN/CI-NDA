#!/usr/bin/env python3
"""
Database Integrity Check and Migration Script for CI-NDA
Ensures all required tables exist with proper schema
"""

import mysql.connector
import json
import sys
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Update with your MySQL username
    'password': '',  # Update with your MySQL password
    'database': 'ci_nda'
}

# Table schemas
SCHEMAS = {
    'users': """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            role ENUM('student', 'instructor', 'mentor', 'admin') DEFAULT 'student',
            bio TEXT,
            skills JSON,
            experience_level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'beginner',
            profile_image VARCHAR(255),
            location VARCHAR(100),
            website VARCHAR(255),
            social_links JSON,
            is_active BOOLEAN DEFAULT TRUE,
            email_verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_email (email),
            INDEX idx_username (username),
            INDEX idx_role (role),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    
    'courses': """
        CREATE TABLE IF NOT EXISTS courses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            instructor VARCHAR(100) NOT NULL,
            instructor_id INT,
            category ENUM('directing', 'cinematography', 'editing', 'screenwriting', 'sound', 'production') NOT NULL,
            level ENUM('beginner', 'intermediate', 'advanced') NOT NULL,
            duration VARCHAR(50),
            price DECIMAL(10,2) DEFAULT 0.00,
            thumbnail VARCHAR(255),
            video_url VARCHAR(255),
            syllabus TEXT,
            requirements TEXT,
            learning_outcomes JSON,
            enrolled_count INT DEFAULT 0,
            rating DECIMAL(3,2) DEFAULT 0.00,
            total_ratings INT DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (instructor_id) REFERENCES users(id) ON DELETE SET NULL,
            INDEX idx_category (category),
            INDEX idx_level (level),
            INDEX idx_instructor (instructor_id),
            INDEX idx_created_at (created_at),
            INDEX idx_rating (rating),
            FULLTEXT KEY ft_search (title, description, instructor)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    
    'course_enrollments': """
        CREATE TABLE IF NOT EXISTS course_enrollments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            course_id INT NOT NULL,
            motivation TEXT,
            progress_percentage DECIMAL(5,2) DEFAULT 0.00,
            completed_lessons JSON,
            status ENUM('enrolled', 'in_progress', 'completed', 'dropped') DEFAULT 'enrolled',
            completion_date TIMESTAMP NULL,
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            UNIQUE KEY unique_enrollment (user_id, course_id),
            INDEX idx_user_id (user_id),
            INDEX idx_course_id (course_id),
            INDEX idx_status (status),
            INDEX idx_enrolled_at (enrolled_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    
    'opportunities': """
        CREATE TABLE IF NOT EXISTS opportunities (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            company VARCHAR(100) NOT NULL,
            type ENUM('job', 'internship', 'freelance', 'collaboration') NOT NULL,
            location VARCHAR(100),
            remote_allowed BOOLEAN DEFAULT FALSE,
            salary_range VARCHAR(50),
            requirements TEXT,
            responsibilities TEXT,
            skills_required JSON,
            experience_level ENUM('entry', 'mid', 'senior') NOT NULL,
            application_deadline DATE,
            external_url VARCHAR(255),
            contact_email VARCHAR(100),
            status ENUM('open', 'closed', 'filled') DEFAULT 'open',
            applications_count INT DEFAULT 0,
            created_by INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
            INDEX idx_type (type),
            INDEX idx_experience_level (experience_level),
            INDEX idx_status (status),
            INDEX idx_deadline (application_deadline),
            INDEX idx_created_at (created_at),
            FULLTEXT KEY ft_search (title, description, company, location)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    
    'opportunity_applications': """
        CREATE TABLE IF NOT EXISTS opportunity_applications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            opportunity_id INT NOT NULL,
            cover_letter TEXT,
            portfolio_url VARCHAR(255),
            resume_url VARCHAR(255),
            status ENUM('pending', 'reviewed', 'shortlisted', 'rejected', 'accepted') DEFAULT 'pending',
            notes TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (opportunity_id) REFERENCES opportunities(id) ON DELETE CASCADE,
            UNIQUE KEY unique_application (user_id, opportunity_id),
            INDEX idx_user_id (user_id),
            INDEX idx_opportunity_id (opportunity_id),
            INDEX idx_status (status),
            INDEX idx_applied_at (applied_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    
    'portfolios': """
        CREATE TABLE IF NOT EXISTS portfolios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            category ENUM('film', 'video', 'photography', 'audio', 'script', 'other') NOT NULL,
            media_type ENUM('video', 'image', 'audio', 'document', 'link') NOT NULL,
            file_url VARCHAR(255),
            thumbnail_url VARCHAR(255),
            external_url VARCHAR(255),
            duration INT, -- in seconds for video/audio
            file_size BIGINT, -- in bytes
            tags JSON,
            technical_specs JSON,
            equipment_used TEXT,
            collaborators JSON,
            awards TEXT,
            featured BOOLEAN DEFAULT FALSE,
            view_count INT DEFAULT 0,
            like_count INT DEFAULT 0,
            privacy ENUM('public', 'private', 'unlisted') DEFAULT 'public',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_category (category),
            INDEX idx_media_type (media_type),
            INDEX idx_privacy (privacy),
            INDEX idx_featured (featured),
            INDEX idx_created_at (created_at),
            FULLTEXT KEY ft_search (title, description, equipment_used)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    
    'mentorship': """
        CREATE TABLE IF NOT EXISTS mentorship (
            id INT AUTO_INCREMENT PRIMARY KEY,
            mentor_id INT NOT NULL,
            mentee_id INT NOT NULL,
            topic VARCHAR(200) NOT NULL,
            description TEXT,
            duration_weeks INT DEFAULT 4,
            status ENUM('pending', 'active', 'completed', 'cancelled') DEFAULT 'pending',
            meeting_frequency ENUM('weekly', 'bi-weekly', 'monthly', 'as-needed') DEFAULT 'weekly',
            preferred_communication ENUM('video', 'audio', 'chat', 'in-person') DEFAULT 'video',
            goals TEXT,
            progress_notes TEXT,
            mentor_feedback TEXT,
            mentee_feedback TEXT,
            rating DECIMAL(3,2),
            start_date DATE,
            end_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (mentor_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (mentee_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_mentor_id (mentor_id),
            INDEX idx_mentee_id (mentee_id),
            INDEX idx_status (status),
            INDEX idx_start_date (start_date),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    
    'mentorship_sessions': """
        CREATE TABLE IF NOT EXISTS mentorship_sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            mentorship_id INT NOT NULL,
            session_date DATETIME NOT NULL,
            duration_minutes INT DEFAULT 60,
            session_type ENUM('video', 'audio', 'chat', 'in-person') NOT NULL,
            agenda TEXT,
            notes TEXT,
            homework_assigned TEXT,
            status ENUM('scheduled', 'completed', 'cancelled', 'no-show') DEFAULT 'scheduled',
            recording_url VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (mentorship_id) REFERENCES mentorship(id) ON DELETE CASCADE,
            INDEX idx_mentorship_id (mentorship_id),
            INDEX idx_session_date (session_date),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
}

# Sample data for testing
SAMPLE_DATA = {
    'courses': [
        {
            'title': 'Introduction to Filmmaking',
            'description': 'Learn the fundamentals of filmmaking from pre-production to post-production.',
            'instructor': 'Jane Director',
            'category': 'directing',
            'level': 'beginner',
            'duration': '8 weeks',
            'price': 0.00,
            'syllabus': 'Week 1: Story Development\nWeek 2: Pre-Production Planning\nWeek 3: Cinematography Basics\nWeek 4: Directing Actors\nWeek 5: Sound Recording\nWeek 6: Editing Fundamentals\nWeek 7: Color Correction\nWeek 8: Final Project'
        },
        {
            'title': 'Advanced Cinematography Techniques',
            'description': 'Master advanced camera movements, lighting, and composition techniques.',
            'instructor': 'Michael Lens',
            'category': 'cinematography',
            'level': 'advanced',
            'duration': '6 weeks',
            'price': 99.99,
            'syllabus': 'Advanced lighting setups, complex camera movements, color theory, lens selection, and visual storytelling techniques.'
        },
        {
            'title': 'Video Editing Masterclass',
            'description': 'Comprehensive video editing course covering all major editing software.',
            'instructor': 'Sarah Editor',
            'category': 'editing',
            'level': 'intermediate',
            'duration': '10 weeks',
            'price': 79.99,
            'syllabus': 'Non-linear editing, color grading, audio mixing, effects, and workflow optimization.'
        },
        {
            'title': 'Screenwriting Fundamentals',
            'description': 'Learn to craft compelling stories for the screen.',
            'instructor': 'David Writer',
            'category': 'screenwriting',
            'level': 'beginner',
            'duration': '12 weeks',
            'price': 59.99,
            'syllabus': 'Story structure, character development, dialogue, formatting, and industry standards.'
        },
        {
            'title': 'Sound Design for Film',
            'description': 'Create immersive audio experiences for your films.',
            'instructor': 'Alex Sound',
            'category': 'sound',
            'level': 'intermediate',
            'duration': '8 weeks',
            'price': 89.99,
            'syllabus': 'Recording techniques, mixing, sound effects, music integration, and audio post-production.'
        }
    ],
    
    'opportunities': [
        {
            'title': 'Junior Video Editor',
            'description': 'Seeking a talented junior video editor to join our creative team.',
            'company': 'Creative Studios Inc.',
            'type': 'job',
            'location': 'Los Angeles, CA',
            'remote_allowed': True,
            'salary_range': '$40,000 - $60,000',
            'requirements': 'Experience with Premiere Pro, After Effects, and basic motion graphics skills.',
            'experience_level': 'entry',
            'contact_email': 'careers@creativestudios.com'
        },
        {
            'title': 'Freelance Cinematographer',
            'description': 'Looking for experienced cinematographer for independent film project.',
            'company': 'Indie Film Collective',
            'type': 'freelance',
            'location': 'New York, NY',
            'remote_allowed': False,
            'salary_range': '$500 - $1,500/day',
            'requirements': 'Own camera equipment, 3+ years experience, portfolio required.',
            'experience_level': 'mid',
            'contact_email': 'projects@indiefilm.com'
        },
        {
            'title': 'Production Intern',
            'description': 'Hands-on internship opportunity on upcoming feature film.',
            'company': 'Major Motion Pictures',
            'type': 'internship',
            'location': 'Atlanta, GA',
            'remote_allowed': False,
            'salary_range': 'Unpaid',
            'requirements': 'Film school student or recent graduate, passion for filmmaking.',
            'experience_level': 'entry',
            'contact_email': 'internships@majormotion.com'
        }
    ]
}

def connect_db():
    """Connect to MySQL database"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def create_database():
    """Create database if it doesn't exist"""
    try:
        # Connect without specifying database
        config = DB_CONFIG.copy()
        config.pop('database', None)
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Database '{DB_CONFIG['database']}' created or already exists")
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"❌ Error creating database: {err}")
        return False
    
    return True

def check_and_create_tables():
    """Check if tables exist and create them if they don't"""
    connection = connect_db()
    if not connection:
        return False
    
    cursor = connection.cursor()
    tables_created = 0
    
    try:
        for table_name, schema in SCHEMAS.items():
            cursor.execute(schema)
            print(f"✅ Table '{table_name}' ensured")
            tables_created += 1
        
        connection.commit()
        print(f"✅ All {tables_created} tables checked/created successfully")
        
    except mysql.connector.Error as err:
        print(f"❌ Error creating tables: {err}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()
    
    return True

def check_data_integrity():
    """Check database for existing data and basic integrity"""
    connection = connect_db()
    if not connection:
        return False
    
    cursor = connection.cursor()
    
    try:
        print("\n📊 Database Status Report:")
        print("=" * 50)
        
        for table_name in SCHEMAS.keys():
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  {table_name}: {count} records")
        
        print("=" * 50)
        
        # Check for admin user
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            print("⚠️  No admin users found")
        else:
            print(f"✅ {admin_count} admin user(s) found")
        
        # Check for foreign key constraints
        cursor.execute("""
            SELECT TABLE_NAME, CONSTRAINT_NAME 
            FROM information_schema.TABLE_CONSTRAINTS 
            WHERE CONSTRAINT_TYPE = 'FOREIGN KEY' 
            AND TABLE_SCHEMA = %s
        """, (DB_CONFIG['database'],))
        
        fk_constraints = cursor.fetchall()
        print(f"✅ {len(fk_constraints)} foreign key constraints active")
        
    except mysql.connector.Error as err:
        print(f"❌ Error checking data integrity: {err}")
        return False
    finally:
        cursor.close()
        connection.close()
    
    return True

def add_sample_data():
    """Add sample data for testing if tables are empty"""
    connection = connect_db()
    if not connection:
        return False
    
    cursor = connection.cursor()
    
    try:
        # Check if courses table is empty
        cursor.execute("SELECT COUNT(*) FROM courses")
        course_count = cursor.fetchone()[0]
        
        if course_count == 0:
            print("\n🌱 Adding sample courses...")
            for course in SAMPLE_DATA['courses']:
                cursor.execute("""
                    INSERT INTO courses (title, description, instructor, category, level, duration, price, syllabus)
                    VALUES (%(title)s, %(description)s, %(instructor)s, %(category)s, %(level)s, %(duration)s, %(price)s, %(syllabus)s)
                """, course)
            print(f"✅ Added {len(SAMPLE_DATA['courses'])} sample courses")
        
        # Check if opportunities table is empty
        cursor.execute("SELECT COUNT(*) FROM opportunities")
        opportunity_count = cursor.fetchone()[0]
        
        if opportunity_count == 0:
            print("\n💼 Adding sample opportunities...")
            for opportunity in SAMPLE_DATA['opportunities']:
                cursor.execute("""
                    INSERT INTO opportunities (title, description, company, type, location, remote_allowed, 
                                             salary_range, requirements, experience_level, contact_email)
                    VALUES (%(title)s, %(description)s, %(company)s, %(type)s, %(location)s, %(remote_allowed)s,
                            %(salary_range)s, %(requirements)s, %(experience_level)s, %(contact_email)s)
                """, opportunity)
            print(f"✅ Added {len(SAMPLE_DATA['opportunities'])} sample opportunities")
        
        connection.commit()
        
    except mysql.connector.Error as err:
        print(f"❌ Error adding sample data: {err}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()
    
    return True

def optimize_database():
    """Run database optimization commands"""
    connection = connect_db()
    if not connection:
        return False
    
    cursor = connection.cursor()
    
    try:
        print("\n🔧 Optimizing database...")
        
        # Analyze tables for better query performance
        for table_name in SCHEMAS.keys():
            cursor.execute(f"ANALYZE TABLE {table_name}")
            print(f"  Analyzed table: {table_name}")
        
        print("✅ Database optimization complete")
        
    except mysql.connector.Error as err:
        print(f"❌ Error optimizing database: {err}")
        return False
    finally:
        cursor.close()
        connection.close()
    
    return True

def main():
    """Main function to run database integrity check and setup"""
    print("🔍 CI-NDA Database Integrity Check & Migration")
    print("=" * 60)
    
    # Step 1: Create database
    if not create_database():
        print("❌ Failed to create database")
        sys.exit(1)
    
    # Step 2: Create tables
    if not check_and_create_tables():
        print("❌ Failed to create tables")
        sys.exit(1)
    
    # Step 3: Check data integrity
    if not check_data_integrity():
        print("❌ Data integrity check failed")
        sys.exit(1)
    
    # Step 4: Add sample data if needed
    if not add_sample_data():
        print("❌ Failed to add sample data")
        sys.exit(1)
    
    # Step 5: Optimize database
    if not optimize_database():
        print("❌ Database optimization failed")
        sys.exit(1)
    
    print("\n🎉 Database setup and integrity check completed successfully!")
    print("\nNext steps:")
    print("1. Update database credentials in server.py if needed")
    print("2. Create an admin user through the registration system")
    print("3. Test the application endpoints")
    
if __name__ == "__main__":
    main()