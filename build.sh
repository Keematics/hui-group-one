#!/usr/bin/env bash
# =====================================
# Render.com Build Script
# =====================================
# This script is executed by Render during the build process
# It sets up the environment and prepares the application for deployment

# Exit on error - if any command fails, stop the build
set -o errexit

# =====================================
# STEP 1: Install Python Dependencies
# =====================================
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# =====================================
# STEP 2: Collect Static Files
# =====================================
# Django needs to collect all static files (CSS, JS, images) into a single directory
# WhiteNoise will serve these files efficiently in production
echo "Collecting static files..."
python manage.py collectstatic --no-input

# =====================================
# STEP 3: Run Database Migrations
# =====================================
# Apply all database migrations to create/update database schema
# Render automatically provides DATABASE_URL environment variable
echo "Running database migrations..."
python manage.py migrate --no-input

# =====================================
# STEP 4: Create Superuser (Optional)
# =====================================
# Uncomment the following lines to create a superuser automatically
# Make sure to set these environment variables in Render dashboard:
# - DJANGO_SUPERUSER_USERNAME
# - DJANGO_SUPERUSER_PASSWORD
# - DJANGO_SUPERUSER_EMAIL

# echo "Creating superuser..."
# python manage.py createsuperuser \
#     --noinput \
#     --username $DJANGO_SUPERUSER_USERNAME \
#     --email $DJANGO_SUPERUSER_EMAIL || true

echo "Build completed successfully!"
