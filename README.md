# CI-NDA - Filmmaker Platform

A comprehensive platform for filmmakers, mentors, and sponsors to connect, learn, and collaborate.

## Original Mission
**Ci-NDA: A Digital Platform for Cinematography Skill Development & Global Exposure**  
*Prepared by: NTARE GAMA Allan*  
*Institution: African Leadership University*  
*Date: 12/10/2025*

### The Mission
My mission at ALU is to empower Rwandans with the skills and opportunities to thrive in cinematography. Through Ci-NDA, I aim to provide accessible digital resources, mentorship, and exposure pathways that elevate filmmaking standards. This mission seeks to bridge the gap between local talent and international platforms, ensuring that Rwandan stories are told authentically and competitively. By doing so, we strengthen youth employment, cultural identity, and Rwanda's position in the global creative economy.

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or later
- MySQL/MariaDB (or access to phpMyAdmin)
- A modern web browser

### Installation

1. **Clone or download this repository**

2. **Run the setup script** (Windows):
   ```bash
   setup.bat
   ```

3. **Configure database**:
   - Edit `.env` file with your database credentials
   - Import `database_schema.sql` into phpMyAdmin

4. **Start the server**:
   ```bash
   python server.py
   ```

5. **Open your browser** and navigate to your HTML files

## 🗄️ Database Setup

### Using phpMyAdmin:
1. Open phpMyAdmin in your browser
2. Click "Import" tab
3. Choose file: `database_schema.sql`
4. Click "Go" to import

The script will:
- Create the `cinda_db` database
- Create all necessary tables with proper relationships
- Insert sample data for testing
- Set up indexes and views for optimal performance

## 🔧 Configuration

Edit the `.env` file (created from `.env.example`) with your settings:

```env
# Database Configuration
DB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=cinda_db

# Security Keys (change these!)
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/social-login` - Social media login
- `POST /api/auth/logout` - Logout user

### Users
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile

### Courses
- `GET /api/courses` - Get all courses (with filtering)
- `GET /api/courses/:id` - Get specific course
- `POST /api/courses/:id/enroll` - Enroll in course

### Opportunities
- `GET /api/opportunities` - Get all opportunities (with filtering)
- `POST /api/opportunities/:id/apply` - Apply to opportunity

### Portfolios
- `GET /api/portfolios` - Get all portfolios (with filtering)
- `POST /api/portfolios` - Create new portfolio

### File Upload
- `POST /api/upload` - Upload files (images, videos)

### Search
- `GET /api/search` - Global search across all content

## 🏗️ Project Structure

```
CI-NDA/
├── server.py              # Main Flask backend server
├── database_schema.sql    # Complete database schema
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── setup.bat             # Windows setup script
├── public/
│   └── js/
│       └── api.js        # Frontend API client
├── uploads/              # File upload directory
├── *.html               # Frontend pages
└── README.md            # This file
```

## 🔐 Authentication

The system supports:
- Email/password registration and login
- Social media login (Google, Facebook) - ready for integration
- JWT token-based authentication
- Session management
- Password hashing with bcrypt

## 📊 Database Schema

The database includes these main tables:
- `users` - User accounts and profiles
- `courses` - Educational courses
- `course_enrollments` - User course enrollments
- `opportunities` - Jobs, grants, competitions
- `opportunity_applications` - User applications
- `portfolios` - User project portfolios
- `portfolio_likes` - Portfolio likes/reactions
- `portfolio_comments` - Portfolio comments
- `mentorships` - Mentor-mentee relationships
- `mentorship_messages` - Mentorship communications
- `notifications` - System notifications

## 🎯 Features

### For Filmmakers:
- Create and manage portfolios
- Enroll in courses
- Apply to opportunities
- Find mentors
- Search for resources

### For Mentors:
- Offer mentorship programs
- Manage mentee relationships
- Share expertise through courses

### For Sponsors:
- Post opportunities (jobs, grants, competitions)
- Discover talent through portfolios
- Support emerging filmmakers

## 🔍 Search & Filtering

Advanced search capabilities:
- Global search across all content types
- Category-specific filtering
- Date range filtering
- Location-based filtering
- Tag-based filtering

## 📱 Frontend Integration

The frontend API client (`public/js/api.js`) provides:
- Automatic authentication handling
- Error handling and user feedback
- File upload support
- Search functionality
- Real-time data updates

### Usage Example:
```javascript
// Login user
const result = await api.login({ email: 'user@example.com', password: 'password' });

// Get courses
const courses = await api.getCourses({ category: 'CINEMATOGRAPHY', level: 'Beginner' });

// Upload file
const upload = await api.uploadFile(fileInput.files[0]);
```

## 🚦 Running the Application

1. **Start the Flask server**:
   ```bash
   python server.py
   ```

2. **Access the application**:
   - Backend API: http://localhost:5000
   - Frontend: Open any HTML file in your browser
   - Health check: http://localhost:5000/api/health

## 📝 Sample Data

The database comes with sample data including:
- 3 sample users (filmmaker, mentor, sponsor)
- 2 sample courses
- 3 sample opportunities
- 3 sample portfolios
- 1 sample mentorship

## 🔒 Security Features

- Password hashing with bcrypt
- JWT token authentication
- CORS protection
- SQL injection prevention
- File upload security
- Input validation and sanitization

## 🛠️ Development

### Adding New Features:
1. Add database tables/columns as needed
2. Update the Flask routes in `server.py`
3. Update the frontend API client
4. Test thoroughly

### Environment Variables:
Use the `.env` file to configure:
- Database connection
- Security keys
- File upload settings
- CORS origins
- Email settings (for future features)

## 📞 Support

If you encounter issues:
1. Check the console for error messages
2. Verify database connection settings
3. Ensure all Python dependencies are installed
4. Check that the Flask server is running on port 5000

## 🔄 Updates

To update the application:
1. Pull latest changes
2. Run `pip install -r requirements.txt`
3. Check for database schema updates
4. Restart the Flask server

---

**Happy Filmmaking!** 🎬

 Africa’s creative economy is booming, but Rwandan filmmakers lack easy access to structured training and global opportunities. Ci-NDA bridges that gap by making resources and opportunities accessible from anywhere in Rwanda, especially for youth who can’t afford expensive film schools.

2. Problem Statement
      “Rwandan filmmakers lack skills, resources, and exposure.”
Rwandan filmmakers struggle to access the skills, resources, and opportunities needed to compete in today’s global cinema industry. The creative sector contributes less than 2% to Rwanda’s GDP compared to Nigeria’s Nollywood at 5%, highlighting a major gap in growth potential. Filmmakers face a lack of advanced training programs, mentorship, and structured career pathways. Access to professional-grade equipment and affordable learning resources remains limited. Opportunities for international exposure and festival participation are scarce, leaving many unable to showcase their talent on global platforms. Without a centralized system to connect them with knowledge, resources, and opportunities, Rwanda risks underutilizing its creative talent pool.

3. Software Development Model
To address this challenge, the Incremental Prototyping Model will guide the development of the platform. The first phase will deliver a Minimum Viable Product (MVP) featuring mentorship and structured training resources for filmmakers. The second phase will allow users to upload portfolios and access a resource library to elevate their skills. The third phase will integrate tools for festival submissions and international collaboration. Finally, an investor and sponsorship analytics dashboard will connect creators with financial opportunities. This staged model ensures that each release delivers tangible value, reduces upfront risk, and allows feedback-driven improvements. Investors can track growth and fund development gradually, making progress measurable at every step.

4. Hypothesis of the Solution
If aspiring filmmakers are given a digital platform that provides structured learning, mentorship, and access to global opportunities, then Rwanda’s cinema industry can be transformed into a thriving regional hub. With curated resources, creators will sharpen their technical and creative skills while gaining visibility for their work. Portfolio showcases and submission tools will expand their reach to festivals, investors, and distributors worldwide. This will drive youth employment, stimulate innovation, and increase Rwanda’s cultural exports. Within 5–10 years, the country can build a self-sustaining creative ecosystem recognized on global platforms. The solution will bridge the gap between talent, training, and opportunity.



5. References (APA Style)
UNESCO. (2022). The African Creative Economy Report.


Rwanda Development Board. (2023). Creative Industries Policy Brief.


African Union. (2021). Agenda 2063: The Africa We Want.





