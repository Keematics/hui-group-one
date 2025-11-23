# 🚀 Deployment Guide for Render.com

This guide provides step-by-step instructions for deploying your Django Learning Platform on Render.com.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Prepare for Deployment](#prepare-for-deployment)
3. [Deploy to Render](#deploy-to-render)
4. [Post-Deployment Configuration](#post-deployment-configuration)
5. [Managing Your Application](#managing-your-application)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Prerequisites

Before deploying, ensure you have:

- [ ] A GitHub or GitLab account with your code pushed
- [ ] A Render.com account (sign up at https://render.com)
- [ ] A Cloudinary account (sign up at https://cloudinary.com)
- [ ] PostgreSQL installed locally for testing (optional but recommended)

---

## 🛠️ Prepare for Deployment

### Step 1: Get Cloudinary Credentials

1. Go to https://cloudinary.com and sign up/login
2. Navigate to Dashboard → Settings → Account
3. Copy the following credentials:
   - **Cloud Name**
   - **API Key**
   - **API Secret**
4. Keep these handy - you'll need them later

### Step 2: Test Locally with PostgreSQL (Recommended)

```bash
# Install PostgreSQL
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Windows: Download from https://www.postgresql.org/download/windows/

# Start PostgreSQL service
# macOS
brew services start postgresql

# Ubuntu/Debian
sudo service postgresql start

# Create database
createdb learning_platform

# Update .env file with your PostgreSQL password
DB_PASSWORD=your_password_here

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Test the application
python manage.py runserver
```

### Step 3: Push Code to GitHub

```bash
# Make sure all changes are committed
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

---

## 🌐 Deploy to Render

### Method 1: Using render.yaml (Recommended - Automated)

1. **Go to Render Dashboard**
   - Visit https://dashboard.render.com
   - Login with your account

2. **Create New Blueprint**
   - Click **"New +"** button in top right
   - Select **"Blueprint"**

3. **Connect Repository**
   - Choose **"Connect GitHub"** or **"Connect GitLab"**
   - Authorize Render to access your repositories
   - Select your **hui-group-one** repository

4. **Configure Blueprint**
   - Render will automatically detect `render.yaml`
   - Review the services to be created:
     - PostgreSQL database
     - Web service
   - Click **"Apply"**

5. **Wait for Deployment**
   - Render will create the database first (~2 minutes)
   - Then build and deploy your web service (~5-10 minutes)
   - Watch the logs in real-time

6. **Deployment Complete!**
   - Your app URL will be: `https://learning-platform-XXXX.onrender.com`
   - The database will be automatically connected

### Method 2: Manual Setup (Alternative)

If you prefer manual setup or render.yaml doesn't work:

#### Create Database

1. Click **"New +"** → **"PostgreSQL"**
2. Configure:
   - Name: `learning-platform-db`
   - Database: `learning_platform`
   - User: `learning_platform_user`
   - Region: Choose closest to you
   - Plan: **Free**
3. Click **"Create Database"**
4. Copy the **Internal Database URL** (starts with `postgresql://`)

#### Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your repository
3. Configure:
   - **Name**: `learning-platform`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn learning_platform.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
   - **Plan**: **Free**

4. **Add Environment Variables** (click "Advanced"):
   ```
   DEBUG=False
   SECRET_KEY=(click "Generate" button)
   DATABASE_URL=(paste the Internal Database URL from database)
   ALLOWED_HOSTS=.onrender.com
   ```

5. Click **"Create Web Service"**

---

## ⚙️ Post-Deployment Configuration

### Step 1: Add Cloudinary Credentials

1. Go to your web service in Render dashboard
2. Click **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Add these three variables:

   ```
   CLOUDINARY_CLOUD_NAME = your_cloud_name
   CLOUDINARY_API_KEY = your_api_key
   CLOUDINARY_API_SECRET = your_api_secret  (mark as "Secret")
   ```

5. Click **"Save Changes"**
6. Your service will automatically redeploy

### Step 2: Create Superuser Account

**Option A: Using Shell (Recommended)**

1. Go to your web service → **"Shell"** tab
2. Wait for shell to connect
3. Run these commands:
   ```bash
   python manage.py createsuperuser
   ```
4. Follow the prompts:
   - Username: `admin`
   - Email: `your-email@example.com`
   - Password: (choose a strong password)
   - Confirm password: (repeat password)

**Option B: Auto-create on Deployment**

1. Go to web service → **"Environment"** tab
2. Add these variables:
   ```
   DJANGO_SUPERUSER_USERNAME = admin
   DJANGO_SUPERUSER_PASSWORD = your_secure_password (mark as "Secret")
   DJANGO_SUPERUSER_EMAIL = admin@example.com
   ```
3. Uncomment the superuser creation section in `build.sh`:
   ```bash
   # Remove the # from these lines
   echo "Creating superuser..."
   python manage.py createsuperuser \
       --noinput \
       --username $DJANGO_SUPERUSER_USERNAME \
       --email $DJANGO_SUPERUSER_EMAIL || true
   ```
4. Push changes and redeploy

### Step 3: Set Group Members as Instructors

1. Access admin panel: `https://your-app.onrender.com/admin`
2. Login with superuser credentials
3. Go to **Users**
4. For each group member:
   - Click on their username
   - Scroll to **"Additional Info"** section
   - Change **Role** to **"Instructor"**
   - Click **"Save"**

5. Go to **Group Members**
6. Add each group member:
   - Select the user
   - Add matric number
   - Add title (e.g., "Group Leader", "Developer")
   - Check **"Is leader"** for the group leader
   - Set display order (1, 2, 3...)
   - Click **"Save"**

---

## 📊 Managing Your Application

### Viewing Logs

1. Go to your web service in Render dashboard
2. Click **"Logs"** tab
3. View real-time application logs
4. Use for debugging errors

### Manual Deploy

1. Go to your web service
2. Click **"Manual Deploy"** button
3. Select **"Deploy latest commit"**
4. Use this after:
   - Pushing new code
   - Changing environment variables
   - Troubleshooting issues

### Running Management Commands

1. Go to web service → **"Shell"** tab
2. Run Django commands:
   ```bash
   # Create migrations
   python manage.py makemigrations

   # Apply migrations
   python manage.py migrate

   # Collect static files
   python manage.py collectstatic --no-input

   # Create superuser
   python manage.py createsuperuser

   # Access Django shell
   python manage.py shell
   ```

### Database Management

1. Go to your PostgreSQL database in Render dashboard
2. Click **"Info"** tab to see connection details
3. Click **"Connect"** tab for connection commands
4. Use tools like pgAdmin or psql to manage database

### Monitoring

1. **Health Checks**: Render automatically monitors your app
2. **Metrics**: View in dashboard (requests, response times, errors)
3. **Alerts**: Configure in Settings → Notifications

---

## 🔧 Troubleshooting

### Issue: App returns 400 Bad Request

**Cause**: ALLOWED_HOSTS not configured correctly

**Solution**:
1. Go to Environment variables
2. Update ALLOWED_HOSTS:
   ```
   ALLOWED_HOSTS=.onrender.com,your-app-name.onrender.com
   ```
3. Or to allow all (development only):
   ```
   ALLOWED_HOSTS=*
   ```

### Issue: Static files not loading (CSS/JS missing)

**Cause**: Static files not collected or WhiteNoise not configured

**Solution**:
1. Check build logs - should see "Collecting static files..."
2. If not collected, run in Shell:
   ```bash
   python manage.py collectstatic --no-input
   ```
3. Verify `whitenoise` is in requirements.txt
4. Check settings.py has WhiteNoise middleware

### Issue: Images/videos not uploading

**Cause**: Cloudinary credentials missing or incorrect

**Solution**:
1. Verify Cloudinary credentials in Environment variables
2. Check if they're correct (copy from Cloudinary dashboard)
3. Ensure CLOUDINARY_API_SECRET is marked as "Secret"
4. Redeploy after adding/fixing credentials

### Issue: Database connection error

**Cause**: DATABASE_URL not set or database not created

**Solution**:
1. Check Environment variables for DATABASE_URL
2. Should start with `postgresql://`
3. If using Blueprint, database should be auto-connected
4. If manual setup, copy Internal Database URL from database
5. Make sure database and web service are in same region

### Issue: App sleeps and cold starts (Free tier)

**Cause**: Free tier spins down after 15 minutes of inactivity

**Solution**:
1. This is normal for free tier
2. First request after sleep takes 30-60 seconds
3. For production, upgrade to paid plan ($7/month)
4. Or use external monitoring service to keep app awake

### Issue: Build fails

**Cause**: Various reasons - check build logs

**Common fixes**:
1. Check build.sh has execute permissions:
   ```bash
   chmod +x build.sh
   git add build.sh
   git commit -m "Make build.sh executable"
   git push
   ```

2. Check requirements.txt is correct
3. Look for error in build logs
4. Common errors:
   - Missing dependencies
   - Python version mismatch
   - Syntax errors in code

### Issue: Migrations fail

**Cause**: Database schema conflicts

**Solution**:
1. In Shell, run:
   ```bash
   python manage.py migrate --fake-initial
   ```
2. Or reset migrations:
   ```bash
   python manage.py migrate --run-syncdb
   ```
3. Last resort: Delete database and recreate (loses all data!)

### Issue: Permission denied when creating courses

**Cause**: User role not set to instructor

**Solution**:
1. Login to admin panel
2. Go to Users
3. Find the user
4. Change Role to "Instructor"
5. Save

---

## 🎓 Best Practices

### Security

- ✅ Set `DEBUG=False` in production (already configured)
- ✅ Use strong SECRET_KEY (Render generates automatically)
- ✅ Mark sensitive variables as "Secret" in Render
- ✅ Use HTTPS (Render provides automatically)
- ✅ Keep API keys secure (never commit to Git)

### Performance

- ✅ Use Cloudinary for media files (not local storage)
- ✅ Enable WhiteNoise for static files (already configured)
- ✅ Use appropriate worker count (2-4 for free tier)
- ✅ Optimize database queries
- ✅ Add database indexes if needed

### Maintenance

- ✅ Regular backups (Render Free: 90-day retention)
- ✅ Monitor logs for errors
- ✅ Keep dependencies updated
- ✅ Test changes locally before deploying
- ✅ Use version control (Git)

---

## 📚 Additional Resources

- **Render Documentation**: https://render.com/docs
- **Django Deployment Checklist**: https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
- **Cloudinary Django**: https://cloudinary.com/documentation/django_integration
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/

---

## ✅ Post-Deployment Checklist

After deployment, verify:

- [ ] App loads at Render URL
- [ ] Admin panel accessible
- [ ] Can login/register users
- [ ] Can create certifications (as instructor)
- [ ] Can create courses (as instructor)
- [ ] Can upload images/videos
- [ ] Can enroll in certifications
- [ ] Progress tracking works
- [ ] Certificates download correctly
- [ ] Group members displayed on homepage
- [ ] Mobile responsive design works

---

## 🎉 Congratulations!

Your Django Learning Platform is now live on Render! Share your URL with your group members and start learning.

**Your App**: `https://your-app-name.onrender.com`

**Admin Panel**: `https://your-app-name.onrender.com/admin`

---

## 💡 Need Help?

- Check Render Community: https://community.render.com
- Django Forum: https://forum.djangoproject.com
- Stack Overflow: Tag questions with `django` and `render.com`

**Good luck with your project! 🚀**
