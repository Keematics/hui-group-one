# LearnHub - Django Learning Management System

A comprehensive learning platform built with Django, featuring professional certifications, progress tracking, and certificate generation.

## 🎓 Project Overview

This is a group assignment project that provides a simplified version of learning platforms like Coursera. It allows users to:

- Register and login with automatic authentication
- Access professional certifications with multiple courses
- Learn through various module types (text, images, videos, or combinations)
- Track progress across all courses and modules
- Earn certificates upon course completion (90% threshold)
- Download professional certification certificates

## 👥 Group Members

*Add your team members here through the Django admin panel*

## ✨ Key Features

### 1. User Authentication
- User registration with automatic login
- Secure login/logout functionality
- Profile management with matric numbers and profile pictures

### 2. Professional Certifications & Courses
- Multiple professional certifications
- Each certification contains multiple courses
- Each course contains multiple modules

### 3. Module Types
- **Text Modules**: Read and mark as complete
- **Picture Modules**: View images and mark as complete
- **Video Modules**: Watch videos with automatic progress tracking (85% threshold)
- **Text + Picture Modules**: Combined content

### 4. Progress Tracking
- Real-time progress tracking with jQuery/AJAX
- Video modules track watch time automatically
- Text/picture modules require manual "mark as read"
- Progress bars at course and certification levels

### 5. Certificate Generation
- Automatic PDF certificate generation
- Course certificates (90% completion required)
- Professional certification certificates (all courses completed)
- Downloadable certificates with unique IDs

### 6. Confetti Animation
- Celebratory confetti animation upon course completion
- Enhances user experience and motivation

## 🛠️ Technology Stack

- **Backend**: Django 5.2.8
- **Database**: MySQL (with PyMySQL adapter)
- **Frontend**: Bootstrap 5, jQuery, Font Awesome
- **Media Storage**: Cloudinary
- **PDF Generation**: ReportLab
- **Environment Management**: python-dotenv

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.11+
- MySQL Server
- Git

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd hui-group-one
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Edit the `.env` file with your configurations:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings (MySQL)
DB_NAME=learning_platform
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_HOST=localhost
DB_PORT=3306

# Cloudinary Settings (Get free account at cloudinary.com)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### 5. Create MySQL Database

```bash
mysql -u root -p
```

```sql
CREATE DATABASE learning_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 8. Create Static Directories

```bash
mkdir -p static/css static/js static/images media
```

### 9. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to see your application!

## 📊 Admin Panel

Access the admin panel at `http://localhost:8000/admin/` to:

- Add professional certifications
- Create courses under certifications
- Add modules to courses
- Manage users and group members
- View progress and certificates

### Adding Content

1. **Create Professional Certification**
   - Login to admin panel
   - Go to Professional Certifications
   - Add title, description, and thumbnail (optional)

2. **Create Courses**
   - Go to Courses
   - Select a certification
   - Add title, description, order number, and thumbnail

3. **Create Modules**
   - Go to Modules
   - Select a course
   - Choose module type (text, picture, video, or text+picture)
   - Add content based on type
   - For videos, add duration in seconds for proper tracking

4. **Add Group Members**
   - Go to Group Members
   - Select a user
   - Add matric number, title, and set if they're the leader
   - Set display order

## 🎯 Usage Guide

### For Students

1. **Register**: Create an account with your details
2. **Browse Certifications**: View available professional certifications
3. **Enroll in Courses**: Start learning from any certification
4. **Complete Modules**:
   - Text/Picture: Click "Mark as Read"
   - Video: Watch at least 85% of the video
5. **Track Progress**: Monitor your progress in the dashboard
6. **Earn Certificates**: Complete 90% of modules to get course certificate
7. **Professional Certificate**: Complete all courses in a certification

### For Administrators

1. Login to `/admin/`
2. Create professional certifications and courses
3. Upload content (videos, images via Cloudinary)
4. Monitor student progress
5. Manage group member profiles

## 📁 Project Structure

```
learning_platform/
├── courses/                 # Main app
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── admin.py            # Admin configurations
│   └── urls.py             # URL patterns
├── learning_platform/       # Project settings
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI configuration
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   └── courses/           # Course templates
├── static/                # Static files
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── images/           # Images
├── media/                 # Uploaded files (local)
├── .env                   # Environment variables
├── .env.example          # Environment template
├── manage.py             # Django management script
└── requirements.txt      # Python dependencies
```

## 🔐 Security Notes

- Never commit `.env` file with real credentials
- Change `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Use strong passwords for admin accounts
- Regularly update dependencies

## 🌐 Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Configure `ALLOWED_HOSTS` with your domain
3. Set up proper MySQL credentials
4. Configure Cloudinary for media storage
5. Collect static files: `python manage.py collectstatic`
6. Use a production server (Gunicorn, uWSGI)
7. Set up HTTPS with Let's Encrypt

## 🐛 Troubleshooting

### MySQL Connection Issues
- Ensure MySQL server is running
- Check database credentials in `.env`
- Verify database exists: `SHOW DATABASES;`

### Cloudinary Upload Issues
- Verify Cloudinary credentials
- Check file size limits
- Ensure proper permissions

### Migration Errors
- Delete migration files (except `__init__.py`)
- Run `python manage.py makemigrations`
- Run `python manage.py migrate`

## 📝 License

This project is created for educational purposes as part of a group assignment.

## 🤝 Contributing

This is a group assignment project. All group members contribute equally.

## 📧 Support

For issues or questions, please contact the group leader.

---

**Built with ❤️ by Group 1**
