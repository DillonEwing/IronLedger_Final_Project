#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Changing to ironledger directory..."
pushd ironledger

echo "Creating staticfiles directory..."
mkdir -p staticfiles

echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "Running migrations..."
python manage.py migrate --no-input

echo "Creating superuser from environment variables..."
python manage.py create_superuser_from_env

echo "Populating sample workout data..."
python manage.py populate_sample_data

echo "Returning to project root..."
popd

echo "Build completed successfully!"
