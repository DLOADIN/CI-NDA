-- CI-NDA Database Schema
-- Run this SQL script in phpMyAdmin to create the database and all tables

-- Create database
CREATE DATABASE IF NOT EXISTS `cinda_db` 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

USE `cinda_db`;

-- ============================================================================
-- USERS TABLE
-- ============================================================================
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
  KEY `idx_created_at` (`created_at`),
  UNIQUE KEY `unique_social_login` (`social_provider`, `social_provider_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- COURSES TABLE
-- ============================================================================
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
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_category` (`category`),
  KEY `idx_level` (`level`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- COURSE ENROLLMENTS TABLE
-- ============================================================================
CREATE TABLE `course_enrollments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `progress` int(11) DEFAULT 0,
  `enrolled_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  `completed_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_enrollment` (`user_id`, `course_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_course_id` (`course_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- OPPORTUNITIES TABLE
-- ============================================================================
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- OPPORTUNITY APPLICATIONS TABLE
-- ============================================================================
CREATE TABLE `opportunity_applications` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `opportunity_id` int(11) NOT NULL,
  `cover_letter` text NOT NULL,
  `status` enum('pending','accepted','rejected') DEFAULT 'pending',
  `applied_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  `reviewed_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_application` (`user_id`, `opportunity_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_opportunity_id` (`opportunity_id`),
  KEY `idx_status` (`status`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`opportunity_id`) REFERENCES `opportunities`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- PORTFOLIOS TABLE
-- ============================================================================
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- PORTFOLIO LIKES TABLE
-- ============================================================================
CREATE TABLE `portfolio_likes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `portfolio_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_like` (`portfolio_id`, `user_id`),
  KEY `idx_portfolio_id` (`portfolio_id`),
  KEY `idx_user_id` (`user_id`),
  FOREIGN KEY (`portfolio_id`) REFERENCES `portfolios`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- PORTFOLIO COMMENTS TABLE
-- ============================================================================
CREATE TABLE `portfolio_comments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `portfolio_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_portfolio_id` (`portfolio_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_created_at` (`created_at`),
  FOREIGN KEY (`portfolio_id`) REFERENCES `portfolios`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- MENTORSHIPS TABLE
-- ============================================================================
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
  UNIQUE KEY `unique_mentorship` (`mentor_id`, `mentee_id`),
  KEY `idx_mentor_id` (`mentor_id`),
  KEY `idx_mentee_id` (`mentee_id`),
  KEY `idx_status` (`status`),
  FOREIGN KEY (`mentor_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`mentee_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- MENTORSHIP MESSAGES TABLE
-- ============================================================================
CREATE TABLE `mentorship_messages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mentorship_id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `is_read` boolean DEFAULT FALSE,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_mentorship_id` (`mentorship_id`),
  KEY `idx_sender_id` (`sender_id`),
  KEY `idx_created_at` (`created_at`),
  FOREIGN KEY (`mentorship_id`) REFERENCES `mentorships`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`sender_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- NOTIFICATIONS TABLE
-- ============================================================================
CREATE TABLE `notifications` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `type` varchar(50) NOT NULL,
  `title` varchar(255) NOT NULL,
  `message` text NOT NULL,
  `data` json DEFAULT NULL,
  `is_read` boolean DEFAULT FALSE,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_is_read` (`is_read`),
  KEY `idx_created_at` (`created_at`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- INSERT SAMPLE DATA
-- ============================================================================

-- Sample Users
INSERT INTO `users` (`name`, `email`, `password`, `user_type`, `bio`, `location`, `specialization`, `is_verified`, `followers`, `following`, `projects`, `awards`) VALUES
('John Filmmaker', 'john@example.com', '$2b$10$example.hash.here', 'filmmaker', 'Passionate filmmaker with 5 years of experience in documentaries and short films.', 'Los Angeles, CA', '["Documentary", "Cinematography"]', TRUE, 150, 75, 12, 3),
('Sarah Mentor', 'sarah@example.com', '$2b$10$example.hash.here', 'mentor', 'Award-winning director with 15 years in the industry, specializing in narrative films.', 'New York, NY', '["Directing", "Screenwriting"]', TRUE, 500, 200, 25, 8),
('Alex Producer', 'alex@example.com', '$2b$10$example.hash.here', 'sponsor', 'Film producer and investor looking to support emerging talent.', 'London, UK', '["Production", "Financing"]', TRUE, 75, 150, 8, 2);

-- Sample Courses
INSERT INTO `courses` (`title`, `category`, `instructor`, `description`, `duration`, `level`, `price`, `lessons`) VALUES
('Cinematic Storytelling Fundamentals', 'CINEMATOGRAPHY', 
 '{"name": "Michael Rodriguez", "bio": "Award-winning cinematographer with 20+ years experience", "avatar": ""}',
 'Learn the fundamentals of visual storytelling through camera work, composition, and lighting techniques.',
 '6 weeks', 'Beginner', 99.99,
 '[{"title": "Introduction to Visual Storytelling", "duration": 45, "videoUrl": ""}, {"title": "Camera Basics and Movement", "duration": 60, "videoUrl": ""}]'
),
('Advanced Video Editing Techniques', 'EDITING', 
 '{"name": "Lisa Chen", "bio": "Professional editor for major studios", "avatar": ""}',
 'Master professional editing techniques using industry-standard software and workflows.',
 '8 weeks', 'Advanced', 149.99,
 '[{"title": "Timeline Organization", "duration": 50, "videoUrl": ""}, {"title": "Color Correction", "duration": 75, "videoUrl": ""}]'
);

-- Sample Opportunities
INSERT INTO `opportunities` (`type`, `title`, `company`, `description`, `details`, `deadline`, `location`, `category`) VALUES
('GRANT', 'Emerging Filmmaker Grant 2024', 'Film Foundation', 'Supporting new voices in cinema with funding up to $50,000 for debut features.', 
 '{"funding": "$50,000", "duration": "12 months", "requirements": ["First-time feature director", "Completed script"]}',
 DATE_ADD(NOW(), INTERVAL 60 DAY), 'Global', 'Feature Films'
),
('JOB', 'Video Editor Position', 'Creative Studios Inc', 'Full-time video editor position for commercial and corporate content.',
 '{"salary": "$55,000 - $70,000", "requirements": ["3+ years experience", "Premiere Pro", "After Effects"]}',
 DATE_ADD(NOW(), INTERVAL 30 DAY), 'Remote', 'Post-Production'
),
('COMPETITION', 'Short Film Festival 2024', 'Indie Film Fest', 'Annual competition for short films under 20 minutes.',
 '{"prizes": "Winner receives $10,000 + distribution deal", "categories": ["Drama", "Comedy", "Documentary"]}',
 DATE_ADD(NOW(), INTERVAL 90 DAY), 'Various Cities', 'Short Films'
);

-- Sample Portfolios
INSERT INTO `portfolios` (`user_id`, `title`, `description`, `category`, `tags`, `views`) VALUES
(1, 'Urban Stories', 'A documentary exploring life in modern cities through the eyes of street artists.', 
 'Documentaries', '["urban", "street art", "documentary", "social commentary"]', 1250),
(1, 'Midnight Drive', 'A noir-inspired short film about a late-night taxi driver in the city.',
 'Short Films', '["noir", "thriller", "urban", "night photography"]', 890),
(3, 'Brand Commercial Reel', 'Collection of commercial work for various brands and products.',
 'Commercials', '["commercial", "branding", "product", "marketing"]', 650);

-- Sample Mentorships
INSERT INTO `mentorships` (`mentor_id`, `mentee_id`, `status`, `specialties`, `bio`, `years_experience`, `available_slots`) VALUES
(2, 1, 'active', '["Directing", "Screenwriting", "Film Production"]', 
 'Experienced mentor helping emerging filmmakers develop their craft and navigate the industry.', 
 15, 3);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Additional indexes for better query performance
CREATE INDEX `idx_courses_category_level` ON `courses`(`category`, `level`);
CREATE INDEX `idx_opportunities_type_deadline` ON `opportunities`(`type`, `deadline`);
CREATE INDEX `idx_portfolios_user_category` ON `portfolios`(`user_id`, `category`);
CREATE INDEX `idx_users_type_verified` ON `users`(`user_type`, `is_verified`);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View for user statistics
CREATE VIEW `user_stats` AS
SELECT 
  u.id,
  u.name,
  u.email,
  u.user_type,
  COUNT(DISTINCT p.id) as portfolio_count,
  COUNT(DISTINCT ce.id) as enrolled_courses_count,
  COUNT(DISTINCT oa.id) as applications_count,
  u.followers,
  u.following,
  u.projects,
  u.awards
FROM users u
LEFT JOIN portfolios p ON u.id = p.user_id
LEFT JOIN course_enrollments ce ON u.id = ce.user_id
LEFT JOIN opportunity_applications oa ON u.id = oa.user_id
GROUP BY u.id;

-- View for popular courses
CREATE VIEW `popular_courses` AS
SELECT 
  c.*,
  COUNT(ce.id) as enrollment_count,
  COALESCE(AVG(ce.progress), 0) as avg_progress
FROM courses c
LEFT JOIN course_enrollments ce ON c.id = ce.course_id
GROUP BY c.id
ORDER BY enrollment_count DESC, c.created_at DESC;

-- View for active opportunities
CREATE VIEW `active_opportunities` AS
SELECT 
  o.*,
  COUNT(oa.id) as applications_count
FROM opportunities o
LEFT JOIN opportunity_applications oa ON o.id = oa.opportunity_id
WHERE o.is_active = TRUE 
  AND o.deadline > NOW()
GROUP BY o.id
ORDER BY o.deadline ASC;

-- ============================================================================
-- STORED PROCEDURES
-- ============================================================================

DELIMITER //

-- Procedure to update user stats
CREATE PROCEDURE UpdateUserStats(IN user_id INT)
BEGIN
  DECLARE portfolio_count INT DEFAULT 0;
  
  -- Count portfolios
  SELECT COUNT(*) INTO portfolio_count 
  FROM portfolios 
  WHERE user_id = user_id;
  
  -- Update user projects count
  UPDATE users 
  SET projects = portfolio_count 
  WHERE id = user_id;
END //

-- Procedure to clean up expired opportunities
CREATE PROCEDURE CleanupExpiredOpportunities()
BEGIN
  UPDATE opportunities 
  SET is_active = FALSE 
  WHERE deadline < NOW() AND is_active = TRUE;
END //

DELIMITER ;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

DELIMITER //

-- Trigger to update user stats when portfolio is added
CREATE TRIGGER update_user_stats_after_portfolio_insert
AFTER INSERT ON portfolios
FOR EACH ROW
BEGIN
  UPDATE users 
  SET projects = projects + 1 
  WHERE id = NEW.user_id;
END //

-- Trigger to update user stats when portfolio is deleted
CREATE TRIGGER update_user_stats_after_portfolio_delete
AFTER DELETE ON portfolios
FOR EACH ROW
BEGIN
  UPDATE users 
  SET projects = projects - 1 
  WHERE id = OLD.user_id;
END //

-- Trigger to update portfolio views
CREATE TRIGGER increment_portfolio_views
AFTER INSERT ON portfolio_likes
FOR EACH ROW
BEGIN
  UPDATE portfolios 
  SET views = views + 1 
  WHERE id = NEW.portfolio_id;
END //

DELIMITER ;

-- ============================================================================
-- FINAL SETUP
-- ============================================================================

-- Set timezone
SET time_zone = '+00:00';

-- Optimize tables
OPTIMIZE TABLE users, courses, opportunities, portfolios;

-- Show completion message
SELECT 'Database schema created successfully! You can now run your Flask server.' as message;