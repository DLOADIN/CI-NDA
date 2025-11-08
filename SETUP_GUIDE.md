# CI-NDA Full-Stack Application Setup Guide

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.8+** - Download from [python.org](https://python.org)
- **XAMPP/MySQL** - Download from [apachefriends.org](https://apachefriends.org)
- **Web Browser** - Chrome, Firefox, Edge, or Safari

### 2. Database Setup
1. **Start XAMPP Control Panel**
2. **Start MySQL service**
3. **Open phpMyAdmin** (usually http://localhost/phpmyadmin)
4. **Create database:**
   - Click "New" in phpMyAdmin
   - Database name: `ci_nda_db`
   - Collation: `utf8mb4_general_ci`
   - Click "Create"
5. **Import schema:**
   - Select `ci_nda_db` database
   - Click "Import" tab
   - Choose file: `database_schema.sql`
   - Click "Go"

### 3. Environment Configuration
1. **Copy the example environment file:**
   ```
   cp .env.example .env
   ```
   Or manually create `.env` file with your database settings:
   ```
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=
   DB_NAME=ci_nda_db
   JWT_SECRET=your-super-secret-jwt-key-here
   CORS_ORIGINS=http://localhost:5000,http://127.0.0.1:5000
   ```

### 4. Installation
**Option A: Automatic (Windows)**
- Double-click `start.bat`
- Follow the prompts

**Option B: Manual**
```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python server.py
```

### 5. Access the Application
- **Main Application:** http://localhost:5000
- **Authentication:** http://localhost:5000/authentication.html
- **Backend Test:** http://localhost:5000/test_backend.html
- **API Documentation:** http://localhost:5000/api

## 🔧 Application Features

### Frontend Pages
- **index.html** - Homepage with featured content
- **authentication.html** - Login/Register with toggle functionality
- **courses.html** - Browse and search courses
- **opportunities.html** - Find funding and job opportunities
- **portfolios.html** - Showcase and browse filmmaker portfolios
- **mentorship.html** - Connect with industry mentors
- **profile.html** - User dashboard and profile management

### Backend APIs
- **Authentication:** `/api/auth/login`, `/api/auth/register`
- **Courses:** `/api/courses` (CRUD operations)
- **Opportunities:** `/api/opportunities` (CRUD operations)
- **Portfolios:** `/api/portfolios` (CRUD operations)
- **Mentorships:** `/api/mentorships` (CRUD operations)
- **Users:** `/api/users` (profile management)

### Database Schema
- **users** - User accounts and authentication
- **courses** - Film education courses
- **opportunities** - Funding and job opportunities
- **portfolios** - User portfolio showcases
- **mentorships** - Mentor-mentee relationships

## 🛠 Troubleshooting

### Common Issues

**1. "Database connection failed"**
- Ensure MySQL is running in XAMPP
- Check database credentials in `.env`
- Verify database `ci_nda_db` exists
- Import `database_schema.sql` if tables are missing

**2. "Python not found"**
- Install Python 3.8+ from python.org
- Add Python to system PATH
- Restart command prompt/terminal

**3. "Module not found" errors**
- Run: `pip install -r requirements.txt`
- Use virtual environment if needed:
  ```bash
  python -m venv venv
  venv\Scripts\activate  # Windows
  source venv/bin/activate  # Linux/Mac
  pip install -r requirements.txt
  ```

**4. "Port 5000 already in use"**
- Close other applications using port 5000
- Or change port in `server.py` and `.env`

**5. CORS errors**
- Check `CORS_ORIGINS` in `.env`
- Ensure frontend URL matches allowed origins

### Database Issues
- **Reset database:** Drop `ci_nda_db` and recreate with schema
- **Check logs:** Look for MySQL error messages in XAMPP logs
- **Permissions:** Ensure MySQL user has proper privileges

## 📚 API Usage Examples

### Authentication
```javascript
// Register new user
const response = await api.register({
  email: 'user@example.com',
  password: 'password123',
  firstName: 'John',
  lastName: 'Doe',
  userType: 'filmmaker'
});

// Login
const response = await api.login({
  email: 'user@example.com',
  password: 'password123',
  userType: 'filmmaker'
});
```

### Courses
```javascript
// Get all courses
const courses = await api.getCourses();

// Create new course
const course = await api.createCourse({
  title: 'Cinematography Basics',
  description: 'Learn the fundamentals of cinematography',
  instructor: 'Roger Deakins',
  duration: '8 weeks',
  price: 299.99
});
```

## 🔐 Security Features
- **JWT Authentication** - Secure token-based authentication
- **Password Hashing** - bcrypt for secure password storage
- **CORS Protection** - Configured allowed origins
- **Input Validation** - Server-side validation for all inputs
- **SQL Injection Prevention** - Parameterized queries

## 🌟 Additional Features
- **Search Functionality** - Real-time search across all content
- **Filter Options** - Advanced filtering for courses, opportunities
- **Responsive Design** - Mobile-friendly interface
- **Dynamic Content** - Real-time updates from backend
- **User Authentication** - Secure login/register system

## 📞 Support
If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Check browser console for error messages
4. Test backend connectivity using `/test_backend.html`

## 🔄 Development
For development and customization:
- Frontend files: HTML, CSS, JavaScript
- Backend: Flask Python application
- Database: MySQL with phpMyAdmin interface
- API client: `public/js/api.js`

The application is now fully integrated and ready for use!