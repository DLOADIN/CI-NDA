#!/usr/bin/env python3
"""
Create compatible database for CI-NDA
Uses older MySQL collation for compatibility
"""

import mysql.connector
from mysql.connector import Error
import sys

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'port': 3306
}

def create_compatible_database():
    """Create database with compatible collation"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Drop existing database if it exists
        cursor.execute("DROP DATABASE IF EXISTS `cinda_db`")
        print("✅ Dropped existing database (if any)")
        
        # Create new database with compatible collation
        cursor.execute("CREATE DATABASE `cinda_db` CHARACTER SET utf8mb4")
        print("✅ Created database 'cinda_db' with utf8mb4 charset")
        
        # Use the database
        cursor.execute("USE `cinda_db`")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE `users` (
              `id` int(11) NOT NULL AUTO_INCREMENT,
              `name` varchar(255) NOT NULL,
              `email` varchar(255) NOT NULL UNIQUE,
              `password` varchar(255) DEFAULT NULL,
              `user_type` enum('filmmaker','mentor','sponsor') DEFAULT 'filmmaker',
              `avatar` varchar(500) DEFAULT NULL,
              `bio` text DEFAULT NULL,
              `location` varchar(255) DEFAULT NULL,
              `website` varchar(500) DEFAULT NULL,
              `specialization` json DEFAULT NULL,
              `social_provider` varchar(50) DEFAULT NULL,
              `social_provider_id` varchar(255) DEFAULT NULL,
              `followers` int(11) DEFAULT 0,
              `following` int(11) DEFAULT 0,
              `projects` int(11) DEFAULT 0,
              `awards` int(11) DEFAULT 0,
              `is_verified` boolean DEFAULT FALSE,
              `last_login` timestamp NULL DEFAULT NULL,
              `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
              `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              PRIMARY KEY (`id`),
              KEY `idx_email` (`email`),
              KEY `idx_user_type` (`user_type`),
              KEY `idx_created_at` (`created_at`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Created users table")
        
        # Create courses table
        cursor.execute("""
            CREATE TABLE `courses` (
              `id` int(11) NOT NULL AUTO_INCREMENT,
              `title` varchar(255) NOT NULL,
              `category` enum('CINEMATOGRAPHY','EDITING','DIRECTING','SOUND DESIGN','SCREENWRITING','LIGHTING','PRODUCTION DESIGN','COLOR GRADING','DOCUMENTARY') NOT NULL,
              `instructor` json DEFAULT NULL,
              `description` text NOT NULL,
              `image` varchar(500) DEFAULT NULL,
              `duration` varchar(100) DEFAULT NULL,
              `level` enum('Beginner','Intermediate','Advanced') NOT NULL,
              `price` decimal(10,2) DEFAULT 0.00,
              `lessons` json DEFAULT NULL,
              `is_published` boolean DEFAULT TRUE,
              `enrolled_count` int(11) DEFAULT 0,
              `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
              `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              PRIMARY KEY (`id`),
              KEY `idx_category` (`category`),
              KEY `idx_level` (`level`),
              KEY `idx_created_at` (`created_at`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Created courses table")
        
        # Create opportunities table
        cursor.execute("""
            CREATE TABLE `opportunities` (
              `id` int(11) NOT NULL AUTO_INCREMENT,
              `type` enum('GRANT','JOB','COMPETITION','COLLABORATION','INTERNSHIP') NOT NULL,
              `title` varchar(255) NOT NULL,
              `company` varchar(255) NOT NULL,
              `description` text NOT NULL,
              `details` json DEFAULT NULL,
              `funding` varchar(255) DEFAULT NULL,
              `location` varchar(255) DEFAULT NULL,
              `category` varchar(255) DEFAULT NULL,
              `deadline` timestamp NOT NULL,
              `is_active` boolean DEFAULT TRUE,
              `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
              `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              PRIMARY KEY (`id`),
              KEY `idx_type` (`type`),
              KEY `idx_deadline` (`deadline`),
              KEY `idx_is_active` (`is_active`),
              KEY `idx_created_at` (`created_at`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Created opportunities table")
        
        # Create portfolios table
        cursor.execute("""
            CREATE TABLE `portfolios` (
              `id` int(11) NOT NULL AUTO_INCREMENT,
              `user_id` int(11) NOT NULL,
              `title` varchar(255) NOT NULL,
              `description` text DEFAULT NULL,
              `thumbnail` varchar(500) DEFAULT NULL,
              `video_url` varchar(500) DEFAULT NULL,
              `tags` json DEFAULT NULL,
              `category` enum('Short Films','Documentaries','Music Videos','Commercials','Experimental') DEFAULT NULL,
              `views` int(11) DEFAULT 0,
              `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
              `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              PRIMARY KEY (`id`),
              KEY `idx_user_id` (`user_id`),
              KEY `idx_category` (`category`),
              KEY `idx_created_at` (`created_at`),
              FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Created portfolios table")
        
        # Create mentorships table
        cursor.execute("""
            CREATE TABLE `mentorships` (
              `id` int(11) NOT NULL AUTO_INCREMENT,
              `mentor_id` int(11) NOT NULL,
              `mentee_id` int(11) NOT NULL,
              `status` enum('pending','active','completed','cancelled') DEFAULT 'pending',
              `specialties` json DEFAULT NULL,
              `bio` text DEFAULT NULL,
              `years_experience` int(11) DEFAULT NULL,
              `available_slots` int(11) DEFAULT 5,
              `sessions` json DEFAULT NULL,
              `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
              `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              PRIMARY KEY (`id`),
              KEY `idx_mentor_id` (`mentor_id`),
              KEY `idx_mentee_id` (`mentee_id`),
              KEY `idx_status` (`status`),
              FOREIGN KEY (`mentor_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
              FOREIGN KEY (`mentee_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Created mentorships table")
        
        # Insert sample data
        cursor.execute("""
            INSERT INTO `users` (`name`, `email`, `password`, `user_type`, `bio`, `location`, `followers`, `following`, `projects`) VALUES
            ('John Filmmaker', 'john@example.com', '$2b$12$dummy.hash.here', 'filmmaker', 'Passionate filmmaker', 'Los Angeles, CA', 150, 75, 12),
            ('Sarah Mentor', 'sarah@example.com', '$2b$12$dummy.hash.here', 'mentor', 'Experienced director', 'New York, NY', 500, 200, 25),
            ('Alex Producer', 'alex@example.com', '$2b$12$dummy.hash.here', 'sponsor', 'Film producer', 'London, UK', 75, 150, 8)
        """)
        print("✅ Added sample users")
        
        cursor.execute("""
            INSERT INTO `courses` (`title`, `category`, `description`, `level`, `price`, `enrolled_count`) VALUES
            ('Introduction to Filmmaking', 'DIRECTING', 'Learn the basics of filmmaking', 'Beginner', 0.00, 45),
            ('Advanced Cinematography', 'CINEMATOGRAPHY', 'Master camera techniques', 'Advanced', 99.99, 23),
            ('Video Editing Masterclass', 'EDITING', 'Professional editing skills', 'Intermediate', 79.99, 67),
            ('Screenwriting Fundamentals', 'SCREENWRITING', 'Write compelling scripts', 'Beginner', 59.99, 89),
            ('Sound Design for Film', 'SOUND DESIGN', 'Create immersive audio', 'Intermediate', 89.99, 34)
        """)
        print("✅ Added sample courses")
        
        cursor.execute("""
            INSERT INTO `opportunities` (`type`, `title`, `company`, `description`, `deadline`, `location`) VALUES
            ('GRANT', 'Emerging Filmmaker Grant', 'Film Foundation', 'Support for new filmmakers', DATE_ADD(NOW(), INTERVAL 60 DAY), 'Global'),
            ('JOB', 'Video Editor Position', 'Creative Studios', 'Full-time editor needed', DATE_ADD(NOW(), INTERVAL 30 DAY), 'Remote'),
            ('COMPETITION', 'Short Film Festival', 'Indie Film Fest', 'Annual short film competition', DATE_ADD(NOW(), INTERVAL 90 DAY), 'Various')
        """)
        print("✅ Added sample opportunities")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    print("🗄️  Creating CI-NDA Compatible Database")
    print("=" * 40)
    
    if create_compatible_database():
        print("\n🎉 Database created successfully!")
        print("\nYou can now:")
        print("1. Start your Flask server: python server.py")
        print("2. Access your webapp at: http://localhost:5000")
        print("3. Test connection: python test_db.py")
    else:
        print("\n❌ Database creation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()